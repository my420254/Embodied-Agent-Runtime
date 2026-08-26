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

        lines = self.path.read_text(encoding="utf-8").splitlines()
        recent = lines[-limit:]
        records: list[dict[str, Any]] = []
        for line in recent:
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

    def summarize_recent(self, limit: int = 100) -> dict[str, Any]:
        records = self.read_recent(limit=limit)
        budget_events = [
            event
            for record in records
            for event in _list_of_dicts(record.get("bt_recovery_retry_budget"))
        ]
        bt_attempts = [
            attempt
            for record in records
            for attempt in _list_of_dicts(record.get("behavior_tree_execution_attempts"))
        ]
        reflection_attempts = [
            attempt
            for record in records
            for attempt in _list_of_dicts(record.get("execution_reflection_attempts"))
        ]
        checkpoint_repairs = [
            repair
            for record in records
            if (repair := _checkpoint_suffix_repair(record))
        ]
        checkpoint_suffix_step_counts = [
            _int_field(_planning_node(record).get("suffix_step_count"))
            for record in records
            if _checkpoint_suffix_repair(record)
        ]
        selected_skill_counts: dict[str, int] = {}
        for record in records:
            for skill_id in _list_of_strings(record.get("selected_skill_ids")):
                selected_skill_counts[skill_id] = selected_skill_counts.get(skill_id, 0) + 1
        orchestration_route_counts: dict[str, int] = {}
        route_buckets: dict[str, dict[str, Any]] = {}
        for record in records:
            route = _orchestration_route(record)
            orchestration_route_counts[route] = orchestration_route_counts.get(route, 0) + 1
            bucket = route_buckets.setdefault(
                route,
                {
                    "trace_count": 0,
                    "safety_check_count": 0,
                    "safety_passed_count": 0,
                    "sandbox_check_count": 0,
                    "sandbox_passed_count": 0,
                    "kg_query_counts": [],
                    "scene_query_counts": [],
                },
            )
            bucket["trace_count"] += 1
            safety = _dict_field(record.get("safety"))
            if "passed" in safety:
                bucket["safety_check_count"] += 1
                if safety.get("passed") is True:
                    bucket["safety_passed_count"] += 1
            sandbox = _dict_field(record.get("sandbox"))
            if "passed" in sandbox:
                bucket["sandbox_check_count"] += 1
                if sandbox.get("passed") is True:
                    bucket["sandbox_passed_count"] += 1
            bucket["kg_query_counts"].append(_kg_query_count(record))
            bucket["scene_query_counts"].append(_scene_query_count(record))
        safety_records = [_dict_field(record.get("safety")) for record in records if "passed" in _dict_field(record.get("safety"))]
        sandbox_records = [_dict_field(record.get("sandbox")) for record in records if "passed" in _dict_field(record.get("sandbox"))]
        safety_passed = sum(1 for safety in safety_records if safety.get("passed") is True)
        sandbox_passed = sum(1 for sandbox in sandbox_records if sandbox.get("passed") is True)
        sandbox_failure_categories: dict[str, int] = {}
        for sandbox in sandbox_records:
            if sandbox.get("passed") is True:
                continue
            category = str(sandbox.get("failure_category") or "uncategorized")
            sandbox_failure_categories[category] = sandbox_failure_categories.get(category, 0) + 1
        budget_used_values = [_int_field(event.get("used")) for event in budget_events]
        budget_exhausted = sum(1 for event in budget_events if event.get("exhausted") is True)
        reflection_limit_count = sum(1 for attempt in reflection_attempts if attempt.get("limit_reached") is True)
        checkpoint_aligned = sum(1 for repair in checkpoint_repairs if repair.get("aligned") is True)
        checkpoint_prefix_reused = sum(
            1 for repair in checkpoint_repairs if repair.get("reuse_validated_prefix") is True
        )
        return {
            "trace_count": len(records),
            "selected_skill_counts": selected_skill_counts,
            "orchestration_route_counts": dict(sorted(orchestration_route_counts.items())),
            "orchestration_route_metrics": _route_metrics(route_buckets),
            "safety_check_count": len(safety_records),
            "safety_passed_count": safety_passed,
            "safety_failed_count": len(safety_records) - safety_passed,
            "safety_pass_rate": _rate(safety_passed, len(safety_records)),
            "sandbox_check_count": len(sandbox_records),
            "sandbox_passed_count": sandbox_passed,
            "sandbox_failed_count": len(sandbox_records) - sandbox_passed,
            "sandbox_pass_rate": _rate(sandbox_passed, len(sandbox_records)),
            "sandbox_failure_category_counts": sandbox_failure_categories,
            "bt_recovery_budget_event_count": len(budget_events),
            "bt_recovery_budget_exhausted_count": budget_exhausted,
            "bt_recovery_budget_exhaustion_rate": _rate(budget_exhausted, len(budget_events)),
            "avg_bt_recovery_budget_used": _avg(budget_used_values),
            "max_bt_recovery_budget_used": max(budget_used_values, default=0),
            "bt_execution_attempt_count": len(bt_attempts),
            "execution_reflection_attempt_count": len(reflection_attempts),
            "execution_reflection_limit_count": reflection_limit_count,
            "execution_reflection_limit_rate": _rate(reflection_limit_count, len(reflection_attempts)),
            "checkpoint_suffix_check_count": len(checkpoint_repairs),
            "checkpoint_suffix_aligned_count": checkpoint_aligned,
            "checkpoint_suffix_alignment_rate": _rate(checkpoint_aligned, len(checkpoint_repairs)),
            "checkpoint_suffix_prefix_reuse_count": checkpoint_prefix_reused,
            "checkpoint_suffix_prefix_reuse_rate": _rate(checkpoint_prefix_reused, len(checkpoint_repairs)),
            "avg_checkpoint_suffix_validated_step_count": _avg(
                _int_field(repair.get("validated_step_count")) for repair in checkpoint_repairs
            ),
            "avg_checkpoint_suffix_step_count": _avg(checkpoint_suffix_step_counts),
        }


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, dict)]


