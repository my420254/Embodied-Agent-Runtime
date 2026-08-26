from __future__ import annotations

from collections.abc import Callable

from ..dependencies import EvaluationDependencies
from ..models import EvaluationSession, EvaluationStageOutcome
from .semantic import run_semantic_audit
from .state_diff import run_state_diff_audit


AuditStage = Callable[
    [EvaluationSession, EvaluationDependencies],
    EvaluationStageOutcome,
]


def run_evaluation_audits(
    session: EvaluationSession,
    dependencies: EvaluationDependencies,
) -> EvaluationStageOutcome:
    """Run post-simulation audits in their required fail-fast order."""

    stages: tuple[AuditStage, ...] = (
        run_state_diff_audit,
        run_semantic_audit,
    )
    for stage in stages:
        outcome = stage(session, dependencies)
        if outcome is not None:
            return outcome
    return None


__all__ = ["run_evaluation_audits"]
