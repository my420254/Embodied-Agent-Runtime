from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from benchmark.reporting.store import write_json


TRACE_SCHEMA_VERSION = "framework_trace_v3"


def _dict_value(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    return str(value)


def _first_non_empty(*values: Any) -> str:
    for value in values:
        text = _string_value(value).strip()
        if text:
            return text
    return ""


def _messages_to_text(messages: Any) -> str:
    if isinstance(messages, str):
        return messages
    if not isinstance(messages, list):
        return ""
    chunks: list[str] = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        role = _string_value(message.get("role") or message.get("type")).strip()
        content = _string_value(message.get("content")).strip()
        if content:
            chunks.append(f"{role}: {content}" if role else content)
    return "\n\n".join(chunks)


def _llm_entry_prompt(entry: dict[str, Any]) -> str:
    return _first_non_empty(
        _messages_to_text(entry.get("messages")),
        _messages_to_text(entry.get("input")),
        entry.get("prompt"),
    )


def _extract_input_prompt(trace: dict[str, Any], planning_input: dict[str, Any]) -> str:
    llm_io = trace.get("llm_io", [])
    if isinstance(llm_io, list):
        for entry in llm_io:
            if not isinstance(entry, dict) or str(entry.get("module") or "").lower() != "planning":
                continue
            text = _llm_entry_prompt(entry)
            if text:
                return text
    return ""


def _prompt_reference(trace: dict[str, Any], planning_input: dict[str, Any]) -> dict[str, Any]:
    prompt = _extract_input_prompt(trace, planning_input)
    return {
        "stored_in": ["llm_io.json", "rounds/round_*_planning_input.md"],
        "available": bool(prompt),
        "length": len(prompt),
        "preview": prompt[:800],
    }


def _final_state_packet(planning_output: dict[str, Any]) -> dict[str, Any]:
    audit = planning_output.get("state_diff_audit", {}) if isinstance(planning_output, dict) else {}
    if not isinstance(audit, dict):
        return {}
    result = audit.get("result", {})
    if isinstance(result, dict) and isinstance(result.get("final_state_packet"), dict):
        return result["final_state_packet"]
    return {}


def _benchmark_final_state_compare(planning_output: dict[str, Any]) -> dict[str, Any]:
    audit = planning_output.get("state_diff_audit", {}) if isinstance(planning_output, dict) else {}
    result = audit.get("result", {}) if isinstance(audit, dict) else {}
    if isinstance(result, dict) and isinstance(result.get("benchmark_final_state_compare"), dict):
        return result["benchmark_final_state_compare"]
    packet = _final_state_packet(planning_output)
    compare = packet.get("benchmark_final_state_compare", {}) if isinstance(packet, dict) else {}
    return compare if isinstance(compare, dict) else {}


def _trace_stage_payload(trace: dict[str, Any], name: str) -> tuple[dict[str, Any], dict[str, Any]]:
    summary = _dict_value(trace.get(name, {}))
    full = _dict_value(trace.get(f"{name}_full", summary))
    return full, summary


def _process_name(record: dict[str, Any]) -> str:
    return _string_value(record.get("process_name")).strip()


def _feature_records(planning_output: dict[str, Any]) -> list[dict[str, Any]]:
    records = planning_output.get("planning_feature_records", [])
    return [item for item in records if isinstance(item, dict)] if isinstance(records, list) else []


def _feature_record(records: list[dict[str, Any]], process_name: str) -> dict[str, Any]:
    for record in reversed(records):
        if _process_name(record) == process_name:
            return copy.deepcopy(record)
    return {}


def _feature_status(records: list[dict[str, Any]], process_name: str) -> str:
    for record in reversed(records):
        if _process_name(record) == process_name:
            return _string_value(record.get("status")) or "recorded"
    return "not_recorded"


def _llm_call_records(trace: dict[str, Any]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for index, entry in enumerate(_list_value(trace.get("llm_io", [])), start=1):
        if not isinstance(entry, dict):
            continue
        prompt = _llm_entry_prompt(entry)
        output = _string_value(entry.get("output"))
        calls.append(
            {
                "turn_index": index,
                "module": _string_value(entry.get("module")),
                "process_name": _string_value(entry.get("process_name") or entry.get("module")),
                "prompt_name": _string_value(entry.get("prompt_name")),
                "call_stage": _string_value(entry.get("call_stage")),
                "attempt": entry.get("attempt"),
                "planning_iteration": entry.get("planning_iteration"),
                "input_chars": len(prompt),
                "output_chars": len(output),
            }
        )
    return calls


def _planning_debug_events(planning_output: dict[str, Any]) -> list[dict[str, Any]]:
    events = planning_output.get("planning_debug_events", [])
    if not isinstance(events, list):
        return []
    return [copy.deepcopy(event) for event in events if isinstance(event, dict)]


def _todo_contract_events(planning_output: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        event
        for event in _planning_debug_events(planning_output)
        if _string_value(event.get("layer")).strip().lower() == "todo_contract"
    ]


def _step_action_label(step: Any) -> str:
    if not isinstance(step, dict):
        return ""
    action = _string_value(step.get("action")).strip()
    if action:
        return action
    skill = _string_value(step.get("skill")).strip()
    if skill:
        return skill
    execution = step.get("execution", {})
    if isinstance(execution, dict):
        return _string_value(execution.get("skill")).strip()
    return ""


def _todo_list_shape(todo_list: Any) -> dict[str, Any]:
    steps = todo_list if isinstance(todo_list, list) else []
    key_counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}
    wrapper_count = 0
    samples: list[dict[str, Any]] = []
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            samples.append(
                {
                    "index": index,
                    "python_type": type(step).__name__,
                    "action": "",
                    "keys": [],
                    "has_execution_wrapper": False,
                }
            )
            continue
        for key in step:
            key_counts[str(key)] = key_counts.get(str(key), 0) + 1
        action = _step_action_label(step)
        if action:
            action_counts[action] = action_counts.get(action, 0) + 1
        has_execution = isinstance(step.get("execution"), dict)
        if has_execution:
            wrapper_count += 1
        if len(samples) < 20:
            samples.append(
                {
                    "index": step.get("step", index),
                    "action": action,
                    "keys": sorted(str(key) for key in step.keys()),
                    "has_execution_wrapper": has_execution,
                    "raw_step": copy.deepcopy(step),
                }
            )
    return {
        "count": len(steps),
        "top_level_key_counts": key_counts,
        "action_counts": action_counts,
        "execution_wrapper_count": wrapper_count,
        "sample": samples,
        "truncated": len(steps) > len(samples),
    }


def _contract_status(
    *,
    events: list[dict[str, Any]],
    todo_list: Any,
    planning_contract: dict[str, Any],
) -> str:
    event_types = {_string_value(event.get("type")).strip().lower() for event in events}
    if "rejected" in event_types:
        return "rejected"
    if "passed" in event_types:
        return "passed"
    raw_count = planning_contract.get("raw_contract_count")
    if isinstance(raw_count, int) and raw_count <= 0:
        return "disabled_no_raw_contract"
    if isinstance(todo_list, list) and not todo_list:
        return "no_todo_list"
    return "not_recorded"


def _contract_action_coverage(todo_list: Any, planning_contract: dict[str, Any]) -> dict[str, Any]:
    configured = {
        _string_value(action).strip()
        for action in _list_value(planning_contract.get("raw_action_names", []))
        if _string_value(action).strip()
    }
    observed: list[str] = []
    for step in todo_list if isinstance(todo_list, list) else []:
        label = _step_action_label(step)
        if label:
            observed.append(label)
    unknown = sorted({action for action in observed if configured and action not in configured})
    return {
        "configured_raw_action_count": len(configured),
        "configured_raw_actions": sorted(configured),
        "observed_action_count": len(observed),
        "observed_actions": observed,
        "unknown_observed_actions": unknown,
    }


def _contract_audit(
    *,
    planning_input_summary: dict[str, Any],
    planning_output_summary: dict[str, Any],
    planning_output: dict[str, Any],
) -> dict[str, Any]:
    planning_config = _dict_value(planning_input_summary.get("config"))
    planning_contract = _dict_value(planning_config.get("planning_contract"))
    todo_list = planning_output.get("todo_list", [])
    events = _todo_contract_events(planning_output)
    status = _contract_status(events=events, todo_list=todo_list, planning_contract=planning_contract)
    return {
        "schema_version": TRACE_SCHEMA_VERSION,
        "process_name": "todo_contract",
        "payload_role": "audit",
        "status": status,
        "skill_profile": planning_config.get("skill_profile"),
        "todo_output_parser_path": planning_config.get("todo_output_parser_path", ""),
        "todo_step_adapter_path": planning_config.get("todo_step_adapter_path", ""),
        "todo_list_validator_path": planning_config.get("todo_list_validator_path", ""),
        "planning_contract": planning_contract,
        "todo_list_shape": _todo_list_shape(todo_list),
        "action_coverage": _contract_action_coverage(todo_list, planning_contract),
        "contract_events": events,
        "planning_status": _dict_value(planning_output_summary.get("status")),
        "validated_outputs": {
            "todo_list_count": len(todo_list) if isinstance(todo_list, list) else 0,
            "validated_todo_actions_count": len(_list_value(planning_output.get("validated_todo_actions", []))),
            "validated_steps_count": len(_list_value(planning_output.get("validated_steps", []))),
        },
    }


def _feature_flags(planning_input_summary: dict[str, Any]) -> dict[str, Any]:
    config = _dict_value(planning_input_summary.get("config"))
    return _dict_value(config.get("feature_flags"))


def _final_state_audit_status(records: list[dict[str, Any]], planning_input_summary: dict[str, Any]) -> str:
    status = _feature_status(records, "final_state_audit")
    if status != "not_recorded":
        return status
    if _feature_flags(planning_input_summary).get("state_diff_audit") is False:
        return "disabled"
    return status


def _rate_value(value: Any) -> float | None:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if not isinstance(value, (int, float)):
        return None
    rate = float(value)
    if rate > 1.0:
        rate /= 100.0
    return rate


def _official_available(prediction: dict[str, Any], evaluation_summary: Any = None) -> bool | None:
    if "official_available" in prediction:
        return bool(prediction.get("official_available"))
    if "val_available" in prediction:
        return bool(prediction.get("val_available"))
    if isinstance(evaluation_summary, dict) and evaluation_summary:
        return True
    return None


def _task_success_rate(prediction: dict[str, Any], evaluation_summary: Any = None) -> float | None:
    direct = _rate_value(prediction.get("task_success_rate"))
    if direct is not None:
        return direct
    if "val_success" in prediction:
        return 1.0 if bool(prediction.get("val_success")) else 0.0
    for key in ("goal_success_rate",):
        rate = _rate_value(prediction.get(key))
        if rate is not None:
            return rate
    if isinstance(evaluation_summary, dict):
        goal_eval = evaluation_summary.get("goal_evaluation")
        if isinstance(goal_eval, dict):
            rate = _rate_value(goal_eval.get("task_success_rate"))
            if rate is not None:
                return rate
    return None


def _task_success(prediction: dict[str, Any], evaluation_summary: Any = None) -> bool | None:
    if "task_success" in prediction:
        value = prediction.get("task_success")
        return None if value is None else bool(value)
    rate = _task_success_rate(prediction, evaluation_summary)
    return None if rate is None else rate >= 1.0


def _execution_success(prediction: dict[str, Any], evaluation_summary: Any = None) -> bool | None:
    if "execution_success" in prediction:
        value = prediction.get("execution_success")
        return None if value is None else bool(value)
    if isinstance(evaluation_summary, dict):
        trajectory_eval = evaluation_summary.get("trajectory_evaluation")
        if isinstance(trajectory_eval, dict):
            rate = _rate_value(trajectory_eval.get("execution_success_rate"))
            if rate is not None:
                return rate >= 1.0
    return None


def _evaluation_mode(prediction: dict[str, Any], evaluation_summary: Any = None) -> str:
    mode = _string_value(prediction.get("evaluation_mode")).strip()
    if mode:
        return mode
    if isinstance(evaluation_summary, dict):
        metadata = evaluation_summary.get("metadata")
        if isinstance(metadata, dict):
            evaluator = _string_value(metadata.get("evaluator")).strip()
            if evaluator:
                return evaluator
    provenance = prediction.get("input_provenance")
    dataset = ""
    if isinstance(provenance, dict):
        dataset = _string_value(provenance.get("dataset")).strip()
    dataset = dataset or _string_value(prediction.get("dataset")).strip()
    if dataset in {"behavior", "virtualhome"}:
        return f"eai_{dataset}_action_sequencing"
    return ""


def _process_summary(
    *,
    trace: dict[str, Any],
    case_input_summary: dict[str, Any],
    prepared_environment_summary: dict[str, Any],
    understanding_input_summary: dict[str, Any],
    understanding_output_summary: dict[str, Any],
    planning_input_summary: dict[str, Any],
    planning_output_summary: dict[str, Any],
    planning_output: dict[str, Any],
    official_eval: dict[str, Any],
    contract_audit: dict[str, Any],
) -> dict[str, Any]:
    feature_records = _feature_records(planning_output)
    llm_calls = _llm_call_records(trace)
    sandbox_record = _feature_record(feature_records, "sandbox_validation")
    dependency_record = _feature_record(feature_records, "dependency_repair")
    final_state_record = _feature_record(feature_records, "final_state_audit")
    benchmark_compare = _benchmark_final_state_compare(planning_output)
    official_available = official_eval.get("official_available")
    if official_available is None:
        official_available = bool(official_eval.get("evaluation_summary") or official_eval.get("pddl_validation"))
    return {
        "schema_version": TRACE_SCHEMA_VERSION,
        "processes": [
            {
                "process_name": "case_input",
                "status": "recorded" if case_input_summary else "missing",
                "artifact_files": ["case_input.json", "case_input_summary.json"],
                "summary": case_input_summary,
            },
            {
                "process_name": "environment_preparation",
                "status": "recorded" if prepared_environment_summary else "missing",
                "artifact_files": ["prepared_environment.json", "prepared_environment_summary.json", "environment_audit.json"],
                "summary": prepared_environment_summary,
            },
            {
                "process_name": "understanding",
                "status": "recorded" if understanding_output_summary else "missing",
                "artifact_files": [
                    "understanding_input.json",
                    "understanding_input_summary.json",
                    "understanding_output.json",
                    "understanding_output_summary.json",
                ],
                "input_summary": understanding_input_summary,
                "output_summary": understanding_output_summary,
            },
            {
                "process_name": "planning",
                "status": _string_value(_dict_value(planning_output_summary.get("status", {})).get("execution_status"))
                or "recorded",
                "artifact_files": ["planning_input.json", "planning_input_summary.json", "planning_output.json", "planning_output_summary.json"],
                "input_summary": planning_input_summary,
                "output_summary": planning_output_summary,
            },
            {
                "process_name": "todo_contract",
                "status": _string_value(contract_audit.get("status")) or "not_recorded",
                "artifact_files": ["contract_audit.json", "planning_input.json", "planning_output.json"],
                "summary": contract_audit,
            },
            {
                "process_name": "sandbox_validation",
                "status": _feature_status(feature_records, "sandbox_validation"),
                "artifact_files": ["planning_feature_records.json"],
                "summary": sandbox_record,
            },
            {
                "process_name": "dependency_repair",
                "status": _feature_status(feature_records, "dependency_repair"),
                "artifact_files": ["planning_feature_records.json"],
                "summary": dependency_record,
            },
            {
                "process_name": "final_state_audit",
                "status": _final_state_audit_status(feature_records, planning_input_summary),
                "artifact_files": ["planning_feature_records.json", "goal_check.json"],
                "summary": {
                    "feature_record": final_state_record,
                    "benchmark_final_state_compare": benchmark_compare,
                },
            },
            {
                "process_name": "model_calls",
                "status": "recorded" if llm_calls else "missing",
                "artifact_files": ["llm_io.json", "rounds/round_*_input.md", "rounds/round_*_output.txt"],
                "summary": {
                    "llm_call_count": len(llm_calls),
                    "calls": llm_calls,
                },
            },
            {
                "process_name": "official_evaluation",
                "status": "available" if bool(official_available) else "missing",
                "artifact_files": ["official_eval.json", "goal_check.json"],
                "summary": official_eval,
            },
        ],
    }


def _prediction_official_summary(prediction: dict[str, Any], evaluation_summary: Any = None) -> dict[str, Any]:
    return {
        "evaluation_mode": _evaluation_mode(prediction, evaluation_summary),
        "evaluation_route": prediction.get("evaluation_route", ""),
        "official_available": _official_available(prediction, evaluation_summary),
        "task_success": _task_success(prediction, evaluation_summary),
        "task_success_rate": _task_success_rate(prediction, evaluation_summary),
        "execution_success": _execution_success(prediction, evaluation_summary),
        "official_failure_reason": prediction.get("official_failure_reason", prediction.get("evaluation_error", "")),
        "goal_success_rate": prediction.get("goal_success_rate"),
        "subgoal_success_rate": prediction.get("subgoal_success_rate"),
        "satisfied_goals": prediction.get("satisfied_goals", []),
        "unsatisfied_goals": prediction.get("unsatisfied_goals", []),
        "pddl_validation": prediction.get("pddl_validation", {}),
        "terminate_info": prediction.get("terminate_info", {}),
    }


def _official_eval_payload(
    prediction: dict[str, Any],
    *,
    evaluation_summary: Any = None,
    evaluation_detail: Any = None,
) -> dict[str, Any]:
    payload = _prediction_official_summary(prediction, evaluation_summary)
    payload.update(
        {
            "official_actions": prediction.get("official_actions", []),
            "evaluator_execution_calls": prediction.get("evaluator_execution_calls", []),
            "action_trace": prediction.get("action_trace", []),
        }
    )
    if evaluation_summary is not None:
        payload["evaluation_summary"] = evaluation_summary
    if evaluation_detail is not None:
        payload["evaluation_detail"] = evaluation_detail
    return payload


def _summary_path(summary: dict[str, Any], *path: str) -> Any:
    current: Any = summary
    for key in path:
        if not isinstance(current, dict):
            return {}
        current = current.get(key, {})
    return current


def _environment_audit(
    *,
    prepared_environment_summary: dict[str, Any],
    planning_input_summary: dict[str, Any],
    planning_output_summary: dict[str, Any],
) -> dict[str, Any]:
    prepared_scene = _dict_value(prepared_environment_summary.get("scene"))
    planning_input_environment = _dict_value(_summary_path(planning_input_summary, "input", "environment"))
    planning_output_environment = _dict_value(_summary_path(planning_output_summary, "state", "environment"))
    return {
        "schema_version": TRACE_SCHEMA_VERSION,
        "process_name": "environment_audit",
        "payload_role": "summary",
        "prepared_scene": {
            "entity_count": prepared_scene.get("entity_count"),
            "type_counts": prepared_scene.get("type_counts", {}),
            "nesting": prepared_scene.get("nesting", {}),
            "flat_schema": prepared_scene.get("flat_schema", {}),
        },
        "planning_input_environment": {
            "source": _summary_path(planning_input_summary, "input", "environment_source"),
            "summary": planning_input_environment,
            "schema": _dict_value(planning_input_environment.get("schema")),
        },
        "planning_output_environment": {
            "summary": planning_output_environment,
            "schema": _dict_value(planning_output_environment.get("schema")),
        },
    }


def standard_trace_artifacts(
    *,
    trace: dict[str, Any],
    prediction: dict[str, Any],
    evaluation_summary: Any = None,
    evaluation_detail: Any = None,
) -> dict[str, Any]:
    """Build the shared artifact schema for framework benchmark reports."""
    trace = _dict_value(trace)
    prediction = _dict_value(prediction)
    case_input, case_input_summary = _trace_stage_payload(trace, "case_input")
    prepared_environment, prepared_environment_summary = _trace_stage_payload(trace, "prepared_environment")
    understanding_input, understanding_input_summary = _trace_stage_payload(trace, "understanding_input")
    understanding_output, understanding_output_summary = _trace_stage_payload(trace, "understanding_output")
    planning_input, planning_input_summary = _trace_stage_payload(trace, "planning_input")
    planning_output, planning_output_summary = _trace_stage_payload(trace, "planning_output")
    official_summary = _prediction_official_summary(prediction, evaluation_summary)
    if evaluation_summary is not None:
        official_summary["evaluation_summary"] = evaluation_summary
    official_eval = _official_eval_payload(
        prediction,
        evaluation_summary=evaluation_summary,
        evaluation_detail=evaluation_detail,
    )
    environment_audit = _environment_audit(
        prepared_environment_summary=prepared_environment_summary,
        planning_input_summary=planning_input_summary,
        planning_output_summary=planning_output_summary,
    )
    contract_audit = _contract_audit(
        planning_input_summary=planning_input_summary,
        planning_output_summary=planning_output_summary,
        planning_output=planning_output,
    )

    goal_check = {
        "symbolic_official_alignment": prediction.get("symbolic_official_alignment", {}),
        "final_state_packet": _final_state_packet(planning_output),
        "benchmark_final_state_compare": _benchmark_final_state_compare(planning_output),
        "state_diff_audit": planning_output.get("state_diff_audit", {}),
        "task_context": planning_input.get("task_context", {}),
        "planning_prompt_ref": _prompt_reference(trace, planning_input),
        "official_evaluator_summary": official_summary or {},
    }
    if evaluation_detail is not None:
        goal_check["official_evaluator_detail"] = evaluation_detail

    return {
        "case_input.json": case_input,
        "case_input_summary.json": case_input_summary,
        "prepared_environment.json": prepared_environment,
        "prepared_environment_summary.json": prepared_environment_summary,
        "environment_audit.json": environment_audit,
        "understanding_input.json": understanding_input,
        "understanding_input_summary.json": understanding_input_summary,
        "understanding_output.json": understanding_output,
        "understanding_output_summary.json": understanding_output_summary,
        "planning_input.json": planning_input,
        "planning_input_summary.json": planning_input_summary,
        "planning_output.json": planning_output,
        "planning_output_summary.json": planning_output_summary,
        "contract_audit.json": contract_audit,
        "planning_feature_records.json": _feature_records(planning_output),
        "llm_io.json": _list_value(trace.get("llm_io", [])),
        "goal_check.json": goal_check,
        "official_eval.json": official_eval,
        "process_summary.json": _process_summary(
            trace=trace,
            case_input_summary=case_input_summary,
            prepared_environment_summary=prepared_environment_summary,
            understanding_input_summary=understanding_input_summary,
            understanding_output_summary=understanding_output_summary,
            planning_input_summary=planning_input_summary,
            planning_output_summary=planning_output_summary,
            planning_output=planning_output,
            official_eval=official_eval,
            contract_audit=contract_audit,
        ),
    }


def write_standard_trace_artifacts(
    artifacts_root: Path,
    *,
    trace: dict[str, Any],
    prediction: dict[str, Any],
    evaluation_summary: Any = None,
    evaluation_detail: Any = None,
) -> None:
    for filename, payload in standard_trace_artifacts(
        trace=trace,
        prediction=prediction,
        evaluation_summary=evaluation_summary,
        evaluation_detail=evaluation_detail,
    ).items():
        write_json(artifacts_root / filename, payload)