def _list_of_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item]


def _dict_field(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _orchestration_route(record: dict[str, Any]) -> str:
    orchestration = _dict_field(record.get("orchestration"))
    route = str(orchestration.get("path") or "")
    return route or "unknown"


def _kg_query_count(record: dict[str, Any]) -> int:
    return int(bool(record.get("kg_query") or record.get("kg_query_type")))


def _scene_query_count(record: dict[str, Any]) -> int:
    scene_queries = record.get("scene_queries")
    return len(scene_queries) if isinstance(scene_queries, list) else 0


def _route_metrics(route_buckets: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    metrics: dict[str, dict[str, Any]] = {}
    for route, bucket in route_buckets.items():
        safety_check_count = int(bucket.get("safety_check_count") or 0)
        safety_passed_count = int(bucket.get("safety_passed_count") or 0)
        sandbox_check_count = int(bucket.get("sandbox_check_count") or 0)
        sandbox_passed_count = int(bucket.get("sandbox_passed_count") or 0)
        metrics[route] = {
            "trace_count": int(bucket.get("trace_count") or 0),
            "safety_check_count": safety_check_count,
            "safety_passed_count": safety_passed_count,
            "safety_pass_rate": _rate(safety_passed_count, safety_check_count),
            "sandbox_check_count": sandbox_check_count,
            "sandbox_passed_count": sandbox_passed_count,
            "sandbox_pass_rate": _rate(sandbox_passed_count, sandbox_check_count),
            "avg_kg_query_count": _avg(bucket.get("kg_query_counts") or []),
            "avg_scene_query_count": _avg(bucket.get("scene_query_counts") or []),
        }
    return {route: metrics[route] for route in sorted(metrics)}


def _planning_node(record: dict[str, Any]) -> dict[str, Any]:
    planning_node = record.get("planning_node", {})
    return dict(planning_node) if isinstance(planning_node, dict) else {}


def _checkpoint_suffix_repair(record: dict[str, Any]) -> dict[str, Any]:
    repair = _planning_node(record).get("checkpoint_suffix_repair", {})
    return dict(repair) if isinstance(repair, dict) and repair else {}


def _int_field(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _avg(values: Any) -> float:
    items = list(values)
    if not items:
        return 0.0
    return sum(items) / len(items)


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator
