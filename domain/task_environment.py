from __future__ import annotations

import copy
from typing import Any

from domain.scene import flatten_scene


def _flatten_required_item_names(required_item_names: dict | None) -> list[str]:
    if not isinstance(required_item_names, dict):
        return []

    names: list[str] = []
    for key in ("targets", "tools", "receptacles"):
        bucket = required_item_names.get(key, {})
        if isinstance(bucket, dict):
            names.extend(str(name) for name in bucket.get("primary", []) if name)
            names.extend(str(name) for name in bucket.get("alternatives", []) if name)
        elif isinstance(bucket, list):
            names.extend(str(name) for name in bucket if name)
    return list(dict.fromkeys(names))


_EMPTY_ENTITY_VALUES = {"", "空", "none", "null", "unknown", "未知", "未知环境"}


def _goal_robot_target_names(robot_goal: Any) -> list[str]:
    if not isinstance(robot_goal, dict):
        return []

    raw_values = [
        robot_goal.get(field)
        for field in ("robot_holding", "robot_inventory", "robot_holding_items")
    ]
    raw_values.append(robot_goal.get("robot_hands"))
    names: list[str] = []

    def collect(value: Any) -> None:
        if isinstance(value, dict):
            for nested in value.values():
                collect(nested)
            return
        if isinstance(value, (list, tuple, set)):
            for nested in value:
                collect(nested)
            return
        text = str(value or "").strip()
        if not text:
            return
        for part in text.replace(",", ";").split(";"):
            candidate = part.strip()
            if ":" in candidate:
                candidate = candidate.rsplit(":", 1)[-1].strip()
            if candidate and candidate.lower() not in _EMPTY_ENTITY_VALUES:
                names.append(candidate)

    for raw_value in raw_values:
        collect(raw_value)
    return list(dict.fromkeys(names))


