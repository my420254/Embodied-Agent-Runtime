"""Pure entity-validation helpers for planning evaluation."""

import copy
from typing import Any


def _flatten_name_values(value: Any) -> list[str]:
    if isinstance(value, dict):
        names: list[str] = []
        for key in ("primary", "alternatives"):
            names.extend(_flatten_name_values(value.get(key, [])))
        return names
    if isinstance(value, (list, tuple, set)):
        names = []
        for item in value:
            names.extend(_flatten_name_values(item))
        return names
    text = str(value or "").strip()
    return [text] if text else []


def _unique_names(values: list[str]) -> list[str]:
    ordered: list[str] = []
    seen = set()
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        ordered.append(text)
    return ordered


def _task_target_entities(structured_task: dict | None) -> list[str]:
    names_info = structured_task.get("required_item_names", {}) if isinstance(structured_task, dict) else {}
    if not isinstance(names_info, dict):
        return []
    targets = names_info.get("targets", {})
    return _unique_names(_flatten_name_values(targets))


def _task_referenced_entities(structured_task: dict | None) -> list[str]:
    names_info = structured_task.get("required_item_names", {}) if isinstance(structured_task, dict) else {}
    if not isinstance(names_info, dict):
        return []
    names: list[str] = []
    for key in ("targets", "tools", "receptacles"):
        names.extend(_flatten_name_values(names_info.get(key, [])))
    return _unique_names(names)


def _parent_chain(entity: str, env: dict[str, Any]) -> list[str]:
    chain: list[str] = []
    seen = set()
    current = entity
    while current in env and current not in seen:
        seen.add(current)
        info = env.get(current, {})
        parent = str(info.get("direct_parent", "") or "") if isinstance(info, dict) else ""
        if not parent or parent in {"robot_hand", "未知环境"} or parent not in env:
            break
        chain.append(parent)
        current = parent
    return chain


def _is_descendant(entity: str, ancestor: str, env: dict[str, Any]) -> bool:
    return bool(entity and ancestor and ancestor in _parent_chain(entity, env))


def _todo_entity_names(todo_list: list, env: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for step in todo_list or []:
        execution = step.get("execution", {}) if isinstance(step, dict) else {}
        params = execution.get("parameters", {}) if isinstance(execution, dict) else {}
        if not isinstance(params, dict):
            continue
        for value in params.values():
            name = str(value or "").strip()
            if name in env:
                names.append(name)
    return _unique_names(names)


def _find_unallowed_manipulated_entities(
    todo_list: list,
    env: dict[str, Any],
    structured_task: dict | None,
    repair_catalog,
) -> list[dict[str, Any]]:
    """检测规划序列里是否被抓取/放置/加工了“理解层未授权”的实体：
    item 参数既出现在当前环境中、又不在任务声明的实体集合里，即为违规。"""
    allowed = set(_task_referenced_entities(structured_task))
    if not allowed or not repair_catalog:
        return []

    task_targets = [
        name for name in _task_target_entities(structured_task) if name in env
    ]
    violations: list[dict[str, Any]] = []
    for step in todo_list or []:
        execution = step.get("execution", {}) if isinstance(step, dict) else {}
        if not isinstance(execution, dict):
            continue
        action = {
            "skill": str(execution.get("skill", "") or ""),
            "parameters": execution.get("parameters", {}) if isinstance(execution.get("parameters"), dict) else {},
        }
        spec = repair_catalog.get(action["skill"])
        if not spec or not spec.item_param:
            continue
        item = spec.item_value(action)
        carrier_of_task_target = (
            bool(spec.can_transform_item)
            and any(_is_descendant(target, item, env) for target in task_targets)
        )
        if item and item in env and item not in allowed and not carrier_of_task_target:
            violations.append(
                {
                    "step": step.get("step"),
                    "skill": action["skill"],
                    "parameter": spec.item_param,
                    "entity": item,
                    "allowed_entities": sorted(allowed),
                }
            )
    return violations


__all__ = [
    "_flatten_name_values",
    "_unique_names",
    "_task_target_entities",
    "_task_referenced_entities",
    "_parent_chain",
    "_is_descendant",
    "_todo_entity_names",
    "_find_unallowed_manipulated_entities",
]
