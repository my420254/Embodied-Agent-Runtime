from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import uuid4

from .jsonl import JsonlTraceRecorder


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _new_trace_id() -> str:
    return f"trace-{uuid4().hex[:12]}"


def _new_task_id() -> str:
    return f"task-{uuid4().hex[:12]}"


def _clip(value: Any, limit: int) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\r", "\\r").replace("\n", "\\n")
    return text if len(text) <= limit else text[: limit - 3] + "..."


@dataclass(frozen=True)
class TraceEvent:
    trace_id: str
    task_id: str
    event_type: str
    status: str = "ok"
    node: str = ""
    input_summary: str = ""
    output_summary: str = ""
    error: str = ""
    latency_ms: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now_iso)

    def to_record(self) -> dict[str, Any]:
        record = asdict(self)
        record["kind"] = "trace_event"
        return record


class TraceHarness:
    """Trace facade for runtime replay, failure定位 and interview demos.

    The harness stores observable summaries, not model chain-of-thought. This keeps
    logs useful for debugging while avoiding private reasoning leakage.
    """

    def __init__(
        self,
        recorder: JsonlTraceRecorder | None = None,
        *,
        trace_id: str | None = None,
        task_id: str | None = None,
        max_summary_chars: int = 800,
    ) -> None:
        self.recorder = recorder or JsonlTraceRecorder()
        self.trace_id = trace_id or _new_trace_id()
        self.task_id = task_id or _new_task_id()
        self.max_summary_chars = max(80, max_summary_chars)

    def record_event(
        self,
        event_type: str,
        *,
        status: str = "ok",
        node: str = "",
        input_summary: Any = "",
        output_summary: Any = "",
        error: Any = "",
        latency_ms: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        event = TraceEvent(
            trace_id=self.trace_id,
            task_id=self.task_id,
            event_type=str(event_type or "event"),
            status=str(status or "ok"),
            node=str(node or ""),
            input_summary=_clip(input_summary, self.max_summary_chars),
            output_summary=_clip(output_summary, self.max_summary_chars),
            error=_clip(error, self.max_summary_chars),
            latency_ms=latency_ms,
            metadata=dict(metadata or {}),
        )
        return self.recorder.record(event.to_record())

    def record_node(
        self,
        node: str,
        *,
        input_summary: Any = "",
        output_summary: Any = "",
        status: str = "ok",
        latency_ms: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        return self.record_event(
            "node",
            status=status,
            node=node,
            input_summary=input_summary,
            output_summary=output_summary,
            latency_ms=latency_ms,
            metadata=metadata,
        )

    def record_tool(
        self,
        tool_name: str,
        *,
        arguments: Any = None,
        observation: Any = "",
        ok: bool = True,
        latency_ms: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        tool_metadata = dict(metadata or {})
        tool_metadata["tool_name"] = str(tool_name or "")
        return self.record_event(
            "tool",
            status="ok" if ok else "failed",
            node=str(tool_name or ""),
            input_summary=arguments,
            output_summary=observation,
            latency_ms=latency_ms,
            metadata=tool_metadata,
        )

    def record_failure(
        self,
        layer: str,
        error: Any,
        *,
        node: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        failure_metadata = dict(metadata or {})
        failure_metadata["failure_layer"] = str(layer or "unknown")
        return self.record_event(
            "failure",
            status="failed",
            node=node,
            error=error,
            metadata=failure_metadata,
        )

    def replay(self, trace_id: str | None = None) -> list[dict[str, Any]]:
        target = trace_id or self.trace_id
        records = [
            record
            for record in self.recorder.read_all()
            if record.get("kind") == "trace_event" and record.get("trace_id") == target
        ]
        return sorted(records, key=lambda record: str(record.get("recorded_at") or ""))

    @staticmethod
    def summarize(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
        events = list(records)
        failed = [
            record
            for record in events
            if str(record.get("status") or "").lower() not in {"ok", "success", "skipped"}
            or bool(record.get("error"))
        ]
        layers = sorted(
            {
                str((record.get("metadata") or {}).get("failure_layer"))
                for record in failed
                if (record.get("metadata") or {}).get("failure_layer")
            }
        )
        nodes: dict[str, int] = {}
        total_latency_ms = 0.0
        for record in events:
            node = str(record.get("node") or record.get("event_type") or "event")
            nodes[node] = nodes.get(node, 0) + 1
            latency = record.get("latency_ms")
            if isinstance(latency, (int, float)):
                total_latency_ms += float(latency)
        return {
            "trace_id": events[0].get("trace_id") if events else "",
            "task_id": events[0].get("task_id") if events else "",
            "ok": not failed,
            "step_count": len(events),
            "failed_event_count": len(failed),
            "failure_layers": layers,
            "nodes": nodes,
            "total_latency_ms": round(total_latency_ms, 3),
        }

    @staticmethod
    def compare(left: Iterable[dict[str, Any]], right: Iterable[dict[str, Any]]) -> dict[str, Any]:
        left_summary = TraceHarness.summarize(left)
        right_summary = TraceHarness.summarize(right)
        return {
            "left": left_summary,
            "right": right_summary,
            "delta_step_count": right_summary["step_count"] - left_summary["step_count"],
            "delta_latency_ms": round(
                right_summary["total_latency_ms"] - left_summary["total_latency_ms"], 3
            ),
            "status_changed": left_summary["ok"] != right_summary["ok"],
        }


__all__ = ["TraceEvent", "TraceHarness"]
