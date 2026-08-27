from __future__ import annotations

from typing import Any


def robot_only_goal_has_non_robot_requirements(
    structured_task: dict,
    task_context: dict | None,
    entity_goals: list[dict[str, Any]],
    robot_goal: dict[str, Any],
) -> bool:
    if entity_goals or not robot_goal:
        return False
    robot_goal_keys = {str(key).strip().lower() for key in robot_goal if str(key).strip()}
    if not robot_goal_keys or robot_goal_keys - {"battery", "battery_full"}:
        return False

    text_parts = [
        str(structured_task.get("intent") or ""),
    ]
    required_items = structured_task.get("required_item_names")
    if isinstance(required_items, dict):
        for value in required_items.values():
            if isinstance(value, dict):
                text_parts.extend(str(item) for item in value.get("primary") or [])
                text_parts.extend(str(item) for item in value.get("alternatives") or [])
            elif isinstance(value, list):
                text_parts.extend(str(item) for item in value)
    text = " ".join(text_parts).lower()
    non_robot_markers = {
        "assemble",
        "banana_peel",
        "bring",
        "clean_mop",
        "cola_can",
        "dining_table",
        "dispose",
        "floor",
        "floor_clean",
        "food residue",
        "item_disposed",
        "load",
        "mop",
        "mop_clean",
        "place",
        "rotting_apple",
        "rubbish",
        "trash",
        "unload",
    }
    return any(marker in text for marker in non_robot_markers)
