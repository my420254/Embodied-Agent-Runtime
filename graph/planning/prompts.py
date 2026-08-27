from __future__ import annotations

import json
import copy
from typing import Any

try:
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
except Exception:  # pragma: no cover

    class _Message:  # type: ignore[no-redef]
        def __init__(self, content: str):
            self.content = content

    class AIMessage(_Message):
        pass

    class HumanMessage(_Message):
        pass

    class SystemMessage(_Message):
        pass


from config.module_loader import call_configured_module_function
from config.prompts import render_prompt


PROMPT_INPUTS_MODULE = "graph.prompt_inputs"
DEFAULT_PLANNING_USER_MESSAGE = "开始规划。"


def _planning_main_inputs(result) -> tuple[dict[str, Any], list[str]]:
    if not isinstance(result, tuple) or len(result) != 2:
        raise TypeError(
            "build_planning_main_inputs must return (variables, injected_rule_ids)"
        )
    variables, injected_rule_ids = result
    if not isinstance(variables, dict):
        raise TypeError("build_planning_main_inputs variables must be a dict")
    if not isinstance(injected_rule_ids, list):
        raise TypeError("build_planning_main_inputs injected_rule_ids must be a list")
    return variables, injected_rule_ids


def _repair_inputs(
    *,
    feedback: str,
    repair_state_json: str,
    next_step_num: int,
    feature_flags: dict | None,
) -> dict[str, Any]:
    return call_configured_module_function(
        ("files", "prompt_inputs_module"),
        PROMPT_INPUTS_MODULE,
        "build_planning_repair_inputs",
        feedback=feedback,
        repair_state_json=repair_state_json,
        re_trac_state_json=repair_state_json,
        next_step_num=next_step_num,
        feature_flags=feature_flags,
    )


def _todo_action_prefix_for_prompt(steps: list) -> list[dict[str, Any]]:
    prefix: list[dict[str, Any]] = []
    for step in steps or []:
        if not isinstance(step, dict):
            continue
        item = {
            key: copy.deepcopy(value) for key, value in step.items() if key != "step"
        }
        if item:
            prefix.append(item)
    return prefix


def _strip_todo_step_numbers(value: Any) -> Any:
    if isinstance(value, list):
        return [_strip_todo_step_numbers(item) for item in value]
    if isinstance(value, dict):
        return {
            key: _strip_todo_step_numbers(item)
            for key, item in value.items()
            if key != "step"
        }
    return copy.deepcopy(value)


def _todo_repair_handoff_for_prompt(repair_handoff: dict | None) -> dict:
    if not isinstance(repair_handoff, dict):
        return {}
    payload = copy.deepcopy(repair_handoff)
    todo_trajectory = payload.get("todo_trajectory")
    if isinstance(todo_trajectory, dict):
        payload["todo_trajectory"] = _strip_todo_step_numbers(todo_trajectory)
        todo_trajectory = payload["todo_trajectory"]
        payload.pop("trajectory", None)
        failure = payload.get("failure")
        todo_wrong_step = todo_trajectory.get("wrong_step")
        if isinstance(failure, dict) and isinstance(todo_wrong_step, dict):
            failure["wrong_step"] = _strip_todo_step_numbers(todo_wrong_step)
        frontier = payload.get("frontier")
        if isinstance(frontier, dict):
            next_step = todo_trajectory.get("next_step_num")
            if next_step is not None:
                frontier["next_step_num"] = next_step
            frontier["instruction"] = (
                "保留已验证前缀，只根据 current_simulated_state 生成后续 todo_list 动作。"
            )
    return payload


def _json_equivalent(left: Any, right: Any) -> bool:
    """Compare checkpoint payloads without depending on dictionary order."""
    try:
        return json.dumps(
            left, ensure_ascii=False, sort_keys=True, default=str
        ) == json.dumps(
            right,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )
    except TypeError:
        return left == right


