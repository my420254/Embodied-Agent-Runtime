from __future__ import annotations

import copy
import json
from typing import Any


EMPTY_FAILED_LESSONS_TEXT = "暂无相关拦截记录"


def coerce_memory(memory: dict | None = None) -> dict[str, Any]:
    if not isinstance(memory, dict):
        return {"failed_lessons": []}
    lessons = memory.get("failed_lessons", [])
    return {
        **memory,
        "failed_lessons": list(lessons) if isinstance(lessons, list) else [],
    }


def empty_checkpoint_state() -> dict[str, Any]:
    return {
        "validated_steps": [],
        "checkpoint_env": {},
        "checkpoint_robot": {},
    }


def initial_evaluation_state() -> dict[str, Any]:
    return {
        **empty_checkpoint_state(),
        "repair_memory": coerce_memory(),
        "repair_handoff": {},
        "planning_continuation": {},
        "evaluation_repair_request": {},
        "repair_todo_list": [],
        "evaluation_recheck": False,
        "evaluation_revision_context": {},
        "repair_history": [],
    }


def format_failed_lessons(memory: dict | None) -> str:
    lessons = coerce_memory(memory).get("failed_lessons", [])
    if not lessons:
        return EMPTY_FAILED_LESSONS_TEXT
    return "\n".join(str(lesson) for lesson in lessons)


def build_planning_continuation(
    *,
    validated_steps: list | None,
    checkpoint_env: dict | None,
    checkpoint_robot: dict | None,
    repair_memory: dict | None,
    repair_handoff: dict | None,
    enabled: bool,
) -> dict[str, Any]:
    """Project an evaluator outcome into the next planner request."""

    if not enabled:
        return {}
    prefix = [
        copy.deepcopy(step)
        for step in (validated_steps or [])
        if isinstance(step, dict)
    ]
    return {
        "validated_steps": prefix,
        "current_env": copy.deepcopy(checkpoint_env or {}),
        "current_robot": copy.deepcopy(checkpoint_robot or {}),
        "next_step_num": len(prefix) + 1,
        "failed_lessons": format_failed_lessons(repair_memory),
        "repair_handoff": copy.deepcopy(repair_handoff or {}),
        "aligned": True,
        "reuse_validated_prefix": bool(prefix),
        "validated_step_count": len(prefix),
    }


def strip_repeated_prefix(
    validated_steps: list | None,
    candidate_steps: list | None,
) -> list[dict[str, Any]]:
    candidates = [
        copy.deepcopy(step)
        for step in (candidate_steps or [])
        if isinstance(step, dict)
    ]
    prefix = [step for step in (validated_steps or []) if isinstance(step, dict)]
    if not prefix or not candidates:
        return candidates

    matched = 0
    for candidate in candidates:
        if matched >= len(prefix):
            break
        if _action_signature(candidate) != _action_signature(prefix[matched]):
            break
        matched += 1
    return candidates[matched:] if matched else candidates


def _action_signature(step: dict) -> str:
    execution = step.get("execution", {}) if isinstance(step, dict) else {}
    if not isinstance(execution, dict):
        execution = {}
    params = execution.get("parameters", {}) or {}
    try:
        params_json = json.dumps(
            params,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )
    except TypeError:
        params_json = str(params)
    return f"{execution.get('skill', '')}:{params_json}"


__all__ = [
    "EMPTY_FAILED_LESSONS_TEXT",
    "build_planning_continuation",
    "coerce_memory",
    "empty_checkpoint_state",
    "format_failed_lessons",
    "initial_evaluation_state",
    "strip_repeated_prefix",
]
