from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .outcomes.handoff import CheckpointFailureHandoff
    from .repair_strategies.contracts import RepairStrategyRegistry


@dataclass(frozen=True)
class EvaluationDependencies:
    """Infrastructure used by the planning evaluation pipeline."""

    apply_sandbox_action: Callable[..., tuple[bool, str, str]]
    get_full_flat_house: Callable[[Any], dict]
    get_planning_llm: Callable[[], Any]
    load_skill_catalog: Callable[[str | None], Any]
    load_enabled_skill_prompts: Callable[..., str]
    record_rule_feedback: Callable[..., Any]
    learn_from_success: Callable[..., Any]
    save_evaluator_finding: Callable[..., Any]
    trace_recorder_factory: Callable[[], Any]
    get_skill_handlers: Callable[[str | None], dict[str, Any]]
    repair_registry: RepairStrategyRegistry
    failure_handoff: CheckpointFailureHandoff


__all__ = ["EvaluationDependencies"]
