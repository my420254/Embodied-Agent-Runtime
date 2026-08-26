from __future__ import annotations

import copy
from typing import Any
from domain.scene import flatten_scene
from config.settings import active_config_file, get_config
from graph.planning.config import active_repair_strategy
from skills.planning_catalog import load_planning_catalog


TRACE_SCHEMA_VERSION = "framework_trace_v3"


def process_header(process_name: str, payload_role: str) -> dict[str, str]:
    return {
        "schema_version": TRACE_SCHEMA_VERSION,
        "process_name": process_name,
        "payload_role": payload_role,
    }


def compact_value(value: Any, *, max_chars: int = 500) -> Any:
    if isinstance(value, str):
        return value if len(value) <= max_chars else value[:max_chars] + f"... <truncated {len(value) - max_chars} chars>"
    if isinstance(value, dict):
        return {str(key): compact_value(item, max_chars=max_chars) for key, item in value.items()}
    if isinstance(value, list):
        return [compact_value(item, max_chars=max_chars) for item in value]
    return value


def benchmark_trace_counters(benchmark_trace: dict | None) -> dict[str, int]:
    trace = benchmark_trace if isinstance(benchmark_trace, dict) else {}
    llm_io = trace.get("llm_io", []) if isinstance(trace.get("llm_io"), list) else []
    planning_output = {}
    if isinstance(trace.get("planning_output_full"), dict):
        planning_output = trace["planning_output_full"]
    elif isinstance(trace.get("planning_output"), dict):
        planning_output = trace["planning_output"]
    debug_events = planning_output.get("planning_debug_events", [])
    if not isinstance(debug_events, list):
        debug_events = []

    sandbox_reject_count = 0
    total_sandbox_checks = 0
    total_planning_audit_failures = 0
    todo_contract_pass_count = 0
    todo_contract_reject_count = 0
    for event in debug_events:
        if not isinstance(event, dict):
            continue
        layer = str(event.get("layer", ""))
        event_type = str(event.get("type", ""))
        if layer == "sandbox" and event_type == "step_check":
            total_sandbox_checks += 1
            if not bool(event.get("ok", False)):
                sandbox_reject_count += 1
        if layer == "planning_evaluator" and event_type == "audit_failure":
            total_planning_audit_failures += 1
        if layer == "todo_contract" and event_type == "passed":
            todo_contract_pass_count += 1
        if layer == "todo_contract" and event_type == "rejected":
            todo_contract_reject_count += 1

    return {
        "llm_call_count": len(llm_io),
        "sandbox_reject_count": sandbox_reject_count,
        "total_sandbox_checks": total_sandbox_checks,
        "total_planning_audit_failures": total_planning_audit_failures,
        "todo_contract_pass_count": todo_contract_pass_count,
        "todo_contract_reject_count": todo_contract_reject_count,
    }


def sample_list(values: list[Any], *, limit: int = 40) -> dict[str, Any]:
    normalized = [str(value) for value in values]
    return {
        "count": len(normalized),
        "sample": normalized[:limit],
        "truncated": len(normalized) > limit,
    }


def sequence_summary(values: Any, *, limit: int = 8) -> dict[str, Any]:
    items = values if isinstance(values, list) else []
    return {
        "count": len(items),
        "sample": compact_value(items[:limit]),
        "truncated": len(items) > limit,
    }


def _planning_contract_action_summary(spec: Any) -> dict[str, Any]:
    return {
        "skill": str(getattr(spec, "name", "") or ""),
        "action_name": str(getattr(spec, "action_name", "") or ""),
        "action_field": str(getattr(spec, "action_field", "") or ""),
        "required_fields": list(getattr(spec, "required_fields", ()) or ()),
        "fixed_fields": [
            {"field": field, "value": value}
            for field, value in (getattr(spec, "fixed_fields", ()) or ())
        ],
        "entity_fields": list(getattr(spec, "entity_fields", ()) or ()),
        "room_fields": list(getattr(spec, "room_fields", ()) or ()),
        "args_field": str(getattr(spec, "args_field", "") or ""),
        "args_arity": getattr(spec, "args_arity", None),
        "entity_args": list(getattr(spec, "entity_args", ()) or ()),
        "allow_extra_fields": bool(getattr(spec, "allow_extra_fields", False)),
        "allow_comma_separated_entities": bool(getattr(spec, "allow_comma_separated_entities", False)),
        "entity_pattern": str(getattr(spec, "entity_pattern", "") or ""),
        "dynamic_entity_rule": str(getattr(spec, "dynamic_entity_rule", "") or ""),
        "unchecked_fields": list(getattr(spec, "unchecked_fields", ()) or ()),
        "context_field": str(getattr(spec, "context_field", "") or ""),
        "context_values": list(getattr(spec, "context_values", ()) or ()),
    }


