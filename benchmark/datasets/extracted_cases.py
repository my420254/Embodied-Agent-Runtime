from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


def load_extracted_cases(path: str | Path) -> list[dict[str, Any]]:
    manifest_path = Path(path)
    if not manifest_path.exists():
        raise FileNotFoundError(f"missing extracted case manifest: {manifest_path}")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    cases = payload.get("cases", []) if isinstance(payload, dict) else payload
    if not isinstance(cases, list):
        raise ValueError(f"extracted case manifest must contain a cases list: {manifest_path}")
    return [copy.deepcopy(case) for case in cases if isinstance(case, dict)]


def filter_extracted_cases(
    cases: list[dict[str, Any]],
    *,
    case_ids: set[str] | None = None,
    task_name: str | None = None,
    valid_case_ids: set[str] | None = None,
    scene_id: int | None = None,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    wanted = {str(case_id) for case_id in (case_ids or set()) if str(case_id).strip()}
    valid = {str(case_id) for case_id in (valid_case_ids or set()) if str(case_id).strip()}
    task_name = str(task_name or "").strip()
    for case in cases:
        case_id = str(case.get("case_id", "") or "")
        case_input = case.get("input", {}) if isinstance(case.get("input"), dict) else {}
        identifier = str(case_input.get("identifier") or case_input.get("task_id") or case_id)
        if wanted and case_id not in wanted and identifier not in wanted:
            continue
        if valid and case_id not in valid and identifier not in valid:
            continue
        if task_name:
            names = {
                str(case_input.get("instruction", "") or ""),
                str(case_input.get("task_name", "") or ""),
                str((case.get("metadata", {}) if isinstance(case.get("metadata"), dict) else {}).get("task_name", "") or ""),
            }
            if task_name not in names:
                continue
        copied = copy.deepcopy(case)
        if scene_id is not None:
            copied.setdefault("input", {})["scene_id"] = int(scene_id)
            copied.setdefault("metadata", {})["scene_id"] = int(scene_id)
        selected.append(copied)
    return selected

