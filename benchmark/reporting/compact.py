from __future__ import annotations

from typing import Any

from benchmark.reporting.trace_payloads import benchmark_trace_counters, compact_value


_PREDICTION_SCALAR_KEYS = (
    "identifier",
    "evaluation_route",
    "val_success",
    "val_available",
    "symbolic_success",
    "execution_status",
    "is_feasible",
    "feedback",
    "error_feedback",
    "failure_layer",
    "failed_action",
    "sandbox_failure_reason",
    "sandbox_repair_hint",
    "goal_success_rate",
    "subgoal_success_rate",
    "evaluation_mode",
    "official_available",
    "official_failure_reason",
    "evaluation_error",
    "todo_parse_error",
    "repair_strategy",
    "execution_success",
    "task_success",
    "task_success_rate",
    "llm_call_count",
    "sandbox_reject_count",
    "total_sandbox_checks",
    "total_planning_audit_failures",
    "official_actions_len",
    "evaluator_execution_calls_len",
    "reference_text_available",
    "reference_text_error",
    "reference_step_count",
    "generated_step_count",
    "step_count_abs_diff",
    "step_count_sq_diff",
    "step_rouge1_f1_avg",
    "step_match_rate_f1_gt_0_2",
    "step_match_rate_f1_gt_0_5",
    "reference_step_coverage_f1_gt_0_5",
    "overall_rouge1_f1",
    "overall_rouge2_f1",
    "overall_rougeL_f1",
    "validated_steps_count",
    "state_diff_passed",
)

_PREDICTION_COMPACT_KEYS = (
    "planning_result",
    "input_provenance",
    "pddl_validation",
    "symbolic_official_alignment",
    "evaluation_summary",
    "reference_text_metrics",
)

_PREDICTION_LIST_KEYS = (
    "official_actions",
    "validated_todo_actions",
    "evaluator_execution_calls",
    "evaluator_findings",
    "satisfied_goals",
    "unsatisfied_goals",
)

_PREDICTION_TEXT_KEYS = (
    "llm_output",
    "todo_llm_output",
)


def _sample_list(value: Any, *, limit: int = 20, max_chars: int = 1000) -> dict[str, Any]:
    if not isinstance(value, list):
        return {"count": 0, "sample": [], "truncated": False}
    return {
        "count": len(value),
        "sample": compact_value(value[:limit], max_chars=max_chars),
        "truncated": len(value) > limit,
    }


def _text_preview(value: Any, *, max_chars: int = 1200) -> dict[str, Any]:
    text = str(value or "")
    return {
        "length": len(text),
        "preview": compact_value(text, max_chars=max_chars),
        "truncated": len(text) > max_chars,
    }


def _input_summary(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {"available": False}
    summary = {
        "available": True,
        "keys": sorted(str(key) for key in value.keys()),
    }
    for key in (
        "identifier",
        "task_id",
        "dataset",
        "instruction",
        "task_desc",
        "task_name",
        "domain",
        "scene_name",
        "scene_id",
        "eval_type",
        "initial_environment_cache_path",
        "initial_environment_source",
        "environment_source",
        "task_source",
    ):
        if key in value:
            summary[key] = compact_value(value.get(key), max_chars=800)
    if isinstance(value.get("raw_initial_condition"), list):
        summary["raw_initial_condition_count"] = len(value["raw_initial_condition"])
    if isinstance(value.get("raw_goal_condition"), list):
        summary["raw_goal_condition_count"] = len(value["raw_goal_condition"])
    if isinstance(value.get("pddl_objects"), list):
        summary["pddl_objects_count"] = len(value["pddl_objects"])
    if isinstance(value.get("pddl_init"), list):
        summary["pddl_init_count"] = len(value["pddl_init"])
    if isinstance(value.get("pddl_goal"), list):
        summary["pddl_goal_count"] = len(value["pddl_goal"])
    if isinstance(value.get("scene_graph"), dict):
        summary["scene_graph_top_level_count"] = len(value["scene_graph"])
    if isinstance(value.get("init_graph"), dict):
        init_graph = value["init_graph"]
        summary["init_graph_node_count"] = len(init_graph.get("nodes", [])) if isinstance(init_graph.get("nodes"), list) else None
        summary["init_graph_edge_count"] = len(init_graph.get("edges", [])) if isinstance(init_graph.get("edges"), list) else None
    if isinstance(value.get("task_goal"), dict):
        summary["task_goal_keys"] = sorted(str(key) for key in value["task_goal"].keys())
    return summary


def _reference_summary(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {"available": False}
    summary = {
        "available": True,
        "keys": sorted(str(key) for key in value.keys()),
    }
    for key in ("task_name", "goal_condition", "goal_option", "pddl_goal", "task_goal"):
        if isinstance(value.get(key), list):
            summary[f"{key}_count"] = len(value[key])
        elif isinstance(value.get(key), dict):
            summary[f"{key}_keys"] = sorted(str(item) for item in value[key].keys())
        elif key in value:
            summary[key] = compact_value(value[key], max_chars=1000)
    return summary


def compact_prediction(prediction: Any) -> dict[str, Any]:
    if not isinstance(prediction, dict):
        return {}
    compact: dict[str, Any] = {}
    for key in _PREDICTION_SCALAR_KEYS:
        if key in prediction:
            compact[key] = prediction.get(key)
    for key in _PREDICTION_COMPACT_KEYS:
        if key in prediction:
            compact[key] = compact_value(prediction.get(key), max_chars=1600)
    for key in _PREDICTION_LIST_KEYS:
        if key in prediction:
            compact[f"{key}_summary"] = _sample_list(prediction.get(key))
    for key in _PREDICTION_TEXT_KEYS:
        if key in prediction:
            compact[f"{key}_summary"] = _text_preview(prediction.get(key))
    trace = prediction.get("benchmark_trace")
    if isinstance(trace, dict) and trace:
        compact["benchmark_trace_present"] = True
        compact["benchmark_trace_counters"] = benchmark_trace_counters(trace)
        compact["benchmark_trace_sections"] = sorted(str(key) for key in trace.keys())
    return compact


def compact_result_row(row: Any) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {}
    return {
        "case_id": str(row.get("case_id", "") or ""),
        "dataset": str(row.get("dataset", "") or ""),
        "metadata": compact_value(row.get("metadata", {}) if isinstance(row.get("metadata"), dict) else {}, max_chars=1200),
        "source_path": str(row.get("source_path", "") or ""),
        "error": str(row.get("error", "") or ""),
        "timing": compact_value(row.get("timing", {}) if isinstance(row.get("timing"), dict) else {}, max_chars=800),
        "input_summary": _input_summary(row.get("input")),
        "reference_summary": _reference_summary(row.get("reference")),
        "prediction": compact_prediction(row.get("prediction")),
    }


def compact_worker_result(result: Any) -> dict[str, Any]:
    if not isinstance(result, dict):
        return {}
    compact: dict[str, Any] = {}
    for key in (
        "case_id",
        "status",
        "error",
        "raw_output",
        "case_json",
        "report",
        "log",
        "returncode",
        "worker_input",
        "unit_index",
        "endpoint_index",
        "port",
        "api_base",
        "started_at",
        "updated_at",
        "resumed",
        "timing",
    ):
        if key in result:
            compact[key] = compact_value(result.get(key), max_chars=1000)
    if "command" in result:
        compact["command"] = compact_value(result.get("command"), max_chars=1000)
    if "artifacts" in result:
        compact["artifacts"] = compact_value(result.get("artifacts"), max_chars=1000)
    if isinstance(result.get("row"), dict):
        compact["row"] = compact_result_row(result["row"])
    return compact
