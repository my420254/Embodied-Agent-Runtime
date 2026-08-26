from __future__ import annotations

import copy
import json
from typing import Any

from domain.scene import is_room_level_node


def collect_todo_violations(
    todo_list: list,
    environment: dict[str, Any],
    structured_task: dict[str, Any],
    skill_catalog,
    robot_state: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Collect every static action/entity violation without failing fast."""

    if not todo_list:
        return [
            _violation(
                None,
                "empty_plan",
                "必须输出标准动作序列，todo_list 不能为空",
            )
        ]

    violations: list[dict[str, Any]] = []
    current_location = str((robot_state or {}).get("robot_location", "") or "")
    for index, step in enumerate(todo_list or [], start=1):
        step_num = step.get("step", index) if isinstance(step, dict) else index
        if not isinstance(step, dict):
            violations.append(
                _violation(step_num, "invalid_step", "步骤必须是对象", actual=step)
            )
            continue

        execution = step.get("execution")
        if not isinstance(execution, dict):
            violations.append(
                _violation(step_num, "missing_execution", "缺少 execution 对象")
            )
            continue

        skill = str(execution.get("skill", "") or "").strip()
        parameters = execution.get("parameters")
        if not skill:
            violations.append(_violation(step_num, "missing_skill", "缺少动作 skill"))
            continue
        if not isinstance(parameters, dict):
            violations.append(
                _violation(
                    step_num,
                    "invalid_parameters",
                    "parameters 必须是对象",
                    skill=skill,
                    actual=parameters,
                )
            )
            continue

        spec = skill_catalog.get(skill) if skill_catalog else None
        if spec is None:
            violations.append(
                _violation(
                    step_num,
                    "unknown_skill",
                    "动作不在当前 profile 的可用技能中",
                    skill=skill,
                    allowed_skills=sorted(
                        getattr(skill_catalog, "by_name", {}).keys()
                    ),
                )
            )
            continue

        expected_parameters = _entity_parameters(spec)
        for parameter in expected_parameters:
            value = str(parameters.get(parameter, "") or "").strip()
            if not value:
                violations.append(
                    _violation(
                        step_num,
                        "missing_parameter",
                        f"动作缺少必需参数 {parameter}",
                        skill=skill,
                        parameter=parameter,
                    )
                )
            elif environment and value not in environment:
                violations.append(
                    _violation(
                        step_num,
                        "unknown_entity",
                        f"参数 {parameter} 引用了场景中不存在的实体",
                        skill=skill,
                        parameter=parameter,
                        entity=value,
                    )
                )

        for parameter in sorted(set(parameters) - set(expected_parameters)):
            violations.append(
                _violation(
                    step_num,
                    "unexpected_parameter",
                    f"动作包含技能契约未声明的参数 {parameter}",
                    skill=skill,
                    parameter=parameter,
                )
            )

        if spec.can_move_robot:
            target = spec.location_value(
                {"skill": skill, "parameters": parameters}
            )
            if target and target in environment:
                if is_room_level_node(target, environment):
                    violations.append(
                        _violation(
                            step_num,
                            "room_level_navigation",
                            "NavigateTo 目标必须是具体交互节点，不能是房间级节点",
                            skill=skill,
                            entity=target,
                        )
                    )
                elif target != current_location:
                    current_location = target

    return violations


def build_legality_repair_prompt(
    *,
    intent: str,
    todo_list: list,
    violations: list[dict[str, Any]],
    environment: dict[str, Any],
) -> str:
    payload = {
        "intent": intent,
        "previous_todo_list": todo_list,
        "all_violations": violations,
        "available_entity_ids": sorted(str(name) for name in environment),
    }
    return (
        "你是规划合法性修复器。下面列出了当前 todo_list 中发现的全部动作和实体错误。"
        "请一次性修复所有错误并重新生成完整 todo_list，不要保留任何已报告的非法动作。"
        "只能使用附加的可用技能契约和 available_entity_ids 中的实体。"
        "只输出 JSON：{\"todo_list\": [{\"execution\": {\"skill\": \"...\", "
        "\"parameters\": {}}}]}。\n\n"
        + json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    )


def _entity_parameters(spec) -> list[str]:
    names = []
    for name in (
        spec.target_param,
        spec.item_param,
        spec.destination_param,
        spec.location_param,
        spec.device_param,
    ):
        if name and name not in names:
            names.append(name)
    return names


def _violation(step: Any, code: str, message: str, **details: Any) -> dict[str, Any]:
    return {
        "step": step,
        "code": code,
        "message": message,
        **copy.deepcopy(details),
    }


__all__ = ["build_legality_repair_prompt", "collect_todo_violations"]
