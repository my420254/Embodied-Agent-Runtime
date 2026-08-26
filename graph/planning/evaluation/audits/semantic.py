from __future__ import annotations

import json
from typing import Any

from .. import flags
from ..dependencies import EvaluationDependencies
from ..models import EvaluationFailure, EvaluationFailureCode, EvaluationSession
from ..validation.checkpoint import _infer_failed_step_num, _semantic_repair_checkpoint
from . import llm as audit_llm
from .payloads import state_diff_payload_if_present


def run_semantic_audit(
    session: EvaluationSession,
    dependencies: EvaluationDependencies,
) -> EvaluationFailure | None:
    """Use the LLM audit contract to check goal-level plan semantics."""

    if not flags._feature_enabled(
        session.context.feature_flags,
        "semantic_audit",
    ):
        return None

    simulation = session.simulation
    audit_env = (
        simulation.final_env
        if isinstance(simulation.final_env, dict) and simulation.final_env
        else session.context.state.get("environment", {})
    )

    try:
        audit_result = audit_llm._run_semantic_audit(
            intent=session.context.intent,
            trajectory=session.trajectory(),
            current_env_json=json.dumps(audit_env, ensure_ascii=False, indent=2),
            robot_state_json=json.dumps(
                simulation.final_robot,
                ensure_ascii=False,
                indent=2,
            ),
            navigation_contract="",
            skills_markdown=session.skills.prompts,
            get_planning_llm=dependencies.get_planning_llm,
        )
        if audit_result.get("is_passed", True):
            return None
        return _semantic_audit_rejection(
            session,
            audit_result,
        )
    except Exception as exc:
        fix = f"语义审计失败，禁止缺省放行。底层日志: {exc}"
        return EvaluationFailure(
            code=EvaluationFailureCode.SEMANTIC_AUDIT,
            issue_type="判定模块异常",
            fix_advice=fix,
            kind="semantic_audit",
            checkpoint_env=simulation.final_env,
            checkpoint_robot=simulation.final_robot,
            validated_steps=simulation.validated_steps,
            artifacts={
                **state_diff_payload_if_present(session),
            },
        )


def _semantic_audit_rejection(
    session: EvaluationSession,
    audit_result: dict[str, Any],
) -> EvaluationFailure:
    simulation = session.simulation
    issue = audit_result.get("issue", "任务执行未能匹配预期状态。")
    fix_advice = audit_result.get(
        "fix_advice",
        "检查逻辑树或清退遗留状态。",
    )
    failed_step_num = _infer_failed_step_num(
        audit_result.get("issue", ""),
        audit_result.get("fix_advice", ""),
        session.trajectory(),
        fallback=len(simulation.validated_steps) + 1,
    )
    repair_validated_steps, repair_env, repair_robot, failed_step = (
        _semantic_repair_checkpoint(
            failed_step_num=failed_step_num,
            todo_steps=simulation.todo_steps,
            prefix_steps=session.prefix_steps,
            validated_steps=simulation.validated_steps,
            trajectory_records=simulation.trajectory_records,
            sandbox_start_env=simulation.start_env,
            sandbox_start_robot=simulation.start_robot,
            repair_base_env=simulation.repair_base_env,
            repair_base_robot=simulation.repair_base_robot,
        )
    )
    return EvaluationFailure(
        code=EvaluationFailureCode.SEMANTIC_AUDIT,
        issue_type="判定模块拦截",
        fix_advice=f"失败原因: {issue}\n建议: {fix_advice}",
        step=failed_step,
        kind="semantic_audit",
        checkpoint_env=repair_env,
        checkpoint_robot=repair_robot,
        validated_steps=repair_validated_steps,
        todo_list=session.todo_list,
        artifacts={
            **state_diff_payload_if_present(session),
        },
    )


__all__ = ["run_semantic_audit"]
