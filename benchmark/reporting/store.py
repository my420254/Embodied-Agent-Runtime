from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from config.settings import project_path


def timestamp() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S %z")


def safe_case_name(case_id: str) -> str:
    return str(case_id).replace("/", "__").replace(":", "__")


def case_root(run_root: Path, case_id: str) -> Path:
    return run_root / "cases" / safe_case_name(case_id)


def common_case_paths(run_root: Path, case_id: str) -> dict[str, Path]:
    root = case_root(run_root, case_id)
    return {
        "root": root,
        "meta": root / "case.json",
        "raw": root / "raw_output.json",
        "log": root / "run.log",
        "report": root / "trace_report.md",
        "artifacts": root / "artifacts",
    }


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_case_meta(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = read_json(path)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def write_case_meta(path: Path, payload: dict[str, Any]) -> None:
    payload["updated_at"] = timestamp()
    write_json(path, payload)


def benchmark_trace_root(dataset: str, mode: str, run_name: str) -> Path:
    dataset_name = str(dataset or "").strip()
    mode_name = str(mode or "").strip()
    run = str(run_name or "").strip()

    if dataset_name == "delta":
        return project_path("benchmark", "delta", mode_name, "results", run, "trace")
    if dataset_name == "reactree":
        return project_path("benchmark", "reactree", "wah", mode_name, "results", run, "trace")
    if dataset_name == "reactree_alfred":
        return project_path("benchmark", "reactree", "alfred", mode_name, "results", run, "trace")
    if dataset_name == "behavior":
        return project_path("benchmark", "eai", "behavior", mode_name, "results", run, "trace")
    if dataset_name == "virtualhome":
        return project_path("benchmark", "eai", "virtualhome", mode_name, "results", run, "trace")
    return project_path("benchmark", dataset_name, "trace", mode_name, run)
