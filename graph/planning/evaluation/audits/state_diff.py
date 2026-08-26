from __future__ import annotations

from typing import Any

from ..dependencies import EvaluationDependencies
from ..models import (
    CandidateRevision,
    EvaluationFailure,
    EvaluationFailureCode,
    EvaluationSession,
)
from ..validation import state_recovery
from ..validation.checkpoint import _reindex_todo_steps
from ..validation.state_diff import _build_state_audit_context, _build_state_diff
from . import llm as audit_llm


def run_state_diff_audit(
    session: EvaluationSession,
    dependencies: EvaluationDependencies,
) -> EvaluationFailure | CandidateRevision | None:
    """Audit final sandbox diffs and recover reversible side effects."""

    if not session.modes.state_diff_audit:
        return None

    simulation = session.simulation
    state_diff: dict[str, Any] = {}
    try:
        state_diff, audit_context, audit_result = _execute_state_diff_audit(
            session,
            dependencies,
        )
        if not audit_result.get("is_passed", True):
            recovery = state_recovery.recover_reversible_state_diffs(
                audit_result=audit_result,
                before_env=simulation.start_env,
                env=simulation.final_env,
                robot=simulation.final_robot,
                repair_catalog=session.skill_catalog,
                skill_profile=session.context.skill_profile,
                apply_action=session.skills.apply_action,
            )
            if recovery.get("success"):
                if not session.pending_recovery_actions:
                    actions = recovery.get("actions", [])
                    return CandidateRevision(
                        todo_list=_reindex_todo_steps(
                            session.todo_list + actions
                        ),
                        source="state_diff_recovery",
                        artifacts={"recovery_actions": actions},
                    )
            if session.state_diff_audit_payload is None:
                return _state_diff_rejection(
                    session,
                    state_diff=state_diff,
                    audit_context=audit_context,
                    audit_result=audit_result,
                )
        if session.state_diff_audit_payload is None:
            session.state_diff_audit_payload = _state_diff_payload(
                state_diff,
                audit_context,
                audit_result,
                recovery_actions=(
                    session.pending_recovery_actions or None
                ),
            )
    except Exception as exc:
        fix = f"状态差异审计失败，禁止缺省放行。底层日志: {exc}"
        return EvaluationFailure(
            code=EvaluationFailureCode.STATE_DIFF_AUDIT,
            issue_type="状态差异审计异常",
            fix_advice=fix,
            kind="state_diff_audit",
            checkpoint_env=simulation.final_env,
            checkpoint_robot=simulation.final_robot,
            validated_steps=simulation.validated_steps,
            artifacts={
                "state_diff_audit": {
                    "enabled": True,
                    "passed": False,
                    "state_diff": state_diff,
                    "error": str(exc),
                }
            },
        )
    return None


def _execute_state_diff_audit(
    session: EvaluationSession,
    dependencies: EvaluationDependencies,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    simulation = session.simulation
    state_diff = _build_state_diff(
        simulation.start_env,
        simulation.start_robot,
        simulation.final_env,
        simulation.final_robot,
    )
    audit_context = _build_state_audit_context(
        simulation.start_env,
        simulation.start_robot,
        simulation.final_env,
        simulation.final_robot,
        session.todo_list,
        session.context.structured_task,
    )
    audit_result = audit_llm._run_state_diff_audit(
        intent=session.context.intent,
        todo_list=session.todo_list,
        simulated_steps=simulation.todo_steps,
        trajectory=session.trajectory(),
        state_diff=state_diff,
        state_audit_context=audit_context,
        get_planning_llm=dependencies.get_planning_llm,
    )
    return state_diff, audit_context, audit_result


def _state_diff_rejection(
    session: EvaluationSession,
    *,
    state_diff: dict[str, Any],
    audit_context: dict[str, Any],
    audit_result: dict[str, Any],
) -> EvaluationFailure:
    simulation = session.simulation
    issue = audit_result.get("issue", "模拟状态差异不符合任务目标。")
    fix_advice = audit_result.get(
        "fix_advice",
        "修正规划步骤，避免无关状态污染。",
    )
    return EvaluationFailure(
        code=EvaluationFailureCode.STATE_DIFF_AUDIT,
        issue_type="状态差异审计拦截",
        fix_advice=f"失败原因: {issue}\n建议: {fix_advice}",
        kind="state_diff_audit",
        checkpoint_env=simulation.final_env,
        checkpoint_robot=simulation.final_robot,
        validated_steps=simulation.validated_steps,
        todo_list=session.todo_list,
        artifacts={
            "state_diff_audit": {
                "enabled": True,
                "passed": False,
                "state_diff": state_diff,
                "state_audit_context": audit_context,
                "llm_result": audit_result,
            },
        },
    )


def _state_diff_payload(
    state_diff: dict[str, Any],
    audit_context: dict[str, Any],
    audit_result: dict[str, Any],
    *,
    recovery_actions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    payload = {
        "enabled": True,
        "passed": True,
        "state_diff": state_diff,
        "state_audit_context": audit_context,
        "llm_result": audit_result,
    }
    if recovery_actions is not None:
        payload["recovery"] = {
            "success": True,
            "actions": _reindex_todo_steps(recovery_actions),
        }
    return payload


__all__ = ["run_state_diff_audit"]