def planning_contract_summary(profile: str | None = None) -> dict[str, Any]:
    """Record the enabled planner contract that was active for this case."""
    try:
        catalog = load_planning_catalog(profile)
    except Exception as exc:
        return {
            "available": False,
            "profile": str(profile or ""),
            "config_file": active_config_file(),
            "skills_root": str(get_config("skills", "root", default="skills") or ""),
            "error": repr(exc),
        }
    raw_actions = [_planning_contract_action_summary(spec) for spec in catalog.raw_specs]
    framework_specs = [str(getattr(spec, "name", "") or "") for spec in catalog.specs]
    return {
        "available": True,
        "profile": str(profile or ""),
        "config_file": active_config_file(),
        "skills_root": str(get_config("skills", "root", default="skills") or ""),
        "enabled_contract_skill_count": len(catalog.specs),
        "raw_contract_count": len(catalog.raw_specs),
        "framework_contract_skills": framework_specs,
        "raw_action_names": [
            item["action_name"] or item["skill"]
            for item in raw_actions
        ],
        "raw_actions": raw_actions,
    }


def scene_summary(scene: Any) -> dict[str, Any]:
    if not isinstance(scene, dict):
        return {"available": False}
    flat = flatten_scene(scene)
    type_counts: dict[str, int] = {}
    states = {}
    for name, info in flat.items():
        entity_type = str(info.get("type") or "unknown") if isinstance(info, dict) else "unknown"
        type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        entity_states = info.get("states", {}) if isinstance(info, dict) else {}
        if entity_states and len(states) < 20:
            states[name] = entity_states
    rooms = sorted(name for name, info in flat.items() if isinstance(info, dict) and info.get("type") == "room")
    receptacles = sorted(name for name, info in flat.items() if isinstance(info, dict) and info.get("type") == "receptacle")
    return {
        "available": True,
        "entity_count": len(flat),
        "type_counts": type_counts,
        "rooms": sample_list(rooms, limit=20),
        "receptacles": sample_list(receptacles, limit=30),
        "entities": sample_list(sorted(flat.keys()), limit=40),
        "states_sample": states,
        "nesting": nested_scene_audit(scene),
        "flat_schema": environment_schema_audit(flat),
    }


def nested_scene_audit(scene: Any) -> dict[str, Any]:
    if not isinstance(scene, dict):
        return {"available": False}

    contains_node_count = 0
    max_depth = 0

    def walk(node: Any, depth: int) -> None:
        nonlocal contains_node_count, max_depth
        if not isinstance(node, dict):
            return
        contains = node.get("contains")
        if isinstance(contains, dict) and contains:
            contains_node_count += 1
            max_depth = max(max_depth, depth + 1)
            for child in contains.values():
                walk(child, depth + 1)
        environment = node.get("environment")
        if isinstance(environment, dict):
            for child in environment.values():
                walk(child, depth)
        for key, value in node.items():
            if key in {"contains", "environment", "states", "properties"}:
                continue
            if isinstance(value, dict):
                walk(value, depth)

    walk(scene, 0)
    return {
        "available": True,
        "contains_node_count": contains_node_count,
        "max_depth": max_depth,
    }


