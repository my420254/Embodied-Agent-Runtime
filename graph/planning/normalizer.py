from __future__ import annotations

import copy
import json
from typing import Any

from config.module_loader import call_configured_module_function
from domain.scene import flatten_scene
from graph.state import PlanningState
from skills.action_codec import ensure_execution_shape


def _looks_like_flat_scene(value: dict[str, Any]) -> bool:
    if not value:
        return True
    sample = next((item for item in value.values() if isinstance(item, dict)), None)
    if sample is None:
        return False
    return any(key in sample for key in ("direct_parent", "full_path", "states"))


def get_full_flat_house(scene_source: Any = None) -> dict[str, dict[str, Any]]:
    """Return a flat scene index from a request-level scene/environment dict."""

    if isinstance(scene_source, dict):
        data = copy.deepcopy(scene_source)
        return data if _looks_like_flat_scene(data) else flatten_scene(data)
    return {}


def environment_from_state(state: PlanningState) -> dict[str, dict[str, Any]]:
    """Resolve the single planning environment field for this request."""

    environment = state.get("environment")
    if isinstance(environment, dict) and environment:
        return get_full_flat_house(environment)
    return {}


def task_input_payload(state: PlanningState) -> dict[str, Any]:
    payload = state.get("task_input_payload")
    return payload if isinstance(payload, dict) else {}


def task_source_text(state: PlanningState) -> str:
    payload = task_input_payload(state)
    return str(
        state.get("task_source_text")
        or payload.get("llm_prompt", "")
        or state.get("raw_instruction", "")
        or ""
    )


def task_context(state: PlanningState) -> dict[str, Any]:
    current = state.get("task_context")
    return current if isinstance(current, dict) else {}


def planning_debug_events(state: PlanningState) -> list[dict[str, Any]]:
    events = state.get("planning_debug_events")
    return list(events) if isinstance(events, list) else []


def _goal_state_payload(structured_task: dict, task_ctx: dict | None = None) -> object:
    context = task_ctx if isinstance(task_ctx, dict) else {}
    if isinstance(structured_task, dict):
        for key in ("goal_state", "desired_state", "target_state"):
            payload = structured_task.get(key)
            if payload:
                return payload
    for key in ("external_goal_state", "goal_state", "desired_state", "target_state"):
        payload = context.get(key)
        if payload:
            return payload
    return None


def _entity_goal(name: str, data: object) -> dict[str, Any]:
    if not name or not isinstance(data, dict):
        return {}
    states = data.get("states", {})
    if not isinstance(states, dict):
        states = {}
    goal: dict[str, Any] = {"entity": name, "states": copy.deepcopy(states)}
    for key in ("direct_parent", "parent", "location"):
        if key in data:
            goal[key] = copy.deepcopy(data[key])
    return goal


def _iter_entity_goals(payload: object) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        goals = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            name = str(item.get("entity") or item.get("name") or item.get("id") or "").strip()
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


def _robot_goal(payload: object) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    robot_goal = payload.get("robot") or payload.get("robot_state") or {}
    return copy.deepcopy(robot_goal) if isinstance(robot_goal, dict) else {}


def _matches_expected(actual: object, expected: object) -> bool:
    if isinstance(expected, str) and expected.strip().lower() in {"*", "any"}:
        return True
    return actual == expected


def _held_items_from_robot(env_state: dict) -> set[str]:
    held: set[str] = set()
    if not isinstance(env_state, dict):
        return held

    def collect(value: object) -> None:
        if isinstance(value, dict):
            for nested in value.values():
                collect(nested)
            return
        if isinstance(value, (list, tuple, set)):
            for nested in value:
                collect(nested)
            return
        text = str(value or "").strip()
        if not text or text in {"空", "none", "null"}:
            return
        for part in text.replace(",", ";").split(";"):
            candidate = part.strip()
            if ":" in candidate:
                candidate = candidate.rsplit(":", 1)[-1].strip()
            if candidate and candidate not in {"空", "none", "null"}:
                held.add(candidate)

    collect(env_state.get("robot_holding"))
    collect(env_state.get("robot_inventory"))
    collect(env_state.get("robot_holding_items"))
    collect(env_state.get("robot_hands"))
    return held


def _matches_robot_expected(key: str, actual: object, expected: object, env_state: dict) -> bool:
    if _matches_expected(actual, expected):
        return True
    if key in {"robot_holding", "robot_inventory"} and isinstance(expected, (list, tuple, set)):
        held_items = _held_items_from_robot(env_state)
        return all(str(item).strip() in held_items for item in expected if str(item).strip())
    if key in {"robot_holding", "robot_inventory"} and isinstance(expected, str):
        expected_items = [part.strip() for part in expected.replace(",", ";").split(";") if part.strip()]
        held_items = _held_items_from_robot(env_state)
        return all(item in held_items for item in expected_items) if expected_items else False
    if key == "robot_holding_items" and isinstance(expected, list):
        held_items = _held_items_from_robot(env_state)
        return all(str(item) in held_items for item in expected if str(item).strip())
    if key == "robot_hands" and isinstance(expected, dict) and isinstance(actual, dict):
        for hand, expected_item in expected.items():
            if expected_item is None or (isinstance(expected_item, str) and expected_item in {"", "空"}):
                continue
            if actual.get(hand) != expected_item:
                return False
        return True
    return False


