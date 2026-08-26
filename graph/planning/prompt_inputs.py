from __future__ import annotations

import json
from typing import Any

from ace.playbook import load_relevant_section_rules
from skills.registry import load_enabled_skill_prompts


def _json_compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str)


def _json_pretty(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def _feature_enabled(feature_flags: dict | None, name: str, default: bool = True) -> bool:
    if isinstance(feature_flags, dict) and name in feature_flags:
        return bool(feature_flags[name])
    return default


def load_planning_playbook(
    intent: str,
    context: dict | None = None,
    feature_flags: dict | None = None,
) -> tuple[str, list[str]]:
    if not _feature_enabled(feature_flags, "playbook_retrieval"):
        return "", []
    return load_relevant_section_rules(
        "planning",
        intent=intent,
        context=context or {},
        empty_message="当前规划层经验库为空。",
    )


def build_planning_main_inputs(
    *,
    current_robot: dict,
    current_env: dict,
    navigation_contract: str,
    task_environment_facts: str,
    task_context: dict,
    task_source_text: str,
    names_info: dict,
    skill_closure: list[str] | None = None,
    failed_lessons: str,
    intent: str,
    feature_flags: dict | None = None,
    **_: Any,
) -> tuple[dict[str, Any], list[str]]:
    playbook, injected_rule_ids = load_planning_playbook(
        intent,
        context={
            "names_info": names_info,
            "failed_lessons": failed_lessons,
        },
        feature_flags=feature_flags,
    )
    return (
        {
            "robot_location": current_robot.get("robot_location"),
            "robot_holding": current_robot.get("robot_holding"),
            "robot_state_json": _json_compact(current_robot),
            "current_env_json": _json_compact(current_env),
            "navigation_contract": navigation_contract,
            "task_source_text": task_source_text or "",
            "task_environment_facts": task_environment_facts,
            "task_context_json": _json_pretty(task_context or {"message": "无额外任务上下文"}),
            "skills_markdown": load_enabled_skill_prompts(skill_closure),
            "skill_closure_json": _json_pretty(skill_closure or []),
            "names_info_json": _json_pretty(names_info),
            "playbook": playbook,
            "failed_lessons": failed_lessons,
            "intent": intent,
        },
        injected_rule_ids,
    )


def build_planning_repair_inputs(
    *,
    feedback: str,
    repair_state_json: str = "",
    re_trac_state_json: str = "",
    next_step_num: int = 1,
    **_: Any,
) -> dict[str, Any]:
    repair_state_text = repair_state_json or re_trac_state_json or "{}"
    return {
        "feedback": feedback,
        "repair_state_json": repair_state_text,
        "re_trac_state_json": re_trac_state_json,
        "next_step_num": next_step_num,
    }


PLANNING_PROMPT_INPUT_BUILDERS = {
    "planning.main_system": build_planning_main_inputs,
    "planning.repair_user": build_planning_repair_inputs,
}
