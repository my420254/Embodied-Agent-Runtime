from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


CORE_KG_RELATIONS = (
    "category",
    "affords",
    "requires_tool",
    "requires_state",
    "precondition_of",
    "effect_of",
    "uses_primitive",
    "applicable_when",
    "conflicts_with",
    "user_prefers",
    "evidence_for",
    "counterexample_of",
)

SCENE_GRAPH_RELATIONS = (
    "located_in",
    "contains",
    "has_state",
)

PLANNING_RELATION_ALLOWLIST = (
    *SCENE_GRAPH_RELATIONS,
    "category",
    "affords",
    "requires_tool",
    "requires_state",
    "precondition_of",
    "effect_of",
    "conflicts_with",
    "uses_primitive",
    "applicable_when",
    "user_prefers",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:12]}"


_ISO_DURATION_RE = re.compile(
    r"^P(?=\d|T\d)(?:(?:\d+Y)?(?:\d+M)?(?:\d+W)?(?:\d+D)?)(?:T(?:\d+H)?(?:\d+M)?(?:\d+S)?)?$"
)


def _is_valid_ttl(value: str | None) -> bool:
    return bool(str(value or "").strip() and _ISO_DURATION_RE.fullmatch(str(value).strip()))


def is_valid_ttl(value: str | None) -> bool:
    return _is_valid_ttl(value)


class UpdateStatus(str, Enum):
    CANDIDATE = "candidate"
    VALIDATED = "validated"
    COMMITTED = "committed"
    REJECTED = "rejected"


class CandidateUpdateKind(str, Enum):
    FACT = "fact"
    PREFERENCE = "preference"
    RULE = "rule"
    SKILL = "skill"
    RELATION_TYPE = "relation_type"


@dataclass(frozen=True)
class EvidenceRecord:
    source: str
    content: dict[str, Any]
    evidence_id: str = field(default_factory=lambda: _id("evidence"))
    confidence: float = 1.0
    timestamp: str = field(default_factory=_now_iso)
    ttl: str | None = None
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not str(self.source or "").strip():
            raise ValueError("evidence records require source provenance")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("evidence record confidence must be between 0 and 1")
        if self.ttl is not None and not _is_valid_ttl(self.ttl):
            raise ValueError("evidence record TTL must be an ISO-8601 duration")


@dataclass(frozen=True)
class CandidateUpdate:
    kind: CandidateUpdateKind
    payload: dict[str, Any]
    proposed_by: str
    evidence_ids: tuple[str, ...] = ()
    confidence: float = 1.0
    ttl: str | None = None
    candidate_id: str = field(default_factory=lambda: _id("candidate"))
    status: UpdateStatus = UpdateStatus.CANDIDATE
    reason: str = ""
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)

    def validate(self) -> "CandidateUpdate":
        if self.status is not UpdateStatus.CANDIDATE:
            raise ValueError(f"only candidate updates can be validated, got {self.status.value}")
        if not self.evidence_ids:
            raise ValueError("candidate updates require evidence before validation")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("candidate update confidence must be between 0 and 1")
        if not str(self.proposed_by or "").strip():
            raise ValueError("candidate updates require provenance before validation")
        if not _is_valid_ttl(self.ttl):
            raise ValueError("candidate updates require ISO-8601 TTL before validation")
        return replace(self, status=UpdateStatus.VALIDATED, updated_at=_now_iso())

    def reject(self, reason: str) -> "CandidateUpdate":
        if self.status is UpdateStatus.COMMITTED:
            raise ValueError("committed updates cannot be rejected")
        return replace(self, status=UpdateStatus.REJECTED, reason=reason, updated_at=_now_iso())

    def commit(self) -> "CandidateUpdate":
        if self.status is not UpdateStatus.VALIDATED:
            raise ValueError("candidate updates must be validated before commit")
        return replace(self, status=UpdateStatus.COMMITTED, updated_at=_now_iso())


@dataclass(frozen=True)
class KGQuery:
    query_type: str
    payload: dict[str, Any]
    view: str = "planning"
    relation_allowlist: tuple[str, ...] = PLANNING_RELATION_ALLOWLIST
    max_hops: int = 2
    node_budget: int = 50
    edge_budget: int = 120


@dataclass(frozen=True)
class KGQueryResult:
    query_type: str
    facts: tuple[dict[str, Any], ...] = ()
    constraints: tuple[dict[str, Any], ...] = ()
    candidate_skills: tuple[str, ...] = ()
    scene_queries_needed: tuple[dict[str, Any], ...] = ()
    unknowns: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class SceneQuery:
    query_type: str
    payload: dict[str, Any]
    view: str = "runtime"