def _compact_repair_handoff_for_prompt(
    repair_handoff: dict | None,
    *,
    current_env: dict,
    current_robot: dict,
) -> dict:
    """Drop only checkpoint fields already present in the system message.

    If a repair checkpoint is newer than the system snapshot, its full state is
    retained and marked as the authority for the repair prompt.
    """
    if not isinstance(repair_handoff, dict):
        return {}
    payload = copy.deepcopy(repair_handoff)
    checkpoint = payload.get("current_simulated_state")
    if not isinstance(checkpoint, dict):
        return payload

    omitted: list[str] = []
    if isinstance(checkpoint.get("environment"), dict) and _json_equivalent(
        checkpoint["environment"], current_env
    ):
        checkpoint.pop("environment", None)
        omitted.append("environment")
    if isinstance(checkpoint.get("robot"), dict) and _json_equivalent(
        checkpoint["robot"], current_robot
    ):
        checkpoint.pop("robot", None)
        omitted.append("robot")

    if omitted:
        checkpoint["omitted_duplicate_fields"] = omitted
        checkpoint["authority"] = {field: "planning.main_system" for field in omitted}
    if "environment" in checkpoint or "robot" in checkpoint:
        checkpoint.setdefault("authority", "planning.main_system_current_snapshot")
        checkpoint["checkpoint_role"] = "audit_reference_when_snapshot_differs"
    return payload


def _steps_are_framework_wrapped(steps: list) -> bool:
    for step in steps or []:
        if not isinstance(step, dict):
            continue
        execution = step.get("execution")
        if isinstance(execution, dict) and execution:
            return True
    return False


def build_planning_messages(
    *,
    current_robot: dict,
    current_env: dict,
    navigation_contract: str,
    task_environment_facts: str,
    task_context: dict,
    task_source_text: str,
    names_info: dict,
    understanding_final_state: dict | None,
    skill_closure: list[str] | None,
    failed_lessons: str,
    intent: str,
    feedback: str,
    validated_steps: list,
    next_step_num: int,
    repair_handoff: dict | None = None,
    feature_flags: dict | None = None,
) -> tuple[list, list[str]]:
    main_inputs, injected_rule_ids = _planning_main_inputs(
        call_configured_module_function(
            ("files", "prompt_inputs_module"),
            PROMPT_INPUTS_MODULE,
            "build_planning_main_inputs",
            current_robot=current_robot,
            current_env=current_env,
            navigation_contract=navigation_contract,
            task_environment_facts=task_environment_facts,
            task_context=task_context,
            task_source_text=task_source_text,
            names_info=names_info,
            understanding_final_state=understanding_final_state,
            skill_closure=skill_closure,
            failed_lessons=failed_lessons,
            intent=intent,
            feature_flags=feature_flags,
        )
    )

    framework_wrapped_prefix = _steps_are_framework_wrapped(validated_steps)
    messages = [
        SystemMessage(content=render_prompt("planning.main_system", **main_inputs))
    ]
    if validated_steps:
        if not framework_wrapped_prefix:
            messages.append(
                AIMessage(
                    content=json.dumps(
                        _todo_action_prefix_for_prompt(validated_steps),
                        ensure_ascii=False,
                    )
                )
            )
        else:
            messages.append(
                AIMessage(
                    content=json.dumps(
                        {
                            "thought_process": "执行已验证的动作前缀...",
                            "todo_list": validated_steps,
                        },
                        ensure_ascii=False,
                    )
                )
            )
    if validated_steps or str(feedback or "").strip() or repair_handoff:
        prompt_repair_handoff = (
            _todo_repair_handoff_for_prompt(repair_handoff)
            if isinstance(repair_handoff, dict)
            and repair_handoff.get("todo_trajectory")
            else (repair_handoff or {})
        )
        prompt_repair_handoff = _compact_repair_handoff_for_prompt(
            prompt_repair_handoff,
            current_env=current_env,
            current_robot=current_robot,
        )
        messages.append(
            HumanMessage(
                content=render_prompt(
                    "planning.repair_user",
                    **_repair_inputs(
                        feedback=feedback,
                        repair_state_json=json.dumps(
                            prompt_repair_handoff, ensure_ascii=False, indent=2
                        ),
                        next_step_num=next_step_num,
                        feature_flags=feature_flags,
                    ),
                )
            )
        )
    else:
        messages.append(HumanMessage(content=DEFAULT_PLANNING_USER_MESSAGE))
    return messages, injected_rule_ids


__all__ = ["build_planning_messages", "load_planning_playbook"]


def load_planning_playbook(*args, **kwargs):
    from graph.planning.prompt_inputs import load_planning_playbook as _load

    return _load(*args, **kwargs)
