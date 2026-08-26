from __future__ import annotations

import copy
import json
from dataclasses import replace
from typing import Any

from ..models import EvaluationFailure, EvaluationFailureCode, EvaluationSession
from ..validation.legality import collect_todo_violations
from .simulation import run_base_simulation


def evaluate_candidate(
    session: EvaluationSession,
) -> EvaluationFailure | None:
    """Run one complete candidate through legality checks and simulation."""

    violations = collect_todo_violations(
        session.todo_list,
        session.validation_env,
        session.context.structured_task,
        session.skill_catalog,
        session.context.initial_robot,
    )
    if violations:
        return _legality_failure(session, violations)

    if not session.modes.sandbox:
        return None

    simulation = run_base_simulation(session)
    session.record_simulation(simulation)
    if simulation.failure is None:
        return None
    return _simulation_failure(session, simulation.failure)


def _legality_failure(
    session: EvaluationSession,
    violations: list[dict[str, Any]],
) -> EvaluationFailure:
    details = json.dumps(violations, ensure_ascii=False, indent=2, default=str)
    first_step = _step_for_violation(session.todo_list, violations[0])
    issue_type = (
        "序列验证失败"
        if violations[0].get("code") == "empty_plan"
        else "动作与实体合法性检查拦截"
    )
    return EvaluationFailure(
        code=_legality_failure_code(violations),
        issue_type=issue_type,
        fix_advice="请一次性修复以下全部动作和实体错误后重新生成完整 todo_list：\n"
        + details,
        step=first_step,
        kind="plan_legality",
        checkpoint_env=session.validation_env,
        checkpoint_robot=session.context.initial_robot,
        todo_list=session.todo_list,
        artifacts={
            "plan_legality": {
                "passed": False,
                "violations": copy.deepcopy(violations),
                "violation_count": len(violations),
            },
            "repair_history": copy.deepcopy(session.repair_history),
        },
    )


def _simulation_failure(
    session: EvaluationSession,
    failure: EvaluationFailure,
) -> EvaluationFailure:
    return replace(
        failure,
        validated_steps=copy.deepcopy(session.simulation.validated_steps),
        todo_list=copy.deepcopy(session.todo_list),
        artifacts={
            **copy.deepcopy(failure.artifacts),
            "repair_history": copy.deepcopy(session.repair_history),
        },
    )


def _legality_failure_code(
    violations: list[dict[str, Any]],
) -> EvaluationFailureCode:
    codes = {str(item.get("code", "")) for item in violations}
    if "empty_plan" in codes:
        return EvaluationFailureCode.EMPTY_PLAN
    if codes & {
        "invalid_step",
        "missing_execution",
        "missing_skill",
        "invalid_parameters",
    }:
        return EvaluationFailureCode.FORMAT_ERROR
    return EvaluationFailureCode.INVALID_ACTION


def _step_for_violation(todo_list: list[dict], violation: dict) -> dict:
    step_num = violation.get("step")
    for step in todo_list:
        if isinstance(step, dict) and step.get("step") == step_num:
            return step
    return {"step": step_num} if step_num is not None else {}


__all__ = ["evaluate_candidate"]
