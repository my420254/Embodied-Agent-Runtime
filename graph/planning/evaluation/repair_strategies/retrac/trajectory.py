import copy
import re
from typing import Any


RE_TRAC_SCHEMA_VERSION = "re_trac_v1"
MODE_REPAIR_FROM_FAILED_STEP = "repair_from_failed_step"
MODE_APPEND_RECOVERY = "append_recovery_after_valid_plan"


def compact_todo_list(todo_list: list | None) -> list[dict[str, Any]]:
    compact_steps: list[dict[str, Any]] = []
    for step in todo_list or []:
        if not isinstance(step, dict):
            continue
        execution = step.get("execution", {})
        if not isinstance(execution, dict):
            execution = {}
        compact_steps.append(
            {
                "step": step.get("step"),
                "skill": execution.get("skill", ""),
                "parameters": copy.deepcopy(execution.get("parameters", {})),
            }
        )
    return compact_steps


def infer_failed_step_num(*texts: str, fallback: int | None = None) -> int | None:
    for text in texts:
        if not text:
            continue
        for pattern in (
            r"\b[Ss]tep\s*#?\s*(\d+)",
            r"第\s*(\d+)\s*步",
            r"步骤\s*(\d+)",
        ):
            match = re.search(pattern, str(text))
            if match:
                return int(match.group(1))
    return fallback


def _step_num(step: dict | None) -> int | None:
    if not isinstance(step, dict):
        return None
    try:
        return int(step.get("step"))
    except (TypeError, ValueError):
        return None


def _compact_failed_step(step: dict | None) -> dict[str, Any] | None:
    compact = compact_todo_list([step] if isinstance(step, dict) else [])
    return compact[0] if compact else None


def _state_payload(env: dict | None, robot: dict | None, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "robot": copy.deepcopy(robot) if isinstance(robot, dict) else {},
        "environment": copy.deepcopy(env) if isinstance(env, dict) else {},
        "note": "This is a sandbox simulated state for planning repair, not the real runtime scene.",
    }
    if extra:
        payload.update(copy.deepcopy(extra))
    return payload


def build_failed_step_retrac_state(
    *,
    failure_kind: str,
    issue_type: str,
    issue: str,
    fix_advice: str,
    todo_list: list,
    validated_steps: list,
    failed_step: dict | None,
    sim_env: dict,
    sim_robot: dict,
) -> dict[str, Any]:
    failed_step_num = _step_num(failed_step) or len(validated_steps) + 1
    original = compact_todo_list(todo_list)
    verified_prefix = compact_todo_list(validated_steps)
    discarded_suffix = compact_todo_list(
        [
            step
            for step in (todo_list or [])
            if isinstance(step, dict) and (_step_num(step) or 0) >= failed_step_num
        ]
    )
    wrong_step = _compact_failed_step(failed_step)

    return {
        "version": RE_TRAC_SCHEMA_VERSION,
        "mode": MODE_REPAIR_FROM_FAILED_STEP,
        "failure_kind": failure_kind,
        "issue_type": issue_type,
        "failure": {
            "issue": issue,
            "fix_advice": fix_advice,
            "wrong_step": wrong_step,
        },
        "trajectory": {
            "original_todo_list": original,
            "verified_prefix": verified_prefix,
            "validated_prefix": verified_prefix,
            "validated_step_count": len(validated_steps),
            "next_step_num": len(validated_steps) + 1,
            "prefix_is_valid": True,
            "wrong_step": wrong_step,
            "discarded_suffix": discarded_suffix,
        },
        "current_simulated_state": _state_payload(sim_env, sim_robot),
        "frontier": {
            "type": "regenerate_suffix_from_failed_step",
            "next_step_num": len(validated_steps) + 1,
            "instruction": (
                "Keep the verified prefix fixed. Discard the wrong step and all later original actions. "
                "Regenerate only the suffix from next_step_num using current_simulated_state."
            ),
        },
    }


def build_state_diff_retrac_state(
    *,
    issue_type: str,
    issue: str,
    fix_advice: str,
    todo_list: list,
    validated_steps: list,
    sim_env: dict,
    sim_robot: dict,
    state_diff: dict[str, Any],
    audit_result: dict[str, Any],
) -> dict[str, Any]:
    verified_prefix = compact_todo_list(validated_steps)
    return {
        "version": RE_TRAC_SCHEMA_VERSION,
        "mode": MODE_APPEND_RECOVERY,
        "failure_kind": "state_diff_audit",
        "issue_type": issue_type,
        "failure": {
            "issue": issue,
            "fix_advice": fix_advice,
            "unexpected_diffs": copy.deepcopy(audit_result.get("unexpected_diffs", [])),
            "accepted_diffs": copy.deepcopy(audit_result.get("accepted_diffs", [])),
        },
        "trajectory": {
            "original_todo_list": compact_todo_list(todo_list),
            "verified_prefix": verified_prefix,
            "validated_prefix": verified_prefix,
            "validated_step_count": len(validated_steps),
            "next_step_num": len(validated_steps) + 1,
            "prefix_is_valid": True,
            "wrong_step": None,
            "discarded_suffix": [],
        },
        "current_simulated_state": _state_payload(
            sim_env,
            sim_robot,
            {"changed_state_diff": copy.deepcopy(state_diff)},
        ),
        "frontier": {
            "type": "append_recovery_actions",
            "next_step_num": len(validated_steps) + 1,
            "instruction": (
                "The verified plan can achieve the task but leaves recoverable side effects. "
                "Append only recovery or cleanup actions after next_step_num; do not regenerate the plan."
            ),
        },
    }
