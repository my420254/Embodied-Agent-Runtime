from __future__ import annotations

import copy
from dataclasses import dataclass, field
from collections.abc import Callable, Mapping
from enum import Enum
from typing import Any

from graph.state import PlanningState
from .repair_strategies.contracts import RepairSelection


REPAIR_REQUEST_VERSION = "evaluation_repair_v1"
REPAIR_ASSEMBLY_MODES = frozenset({"complete", "strategy"})
REPAIR_REQUEST_FIELDS = frozenset(
    {
        "accepted_prior_repair",
        "assembly_mode",
        "base_prompt",
        "candidate_failure_memory",
        "candidate_failures",
        "failure",
        "merge_context",
        "original_todo_list",
        "prompt",
        "round",
        "skill_contract_mode",
        "stage",
        "strategy_name",
        "version",
        "violations",
    }
)


def validate_evaluation_repair_request(value: Any) -> str:
    """Return an error for malformed or stale cross-node repair requests."""

    if not isinstance(value, dict):
        return "evaluation_repair_request 必须是对象"
    unknown_fields = sorted(set(value) - REPAIR_REQUEST_FIELDS)
    if unknown_fields:
        return "evaluation_repair_request 包含未知字段: " + ", ".join(unknown_fields)
    if value.get("version") != REPAIR_REQUEST_VERSION:
        return f"不支持的 evaluation_repair_request 版本: {value.get('version')!r}"
    if value.get("assembly_mode") not in REPAIR_ASSEMBLY_MODES:
        return f"不支持的 assembly_mode: {value.get('assembly_mode')!r}"
    if not isinstance(value.get("prompt"), str) or not value["prompt"].strip():
        return "evaluation_repair_request 缺少非空 prompt"
    if type(value.get("round")) is not int or value["round"] < 1:
        return "evaluation_repair_request.round 必须是正整数"
    if value.get("stage") not in {"legality", "sandbox"}:
        return f"不支持的 repair stage: {value.get('stage')!r}"
    if not isinstance(value.get("merge_context"), dict):
        return "evaluation_repair_request.merge_context 必须是对象"
    if value["assembly_mode"] == "strategy" and not str(
        value.get("strategy_name", "")
    ).strip():
        return "strategy assembly_mode 缺少 strategy_name"
    return ""


class EvaluationFailureCode(str, Enum):
    """Stable evaluator failure codes; human feedback remains free-form."""

    EMPTY_PLAN = "empty_plan"
    FORMAT_ERROR = "format_error"
    INVALID_ACTION = "invalid_action"
    NAVIGATION_PRECONDITION = "navigation_precondition"
    ACCESSIBILITY = "accessibility"
    CONTAINER_STATE = "container_state"
    ARM_STATE = "arm_state"
    SAFETY_PRECONDITION = "safety_precondition"
    DEVICE_STATE = "device_state"
    SEMANTIC_AUDIT = "semantic_audit"
    STATE_DIFF_AUDIT = "state_diff_audit"
    SCENE_LOAD = "scene_load"
    MODEL_INVOCATION = "model_invocation"
    MODEL_OUTPUT = "model_output"
    CONFIGURATION = "configuration"
    ITERATION_LIMIT = "iteration_limit"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class EvaluationFailure:
    """Structured failure decision passed from a stage to the evaluator."""

    code: EvaluationFailureCode
    issue_type: str
    fix_advice: str
    step: dict[str, Any] = field(default_factory=dict)
    kind: str = "sandbox_failure"
    checkpoint_env: dict[str, Any] = field(default_factory=dict)
    checkpoint_robot: dict[str, Any] = field(default_factory=dict)
    validated_steps: list[dict[str, Any]] = field(default_factory=list)
    todo_list: list[dict[str, Any]] | None = None
    artifacts: dict[str, Any] = field(default_factory=dict)

    @property
    def failed_step(self) -> int | str | None:
        return self.step.get("step") if isinstance(self.step, dict) else None

    @property
    def full_issue(self) -> str:
        if self.kind in {"evaluation_setup", "plan_regeneration"}:
            return self.issue_type
        step_num = self.step.get("step", "?") if isinstance(self.step, dict) else "?"
        return f"第 {step_num} 步物理拦截: {self.issue_type}"


@dataclass(frozen=True)
class EvaluationContext:
    """Request-scoped values shared by every evaluation stage."""

    state: PlanningState
    feature_flags: dict[str, Any]
    skill_profile: Any
    initial_robot: dict[str, Any]
    structured_task: dict[str, Any]
    iteration_count: int
    max_iterations: int
    intent: str
    memory: dict[str, Any]
    injected_rule_ids: list[str]


@dataclass(frozen=True)
class EvaluationModes:
    sandbox: bool
    state_diff_audit: bool
    repair_selection: RepairSelection
    reuse_validated_prefix: bool


