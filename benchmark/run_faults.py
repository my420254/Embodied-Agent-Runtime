from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


_HARD_FAULT_MARKERS = (
    "Traceback (most recent call last)",
    "ModuleNotFoundError",
    "ImportError",
    "CUDA out of memory",
    "Connection error",
    "ReadTimeout",
    "ConnectTimeout",
)


def _iter_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _iter_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_strings(item)


def benchmark_row_has_hard_fault(row: dict[str, Any]) -> bool:
    if not isinstance(row, dict):
        return False
    if row.get("hard_fault") is True:
        return True
    if str(row.get("status", "")).lower() in {"hard_fault", "crashed"}:
        return True
    return any(marker in text for text in _iter_strings(row) for marker in _HARD_FAULT_MARKERS)


def dump_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def truncate_items_on_fault(
    rows: list[dict[str, Any]],
    *,
    fault_predicate: Callable[[dict[str, Any]], bool],
    rewind: int = 0,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int | None]:
    for index, row in enumerate(rows):
        if fault_predicate(row):
            cut_index = max(0, index - max(0, int(rewind or 0)))
            return rows[:cut_index], rows[cut_index:], index
    return rows, [], None
