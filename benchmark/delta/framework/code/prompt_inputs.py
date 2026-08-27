from __future__ import annotations

import copy
import json
from typing import Any

from graph.planning.prompt_inputs import (
    build_planning_main_inputs as _build_core_planning_main_inputs,
    build_planning_repair_inputs,
)
from graph.understanding.prompt_inputs import (
    build_understanding_system_inputs as _build_core_understanding_system_inputs,
)

from benchmark.delta.framework.code.native_actions import (
    allowed_delta_actions_for_domain,
    delta_action_contract_lines,
)
from skills.loader import load_enabled_skill_names, load_skill_spec


def _model_visible_task_context(task_context: Any) -> dict[str, Any]:
    """Keep DELTA source action definitions out of all model-facing prompts.

    DELTA's raw ``add_act`` text is retained in the case source for audit, but
    skills are the only model-facing action contract. This prevents a second
    parameter schema from competing with the PDDL-aligned skill prompts.
    """
    if not isinstance(task_context, dict):
        return {}
    visible = copy.deepcopy(task_context)
    visible.pop("delta_action_knowledge", None)
    return visible


def _json_pretty(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def build_understanding_system_inputs(
    context: dict[str, Any],
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    variables = _build_core_understanding_system_inputs(context, result)
    runtime_options = context.get("runtime_options", {})
    task_context = runtime_options.get("task_context", {}) if isinstance(runtime_options, dict) else {}
    variables["task_context_json"] = _json_pretty(_model_visible_task_context(task_context))
    return variables


def _delta_item_location_table(current_env: Any) -> str:
    """从官方场景图解析出的环境 JSON 提取物体 -> 所在房间清单。

    只呈现官方环境已有的真实位置信息，不新增任何任务知识。
    """
    if not isinstance(current_env, dict):
        return "（无）"
    lines: list[str] = []
    for name, node in sorted(current_env.items()):
        if not isinstance(node, dict):
            continue
        if str(node.get("type") or "").lower() == "room":
            continue
        parent = str(node.get("direct_parent") or "未知")
        lines.append(f"- {name}: {parent}")
    return "\n".join(lines) or "（无）"


def _domain_from_task_context(task_context: Any) -> str:
    return str((task_context if isinstance(task_context, dict) else {}).get("domain") or "").strip().lower()


def _delta_enabled_actions(domain: str) -> tuple[str, ...]:
    enabled = set(load_enabled_skill_names())
    return tuple(action for action in allowed_delta_actions_for_domain(domain) if action in enabled)


def _delta_action_contract(domain: str, allowed: tuple[str, ...]) -> str:
    return "\n".join(delta_action_contract_lines(domain, allowed_actions=allowed))


def _delta_skills_markdown(allowed: tuple[str, ...]) -> str:
    blocks: list[str] = []
    for action in allowed:
        spec = load_skill_spec(action)
        if spec is None:
            blocks.append(f"【系统警报：DELTA 技能 {action} 未在 settings.skills.root 中定义】")
            continue
        prompt_path = spec.path / spec.prompt
        try:
            blocks.append(prompt_path.read_text(encoding="utf-8"))
        except OSError as exc:
            blocks.append(f"【系统警报：读取 DELTA 技能 {action} 说明失败: {exc}】")
    return "\n\n".join(blocks)


def build_planning_main_inputs(*, task_context: dict, **kwargs: Any):
    variables, injected_rule_ids = _build_core_planning_main_inputs(task_context=task_context, **kwargs)
    variables["task_context_json"] = _json_pretty(_model_visible_task_context(task_context))
    domain = _domain_from_task_context(task_context)
    allowed = _delta_enabled_actions(domain)
    skill_closure = kwargs.get("skill_closure")
    if isinstance(skill_closure, list) and skill_closure:
        selected = {str(name) for name in skill_closure if name}
        allowed = tuple(action for action in allowed if action in selected)
    current_env = kwargs.get("current_env")
    item_location_table = _delta_item_location_table(current_env)
    neighbors = (task_context if isinstance(task_context, dict) else {}).get("delta_room_neighbors")
    if isinstance(neighbors, dict) and neighbors:
        neighbor_table = "\n".join(
            f"- {room}: {', '.join(sorted(values))}"
            for room, values in sorted(neighbors.items())
            if isinstance(values, (list, tuple, set)) and values
        )
    else:
        neighbor_table = "（无）"
    add_obj_types = (task_context if isinstance(task_context, dict) else {}).get("delta_add_obj_types") or []
    variables.update(
        {
            "delta_allowed_actions": ", ".join(allowed),
            "delta_action_contract": _delta_action_contract(domain, allowed),
            "skills_markdown": _delta_skills_markdown(allowed),
            "delta_room_neighbors_table": neighbor_table,
            "delta_item_location_table": item_location_table,
            "delta_add_obj_types": ", ".join(str(name) for name in add_obj_types) or "（无）",
        }
    )
    return variables, injected_rule_ids


__all__ = [
    "build_understanding_system_inputs",
    "build_planning_main_inputs",
    "build_planning_repair_inputs",
]