def _entity_goal_satisfied(goal: dict[str, Any], resolved_env: dict) -> bool:
    name = goal.get("entity")
    if not name or name not in resolved_env:
        return False
    info = resolved_env.get(name, {})
    if not isinstance(info, dict):
        return False
    if "direct_parent" in goal and not _matches_expected(info.get("direct_parent"), goal["direct_parent"]):
        return False
    if "parent" in goal and not _matches_expected(info.get("direct_parent"), goal["parent"]):
        return False
    if "location" in goal and not _matches_expected(info.get("direct_parent"), goal["location"]):
        return False
    states = info.get("states", {})
    states = states if isinstance(states, dict) else {}
    for key, expected in goal.get("states", {}).items():
        if not _matches_expected(states.get(key), expected):
            return False
    return True


def _robot_goal_satisfied(goal: dict[str, Any], env_state: dict) -> bool:
    if not goal:
        return True
    if not isinstance(env_state, dict):
        return False
    for key, expected in goal.items():
        if not _matches_robot_expected(key, env_state.get(key), expected, env_state):
            return False
    return True


def robot_only_goal_has_non_robot_requirements(
    structured_task: dict,
    task_ctx: dict | None,
    entity_goals: list[dict[str, Any]],
    robot_goal: dict[str, Any],
) -> bool:
    return False


def _robot_only_goal_has_non_robot_requirements_hook(
    structured_task: dict,
    task_ctx: dict | None,
    entity_goals: list[dict[str, Any]],
    robot_goal: dict[str, Any],
) -> bool:
    return bool(
        call_configured_module_function(
            ("files", "goal_satisfaction_module"),
            "graph.planning.normalizer",
            "robot_only_goal_has_non_robot_requirements",
            structured_task,
            task_ctx,
            entity_goals,
            robot_goal,
            label="goal satisfaction module",
        )
    )


def task_already_satisfied(
    structured_task: dict,
    resolved_env: dict,
    env_state: dict,
    *,
    task_context: dict | None = None,
) -> str:
    # VirtualHome PDDL goals may name a class (e.g. ``light`` or ``computer``)
    # while the scene contains several instances.  Never declare the task
    # complete from whichever duplicate happened to receive the unsuffixed
    # canonical name; the official evaluator may target another instance.
    if isinstance(task_context, dict):
        context_payload = task_context.get("task_context") if isinstance(task_context.get("task_context"), dict) else task_context
        ambiguous = context_payload.get("ambiguous_goal_entities") if isinstance(context_payload, dict) else None
        if isinstance(ambiguous, (list, tuple, set)) and ambiguous:
            return ""
    payload = _goal_state_payload(structured_task, task_context)
    if not payload:
        return ""
    entity_goals = _iter_entity_goals(payload)
    robot_goal = _robot_goal(payload)
    if not entity_goals and not robot_goal:
        return ""
    if _robot_only_goal_has_non_robot_requirements_hook(
        structured_task,
        task_context,
        entity_goals,
        robot_goal,
    ):
        return ""
    entities_satisfied = all(_entity_goal_satisfied(goal, resolved_env) for goal in entity_goals)
    if entities_satisfied and _robot_goal_satisfied(robot_goal, env_state):
        return "显式目标状态已经满足，无需再次执行动作。"
    return ""


def _normalize_todo_list(
    todo_list: list,
    env_state: dict,
    scene_file: str | None = None,
    skill_profile: str | None = None,
    *,
    flat_house: dict | None = None,
) -> list:
    normalized = []

    for index, raw_step in enumerate(todo_list or [], start=1):
        step = copy.deepcopy(raw_step) if isinstance(raw_step, dict) else raw_step
        step = ensure_execution_shape(step, skill_profile)
        if not isinstance(step, dict):
            step = {"raw_step": raw_step}
        step["step"] = index
        normalized.append(step)
    return normalized


def normalize_todo_list(
    todo_list: list,
    skill_profile: str | None = None,
) -> list[dict[str, Any]]:
    return _normalize_todo_list(todo_list, {}, skill_profile=skill_profile)


def reindex_todo_actions(native_actions: list[dict]) -> list[dict]:
    normalized: list[dict] = []
    for index, step in enumerate(native_actions or [], start=1):
        if not isinstance(step, dict):
            continue
        item = copy.deepcopy(step)
        item["step"] = index
        normalized.append(item)
    return normalized


def reindex_todo_steps(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    reindexed: list[dict[str, Any]] = []
    for index, step in enumerate(steps or [], start=1):
        if not isinstance(step, dict):
            continue
        item = copy.deepcopy(step)
        item["step"] = index
        reindexed.append(item)
    return reindexed


def _format_task_environment_facts(resolved_env: dict) -> str:
    rows = []
    for name in sorted(resolved_env.keys()):
        info = resolved_env.get(name, {})
        if not isinstance(info, dict):
            continue
        rows.append(
            {
                "name": name,
                "direct_parent": info.get("direct_parent", ""),
                "full_path": info.get("full_path", []),
                "states": info.get("states", {}),
                "type": info.get("type"),
                "is_container": bool(info.get("is_container", False)),
            }
        )
    return json.dumps(rows, ensure_ascii=False, separators=(",", ":"))


__all__ = [
    "_format_task_environment_facts",
    "_normalize_todo_list",
    "environment_from_state",
    "get_full_flat_house",
    "planning_debug_events",
    "normalize_todo_list",
    "reindex_todo_actions",
    "reindex_todo_steps",
    "robot_only_goal_has_non_robot_requirements",
    "task_already_satisfied",
    "task_context",
    "task_input_payload",
    "task_source_text",
]