@dataclass(frozen=True)
class SceneQueryResult:
    query_type: str
    instances: tuple[dict[str, Any], ...] = ()
    states: dict[str, Any] = field(default_factory=dict)
    unknowns: tuple[str, ...] = ()


@dataclass(frozen=True)
class TaskGraphNode:
    node_id: str
    node_type: str
    label: str
    data: dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class TaskGraphEdge:
    source_id: str
    target_id: str
    relation: str
    data: dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class TaskGraph:
    goal: str
    task_graph_id: str = field(default_factory=lambda: _id("taskgraph"))
    nodes: tuple[TaskGraphNode, ...] = ()
    edges: tuple[TaskGraphEdge, ...] = ()
    missing_facts: tuple[str, ...] = ()
    relation_allowlist: tuple[str, ...] = PLANNING_RELATION_ALLOWLIST
    max_hops: int = 2
    node_budget: int = 50
    edge_budget: int = 120
    phase_view: str = "planning"

    def add_node(self, node: TaskGraphNode) -> "TaskGraph":
        if any(existing.node_id == node.node_id for existing in self.nodes):
            return self
        if len(self.nodes) >= self.node_budget:
            raise ValueError("task graph node budget exceeded")
        return replace(self, nodes=(*self.nodes, node))

    def add_edge(self, edge: TaskGraphEdge) -> "TaskGraph":
        if edge.relation not in self.relation_allowlist:
            raise ValueError(f"relation {edge.relation!r} is not allowed in this task graph")
        if len(self.edges) >= self.edge_budget:
            raise ValueError("task graph edge budget exceeded")
        return replace(self, edges=(*self.edges, edge))

    def with_missing_fact(self, fact: str) -> "TaskGraph":
        if fact in self.missing_facts:
            return self
        return replace(self, missing_facts=(*self.missing_facts, fact))


@dataclass(frozen=True)
class PrimitiveToolContract:
    name: str
    parameters: dict[str, str]
    preconditions: tuple[str, ...] = ()
    effects: tuple[str, ...] = ()
    handler: str = ""
    safety_tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class CognitiveSkillContract:
    skill_id: str
    description: str
    parameters: dict[str, str]
    uses_primitives: tuple[str, ...]
    applicable_when: tuple[str, ...] = ()
    kg_queries: tuple[dict[str, Any], ...] = ()
    success_criteria: tuple[str, ...] = ()
    failure_policy: dict[str, Any] = field(default_factory=dict)
    status: str = "candidate"
    version: str = "0.1.0"


@dataclass(frozen=True)
class PlanStep:
    step: int
    skill: str
    parameters: dict[str, Any]
    preconditions: tuple[str, ...] = ()
    expected_effects: tuple[str, ...] = ()
    success_check: tuple[str, ...] = ()
    failure_policy: dict[str, Any] = field(default_factory=dict)
    retry_policy: dict[str, Any] = field(default_factory=dict)

    def as_todo_step(self) -> dict[str, Any]:
        step: dict[str, Any] = {
            "step": self.step,
            "execution": {
                "skill": self.skill,
                "parameters": self.parameters,
            },
        }
        if self.preconditions:
            step["preconditions"] = list(self.preconditions)
        if self.expected_effects:
            step["expected_effects"] = list(self.expected_effects)
        if self.success_check:
            step["success_check"] = list(self.success_check)
        if self.failure_policy:
            step["failure_policy"] = dict(self.failure_policy)
        if self.retry_policy:
            step["retry_policy"] = dict(self.retry_policy)
        return step


@dataclass(frozen=True)
class TodoList:
    steps: tuple[PlanStep, ...]
    source_skill_id: str | None = None
    task_graph_id: str | None = None

    def as_todo_list(self) -> list[dict[str, Any]]:
        return [step.as_todo_step() for step in self.steps]

    def as_legacy_todo_list(self) -> list[dict[str, Any]]:
        return self.as_todo_list()


@dataclass(frozen=True)
class BehaviorTreeNode:
    node_id: str
    node_type: str
    name: str
    children: tuple["BehaviorTreeNode", ...] = ()
    action: dict[str, Any] = field(default_factory=dict)
    conditions: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "id": self.node_id,
            "type": self.node_type,
            "name": self.name,
            "children": [child.as_dict() for child in self.children],
        }
        if self.action:
            payload["action"] = dict(self.action)
        if self.conditions:
            payload["conditions"] = list(self.conditions)
        if self.metadata:
            payload["metadata"] = dict(self.metadata)
        return payload

    def node_count(self) -> int:
        return 1 + sum(child.node_count() for child in self.children)


