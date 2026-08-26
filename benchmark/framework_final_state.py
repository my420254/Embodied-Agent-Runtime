from __future__ import annotations

import copy
from typing import Any


def _keys_with_values(payload: dict[str, Any]) -> list[str]:
    return sorted(str(key) for key, value in payload.items() if value not in (None, "", [], {}))


def _compact(value: Any, *, max_items: int = 40) -> Any:
    if isinstance(value, dict):
        items = list(value.items())
        compacted = {str(key): _compact(item, max_items=max_items) for key, item in items[:max_items]}
        if len(items) > max_items:
            compacted["_truncated"] = len(items) - max_items
        return compacted
    if isinstance(value, list):
        compacted = [_compact(item, max_items=max_items) for item in value[:max_items]]
        if len(value) > max_items:
            compacted.append({"_truncated": len(value) - max_items})
        return compacted
    return copy.deepcopy(value)


def _state_diff_summary(state_diff: dict[str, Any]) -> dict[str, Any]:
    entities = state_diff.get("entities", [])
    entity_changes = entities if isinstance(entities, list) else []
    changed_names = [
        str(item.get("name", ""))
        for item in entity_changes
        if isinstance(item, dict) and str(item.get("name", "")).strip()
    ]
    robot = state_diff.get("robot", {})
    return {
        "entity_count_compared": state_diff.get("entity_count_compared"),
        "changed_entity_count": state_diff.get("changed_entity_count", len(changed_names)),
        "changed_entities": changed_names[:40],
        "changed_entities_truncated": len(changed_names) > 40,
        "robot_changed": bool(robot.get("changed", False)) if isinstance(robot, dict) else False,
        "robot_change": _compact(robot, max_items=20) if isinstance(robot, dict) else {},
    }


def _environment_summary(environment: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(environment, dict):
        return {"available": False}
    stateful: dict[str, Any] = {}
    relationful: dict[str, Any] = {}
    type_counts: dict[str, int] = {}
    for name, info in environment.items():
        if not isinstance(info, dict):
            type_counts["unknown"] = type_counts.get("unknown", 0) + 1
            continue
        entity_type = str(info.get("type") or "unknown")
        type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        states = info.get("states", {})
        if isinstance(states, dict) and states and len(stateful) < 20:
            stateful[str(name)] = copy.deepcopy(states)
        relation = str(info.get("direct_relation") or "").strip()
        parent = str(info.get("direct_parent") or "").strip()
        if (relation or parent) and len(relationful) < 20:
            relationful[str(name)] = {
                "direct_relation": relation,
                "direct_parent": parent,
            }
    return {
        "available": True,
        "entity_count": len(environment),
        "type_counts": type_counts,
        "states_sample": stateful,
        "relations_sample": relationful,
    }


def build_local_compare(
    packet: dict[str, Any],
    *,
    benchmark: str,
    environment_format: str,
    action_format: str,
    official_evaluator: str,
    task_context_fields: list[str],
    evaluation_context_fields: list[str] | None = None,
    goal_projection: Any = None,
    fairness_notes: list[str] | None = None,
) -> dict[str, Any]:
    task_context = packet.get("task_context", {})
    if not isinstance(task_context, dict):
        task_context = {}
    evaluation_context = packet.get("evaluation_context", {})
    if not isinstance(evaluation_context, dict):
        evaluation_context = {}
    external_goal = packet.get("external_goal", {})
    if not isinstance(external_goal, dict):
        external_goal = {}
    initial = packet.get("initial", {})
    final = packet.get("final", {})
    state_diff = packet.get("state_diff", {})

    selected_task_context = {
        key: copy.deepcopy(task_context.get(key))
        for key in task_context_fields
        if key in task_context and task_context.get(key) not in (None, "", [], {})
    }
    selected_evaluation_context = {
        key: copy.deepcopy(evaluation_context.get(key))
        for key in (evaluation_context_fields or [])
        if key in evaluation_context and evaluation_context.get(key) not in (None, "", [], {})
    }

    return {
        "benchmark": benchmark,
        "status": "prepared_for_framework_llm_judge",
        "environment_format": environment_format,
        "action_format": action_format,
        "official_evaluator": official_evaluator,
        "used_fields": {
            "task_context": sorted(selected_task_context.keys()),
            "evaluation_context": sorted(selected_evaluation_context.keys()),
            "external_goal": _keys_with_values(external_goal),
            "state_diff": ["entities", "robot"],
        },
        "benchmark_goal": {
            "task_context": _compact(selected_task_context),
            "evaluation_context": _compact(selected_evaluation_context),
            "goal_projection": _compact(goal_projection),
            "external_goal": _compact(external_goal),
        },
        "understanding_final_state": copy.deepcopy(external_goal.get("structured_final_state", {})),
        "state_diff_summary": _state_diff_summary(state_diff if isinstance(state_diff, dict) else {}),
        "initial_environment_summary": _environment_summary(initial.get("environment", {}) if isinstance(initial, dict) else {}),
        "final_environment_summary": _environment_summary(final.get("environment", {}) if isinstance(final, dict) else {}),
        "initial_robot": _compact(initial.get("robot", {}) if isinstance(initial, dict) else {}),
        "final_robot": _compact(final.get("robot", {}) if isinstance(final, dict) else {}),
        "fairness_notes": list(fairness_notes or []),
        "judge_contract": (
            "公共 final-state audit 只能依据本 benchmark-local goal packet、understanding_final_state、"
            "sandbox 前后环境差异和任务原文判断完成度；不得转换到其他 benchmark 的动作或环境格式。"
        ),
    }


__all__ = ["build_local_compare"]
