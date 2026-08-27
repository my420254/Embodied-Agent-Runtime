from __future__ import annotations

import argparse
import reprlib
import time
import traceback
from pathlib import Path
from typing import Any

from benchmark.delta.framework.code import case_executor
from benchmark.experiment_utils import (
    case_root,
    exit_if_not_internal_worker,
    read_json,
    timestamp,
    worker_case_row,
    worker_result_payload,
    write_json,
)
from benchmark.reporting import persist_case_bundle


def main() -> int:
    exit_if_not_internal_worker()
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker-input", required=True)
    args = parser.parse_args()
    payload = read_json(args.worker_input, {})
    case_payload = payload.get("case", {}) if isinstance(payload, dict) else {}
    options = payload.get("options", {}) if isinstance(payload, dict) else {}
    run_root = Path(str(payload.get("run_root", "")))
    case_id = str(case_payload.get("case_id", ""))
    root = case_root(run_root, case_id)
    root.mkdir(parents=True, exist_ok=True)

    error = ""
    traceback_text = ""
    prediction: dict[str, Any] = {}
    started_at = timestamp()
    started_epoch = time.time()
    started_monotonic = time.monotonic()
    try:
        prediction = case_executor.run_case(
            case_payload.get("input", {}) if isinstance(case_payload.get("input"), dict) else {},
            plan_output_dir=root / "plans",
            validate_binary=options.get("validate_binary") or None,
            skip_val=bool(options.get("skip_val", False)),
        )
    except Exception as exc:  # pragma: no cover - worker isolation
        error = reprlib.repr(exc)
        traceback_text = traceback.format_exc()
        print(traceback_text, flush=True)

    timing = {
        "started_at": started_at,
        "finished_at": timestamp(),
        "started_at_epoch": started_epoch,
        "finished_at_epoch": time.time(),
        "elapsed_s": round(time.monotonic() - started_monotonic, 3),
    }
    row = worker_case_row(case_payload, prediction, error, default_dataset="delta")
    row["timing"] = timing
    try:
        persist_case_bundle(config_name="delta", run_root=run_root, row=row, source_hint=root / "raw_output.json")
    finally:
        payload = worker_result_payload(
            case_id=case_id,
            status="failed" if error else "done",
            error=error,
            case_root_path=root,
            row=row,
            timing=timing,
        )
        if traceback_text:
            payload["traceback"] = traceback_text
        write_json(root / "worker_result.json", payload)
    return 1 if error else 0


if __name__ == "__main__":
    raise SystemExit(main())