def environment_schema_audit(environment: Any) -> dict[str, Any]:
    if not isinstance(environment, dict):
        return {"available": False}
    standard_fields = (
        "direct_parent",
        "direct_relation",
        "type",
        "states",
        "properties",
        "is_container",
        "full_path",
    )
    field_counts = {field: 0 for field in standard_fields}
    state_entity_count = 0
    property_entity_count = 0
    relation_entity_count = 0
    full_path_entity_count = 0
    container_count = 0
    parent_missing: list[str] = []
    parent_reference_missing: list[str] = []
    names = {str(name) for name in environment}
    for raw_name, info in environment.items():
        name = str(raw_name)
        if not isinstance(info, dict):
            parent_missing.append(name)
            continue
        for field in standard_fields:
            if field in info:
                field_counts[field] += 1
        if isinstance(info.get("states"), dict) and info["states"]:
            state_entity_count += 1
        if isinstance(info.get("properties"), list) and info["properties"]:
            property_entity_count += 1
        if str(info.get("direct_relation") or "").strip():
            relation_entity_count += 1
        if isinstance(info.get("full_path"), list) and info["full_path"]:
            full_path_entity_count += 1
        if bool(info.get("is_container", False)):
            container_count += 1
        parent = str(info.get("direct_parent", "") or "")
        if not parent:
            parent_missing.append(name)
        elif parent not in {"未知环境", "robot_hand"} and parent not in names:
            parent_reference_missing.append(name)
    return {
        "available": True,
        "entity_count": len(environment),
        "standard_field_counts": field_counts,
        "relation_entity_count": relation_entity_count,
        "state_entity_count": state_entity_count,
        "property_entity_count": property_entity_count,
        "container_count": container_count,
        "full_path_entity_count": full_path_entity_count,
        "parent_missing_count": len(parent_missing),
        "parent_missing_sample": parent_missing[:20],
        "parent_reference_missing_count": len(parent_reference_missing),
        "parent_reference_missing_sample": parent_reference_missing[:20],
    }


def environment_summary(environment: Any) -> dict[str, Any]:
    if not isinstance(environment, dict):
        return {"available": False}
    names = sorted(str(name) for name in environment.keys())
    type_counts: dict[str, int] = {}
    states = {}
    for name, info in environment.items():
        entity_type = str(info.get("type") or "unknown") if isinstance(info, dict) else "unknown"
        type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        entity_states = info.get("states", {}) if isinstance(info, dict) else {}
        if entity_states and len(states) < 20:
            states[name] = entity_states
    return {
        "available": True,
        "entity_count": len(environment),
        "type_counts": type_counts,
        "entities": sample_list(names, limit=40),
        "states_sample": states,
        "schema": environment_schema_audit(environment),
    }


def environment_facts(environment: Any, *, limit: int = 80) -> dict[str, Any]:
    if not isinstance(environment, dict):
        return {"available": False}
    facts = []
    for name in sorted(environment.keys())[:limit]:
        info = environment.get(name, {})
        if not isinstance(info, dict):
            continue
        facts.append(
            {
                "name": name,
                "direct_parent": info.get("direct_parent", ""),
                "direct_relation": info.get("direct_relation", ""),
                "full_path": info.get("full_path", []),
                "states": info.get("states", {}),
                "properties": info.get("properties", []),
                "type": info.get("type"),
                "is_container": bool(info.get("is_container", False)),
            }
        )
    return {
        "available": True,
        "entity_count": len(environment),
        "facts": facts,
        "truncated": len(environment) > limit,
    }


def case_input_summary(case_input: dict[str, Any]) -> dict[str, Any]:
    summary = {
        **process_header("case_input", "output"),
        "keys": sorted(case_input.keys()),
        "dataset": case_input.get("dataset"),
        "task_id": case_input.get("task_id"),
        "identifier": case_input.get("identifier"),
        "benchmark_settings_file": case_input.get("benchmark_settings_file", ""),
        "environment_source": case_input.get("environment_source", ""),
        "instruction": case_input.get("instruction") or case_input.get("task_desc"),
    }
    if isinstance(case_input.get("scene_graph"), dict):
        summary["scene_graph"] = {
            "top_level_keys": sorted(case_input["scene_graph"].keys())[:40],
            "top_level_count": len(case_input["scene_graph"]),
        }
    if isinstance(case_input.get("init_graph"), dict):
        init_graph = case_input["init_graph"]
        summary["init_graph"] = {
            "node_count": len(init_graph.get("nodes", [])) if isinstance(init_graph.get("nodes"), list) else None,
            "edge_count": len(init_graph.get("edges", [])) if isinstance(init_graph.get("edges"), list) else None,
        }
    if isinstance(case_input.get("task_goal"), dict):
        summary["task_goal_keys"] = sorted(case_input["task_goal"].keys())
    return compact_value(summary)


def prepared_summary(prepared: Any) -> dict[str, Any]:
    return {
        **process_header("environment_preparation", "output"),
        "instruction": prepared.instruction,
        "env_state": compact_value(prepared.env_state),
        "entity_catalog": sample_list(prepared.entity_catalog, limit=50),
        "scene": scene_summary(prepared.scene),
        "context": compact_value(prepared.context),
    }


