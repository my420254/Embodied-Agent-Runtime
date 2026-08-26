import copy
import json
import re
from typing import Any


RE_TRAC_SCHEMA_VERSION = "re_trac_v1"
MODE_REPAIR_FROM_FAILED_STEP = "repair_from_failed_step"
MODE_APPEND_RECOVERY = "append_recovery_after_valid_plan"


def compact_todo_list(todo_list: list | None) -> list[dict[str, Any]]:
    compact_steps: list[dict[str, Any]] = []
    for index, step in enumerate(todo_list or [], start=1):
        if not isinstance(step, dict):
            continue
        execution = step.get("execution", {})
        if isinstance(execution, dict) and execution:
            compact_steps.append(
                {
                    "step": step.get("step"),
                    "skill": execution.get("skill", ""),
                    "parameters": copy.deepcopy(execution.get("parameters", {})),
                }
            )
            continue
        item = copy.deepcopy(step)
        item["step"] = step.get("step") or index
        compact_steps.append(item)
    return compact_steps


def compact_todo_action_list(todo_actions: list | None) -> list[dict[str, Any]]:
    compact_steps: list[dict[str, Any]] = []
    for index, step in enumerate(todo_actions or [], start=1):
        if not isinstance(step, dict):
            continue
        item = copy.deepcopy(step)
        item["step"] = index
        compact_steps.append(item)
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
    validated_todo_actions: list | None = None,
    failed_todo_step: dict | None = None,
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
    verified_todo_action_prefix = compact_todo_action_list(validated_todo_actions)
    failed_todo_step_num = _step_num(failed_todo_step) or _step_num(failed_step)
    discarded_todo_action_suffix = [
        copy.deepcopy(step)
        for step in original
        if (_step_num(step) or 0) >= (failed_todo_step_num or len(verified_todo_action_prefix) + 1)
    ]
    todo_wrong_step = (
        compact_todo_action_list([failed_todo_step])[0]
        if isinstance(failed_todo_step, dict)
        else None
    )

    payload = {
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
    if verified_todo_action_prefix or todo_wrong_step:
        payload["todo_trajectory"] = {
            "original_todo_list": original,
            "validated_prefix": verified_todo_action_prefix,
            "validated_step_count": len(verified_todo_action_prefix),
            "next_step_num": len(verified_todo_action_prefix) + 1,
            "prefix_is_valid": True,
            "wrong_step": todo_wrong_step,
            "discarded_suffix": discarded_todo_action_suffix,
        }
    return payload


def build_state_diff_retrac_state(
    *,
    issue_type: str,
    issue: str,
    fix_advice: str,
    todo_list: list,
    validated_steps: list,
    validated_todo_actions: list | None = None,
    sim_env: dict,
    sim_robot: dict,
    state_diff: dict[str, Any],
    audit_result: dict[str, Any],
) -> dict[str, Any]:
    verified_prefix = compact_todo_list(validated_steps)
    verified_todo_action_prefix = compact_todo_action_list(validated_todo_actions)
    payload = {
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
    if validated_todo_actions:
        payload["todo_trajectory"] = {
            "original_todo_list": compact_todo_list(todo_list),
            "validated_prefix": verified_todo_action_prefix,
            "validated_step_count": len(verified_todo_action_prefix),
            "next_step_num": len(verified_todo_action_prefix) + 1,
            "prefix_is_valid": True,
            "wrong_step": None,
            "discarded_suffix": [],
        }
    return payload


def _action_signature(step: dict) -> str:
    execution = step.get("execution", {}) if isinstance(step, dict) else {}
    if not isinstance(execution, dict):
        execution = {}
    skill = execution.get("skill", "")
    params = execution.get("parameters", {}) or {}
    try:
        params_json = json.dumps(params, ensure_ascii=False, sort_keys=True, default=str)
    except TypeError:
        params_json = str(params)
    return f"{skill}:{params_json}"


def strip_repeated_prefix(validated_steps: list | None, candidate_steps: list | None) -> list[dict[str, Any]]:
    candidates = [copy.deepcopy(step) for step in (candidate_steps or []) if isinstance(step, dict)]
    prefix = [step for step in (validated_steps or []) if isinstance(step, dict)]
    if not prefix or not candidates:
        return candidates

    prefix_index = 0
    first_suffix_index = 0
    for candidate in candidates:
        if prefix_index >= len(prefix):
            break
        if _action_signature(candidate) != _action_signature(prefix[prefix_index]):
            break
        prefix_index += 1
        first_suffix_index += 1

    if prefix_index == 0:
        return candidates
    return candidates[first_suffix_index:]
