from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from config.settings import project_path


DEFAULT_TRACE_LOG = project_path("logs", "cognitive_planning_traces.jsonl")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class JsonlTraceRecorder:
    """Append-only JSONL recorder for cognitive planning traces."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else DEFAULT_TRACE_LOG

    def record(self, trace: dict[str, Any]) -> str:
        if not isinstance(trace, dict):
            raise TypeError("trace must be a dictionary")

        trace_id = str(trace.get("trace_id") or f"trace-{uuid4().hex[:12]}")
        payload = dict(trace)
        payload["trace_id"] = trace_id
        payload["recorded_at"] = _now_iso()

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
        return trace_id

    def read_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        if limit <= 0 or not self.path.exists():
            return []

        records: list[dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines()[-limit:]:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                records.append(record)
        return records

    def find_by_trace_id(self, trace_id: str) -> dict[str, Any] | None:
        if not trace_id or not self.path.exists():
            return None

        for line in reversed(self.path.read_text(encoding="utf-8").splitlines()):
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict) and record.get("trace_id") == trace_id:
                return record
        return None


__all__ = ["JsonlTraceRecorder"]