def add_goal_entities_to_required_item_names(structured_task: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(structured_task, dict):
        structured_task = {}
    required = structured_task.setdefault("required_item_names", {})
    if not isinstance(required, dict):
        required = {}
        structured_task["required_item_names"] = required
    targets = required.setdefault("targets", {"primary": [], "alternatives": []})
    receptacles = required.setdefault("receptacles", {"primary": [], "alternatives": []})
    required.setdefault("tools", {"primary": [], "alternatives": []})

    goal_state = structured_task.get("goal_state", {})
    entities = goal_state.get("entities", {}) if isinstance(goal_state, dict) else {}
    if not isinstance(entities, dict):
        return structured_task
    if isinstance(targets, dict):
        current_targets = list(targets.get("primary", []) or [])
        for name in entities:
            if name not in current_targets:
                current_targets.append(name)
        targets["primary"] = current_targets
    if isinstance(receptacles, dict):
        current_receptacles = list(receptacles.get("primary", []) or [])
        for payload in entities.values():
            if not isinstance(payload, dict):
                continue
            parent = str(payload.get("direct_parent") or "").strip()
            if parent and parent not in current_receptacles:
                current_receptacles.append(parent)
        receptacles["primary"] = current_receptacles
    if isinstance(targets, dict):
        current_targets = list(targets.get("primary", []) or [])
        robot = goal_state.get("robot", {}) if isinstance(goal_state, dict) else {}
        for name in _goal_robot_target_names(robot):
            if name not in current_targets:
                current_targets.append(name)
        targets["primary"] = current_targets
    return structured_task


def scene_entity_catalog(scene: dict[str, Any] | None) -> list[str]:
    if not isinstance(scene, dict):
        return []
    return sorted(flatten_scene(scene).keys())


def _unique_names(names: list[Any]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for raw_name in names:
        name = str(raw_name or "").strip()
        if name and name not in seen:
            ordered.append(name)
            seen.add(name)
    return ordered


def _as_name_list(value: Any) -> list[Any]:
    if isinstance(value, (list, tuple, set)):
        return list(value)
    if isinstance(value, str) and value.strip():
        return [value]
    return []


def _flat_scene_children(flat_scene: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    children: dict[str, list[str]] = {}
    for child_name, info in flat_scene.items():
        if not isinstance(info, dict):
            continue
        parent = str(info.get("direct_parent", "") or "")
        if parent:
            children.setdefault(parent, []).append(child_name)
    return children


def _exact_scene_names(value: Any, valid_names: set[str]) -> list[str]:
    if isinstance(value, str):
        return [value] if value in valid_names else []
    if isinstance(value, dict):
        names: list[str] = []
        for nested_value in value.values():
            names.extend(_exact_scene_names(nested_value, valid_names))
        return names
    if isinstance(value, (list, tuple, set)):
        names = []
        for nested_value in value:
            names.extend(_exact_scene_names(nested_value, valid_names))
        return names
    return []


def _goal_state_entity_names(goal_state: Any, valid_names: set[str]) -> list[str]:
    if not isinstance(goal_state, dict):
        return []
    names: list[str] = []
    entities = goal_state.get("entities", {})
    if isinstance(entities, dict):
        for entity_name, payload in entities.items():
            name = str(entity_name or "").strip()
            if name in valid_names:
                names.append(name)
            if isinstance(payload, dict):
                for field in (
                    "direct_parent", "parent", "location", "inside", "on", "ontop",
                    "under", "container", "receptacle", "destination",
                ):
                    names.extend(_exact_scene_names(payload.get(field), valid_names))
    robot = goal_state.get("robot", {})
    if isinstance(robot, dict):
        for field in ("robot_location", "location", "robot_holding", "robot_inventory"):
            names.extend(_exact_scene_names(robot.get(field), valid_names))
        names.extend(_exact_scene_names(robot.get("robot_hands"), valid_names))
    return _unique_names(names)


def _robot_context_entity_names(env_state: dict[str, Any] | None, valid_names: set[str]) -> list[str]:
    if not isinstance(env_state, dict):
        return []
    names: list[str] = []
    for field in ("robot_location", "location", "robot_holding", "robot_inventory"):
        names.extend(_exact_scene_names(env_state.get(field), valid_names))
    names.extend(_exact_scene_names(env_state.get("robot_hands"), valid_names))
    return _unique_names(names)


def _task_environment_entity_names(
    structured_task: dict[str, Any],
    flat_scene: dict[str, dict[str, Any]],
    *,
    relevant_item_names: list[Any] | None = None,
) -> list[str]:
    if not isinstance(structured_task, dict):
        structured_task = {}
    valid_names = set(flat_scene.keys())
    names: list[Any] = []
    names.extend(_as_name_list(relevant_item_names))
    names.extend(_as_name_list(structured_task.get("_understanding_relevant_item_names", [])))
    names.extend(_as_name_list(structured_task.get("task_entity_names", [])))
    names.extend(_as_name_list(structured_task.get("understanding_entity_names", [])))
    names.extend(_flatten_required_item_names(structured_task.get("required_item_names", {})))
    names.extend(_goal_state_entity_names(structured_task.get("goal_state", {}), valid_names))
    return [name for name in _unique_names(names) if name in valid_names]


def _resolve_task_environment_closure(
    flat_scene: dict[str, dict[str, Any]],
    entity_names: list[str],
    *,
    context_entity_names: list[str] | None = None,
    include_descendants: bool = True,
) -> dict[str, dict[str, Any]]:
    children = _flat_scene_children(flat_scene)
    selected: dict[str, dict[str, Any]] = {}
    visited: set[tuple[str, bool]] = set()

    def add_entity(entity_name: str, *, descendants: bool) -> None:
        if entity_name not in flat_scene:
            return
        visit_key = (entity_name, descendants)
        if visit_key in visited:
            return
        visited.add(visit_key)
        entity_info = flat_scene[entity_name]
        if entity_name not in selected:
            selected[entity_name] = copy.deepcopy(entity_info)
        for parent_name in entity_info.get("full_path", []) or []:
            if parent_name in flat_scene:
                add_entity(str(parent_name), descendants=False)
        direct_parent = str(entity_info.get("direct_parent", "") or "")
        if direct_parent in flat_scene:
            add_entity(direct_parent, descendants=False)
        if descendants and include_descendants and entity_info.get("type") != "room" and entity_info.get("is_container"):
            for child_name in children.get(entity_name, []):
                add_entity(child_name, descendants=True)

    for name in _unique_names(entity_names):
        add_entity(name, descendants=True)
    for name in _unique_names(context_entity_names or []):
        add_entity(name, descendants=False)
    return selected


def build_task_environment_closure(
    scene: dict[str, Any] | None,
    structured_task: dict[str, Any],
    env_state: dict[str, Any] | None = None,
    *,
    relevant_item_names: list[Any] | None = None,
) -> dict[str, dict[str, Any]]:
    if not isinstance(scene, dict):
        return {}
    flat_scene = flatten_scene(scene)
    valid_names = set(flat_scene.keys())
    task_names = _task_environment_entity_names(
        structured_task,
        flat_scene,
        relevant_item_names=relevant_item_names,
    )
    context_names = _robot_context_entity_names(env_state, valid_names)
    return _resolve_task_environment_closure(
        flat_scene,
        task_names,
        context_entity_names=context_names,
        include_descendants=True,
    )
