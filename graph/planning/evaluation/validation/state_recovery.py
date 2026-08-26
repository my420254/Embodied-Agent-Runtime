"""Build reversible recovery candidates reported by the state-diff audit."""
from __future__ import annotations

import copy
from typing import Any, Callable

from .checkpoint import _state_path_parts


def _execute_contract_action(
    action: dict[str, Any] | None,
    env: dict[str, Any],
    robot: dict[str, Any],
    skill_profile: str | None,
    apply_action: Callable[..., tuple[bool, str, str]],
) -> tuple[bool, dict, dict, dict[str, Any]]:
    if not action or not action.get("skill"):
        return True, env, robot, {}
    next_env = copy.deepcopy(env)
    next_robot = copy.deepcopy(robot)
    ok, issue, fix = apply_action(
        next_env,
        next_robot,
        action.get("skill", ""),
        action.get("parameters", {}) if isinstance(action.get("parameters"), dict) else {},
        profile=skill_profile,
    )
    if not ok:
        return False, env, robot, {"action": action, "issue": issue, "fix": fix}
    return True, next_env, next_robot, {}


def recover_reversible_state_diffs(
    *,
    audit_result: dict[str, Any],
    before_env: dict[str, Any],
    env: dict[str, Any],
    robot: dict[str, Any],
    repair_catalog,
    skill_profile: str | None,
    apply_action: Callable[..., tuple[bool, str, str]],
) -> dict[str, Any]:
    reversible_keys = repair_catalog.reversible_state_keys() if repair_catalog else set()
    if not reversible_keys:
        return {"success": False, "actions": [], "reason": "no_reversible_state_contracts"}

    actions: list[dict[str, Any]] = []
    next_env = copy.deepcopy(env)
    next_robot = copy.deepcopy(robot)
    errors: list[dict[str, Any]] = []

    unexpected_diffs = audit_result.get("unexpected_diffs", []) if isinstance(audit_result, dict) else []
    for item in unexpected_diffs:
        if not isinstance(item, dict):
            continue
        parts = _state_path_parts(item.get("path"))
        targets: list[tuple[str, str]] = []
        if parts:
            targets.append(parts)
        else:
            entity_name = str(item.get("path", "") or "").strip()
            if entity_name in before_env and entity_name in next_env:
                before_states = before_env.get(entity_name, {}).get("states", {}) if isinstance(before_env.get(entity_name), dict) else {}
                after_states = next_env.get(entity_name, {}).get("states", {}) if isinstance(next_env.get(entity_name), dict) else {}
                if isinstance(before_states, dict) and isinstance(after_states, dict):
                    targets.extend(
                        (entity_name, state_key)
                        for state_key in reversible_keys
                        if before_states.get(state_key) is not None and before_states.get(state_key) != after_states.get(state_key)
                    )
        for entity, state_key in targets:
            if state_key not in reversible_keys or entity not in before_env or entity not in next_env:
                continue
            before_states = before_env.get(entity, {}).get("states", {}) if isinstance(before_env.get(entity), dict) else {}
            after_states = next_env.get(entity, {}).get("states", {}) if isinstance(next_env.get(entity), dict) else {}
            if not isinstance(before_states, dict) or not isinstance(after_states, dict):
                continue
            desired_value = before_states.get(state_key)
            if desired_value is None or after_states.get(state_key) == desired_value:
                continue
            state_action = repair_catalog.state_action(state_key, desired_value, entity)
            if not state_action:
                continue
            move_action = repair_catalog.location_action(entity)
            for action in (move_action, state_action):
                if not action:
                    continue
                if action.get("skill") == "NavigateTo" and next_robot.get("robot_location") == action.get("parameters", {}).get("target_location"):
                    continue
                ok, next_env, next_robot, error = _execute_contract_action(
                    action,
                    next_env,
                    next_robot,
                    skill_profile,
                    apply_action,
                )
                if not ok:
                    errors.append(error)
                    break
                actions.append({"execution": copy.deepcopy(action)})
            if errors:
                break
        if errors:
            continue

    if errors:
        return {"success": False, "actions": actions, "errors": errors}
    if not actions:
        return {"success": False, "actions": [], "reason": "no_recoverable_unexpected_reversible_diffs"}
    return {
        "success": True,
        "actions": actions,
        "final_env": next_env,
        "final_robot": next_robot,
    }


__all__ = [
    "recover_reversible_state_diffs",
]