def prepared_payload(prepared: Any) -> dict[str, Any]:
    return {
        **process_header("environment_preparation", "output"),
        "instruction": prepared.instruction,
        "env_state": copy.deepcopy(prepared.env_state),
        "entity_catalog": list(prepared.entity_catalog or []),
        "scene": copy.deepcopy(prepared.scene) if isinstance(prepared.scene, dict) else {},
        "context": copy.deepcopy(prepared.context),
    }


def _message_contents(state: dict[str, Any]) -> list[str]:
    return [str(getattr(message, "content", message)) for message in state.get("messages", [])]


def understanding_input_summary(state: dict[str, Any]) -> dict[str, Any]:
    task_context = state.get("task_context", {})
    return {
        **process_header("understanding", "input"),
        "raw_instruction": state.get("raw_instruction"),
        "original_instruction": state.get("original_instruction"),
        "messages": _message_contents(state),
        "task_context": compact_value(task_context),
        "feature_flags": state.get("feature_flags", {}),
    }


def understanding_input_payload(state: dict[str, Any]) -> dict[str, Any]:
    return {
        **process_header("understanding", "input"),
        "raw_instruction": state.get("raw_instruction"),
        "original_instruction": state.get("original_instruction"),
        "messages": _message_contents(state),
        "task_context": copy.deepcopy(state.get("task_context", {})),
        "feature_flags": copy.deepcopy(state.get("feature_flags", {})),
    }


def understanding_output_summary(understood: dict[str, Any]) -> dict[str, Any]:
    structured_task = understood.get("structured_task", {})
    if not isinstance(structured_task, dict):
        structured_task = {}
    final_state = structured_task.get("final_state", {})
    return {
        **process_header("understanding", "output"),
        "is_complete": understood.get("is_complete"),
        "is_cancel_all": understood.get("is_cancel_all"),
        "clarification_question": understood.get("clarification_question", ""),
        "clarification_suppressed": bool(understood.get("clarification_suppressed", False)),
        "relevant_item_names": sample_list(understood.get("relevant_item_names", []), limit=100),
        "structured_task": compact_value(structured_task),
        "understanding_final_state": compact_value(final_state),
        "entity_repair": compact_value(understood.get("entity_repair", {})),
        "goal_state_extract": compact_value(understood.get("goal_state_extract", {})),
    }


def understanding_output_payload(understood: dict[str, Any]) -> dict[str, Any]:
    structured_task = understood.get("structured_task", {})
    if not isinstance(structured_task, dict):
        structured_task = {}
    final_state = structured_task.get("final_state", {})
    return {
        **process_header("understanding", "output"),
        "is_complete": understood.get("is_complete"),
        "is_cancel_all": understood.get("is_cancel_all"),
        "clarification_question": understood.get("clarification_question", ""),
        "clarification_suppressed": bool(understood.get("clarification_suppressed", False)),
        "relevant_item_names": list(understood.get("relevant_item_names", []) or []),
        "structured_task": copy.deepcopy(structured_task),
        "understanding_final_state": copy.deepcopy(final_state),
        "entity_repair": copy.deepcopy(understood.get("entity_repair", {})),
        "goal_state_extract": copy.deepcopy(understood.get("goal_state_extract", {})),
    }


def planning_input_summary(planning_state: dict[str, Any]) -> dict[str, Any]:
    environment = planning_state.get("environment")
    task_context = planning_state.get("task_context", {})
    skill_profile = planning_state.get("skill_profile")
    resume_state = {
        "validated_todo_actions": sequence_summary(planning_state.get("validated_todo_actions", [])),
        "validated_steps": sequence_summary(planning_state.get("validated_steps", [])),
        "todo_list_before_planning": sequence_summary(planning_state.get("todo_list", [])),
        "checkpoint_env": environment_summary(planning_state.get("checkpoint_env")),
        "todo_checkpoint_env": environment_summary(planning_state.get("todo_checkpoint_env")),
    }
    return {
        **process_header("planning", "input"),
        "config": {
            "skill_profile": skill_profile,
            "repair_strategy": active_repair_strategy(),
            "todo_output_parser_path": planning_state.get("todo_output_parser_path", ""),
            "todo_step_adapter_path": planning_state.get("todo_step_adapter_path", ""),
            "todo_list_validator_path": planning_state.get("todo_list_validator_path", ""),
            "feature_flags": copy.deepcopy(planning_state.get("feature_flags", {})),
            "planning_contract": planning_contract_summary(
                str(skill_profile) if skill_profile is not None else None
            ),
        },
        "input": {
            "understanding_stage_executed": bool(planning_state.get("understanding_stage_executed", True)),
            "structured_task": compact_value(planning_state.get("structured_task", {})),
            "env_state": compact_value(planning_state.get("env_state", {})),
            "task_context": compact_value(task_context, max_chars=2000),
            "feedback": planning_state.get("feedback", ""),
            "environment": environment_summary(environment),
            "environment_facts": environment_facts(environment),
            "environment_source": copy.deepcopy(planning_state.get("environment_source", {})),
        },
        "resume_state": resume_state,
    }


