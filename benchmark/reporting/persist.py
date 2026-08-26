from __future__ import annotations

from pathlib import Path
from typing import Any

from benchmark.reporting.compact import compact_result_row
from benchmark.reporting.rounds import write_rounds_bundle
from benchmark.reporting.store import common_case_paths, write_case_meta, write_json
from benchmark.reporting.trace_artifacts import write_standard_trace_artifacts
from benchmark.reporting.writer import write_case_report


def _result_status(row: dict[str, Any]) -> str:
    prediction = row.get("prediction", {}) if isinstance(row, dict) else {}
    if not isinstance(prediction, dict):
        prediction = {}
    if row.get("error"):
        return "failed"
    if bool(prediction.get("is_feasible", False)):
        return "done"
    return "evaluation_failed"


def _write_artifact_files(artifacts_root: Path, row: dict[str, Any]) -> None:
    prediction = row.get("prediction", {}) if isinstance(row, dict) else {}
    trace = prediction.get("benchmark_trace", {}) if isinstance(prediction, dict) else {}
    if not isinstance(trace, dict):
        return
    write_standard_trace_artifacts(artifacts_root, trace=trace, prediction=prediction)


def persist_case_bundle(
    *,
    config_name: str,
    run_root: str | Path,
    row: dict[str, Any],
    source_hint: str | Path | None = None,
) -> Path:
    run_root = Path(run_root)
    case_id = str(row.get("case_id", "") or "")
    if not case_id:
        raise ValueError("row.case_id is required")

    paths = common_case_paths(run_root, case_id)
    paths["root"].mkdir(parents=True, exist_ok=True)
    paths["artifacts"].mkdir(parents=True, exist_ok=True)
    raw_output_path = paths["raw"]
    write_json(raw_output_path, [compact_result_row(row)])
    paths["log"].touch(exist_ok=True)
    _write_artifact_files(paths["artifacts"], row)
    write_rounds_bundle(paths["root"], row.get("prediction", {}) if isinstance(row, dict) else {}, include_rounds=True)

    prediction = row.get("prediction", {}) if isinstance(row, dict) else {}
    if not isinstance(prediction, dict):
        prediction = {}

    payload = {
        "case_id": case_id,
        "dataset": row.get("dataset"),
        "status": _result_status(row),
        "raw_output": str(raw_output_path),
        "log": str(paths["log"]),
        "report": str(paths["report"]),
        "source_path": row.get("source_path", ""),
        "metadata": row.get("metadata", {}),
        "prediction_summary": {
            "execution_status": prediction.get("execution_status", ""),
            "is_feasible": prediction.get("is_feasible"),
            "feedback": prediction.get("feedback", ""),
            "task_success": prediction.get("task_success"),
            "task_success_rate": prediction.get("task_success_rate"),
            "goal_success_rate": prediction.get("goal_success_rate"),
            "subgoal_success_rate": prediction.get("subgoal_success_rate"),
            "evaluation_mode": prediction.get("evaluation_mode", ""),
            "official_available": prediction.get("official_available"),
            "execution_success": prediction.get("execution_success"),
        },
    }
    write_case_meta(paths["meta"], payload)
    try:
        write_case_report(
            config_name=config_name,
            row=row,
            output_path=paths["report"],
            source_hint=source_hint or raw_output_path,
        )
    except TypeError as exc:
        # EAI's report writer consumes case artifacts rather than a framework
        # row. Preserve the failure record instead of masking it with a
        # secondary signature error on the error path.
        if "unexpected keyword argument 'row'" not in str(exc):
            raise
        paths["report"].write_text(
            "# Case report\n\n"
            f"- case_id: `{case_id}`\n"
            f"- status: `{payload['status']}`\n"
            f"- error: `{row.get('error', '')}`\n",
            encoding="utf-8",
        )
    return paths["root"]
