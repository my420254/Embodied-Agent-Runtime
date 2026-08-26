from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

from ..models import EvaluationFailure
from .continuation import build_planning_continuation, coerce_memory


class CheckpointFailureHandoff:
    """Project one evaluation failure into repair memory and checkpoint state."""

    def load_memory(self, state: Mapping[str, Any]) -> dict[str, Any]:
        return coerce_memory(state.get("repair_memory"))

    def _build_finding(self, failure: EvaluationFailure) -> dict[str, Any]:
        step = failure.step if isinstance(failure.step, dict) else {}
        execution = step.get("execution", {})
        execution = execution if isinstance(execution, dict) else {}
        issue = failure.full_issue
        return {
            "failed_step": step.get("step"),
            "skill": execution.get("skill", ""),
            "parameters": copy.deepcopy(execution.get("parameters", {})),
            "error_type": issue,
            "actual": issue,
            "expected": failure.fix_advice,
            "repair_hint": failure.fix_advice,
            "failure_code": failure.code.value,
        }

    def project_failure(
        self,
        failure: EvaluationFailure,
        memory: Mapping[str, Any],
        *,
        include_handoff: bool,
    ) -> dict[str, Any]:
        issue = failure.full_issue
        result = {
            "is_feasible": False,
            "feedback": f"{issue}\n{failure.fix_advice}",
            "validated_steps": copy.deepcopy(failure.validated_steps),
            "checkpoint_env": copy.deepcopy(failure.checkpoint_env),
            "checkpoint_robot": copy.deepcopy(failure.checkpoint_robot),
            "repair_memory": _add_failed_lesson(
                memory,
                issue,
                failure.fix_advice,
            ),
            "evaluator_findings": [self._build_finding(failure)],
            "failure_category": failure.code.value,
        }
        if not include_handoff:
            return {**result, "planning_continuation": {}}
        state = (
            _state_diff_state(failure)
            if failure.kind == "state_diff_audit"
            else _failed_step_state(failure)
        )
        return {
            **result,
            "repair_handoff": state,
            "planning_continuation": build_planning_continuation(
                validated_steps=failure.validated_steps,
                checkpoint_env=failure.checkpoint_env,
                checkpoint_robot=failure.checkpoint_robot,
                repair_memory=result["repair_memory"],
                repair_handoff=state,
                enabled=True,
            ),
        }


def _add_failed_lesson(memory: Any, issue: str, fix: str) -> dict[str, Any]:
    value = coerce_memory(memory)
    lesson = f"{issue} -> 修复要求: {fix}"
    if lesson not in value["failed_lessons"]:
        value["failed_lessons"].append(lesson)
    return value


def _compact_steps(steps: Any) -> list[dict[str, Any]]:
    compact: list[dict[str, Any]] = []
    for step in steps or []:
        if not isinstance(step, dict):
            continue
        execution = step.get("execution", {})
        execution = execution if isinstance(execution, dict) else {}
        compact.append(
            {
                "step": step.get("step"),
                "skill": execution.get("skill", ""),
                "parameters": copy.deepcopy(execution.get("parameters", {})),
            }
        )
    return compact


def _step_number(step: Any) -> int | None:
    try:
        return int(step.get("step")) if isinstance(step, dict) else None
    except (TypeError, ValueError):
        return None


def _state_payload(env: Any, robot: Any, **extras: Any) -> dict[str, Any]:
    return {
        "robot": copy.deepcopy(robot) if isinstance(robot, dict) else {},
        "environment": copy.deepcopy(env) if isinstance(env, dict) else {},
        "note": "Sandbox checkpoint for planning repair; not runtime state.",
        **copy.deepcopy(extras),
    }


def _failed_step_state(failure: EvaluationFailure) -> dict[str, Any]:
    todo_list = list(failure.todo_list or [])
    validated_steps = list(failure.validated_steps)
    failed_number = _step_number(failure.step) or len(validated_steps) + 1
    verified = _compact_steps(validated_steps)
    wrong_step = _compact_steps([failure.step])
    return {
        "version": "checkpoint_handoff_v1",
        "mode": "repair_from_failed_step",
        "failure_kind": failure.kind,
        "failure_code": failure.code.value,
        "issue_type": failure.issue_type,
        "failure": {
            "issue": failure.full_issue,
            "fix_advice": failure.fix_advice,
            "wrong_step": wrong_step[0] if wrong_step else None,
        },
        "trajectory": {
            "original_todo_list": _compact_steps(todo_list),
            "verified_prefix": verified,
            "validated_prefix": verified,
            "validated_step_count": len(validated_steps),
            "next_step_num": len(validated_steps) + 1,
            "prefix_is_valid": True,
            "wrong_step": wrong_step[0] if wrong_step else None,
            "discarded_suffix": _compact_steps(
                [
                    step
                    for step in todo_list
                    if (_step_number(step) or 0) >= failed_number
                ]
            ),
        },
        "current_simulated_state": _state_payload(
            failure.checkpoint_env,
            failure.checkpoint_robot,
        ),
        "frontier": {
            "type": "regenerate_suffix_from_failed_step",
            "next_step_num": len(validated_steps) + 1,
        },
    }


def _state_diff_state(failure: EvaluationFailure) -> dict[str, Any]:
    validated_steps = list(failure.validated_steps)
    verified = _compact_steps(validated_steps)
    audit_payload = failure.artifacts.get("state_diff_audit", {})
    audit_result = audit_payload.get("llm_result", {})
    return {
        "version": "checkpoint_handoff_v1",
        "mode": "append_recovery_after_valid_plan",
        "failure_kind": failure.kind,
        "failure_code": failure.code.value,
        "issue_type": failure.issue_type,
        "failure": {
            "issue": failure.full_issue,
            "fix_advice": failure.fix_advice,
            "unexpected_diffs": copy.deepcopy(
                audit_result.get("unexpected_diffs", [])
            ),
            "accepted_diffs": copy.deepcopy(
                audit_result.get("accepted_diffs", [])
            ),
        },
        "trajectory": {
            "original_todo_list": _compact_steps(failure.todo_list),
            "verified_prefix": verified,
            "validated_prefix": verified,
            "validated_step_count": len(validated_steps),
            "next_step_num": len(validated_steps) + 1,
            "prefix_is_valid": True,
            "wrong_step": None,
            "discarded_suffix": [],
        },
        "current_simulated_state": _state_payload(
            failure.checkpoint_env,
            failure.checkpoint_robot,
            changed_state_diff=audit_payload.get("state_diff", {}),
        ),
        "frontier": {
            "type": "append_recovery_actions",
            "next_step_num": len(validated_steps) + 1,
        },
    }


__all__ = ["CheckpointFailureHandoff"]
