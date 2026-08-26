# validation/state_diff.py - pure state-diff helpers.
# 这些函数只依赖 copy / json 等标准库以及 entities 里的纯辅助，
# 不读取可被测试 monkeypatch 的全局符号，可安全下沉到子包。
import copy
import json
from typing import Any

from .entities import (
    _parent_chain,
    _task_referenced_entities,
    _todo_entity_names,
    _unique_names,
)


def _json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


def _compact_entity_state(info: Any) -> dict[str, Any]:
    if not isinstance(info, dict):
        return {"value": copy.deepcopy(info)}

    compact: dict[str, Any] = {}
    for key in ("type", "direct_parent", "direct_relation", "is_container", "full_path"):
        if key in info:
            compact[key] = copy.deepcopy(info.get(key))

    states = info.get("states", {})
    compact["states"] = copy.deepcopy(states) if isinstance(states, dict) else copy.deepcopy(states)
    properties = info.get("properties", [])
    compact["properties"] = copy.deepcopy(properties) if isinstance(properties, list) else copy.deepcopy(properties)
    return compact


def _build_state_diff(
    before_env: dict[str, Any] | None,
    before_robot: dict[str, Any] | None,
    after_env: dict[str, Any] | None,
    after_robot: dict[str, Any] | None,
    *,
    max_changed_entities: int = 120,
) -> dict[str, Any]:
    """把 before/after 两侧的扁平环境索引与机器人状态做差异比对，
    返回结构化 diff（仅包含真正发生变化的实体，超出上限则截断计数）。"""
    before_entities = before_env if isinstance(before_env, dict) else {}
    after_entities = after_env if isinstance(after_env, dict) else {}
    entity_names = sorted(set(before_entities) | set(after_entities), key=str)
    changed_entities: list[dict[str, Any]] = []
    truncated_entity_count = 0

    for name in entity_names:
        before_exists = name in before_entities
        after_exists = name in after_entities
        before_state = _compact_entity_state(before_entities.get(name)) if before_exists else None
        after_state = _compact_entity_state(after_entities.get(name)) if after_exists else None
        if before_state == after_state:
            continue

        if not before_exists:
            change_type = "added"
        elif not after_exists:
            change_type = "removed"
        else:
            change_type = "updated"

        if len(changed_entities) < max_changed_entities:
            changed_entities.append(
                {
                    "name": name,
                    "change_type": change_type,
                    "before": before_state,
                    "after": after_state,
                }
            )
        else:
            truncated_entity_count += 1

    robot_before = copy.deepcopy(before_robot) if isinstance(before_robot, dict) else {}
    robot_after = copy.deepcopy(after_robot) if isinstance(after_robot, dict) else {}
    robot_changed = robot_before != robot_after
    changed_entity_count = len(changed_entities) + truncated_entity_count
    return {
        "entity_count_compared": len(entity_names),
        "changed_entity_count": changed_entity_count,
        "truncated_entity_count": truncated_entity_count,
        "has_changes": bool(robot_changed or changed_entity_count),
        "robot": (
            {
                "changed": True,
                "before": robot_before,
                "after": robot_after,
            }
            if robot_changed
            else {"changed": False}
        ),
        "entities": changed_entities,
    }


def _build_state_audit_context(
    before_env: dict[str, Any] | None,
    before_robot: dict[str, Any] | None,
    after_env: dict[str, Any] | None,
    after_robot: dict[str, Any] | None,
    todo_list: list,
    structured_task: dict | None,
    *,
    max_entities: int = 160,
) -> dict[str, Any]:
    """构造交给 LLM 状态差异审计用的上下文：聚焦任务相关 + 真正变化实体，截断冗余。"""
    before_entities = before_env if isinstance(before_env, dict) else {}
    after_entities = after_env if isinstance(after_env, dict) else {}
    all_entities = set(before_entities) | set(after_entities)
    relevant = _task_referenced_entities(structured_task)
    relevant.extend(_todo_entity_names(todo_list, after_entities or before_entities))
    for name in list(relevant):
        if name in after_entities:
            relevant.extend(_parent_chain(name, after_entities))
        elif name in before_entities:
            relevant.extend(_parent_chain(name, before_entities))

    changed = [
        name
        for name in sorted(all_entities, key=str)
        if _compact_entity_state(before_entities.get(name)) != _compact_entity_state(after_entities.get(name))
    ]
    ordered_names = _unique_names([name for name in relevant if name in all_entities] + changed)
    truncated_count = max(0, len(ordered_names) - max_entities)
    selected_names = ordered_names[:max_entities]
    entities = [
        {
            "name": name,
            "changed": _compact_entity_state(before_entities.get(name)) != _compact_entity_state(after_entities.get(name)),
            "before": _compact_entity_state(before_entities.get(name)) if name in before_entities else None,
            "after": _compact_entity_state(after_entities.get(name)) if name in after_entities else None,
        }
        for name in selected_names
    ]
    return {
        "entity_count_available": len(all_entities),
        "entity_count_in_context": len(entities),
        "truncated_entity_count": truncated_count,
        "note": "state_diff only lists changed entities; unchanged entities in this context still prove final goal state when their after state satisfies the task.",
        "robot": {
            "changed": copy.deepcopy(before_robot or {}) != copy.deepcopy(after_robot or {}),
            "before": copy.deepcopy(before_robot or {}),
            "after": copy.deepcopy(after_robot or {}),
        },
        "entities": entities,
    }


__all__ = [
    "_json_dumps",
    "_compact_entity_state",
    "_build_state_diff",
    "_build_state_audit_context",
]