@dataclass(frozen=True)
class EvaluationSkillSnapshot:
    """Profile-scoped skill dependencies frozen for one evaluation request."""

    catalog: Any
    handlers: Mapping[str, Any]
    prompts: str
    apply_action: Callable[[dict, dict, str, dict], tuple[bool, str, str]]


@dataclass(frozen=True)
class CandidateRevision:
    """A candidate replacement that must re-enter the full pipeline."""

    todo_list: list[dict[str, Any]]
    source: str
    artifacts: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SimulationResult:
    """One request-local simulation snapshot consumed by repair and audits."""

    todo_list: list[dict[str, Any]]
    todo_steps: list[dict[str, Any]]
    validated_steps: list[dict[str, Any]]
    final_env: dict[str, Any]
    final_robot: dict[str, Any]
    start_env: dict[str, Any]
    start_robot: dict[str, Any]
    repair_base_env: dict[str, Any]
    repair_base_robot: dict[str, Any]
    trajectory_records: list[dict[str, Any]] = field(default_factory=list)
    failure: EvaluationFailure | None = None
    simulated: bool = False


@dataclass
class EvaluationSession:
    """Mutable state passed between the simulation and audit stages."""

    context: EvaluationContext
    modes: EvaluationModes
    todo_list: list[dict[str, Any]]
    prefix_steps: list[dict[str, Any]]
    skills: EvaluationSkillSnapshot
    validation_env: dict[str, Any]
    simulation: SimulationResult
    repair_history: list[dict[str, Any]] = field(default_factory=list)
    state_diff_audit_payload: dict[str, Any] | None = None
    pending_recovery_actions: list[dict[str, Any]] = field(default_factory=list)

    @property
    def skill_catalog(self) -> Any:
        return self.skills.catalog

    @property
    def skill_handlers(self) -> Mapping[str, Any]:
        return self.skills.handlers

    def trajectory(self) -> str:
        return "\n".join(
            f"Step {step.get('step')}: "
            f"{step.get('execution', {}).get('skill')}"
            f"({list(step.get('execution', {}).get('parameters', {}).values())})"
            for step in self.simulation.todo_steps
        )

    def replace_candidate(self, todo_list: list[dict[str, Any]]) -> None:
        """Replace the candidate while keeping its executable view in sync."""

        self.todo_list = copy.deepcopy(todo_list)
        self.simulation = self._pending_simulation()
        self.state_diff_audit_payload = None

    def record_repair(self, entry: Mapping[str, Any]) -> None:
        self.repair_history.append(copy.deepcopy(dict(entry)))

    def apply_revision(self, revision: CandidateRevision) -> None:
        """Apply one post-audit revision as an atomic session transition."""

        self.replace_candidate(revision.todo_list)
        recovery_actions = revision.artifacts.get("recovery_actions", [])
        self.pending_recovery_actions = (
            copy.deepcopy(recovery_actions)
            if isinstance(recovery_actions, list)
            else []
        )
        self.record_repair(
            {
                "stage": revision.source,
                "generated_count": len(self.pending_recovery_actions),
            }
        )

    def record_simulation(self, result: SimulationResult) -> None:
        """Publish one complete simulation result to downstream stages."""

        self.todo_list = copy.deepcopy(result.todo_list)
        self.simulation = result

    def _pending_simulation(self) -> SimulationResult:
        todo_list = copy.deepcopy(self.todo_list)
        todo_steps = (
            todo_list[len(self.prefix_steps) :]
            if self.modes.reuse_validated_prefix
            else todo_list
        )
        validated_steps = (
            copy.deepcopy(self.prefix_steps)
            if self.modes.reuse_validated_prefix
            else []
        )
        initial_env = copy.deepcopy(self.simulation.repair_base_env)
        initial_robot = copy.deepcopy(self.simulation.repair_base_robot)
        return SimulationResult(
            todo_list=todo_list,
            todo_steps=todo_steps,
            validated_steps=validated_steps,
            final_env=copy.deepcopy(initial_env),
            final_robot=copy.deepcopy(initial_robot),
            start_env=copy.deepcopy(self.simulation.start_env),
            start_robot=copy.deepcopy(self.simulation.start_robot),
            repair_base_env=copy.deepcopy(initial_env),
            repair_base_robot=copy.deepcopy(initial_robot),
        )


EvaluationStageOutcome = CandidateRevision | EvaluationFailure | None


__all__ = [
    "EvaluationFailure",
    "EvaluationFailureCode",
    "EvaluationContext",
    "CandidateRevision",
    "EvaluationModes",
    "EvaluationSession",
    "SimulationResult",
    "EvaluationStageOutcome",
    "EvaluationSkillSnapshot",
    "REPAIR_ASSEMBLY_MODES",
    "REPAIR_REQUEST_VERSION",
    "validate_evaluation_repair_request",
]