@dataclass(frozen=True)
class BehaviorTree:
    root: BehaviorTreeNode
    source: str = "todo_list"
    source_skill_id: str | None = None
    task_graph_id: str | None = None
    schema_version: str = "behavior_tree.v1"

    def node_count(self) -> int:
        return self.root.node_count()

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "source": self.source,
            "source_skill_id": self.source_skill_id,
            "task_graph_id": self.task_graph_id,
            "stats": {"nodes": self.node_count()},
            "root": self.root.as_dict(),
        }


@dataclass(frozen=True)
class BehaviorTreeExecutionEvent:
    node_id: str
    node_type: str
    status: str
    name: str = ""
    message: str = ""
    action_result: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "status": self.status,
        }
        if self.name:
            payload["name"] = self.name
        if self.message:
            payload["message"] = self.message
        if self.action_result:
            payload["action_result"] = dict(self.action_result)
        return payload


@dataclass(frozen=True)
class BehaviorTreeExecutionResult:
    status: str
    node_id: str
    node_type: str
    message: str = ""
    action_result: dict[str, Any] = field(default_factory=dict)
    events: tuple[BehaviorTreeExecutionEvent, ...] = ()

    @property
    def succeeded(self) -> bool:
        return self.status == "success"

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.status,
            "succeeded": self.succeeded,
            "node_id": self.node_id,
            "node_type": self.node_type,
            "events": [event.as_dict() for event in self.events],
        }
        if self.message:
            payload["message"] = self.message
        if self.action_result:
            payload["action_result"] = dict(self.action_result)
        return payload


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    issue: str = ""
    fix: str = ""
    layer: str = ""
    failed_step: int | None = None
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class PlanTrace:
    """Queryable trace for explaining a generated cognitive plan."""

    task: str
    orchestration: dict[str, Any] = field(default_factory=dict)
    selected_skill_ids: tuple[str, ...] = ()
    selected_skill_versions: dict[str, str] = field(default_factory=dict)
    kg_query: dict[str, Any] = field(default_factory=dict)
    kg_facts_used: tuple[dict[str, Any], ...] = ()
    kg_constraints_used: tuple[dict[str, Any], ...] = ()
    kg_unknowns: tuple[str, ...] = ()
    scene_queries: tuple[dict[str, Any], ...] = ()
    scene_instances_bound: tuple[dict[str, Any], ...] = ()
    scene_unknowns: tuple[str, ...] = ()
    missing_facts: tuple[str, ...] = ()
    task_graph_stats: dict[str, int] = field(default_factory=dict)
    task_graph_visualization: dict[str, Any] = field(default_factory=dict)
    plan_summary: dict[str, Any] = field(default_factory=dict)
    safety: dict[str, Any] = field(default_factory=dict)
    sandbox: dict[str, Any] = field(default_factory=dict)
    trace_id: str = field(default_factory=lambda: _id("trace"))
    created_at: str = field(default_factory=_now_iso)

    def as_dict(self) -> dict[str, Any]:
        kg_query_type = str(self.kg_query.get("query_type", ""))
        return {
            "trace_id": self.trace_id,
            "created_at": self.created_at,
            "task": self.task,
            "orchestration": dict(self.orchestration),
            "selected_skill_ids": list(self.selected_skill_ids),
            "selected_skill_versions": dict(self.selected_skill_versions),
            "kg_query": dict(self.kg_query),
            "kg_query_type": kg_query_type,
            "kg_facts_used": [dict(fact) for fact in self.kg_facts_used],
            "kg_constraints_used": [dict(constraint) for constraint in self.kg_constraints_used],
            "kg_unknowns": list(self.kg_unknowns),
            "scene_queries": [dict(query) for query in self.scene_queries],
            "scene_instances_bound": [dict(instance) for instance in self.scene_instances_bound],
            "scene_unknowns": list(self.scene_unknowns),
            "missing_facts": list(self.missing_facts),
            "task_graph_stats": dict(self.task_graph_stats),
            "task_graph_visualization": dict(self.task_graph_visualization),
            "plan_summary": dict(self.plan_summary),
            "safety": dict(self.safety),
            "sandbox": dict(self.sandbox),
        }
