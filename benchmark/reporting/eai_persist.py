from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Iterable

from benchmark.reporting import write_case_report
from benchmark.reporting.compact import compact_prediction
from benchmark.reporting.rounds import write_rounds_bundle
from benchmark.reporting.store import load_case_meta, read_json, write_case_meta, write_json
from benchmark.reporting.trace_artifacts import write_standard_trace_artifacts


API_ERROR_MARKERS = (
    "APIConnectionError",
    "Connection error",
    "ReadTimeout",
    "ConnectTimeout",
    "APITimeoutError",
    "RateLimitError",
    "InternalServerError",
    "ServiceUnavailableError",
    "502 Bad Gateway",
    "503 Service Unavailable",
    "504 Gateway Timeout",
    "RemoteProtocolError",
    "Server disconnected",
    "Connection reset by peer",
    "Unauthorized",
)
TRACEBACK_MARKERS = (
    "Traceback (most recent call last):",
    "ModuleNotFoundError",
    "ImportError",
)
HARD_FAULT_SENTINEL = "OURAGENT_HARD_FAULT_DETECTED"


def _iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
        return
    if isinstance(value, dict):
        for item in value.values():
            yield from _iter_strings(item)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            yield from _iter_strings(item)


def _text_has_any_marker(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)


def _payload_has_api_error(value: Any) -> bool:
    return any(_text_has_any_marker(text, API_ERROR_MARKERS) for text in _iter_strings(value))


def _payload_has_traceback(value: Any) -> bool:
    return any(_text_has_any_marker(text, TRACEBACK_MARKERS) for text in _iter_strings(value))


