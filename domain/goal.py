from __future__ import annotations

import copy


def _goal_state_payload(structured_task: dict) -> object:
    if not isinstance(structured_task, dict):
        return None
    for key in ("goal_state", "desired_state", "target_state"):
        payload = structured_task.get(key)
        if payload:
            return payload
    return None


def _entity_goal(name: str, data: object) -> dict:
    if not name or not isinstance(data, dict):
        return {}

    states = data.get("states", {})
    if not isinstance(states, dict):
        states = {}

    goal = {"entity": name, "states": copy.deepcopy(states)}
    for key in ("direct_parent", "parent", "location"):
        if key in data:
            goal[key] = copy.deepcopy(data[key])
    return goal


def _iter_entity_goals(payload: object) -> list[dict]:
    if isinstance(payload, list):
        goals = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            name = str(
                item.get("entity") or item.get("name") or item.get("id") or ""
            ).strip()
            goal = _entity_goal(name, item)
            if goal:
                goals.append(goal)
        return goals

    if not isinstance(payload, dict):
        return []

    entities = payload.get("entities")
    if isinstance(entities, list):
        return _iter_entity_goals(entities)
    if isinstance(entities, dict):
        return [
            goal
            for name, data in entities.items()
            if (goal := _entity_goal(str(name).strip(), data))
        ]

    goals = []
    for name, data in payload.items():
        if name in {"robot", "robot_state"}:
            continue
        goal = _entity_goal(str(name).strip(), data)
        if goal:
            goals.append(goal)
    return goals


def _robot_goal(payload: object) -> dict:
    if not isinstance(payload, dict):
        return {}
    robot_goal = payload.get("robot") or payload.get("robot_state") or {}
    return copy.deepcopy(robot_goal) if isinstance(robot_goal, dict) else {}


def _matches_expected(actual: object, expected: object) -> bool:
    if isinstance(expected, str) and expected.strip().lower() in {"*", "any"}:
        return True
    return actual == expected


def _entity_goal_satisfied(goal: dict, resolved_env: dict) -> bool:
    name = goal.get("entity")
    if not name or name not in resolved_env:
        return False

    info = resolved_env.get(name, {})
    if not isinstance(info, dict):
        return False

    if "direct_parent" in goal and not _matches_expected(
        info.get("direct_parent"), goal["direct_parent"]
    ):
        return False
    if "parent" in goal and not _matches_expected(
        info.get("direct_parent"), goal["parent"]
    ):
        return False
    if "location" in goal and not _matches_expected(
        info.get("direct_parent"), goal["location"]
    ):
        return False

    states = info.get("states", {})
    states = states if isinstance(states, dict) else {}
    return all(
        _matches_expected(states.get(key), expected)
        for key, expected in goal.get("states", {}).items()
    )


def _robot_goal_satisfied(goal: dict, env_state: dict) -> bool:
    if not goal:
        return True
    if not isinstance(env_state, dict):
        return False
    return all(
        _matches_expected(env_state.get(key), expected)
        for key, expected in goal.items()
    )


def goal_state_satisfied(
    structured_task: dict,
    resolved_env: dict,
    env_state: dict,
) -> bool | None:
    """Return an explicit goal-state verdict, or None without a formal goal."""

    payload = _goal_state_payload(structured_task)
    if not payload:
        return None

    entity_goals = _iter_entity_goals(payload)
    robot_goal = _robot_goal(payload)
    if not entity_goals and not robot_goal:
        return None
    return all(
        _entity_goal_satisfied(goal, resolved_env) for goal in entity_goals
    ) and _robot_goal_satisfied(robot_goal, env_state)


__all__ = ["goal_state_satisfied"]
