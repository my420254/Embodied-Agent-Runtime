from __future__ import annotations

import copy
from dataclasses import dataclass, replace
from typing import Any

from ..dependencies import EvaluationDependencies
from ..models import (
    CandidateRevision,
    EvaluationContext,
    EvaluationFailure,
    EvaluationFailureCode,
    EvaluationSession,
)
from . import trace


@dataclass(frozen=True)
class EvaluationReporter:
    """The only adapter from failure events to planning state artifacts."""

    context: EvaluationContext
    dependencies: EvaluationDependencies
    sandbox_enabled: bool
    repair_enabled: bool = False

    def failure(self, event: EvaluationFailure) -> dict[str, Any]:
        if self.context.iteration_count >= self.context.max_iterations:
            event = replace(event, code=EvaluationFailureCode.ITERATION_LIMIT)

        self.dependencies.save_evaluator_finding(
            event.full_issue,
            event.fix_advice,
            self.context.intent,
            str(event.step),
            feature_flags=self.context.feature_flags,
        )
        self.dependencies.record_rule_feedback(
            "planning",
            self.context.injected_rule_ids,
            outcome="harmful",
            feature_flags=self.context.feature_flags,
        )
        include_handoff = (
            self.repair_enabled
            and self.context.iteration_count < self.context.max_iterations
            and event.todo_list is not None
        )
        result = self.dependencies.failure_handoff.project_failure(
            event,
            self.context.memory,
            include_handoff=include_handoff,
        )
        result["feature_flags"] = dict(self.context.feature_flags or {})
        result.update(
            {
                "evaluation_repair_request": {},
                "repair_todo_list": [],
                "evaluation_recheck": False,
                "evaluation_revision_context": {},
            }
        )
        if include_handoff:
            result["todo_list"] = copy.deepcopy(event.todo_list)
        if event.code is EvaluationFailureCode.ITERATION_LIMIT:
            result.update(
                {
                    "execution_status": "failed",
                    "todo_list": [],
                    "failed_action": "任务规划",
                    "error_feedback": "迭代次数超限",
                    "failure_layer": "planning",
                }
            )
        if event.artifacts:
            result.update(copy.deepcopy(event.artifacts))
        return trace._with_cognitive_sandbox_trace(
            result,
            self.context.state,
            sandbox_enabled=self.sandbox_enabled,
            failure=event,
            recorder_factory=self.dependencies.trace_recorder_factory,
        )

    def complete(self, session: EvaluationSession) -> dict[str, Any]:
        """Commit a successful evaluation and build its public result."""

        context = session.context
        simulation = session.simulation
        self.dependencies.record_rule_feedback(
            "planning",
            context.injected_rule_ids,
            outcome="helpful",
            feature_flags=context.feature_flags,
        )
        self.dependencies.learn_from_success(
            "planning",
            context.intent,
            session.todo_list,
            feature_flags=context.feature_flags,
        )
        result: dict[str, Any] = {
            "todo_list": copy.deepcopy(session.todo_list),
            "is_feasible": True,
            "feedback": (
                "规划修复后合法，验证环节闭环。"
                if session.repair_history
                else "规划合法，验证环节闭环。"
            ),
            "evaluator_findings": [],
            "feature_flags": dict(context.feature_flags or {}),
            "planning_continuation": copy.deepcopy(
                context.state.get("planning_continuation") or {}
            ),
            "evaluation_repair_request": {},
            "repair_todo_list": [],
            "evaluation_recheck": False,
            "evaluation_revision_context": {},
        }
        if session.repair_history:
            result["repair_history"] = copy.deepcopy(session.repair_history)
        if session.state_diff_audit_payload:
            result["state_diff_audit"] = copy.deepcopy(
                session.state_diff_audit_payload
            )
        return trace._with_cognitive_sandbox_trace(
            result,
            self.context.state,
            sandbox_enabled=self.sandbox_enabled,
            validated_steps=simulation.validated_steps,
            recorder_factory=self.dependencies.trace_recorder_factory,
        )

    def revision(
        self,
        session: EvaluationSession,
        revision: CandidateRevision,
    ) -> dict[str, Any]:
        """Return an evaluator-built candidate for graph-level re-evaluation."""

        revision_context = {
            "source": revision.source,
            "artifacts": copy.deepcopy(revision.artifacts),
        }
        repair_transaction = _repair_candidate_transaction(
            session.context.state.get("evaluation_revision_context")
        )
        if repair_transaction:
            revision_context["repair_transaction"] = repair_transaction
        return {
            "todo_list": copy.deepcopy(session.todo_list),
            "is_feasible": False,
            "feedback": f"{revision.source} 已生成完整候选，等待重新评估。",
            "feature_flags": dict(session.context.feature_flags or {}),
            "evaluation_repair_request": {},
            "repair_todo_list": [],
            "evaluation_recheck": True,
            "evaluation_revision_context": revision_context,
            "repair_history": copy.deepcopy(session.repair_history),
            "planning_continuation": {},
            "repair_handoff": {},
        }


def _repair_candidate_transaction(revision: Any) -> dict[str, Any]:
    if not isinstance(revision, dict):
        return {}
    if revision.get("source") == "evaluation_repair_candidate":
        return copy.deepcopy(revision)
    nested = revision.get("repair_transaction")
    if (
        isinstance(nested, dict)
        and nested.get("source") == "evaluation_repair_candidate"
    ):
        return copy.deepcopy(nested)
    return {}


__all__ = ["EvaluationReporter"]