def _path_has_hard_fault(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return _text_has_any_marker(text, API_ERROR_MARKERS) or _text_has_any_marker(text, TRACEBACK_MARKERS)


def _benchmark_row_has_hard_fault(row: dict[str, Any]) -> bool:
    if not isinstance(row, dict):
        return False
    top_error = row.get("error")
    if isinstance(top_error, str) and top_error.strip():
        return True
    prediction = row.get("prediction")
    evaluation_error = ""
    if isinstance(prediction, dict):
        prediction_error = prediction.get("error")
        if isinstance(prediction_error, str) and prediction_error.strip():
            return True
        evaluation_error = prediction.get("evaluation_error", "")
    if isinstance(evaluation_error, str) and evaluation_error.strip():
        return True
    return _payload_has_api_error(row) or _payload_has_traceback(row)


def _load_json_if_exists(path: Path | None) -> Any:
    if path is None or not path.exists():
        return None
    try:
        return read_json(path)
    except Exception:
        return None


def _normalize_task_success(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        numeric = float(value)
        if numeric > 1.0:
            return numeric / 100.0
        if numeric < 0.0:
            return 0.0
        return numeric
    return None


def _official_fields_from_summary(summary: Any) -> dict[str, Any]:
    if not isinstance(summary, dict) or not summary:
        return {
            "official_available": False,
            "task_success": None,
            "task_success_rate": None,
            "execution_success": None,
        }
    goal_eval = summary.get("goal_evaluation", {})
    task_success_rate = None
    if isinstance(goal_eval, dict):
        task_success_rate = _normalize_task_success(goal_eval.get("task_success_rate"))
    trajectory_eval = summary.get("trajectory_evaluation", {})
    execution_success = None
    if isinstance(trajectory_eval, dict):
        execution_rate = _normalize_task_success(trajectory_eval.get("execution_success_rate"))
        execution_success = None if execution_rate is None else execution_rate >= 0.999999
    return {
        "official_available": True,
        "task_success": None if task_success_rate is None else task_success_rate >= 0.999999,
        "task_success_rate": task_success_rate,
        "execution_success": execution_success,
    }


def _write_eai_trace_artifacts(case_root: Path, prediction: dict[str, Any], *, evaluation_summary: Any, evaluation_detail: Any) -> None:
    trace = prediction.get("benchmark_trace", {}) if isinstance(prediction, dict) else {}
    if not isinstance(trace, dict):
        trace = {}
    write_standard_trace_artifacts(
        case_root / "artifacts",
        trace=trace,
        prediction=prediction,
        evaluation_summary=evaluation_summary,
        evaluation_detail=evaluation_detail,
    )


def _evaluation_paths(*, dataset: str, evaluate_root: Path, model_label: str) -> tuple[Path | None, Path | None]:
    if dataset == "behavior":
        summary_path = evaluate_root / "behavior" / "evaluate_results" / "action_sequencing" / "summary" / f"{model_label}_outputs.json"
        detail_path = evaluate_root / "behavior" / "evaluate_results" / "action_sequencing" / "log" / f"{model_label}_outputs.json"
        return summary_path if summary_path.exists() else None, detail_path if detail_path.exists() else None
    case_root = evaluate_root / "virtualhome" / "evaluate_results" / "action_sequencing" / model_label
    summary_path = case_root / "summary.json"
    detail_path = case_root / "error_info.json"
    return summary_path if summary_path.exists() else None, detail_path if detail_path.exists() else None


def persist_eai_case_result(
    *,
    dataset: str,
    mode: str,
    case_id: str,
    case_root: Path,
    case_meta_path: Path,
    raw_output_path: Path,
    log_path: Path,
    model_label: str,
    max_tokens: int,
    temperature: float,
    trace: bool,
    trace_llm_io: bool,
    valid_only: bool,
    task_name_fallback: bool,
    command: list[str],
    started_at: str,
    api_base: str,
    returncode: int,
) -> dict[str, Any]:
    generated_root = case_root / "artifacts" / "generated"
    evaluate_root = case_root / "artifacts" / "evaluated"
    raw_outputs = sorted(generated_root.rglob("*_outputs.json"))
    raw_eval_summaries = sorted(evaluate_root.rglob("summary.json")) + sorted(evaluate_root.rglob("*.json"))
    primary_output = raw_outputs[0] if raw_outputs else None
    copied_summaries: list[str] = []

    seen_summary_paths: set[str] = set()
    for source in raw_eval_summaries:
        source_str = str(source)
        if source_str not in seen_summary_paths:
            copied_summaries.append(source_str)
            seen_summary_paths.add(source_str)

    evaluation_summary_path, evaluation_detail_path = _evaluation_paths(
        dataset=dataset,
        evaluate_root=evaluate_root,
        model_label=model_label,
    )
    evaluation_summary_payload = _load_json_if_exists(evaluation_summary_path)
    evaluation_detail_payload = _load_json_if_exists(evaluation_detail_path)

    raw_data = read_json(primary_output) if primary_output and primary_output.exists() else []
    if isinstance(raw_data, list) and any(_benchmark_row_has_hard_fault(row) for row in raw_data if isinstance(row, dict)):
        raise RuntimeError(f"{HARD_FAULT_SENTINEL}: eai dataset={dataset} case_id={case_id}")
    if returncode != 0 or _path_has_hard_fault(log_path):
        raise RuntimeError(f"{HARD_FAULT_SENTINEL}: eai dataset={dataset} case_id={case_id} rc={returncode}")

    prediction = raw_data[0] if isinstance(raw_data, list) and raw_data else {}
    prediction = prediction if isinstance(prediction, dict) else {}
    official_fields = _official_fields_from_summary(evaluation_summary_payload)
    reported_prediction = {**prediction, **official_fields}
    if isinstance(raw_data, list):
        compact_rows = []
        for item in raw_data:
            if isinstance(item, dict) and item is prediction:
                compact_rows.append(compact_prediction(reported_prediction))
            elif isinstance(item, dict):
                compact_rows.append(compact_prediction({**item, **official_fields}))
            else:
                compact_rows.append({})
        write_json(raw_output_path, compact_rows)
    else:
        write_json(raw_output_path, [compact_prediction(reported_prediction)])
    _write_eai_trace_artifacts(
        case_root,
        reported_prediction,
        evaluation_summary=evaluation_summary_payload,
        evaluation_detail=evaluation_detail_payload,
    )
    prediction_error = str(prediction.get("error", "") or "") if isinstance(prediction, dict) else ""
    if returncode == 0 and not prediction_error:
        status = "done"
    elif primary_output and primary_output.exists():
        status = "evaluation_failed"
    else:
        status = "failed"

    # Keep only the raw result copy and official evaluator outputs.
    shutil.rmtree(generated_root, ignore_errors=True)
    shutil.rmtree(case_root / "artifacts" / "trace", ignore_errors=True)

    payload = {
        "mode": mode,
        "dataset": dataset,
        "case_id": case_id,
        "status": status,
        "returncode": returncode,
        "input": {
            "dataset": dataset,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "trace": trace,
            "trace_llm_io": trace_llm_io,
            "valid_only": valid_only,
            "task_name_fallback": task_name_fallback,
        },
        "raw_output": str(raw_output_path),
        "log": str(log_path),
        "trace_json": "",
        "report": str(case_root / "trace_report.md"),
        "artifacts": copied_summaries,
        "command": command,
        "started_at": started_at,
        "api_base": api_base,
        "evaluation_summary": evaluation_summary_payload,
        "evaluation_detail": evaluation_detail_payload,
        "prediction_summary": {
            "identifier": reported_prediction.get("identifier"),
            "error": reported_prediction.get("error", ""),
            "task_success": reported_prediction.get("task_success"),
            "task_success_rate": reported_prediction.get("task_success_rate"),
            "official_available": reported_prediction.get("official_available"),
            "execution_success": reported_prediction.get("execution_success"),
            "planning_result": reported_prediction.get("planning_result", {}),
            "input_provenance": reported_prediction.get("input_provenance", {}),
            "llm_output_preview": str(reported_prediction.get("llm_output", "") or "")[:1200],
            "benchmark_trace_present": bool(isinstance(reported_prediction.get("benchmark_trace"), dict) and reported_prediction.get("benchmark_trace")),
        },
    }
    payload.update(official_fields)

    write_case_meta(case_meta_path, payload)
    try:
        write_case_report(
            config_name=f"eai_{dataset}",
            output_path=case_root / "trace_report.md",
            case_meta_path=case_meta_path,
            raw_output_path=raw_output_path,
            trace_json_path=None,
            evaluation_summary_path=evaluation_summary_path,
            evaluation_detail_path=evaluation_detail_path,
            dataset=dataset,
        )
    except Exception:
        pass
    write_rounds_bundle(case_root, prediction, include_rounds=True)
    return payload


def summarize_eai_run(run_root: Path) -> dict[str, Any]:
    cases_dir = run_root / "cases"
    rows = []
    if cases_dir.exists():
        for case_dir in sorted(path for path in cases_dir.iterdir() if path.is_dir()):
            meta_path = case_dir / "case.json"
            meta = load_case_meta(meta_path)
            if meta:
                rows.append(meta)
    total_cases = len(rows)
    done_cases = sum(1 for row in rows if row.get("status") == "done")
    failed_cases = sum(1 for row in rows if row.get("status") in {"failed", "evaluation_failed"})
    official_available_count = sum(1 for row in rows if row.get("official_available") is True)
    task_success_count = sum(1 for row in rows if row.get("task_success") is True)
    official_rate_sum = sum(float(row.get("task_success_rate", 0.0) or 0.0) for row in rows if row.get("official_available") is True)
    return {
        "run_name": run_root.name,
        "total_cases": total_cases,
        "done_cases": done_cases,
        "failed_cases": failed_cases,
        "task_success_count": task_success_count,
        "task_success_rate": (task_success_count / total_cases) if total_cases else 0.0,
        "official_available_count": official_available_count,
        "official_task_success_rate": (
            official_rate_sum / official_available_count if official_available_count else None
        ),
        "missing_official_eval_count": total_cases - official_available_count,
        "cases": rows,
    }


def write_eai_summary(run_root: Path) -> dict[str, Any]:
    summary = summarize_eai_run(run_root)
    write_json(run_root / "summary.json", summary)
    return summary