def planning_input_payload(planning_state: dict[str, Any]) -> dict[str, Any]:
    environment = planning_state.get("environment")
    skill_profile = planning_state.get("skill_profile")
    payload = {
        **process_header("planning", "input"),
        "skill_profile": skill_profile,
        "repair_strategy": active_repair_strategy(),
        "todo_output_parser_path": planning_state.get("todo_output_parser_path", ""),
        "todo_step_adapter_path": planning_state.get("todo_step_adapter_path", ""),
        "todo_list_validator_path": planning_state.get("todo_list_validator_path", ""),
        "planning_contract": planning_contract_summary(
            str(skill_profile) if skill_profile is not None else None
        ),
        "feature_flags": copy.deepcopy(planning_state.get("feature_flags", {})),
        "understanding_stage_executed": bool(planning_state.get("understanding_stage_executed", True)),
        "structured_task": copy.deepcopy(planning_state.get("structured_task", {})),
        "env_state": copy.deepcopy(planning_state.get("env_state", {})),
        "task_context": copy.deepcopy(planning_state.get("task_context", {})),
        "feedback": planning_state.get("feedback", ""),
        "environment": copy.deepcopy(environment) if isinstance(environment, dict) else {},
        "environment_facts": environment_facts(environment, limit=max(len(environment), 1)) if isinstance(environment, dict) else {"available": False},
        "environment_source": copy.deepcopy(planning_state.get("environment_source", {})),
        "checkpoint_env": copy.deepcopy(planning_state.get("checkpoint_env", {})),
        "checkpoint_robot": copy.deepcopy(planning_state.get("checkpoint_robot", {})),
        "re_trac_memory": copy.deepcopy(planning_state.get("re_trac_memory", {})),
        "re_trac_state": copy.deepcopy(planning_state.get("re_trac_state", {})),
        "sda_state": copy.deepcopy(planning_state.get("sda_state", {})),
        "todo_list_before_planning": copy.deepcopy(planning_state.get("todo_list", [])),
        "validated_steps": copy.deepcopy(planning_state.get("validated_steps", [])),
        "validated_todo_actions": copy.deepcopy(planning_state.get("validated_todo_actions", [])),
        "todo_checkpoint_env": copy.deepcopy(planning_state.get("todo_checkpoint_env", {})),
        "todo_checkpoint_robot": copy.deepcopy(planning_state.get("todo_checkpoint_robot", {})),
    }
    return payload


