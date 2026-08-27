import copy
from typing import Any


EMPTY_FAILED_LESSONS_TEXT = "暂无相关拦截记录"


def coerce_memory(memory: dict | None = None) -> dict[str, Any]:
    if not isinstance(memory, dict):
        return {"failed_lessons": []}

    lessons = memory.get("failed_lessons", [])
    if not isinstance(lessons, list):
        lessons = []

    return {
        **memory,
        "failed_lessons": list(lessons),
    }


def initial_trace_state() -> dict[str, Any]:
    return {
        **empty_checkpoint_state(),
        "re_trac_memory": coerce_memory(),
    }


def empty_checkpoint_state() -> dict[str, Any]:
    return {
        "validated_steps": [],
        "validated_todo_actions": [],
        "checkpoint_env": {},
        "checkpoint_robot": {},
        "todo_checkpoint_env": {},
        "todo_checkpoint_robot": {},
    }


def add_failed_lesson(memory: dict | None, issue: str, fix: str) -> dict[str, Any]:
    memory = coerce_memory(memory)
    lesson = f"{issue} -> 修复要求: {fix}"
    if lesson not in memory["failed_lessons"]:
        memory["failed_lessons"].append(lesson)
    return memory


def failed_lesson_occurrences(memory: dict | None, issue: str, fix: str) -> int:
    memory = coerce_memory(memory)
    lesson = f"{issue} -> 修复要求: {fix}"
    return sum(1 for item in memory.get("failed_lessons", []) if item == lesson)


def format_failed_lessons(memory: dict | None) -> str:
    lessons = coerce_memory(memory).get("failed_lessons", [])
    if not lessons:
        return EMPTY_FAILED_LESSONS_TEXT
    return "\n".join(lessons)


def build_failure_finding(*, step_info: dict | None, issue: str, fix: str) -> dict[str, Any]:
    step_info = step_info if isinstance(step_info, dict) else {}
    execution = step_info.get("execution", {})
    if not isinstance(execution, dict):
        execution = {}

    return {
        "failed_step": step_info.get("step"),
        "skill": execution.get("skill", ""),
        "parameters": copy.deepcopy(execution.get("parameters", {})),
        "error_type": issue,
        "actual": issue,
        "expected": fix,
        "repair_hint": fix,
    }


def planning_context(
    *,
    state: dict,
    resolved_env: dict,
    fallback_robot: dict,
) -> dict[str, Any]:
    feature_flags = state.get("feature_flags") if isinstance(state, dict) else {}
    repair_enabled = not (
        isinstance(feature_flags, dict)
        and feature_flags.get("checkpoint_repair") is False
    )
    validated_steps = copy.deepcopy(state.get("validated_steps") or []) if repair_enabled else []
    validated_todo_actions = copy.deepcopy(state.get("validated_todo_actions") or []) if repair_enabled else []
    checkpoint_env = (state.get("checkpoint_env") or {}) if repair_enabled else {}
    checkpoint_robot = (state.get("checkpoint_robot") or {}) if repair_enabled else {}
    todo_checkpoint_env = (state.get("todo_checkpoint_env") or {}) if repair_enabled else {}
    todo_checkpoint_robot = (state.get("todo_checkpoint_robot") or {}) if repair_enabled else {}

    return {
        "validated_steps": validated_steps,
        "validated_todo_actions": validated_todo_actions,
        "current_env": copy.deepcopy(checkpoint_env if checkpoint_env else resolved_env),
        "current_robot": copy.deepcopy(checkpoint_robot if checkpoint_robot else fallback_robot),
        "todo_current_env": copy.deepcopy(todo_checkpoint_env if todo_checkpoint_env else resolved_env),
        "todo_current_robot": copy.deepcopy(todo_checkpoint_robot if todo_checkpoint_robot else fallback_robot),
        "next_step_num": len(validated_steps) + 1,
        "next_todo_step_num": len(validated_todo_actions) + 1,
        "failed_lessons": format_failed_lessons(state.get("re_trac_memory")),
        "re_trac_state": copy.deepcopy(state.get("re_trac_state", {})) if repair_enabled else {},
    }


def build_failure_payload(
    *,
    issue: str,
    fix: str,
    memory: dict | None,
    validated_steps: list | None,
    checkpoint_env: dict,
    checkpoint_robot: dict,
    validated_todo_actions: list | None = None,
    todo_checkpoint_env: dict | None = None,
    todo_checkpoint_robot: dict | None = None,
    re_trac_state: dict | None = None,
    finding: dict | None = None,
    record_retrac_memory: bool = True,
) -> dict[str, Any]:
    findings = [copy.deepcopy(finding)] if isinstance(finding, dict) else []
    return {
        "is_feasible": False,
        "feedback": f"{issue}\n{fix}",
        "validated_steps": list(validated_steps or []),
        "validated_todo_actions": list(validated_todo_actions or []),
        "checkpoint_env": copy.deepcopy(checkpoint_env),
        "checkpoint_robot": copy.deepcopy(checkpoint_robot),
        "todo_checkpoint_env": copy.deepcopy(todo_checkpoint_env or {}),
        "todo_checkpoint_robot": copy.deepcopy(todo_checkpoint_robot or {}),
        "re_trac_state": copy.deepcopy(re_trac_state or {}),
        "re_trac_memory": (
            add_failed_lesson(memory, issue, fix)
            if record_retrac_memory
            else coerce_memory(memory)
        ),
        "evaluator_findings": findings,
    }
