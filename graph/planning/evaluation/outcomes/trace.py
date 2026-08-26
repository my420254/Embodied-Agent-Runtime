# trace.py —— 认知规划 trace 注入与持久化。
# trace recorder factory 由调用方注入，便于替换存储后端和独立测试。
from __future__ import annotations

from typing import Any, Callable

from graph.state import PlanningState
from ..models import EvaluationFailure


def _with_cognitive_sandbox_trace(
    result: dict,
    state: PlanningState,
    *,
    sandbox_enabled: bool,
    failure: EvaluationFailure | None = None,
    validated_steps: list | None = None,
    recorder_factory: Callable[[], Any],
) -> dict:
    trace = state.get("cognitive_planning_trace", {})
    if not isinstance(trace, dict):
        return result

    enriched = dict(trace)
    passed = failure is None
    enriched["sandbox"] = {
        "enabled": sandbox_enabled,
        "passed": passed,
        "issue_type": failure.issue_type if failure else "",
        "fix": failure.fix_advice if failure else "",
        "failure_category": failure.code.value if failure else "",
        "failed_step": failure.failed_step if failure else None,
        "validated_step_count": len(
            failure.validated_steps if failure else (validated_steps or [])
        ),
    }
    enriched = _record_cognitive_trace_if_enabled(
        enriched,
        state.get("feature_flags", {}),
        recorder_factory=recorder_factory,
    )
    return {**result, "cognitive_planning_trace": enriched}


def _record_cognitive_trace_if_enabled(
    trace: dict,
    feature_flags: dict | None,
    *,
    recorder_factory: Callable[[], Any],
) -> dict:
    from .. import flags as _flags

    if not _flags._feature_enabled(feature_flags, "cognitive_trace_write", default=False):
        return trace

    enriched = dict(trace)
    try:
        trace_id = recorder_factory().record(enriched)
        enriched["trace_storage"] = {
            "written": True,
            "trace_id": trace_id,
            "format": "jsonl",
        }
    except Exception as exc:
        enriched["trace_storage"] = {
            "written": False,
            "error": str(exc),
            "format": "jsonl",
        }
    return enriched


__all__ = [
    "_with_cognitive_sandbox_trace",
    "_record_cognitive_trace_if_enabled",
]