def planning_output_summary(planned: dict[str, Any]) -> dict[str, Any]:
    environment = planned.get("environment")
    planning_debug_events = planned.get("planning_debug_events", [])
    if not isinstance(planning_debug_events, list):
        planning_debug_events = []
    planning_feature_records = planned.get("planning_feature_records", [])
    if not isinstance(planning_feature_records, list):
        planning_feature_records = []
    repair_strategy = str(planned.get("repair_strategy") or "").strip()
    if not repair_strategy:
        repair_strategy = active_repair_strategy()
    output = {
        "todo_list": sequence_summary(planned.get("todo_list", [])),
        "validated_steps": sequence_summary(planned.get("validated_steps", [])),
        "validated_todo_actions": sequence_summary(planned.get("validated_todo_actions", [])),
        "todo_llm_output": compact_value(planned.get("todo_llm_output", ""), max_chars=2000),
        "todo_parse_error": planned.get("todo_parse_error", ""),
        "evaluator_findings": sequence_summary(planned.get("evaluator_findings", [])),
    }
    return {
        **process_header("planning", "output"),
        "status": {
            "is_feasible": planned.get("is_feasible"),
            "execution_status": planned.get("execution_status", ""),
            "planner_status": planned.get("planner_status", ""),
            "iteration_count": planned.get("iteration_count"),
            "failure_layer": planned.get("failure_layer", ""),
            "failure_category": planned.get("failure_category", ""),
            "failed_action": planned.get("failed_action", ""),
            "feedback": planned.get("feedback", ""),
            "error_feedback": planned.get("error_feedback", ""),
        },
        "output": output,
        "state": {
            "env_state": compact_value(planned.get("env_state", {})),
            "environment": environment_summary(environment),
            "environment_facts": environment_facts(environment),
            "environment_source": copy.deepcopy(planned.get("environment_source", {})),
            "checkpoint_env": environment_summary(planned.get("checkpoint_env")),
            "checkpoint_robot": compact_value(planned.get("checkpoint_robot", {})),
            "todo_checkpoint_env": environment_summary(planned.get("todo_checkpoint_env")),
            "todo_checkpoint_robot": compact_value(planned.get("todo_checkpoint_robot", {})),
            "re_trac_state": compact_value(planned.get("re_trac_state", {}), max_chars=2000),
            "sda_state": compact_value(planned.get("sda_state", {}), max_chars=2000),
        },
        "audit": {
            "repair_strategy": repair_strategy,
            "state_diff_audit": compact_value(planned.get("state_diff_audit", {}), max_chars=2000),
            "planning_feature_records": compact_value(planning_feature_records, max_chars=2000),
            "planning_debug_events": sequence_summary(planning_debug_events),
        },
    }


def planning_output_payload(planned: dict[str, Any]) -> dict[str, Any]:
    planning_debug_events = planned.get("planning_debug_events", [])
    if not isinstance(planning_debug_events, list):
        planning_debug_events = []
    planning_feature_records = planned.get("planning_feature_records", [])
    if not isinstance(planning_feature_records, list):
        planning_feature_records = []
    repair_strategy = str(planned.get("repair_strategy") or "").strip()
    if not repair_strategy:
        repair_strategy = active_repair_strategy()
    environment = planned.get("environment")
    payload = {
        **process_header("planning", "output"),
        "is_feasible": planned.get("is_feasible"),
        "execution_status": planned.get("execution_status", ""),
        "planner_status": planned.get("planner_status", ""),
        "iteration_count": planned.get("iteration_count"),
        "feedback": planned.get("feedback", ""),
        "error_feedback": planned.get("error_feedback", ""),
        "failure_layer": planned.get("failure_layer", ""),
        "failure_category": planned.get("failure_category", ""),
        "failed_action": planned.get("failed_action", ""),
        "todo_list": copy.deepcopy(planned.get("todo_list", [])),
        "validated_steps": copy.deepcopy(planned.get("validated_steps", [])),
        "validated_todo_actions": copy.deepcopy(planned.get("validated_todo_actions", [])),
        "env_state": copy.deepcopy(planned.get("env_state", {})),
        "checkpoint_env": copy.deepcopy(planned.get("checkpoint_env", {})),
        "checkpoint_robot": copy.deepcopy(planned.get("checkpoint_robot", {})),
        "todo_checkpoint_env": copy.deepcopy(planned.get("todo_checkpoint_env", {})),
        "todo_checkpoint_robot": copy.deepcopy(planned.get("todo_checkpoint_robot", {})),
        "re_trac_memory": copy.deepcopy(planned.get("re_trac_memory", {})),
        "re_trac_state": copy.deepcopy(planned.get("re_trac_state", {})),
        "sda_state": copy.deepcopy(planned.get("sda_state", {})),
        "repair_strategy": repair_strategy,
        "todo_llm_output": planned.get("todo_llm_output", ""),
        "todo_parse_error": planned.get("todo_parse_error", ""),
        "environment": copy.deepcopy(environment) if isinstance(environment, dict) else {},
        "environment_facts": environment_facts(environment, limit=max(len(environment), 1)) if isinstance(environment, dict) else {"available": False},
        "environment_source": copy.deepcopy(planned.get("environment_source", {})),
        "evaluator_findings": copy.deepcopy(planned.get("evaluator_findings", [])),
        "state_diff_audit": copy.deepcopy(planned.get("state_diff_audit", {})),
        "planning_feature_records": copy.deepcopy(planning_feature_records),
        "planning_debug_events": copy.deepcopy(planning_debug_events),
    }
    return payload
