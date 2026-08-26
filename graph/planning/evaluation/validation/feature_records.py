from __future__ import annotations

import copy
from typing import Any

from graph.planning.config import sda_max_backtrack_depth, sda_max_subtree_actions


PROCESS_NAME_BY_FEATURE = {
    "sandbox": "sandbox_validation",
    "sda": "dependency_repair",
    "final_state": "final_state_audit",
}


def _compact_value(value: Any, *, max_chars: int = 800, max_items: int = 20) -> Any:
    if isinstance(value, str):
        return value if len(value) <= max_chars else value[:max_chars] + f"... <truncated {len(value) - max_chars} chars>"
    if isinstance(value, dict):
        items = list(value.items())
        compacted = {str(key): _compact_value(item, max_chars=max_chars, max_items=max_items) for key, item in items[:max_items]}
        if len(items) > max_items:
            compacted["_truncated"] = len(items) - max_items
        return compacted
    if isinstance(value, list):
        compacted = [_compact_value(item, max_chars=max_chars, max_items=max_items) for item in value[:max_items]]
        if len(value) > max_items:
            compacted.append({"_truncated": len(value) - max_items})
        return compacted
    return copy.deepcopy(value)


def feature_record(
    name: str,
    *,
    enabled: bool,
    status: str,
    config: dict[str, Any] | None = None,
    inputs: dict[str, Any] | None = None,
    outputs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "process_name": PROCESS_NAME_BY_FEATURE.get(str(name), str(name)),
        "enabled": bool(enabled),
        "status": str(status or "unknown"),
        "config": _compact_value(config or {}),
        "inputs": _compact_value(inputs or {}),
        "outputs": _compact_value(outputs or {}),
    }


def environment_summary(environment: Any) -> dict[str, Any]:
    if not isinstance(environment, dict):
        return {"available": False}
    names = sorted(str(name) for name in environment.keys())
    type_counts: dict[str, int] = {}
    stateful_entities: dict[str, Any] = {}
    for name, info in environment.items():
        if not isinstance(info, dict):
            type_counts["unknown"] = type_counts.get("unknown", 0) + 1
            continue
        entity_type = str(info.get("type") or "unknown")
        type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        states = info.get("states", {})
        if states and len(stateful_entities) < 20:
            stateful_entities[str(name)] = copy.deepcopy(states)
    return {
        "available": True,
        "entity_count": len(environment),
        "type_counts": type_counts,
        "entities_sample": names[:40],
        "entities_truncated": len(names) > 40,
        "states_sample": stateful_entities,
    }


def robot_summary(robot: Any) -> dict[str, Any]:
    return _compact_value(robot if isinstance(robot, dict) else {"available": False}, max_chars=500)


def sequence_summary(sequence: Any) -> dict[str, Any]:
    items = sequence if isinstance(sequence, list) else []
    return {
        "count": len(items),
        "sample": _compact_value(items[:8], max_chars=500, max_items=8),
        "truncated": len(items) > 8,
    }


def state_diff_summary(state_diff: Any) -> dict[str, Any]:
    if not isinstance(state_diff, dict):
        return {"available": False}
    changed = state_diff.get("entities", [])
    changed_names = [
        str(item.get("name", ""))
        for item in changed
        if isinstance(item, dict) and str(item.get("name", "")).strip()
    ] if isinstance(changed, list) else []
    robot = state_diff.get("robot", {})
    return {
        "available": True,
        "entity_count_compared": state_diff.get("entity_count_compared"),
        "changed_entity_count": state_diff.get("changed_entity_count", len(changed_names)),
        "changed_entities_sample": changed_names[:40],
        "changed_entities_truncated": len(changed_names) > 40,
        "robot_changed": bool(robot.get("changed", False)) if isinstance(robot, dict) else False,
    }


def debug_event_counts(events: Any, *, layer: str | None = None) -> dict[str, int]:
    counts: dict[str, int] = {}
    if not isinstance(events, list):
        return counts
    for event in events:
        if not isinstance(event, dict):
            continue
        if layer is not None and str(event.get("layer", "")) != layer:
            continue
        key = str(event.get("type", "unknown") or "unknown")
        counts[key] = counts.get(key, 0) + 1
    return counts


def sandbox_rejection_events(events: Any, *, limit: int = 12) -> list[dict[str, Any]]:
    if not isinstance(events, list):
        return []
    rejected: list[dict[str, Any]] = []
    for event in events:
        if not isinstance(event, dict):
            continue
        if str(event.get("layer", "")) != "sandbox":
            continue
        if str(event.get("type", "")) != "step_check" or bool(event.get("ok", True)):
            continue
        rejected.append(
            {
                "skill": event.get("skill", ""),
                "parameters": _compact_value(event.get("parameters", {}), max_chars=500),
                "todo_step": _compact_value(event.get("todo_step", {}), max_chars=500),
                "issue_type": event.get("issue_type", ""),
                "fix": event.get("fix", ""),
            }
        )
        if len(rejected) >= limit:
            break
    return rejected


def evaluator_failure_events(events: Any, *, limit: int = 12) -> list[dict[str, Any]]:
    if not isinstance(events, list):
        return []
    failures: list[dict[str, Any]] = []
    for event in events:
        if not isinstance(event, dict):
            continue
        if str(event.get("layer", "")) != "planning_evaluator":
            continue
        if str(event.get("type", "")) != "audit_failure":
            continue
        failures.append(
            {
                "issue": event.get("issue", ""),
                "fix": event.get("fix", ""),
                "step_info": _compact_value(event.get("step_info", {}), max_chars=500),
                "validated_steps_count": event.get("validated_steps_count"),
                "validated_todo_actions_count": event.get("validated_todo_actions_count"),
            }
        )
        if len(failures) >= limit:
            break
    return failures


def sandbox_feature_record(
    *,
    sandbox_enabled: bool,
    state: dict[str, Any],
    todo_list: list[dict[str, Any]],
    sandbox_result: Any,
    debug_events: list[dict[str, Any]],
) -> dict[str, Any]:
    failed = sandbox_result.failure_payload is not None
    status = "disabled" if not sandbox_enabled else ("failed" if failed else "passed")
    return feature_record(
        "sandbox",
        enabled=sandbox_enabled,
        status=status,
        config={
            "todo_step_adapter_path": state.get("todo_step_adapter_path", ""),
            "validator": "todo_schema" if state.get("todo_step_adapter_path") else "execution_shape",
        },
        inputs={
            "todo_list": sequence_summary(todo_list),
            "initial_environment": environment_summary(sandbox_result.sandbox_start_env),
            "initial_robot": robot_summary(sandbox_result.sandbox_start_robot),
        },
        outputs={
            "validated_steps": sequence_summary(sandbox_result.validated_steps),
            "validated_todo_actions": sequence_summary(sandbox_result.validated_todo_actions),
            "validated_audit_steps": sequence_summary(sandbox_result.validated_audit_steps),
            "final_environment": environment_summary(sandbox_result.sim_env),
            "final_robot": robot_summary(sandbox_result.sim_robot),
            "debug_event_counts": debug_event_counts(debug_events, layer="sandbox"),
            "sandbox_rejections": sandbox_rejection_events(debug_events),
            "planning_evaluator_failures": evaluator_failure_events(debug_events),
            "failed_action": _compact_value((sandbox_result.failure_payload or {}).get("failed_action", {})),
            "failure_layer": (sandbox_result.failure_payload or {}).get("failure_layer", ""),
            "failure_category": (sandbox_result.failure_payload or {}).get("failure_category", ""),
            "error_feedback": (sandbox_result.failure_payload or {}).get("error_feedback", ""),
            "failure_error_code": (sandbox_result.failure_payload or {}).get("failure_error_code", ""),
            "dataset_failure_diagnosis": _compact_value(
                (sandbox_result.failure_payload or {}).get("dataset_failure_diagnosis", {})
            ),
        },
    )


def sda_feature_record(
    *,
    sda_active: bool,
    repair_strategy: str,
    sandbox_result: Any,
    failure_payload: dict[str, Any] | None,
    debug_events: list[dict[str, Any]],
) -> dict[str, Any]:
    sda_state = sandbox_result.sda_success_state or ((failure_payload or {}).get("sda_state") if isinstance(failure_payload, dict) else {})
    counts = debug_event_counts(debug_events, layer="sda")
    if not sda_active:
        status = "disabled"
    elif counts.get("repair_success", 0):
        status = "repaired"
    elif counts.get("repair_failed", 0) or counts.get("repair_exception", 0) or counts.get("todo_checkpoint_exception", 0):
        status = "failed"
    elif counts:
        status = "recorded"
    else:
        status = "not_triggered"
    return feature_record(
        "sda",
        enabled=sda_active,
        status=status,
        config={
            "repair_strategy": repair_strategy,
            "max_backtrack_depth": sda_max_backtrack_depth(),
            "max_subtree_actions": sda_max_subtree_actions(),
        },
        inputs={
            "sandbox_failure_present": bool(failure_payload),
            "debug_event_counts": counts,
        },
        outputs={
            "sda_state": sda_state if isinstance(sda_state, dict) else {},
            "validated_steps": sequence_summary(sandbox_result.validated_steps),
            "validated_todo_actions": sequence_summary(sandbox_result.validated_todo_actions),
        },
    )


def final_state_feature_record(
    *,
    enabled: bool,
    status: str,
    state_diff: dict[str, Any] | None,
    audit_result: dict[str, Any] | None,
    sandbox_start_env: dict[str, dict[str, Any]] | None,
    sandbox_start_robot: dict[str, Any] | None,
    final_env: dict[str, dict[str, Any]] | None,
    final_robot: dict[str, Any] | None,
    simulated_steps: list[dict[str, Any]] | None,
    task_context: dict[str, Any],
    structured_task: dict[str, Any] | None = None,
) -> dict[str, Any]:
    structured_task = structured_task if isinstance(structured_task, dict) else {}
    goal_state = (
        task_context.get("external_goal_state")
        or task_context.get("final_state")
        or task_context.get("goal_state")
        or structured_task.get("goal_state")
        or structured_task.get("desired_state")
        or structured_task.get("target_state")
        or {}
    )
    return feature_record(
        "final_state",
        enabled=enabled,
        status=status,
        config={
            "state_diff_audit": enabled,
            "auditor": "framework.planning.state_diff_audit_llm" if enabled else "",
            "benchmark_comparer": (audit_result or {}).get("benchmark_final_state_compare", {}).get("comparer_module", ""),
        },
        inputs={
            "understanding_goal": {
                "intent": structured_task.get("intent", ""),
                "required_item_names": structured_task.get("required_item_names", {}),
                "quantity_constraints": structured_task.get("quantity_constraints", []),
                "goal_state": structured_task.get("goal_state", {}),
                "desired_state": structured_task.get("desired_state", {}),
                "target_state": structured_task.get("target_state", {}),
                "final_state": structured_task.get("final_state", {}),
            },
            "has_external_goal": bool(goal_state) or bool(str(task_context.get("external_goal_text", "") or "").strip()),
            "external_goal_state": goal_state if isinstance(goal_state, dict) else {},
            "simulated_steps": sequence_summary(simulated_steps or []),
            "initial_environment": environment_summary(sandbox_start_env or {}),
            "initial_robot": robot_summary(sandbox_start_robot or {}),
            "final_environment": environment_summary(final_env or {}),
            "final_robot": robot_summary(final_robot or {}),
        },
        outputs={
            "state_diff": state_diff_summary(state_diff or {}),
            "audit_passed": bool((audit_result or {}).get("is_passed")) if audit_result else None,
            "issue": (audit_result or {}).get("issue", ""),
            "repair_mode": (audit_result or {}).get("repair_mode", ""),
            "benchmark_compare": (audit_result or {}).get("benchmark_final_state_compare", {}),
        },
    )


def skipped_feature_record(name: str, *, enabled: bool, reason: str, config: dict[str, Any] | None = None) -> dict[str, Any]:
    return feature_record(
        name,
        enabled=enabled,
        status="skipped" if enabled else "disabled",
        config=config or {},
        inputs={"reason": reason},
        outputs={},
    )
