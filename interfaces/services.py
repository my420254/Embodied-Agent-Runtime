from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from interfaces.contracts import (
    BehaviorTree,
    BehaviorTreeExecutionResult,
    CandidateUpdate,
    CognitiveSkillContract,
    EvidenceRecord,
    KGQuery,
    KGQueryResult,
    SceneQuery,
    SceneQueryResult,
    TaskGraph,
    TodoList,
    ValidationResult,
)


@dataclass(frozen=True)
class BrainTask:
    raw_instruction: str
    feature_flags: dict[str, bool] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BrainPlanResult:
    todo_list: TodoList
    validation: ValidationResult
    task_graph: TaskGraph | None = None
    selected_skill_ids: tuple[str, ...] = ()
    trace: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class KGService(Protocol):
    def query(self, query: KGQuery) -> KGQueryResult:
        ...

    def record_observation(self, evidence: EvidenceRecord) -> str:
        ...

    def propose_update(self, update: CandidateUpdate) -> CandidateUpdate:
        ...

    def commit_validated_update(self, update: CandidateUpdate) -> CandidateUpdate:
        ...


@runtime_checkable
class SceneGraphService(Protocol):
    def query(self, query: SceneQuery) -> SceneQueryResult:
        ...


@runtime_checkable
class TaskGraphBuilder(Protocol):
    def build(self, task: BrainTask) -> TaskGraph:
        ...

    def enrich(self, graph: TaskGraph, kg_result: KGQueryResult, scene_result: SceneQueryResult) -> TaskGraph:
        ...


@runtime_checkable
class SkillLibrary(Protocol):
    def get_candidates(self, task: BrainTask, graph: TaskGraph) -> tuple[CognitiveSkillContract, ...]:
        ...


@runtime_checkable
class LLMReasoner(Protocol):
    def generate_plan(self, task: BrainTask, graph: TaskGraph, skills: tuple[CognitiveSkillContract, ...]) -> TodoList:
        ...

    def repair_plan(self, task: BrainTask, graph: TaskGraph, validation: ValidationResult) -> TodoList:
        ...


@runtime_checkable
class SafetyPolicyEngine(Protocol):
    def validate(self, todo_list: TodoList, graph: TaskGraph | None = None) -> ValidationResult:
        ...


@runtime_checkable
class BehaviorTreeExecutor(Protocol):
    def execute(self, behavior_tree: BehaviorTree, context: dict[str, Any] | None = None) -> BehaviorTreeExecutionResult:
        ...


@runtime_checkable
class BrainOrchestrator(Protocol):
    def plan(self, task: BrainTask) -> BrainPlanResult:
        ...
