from __future__ import annotations

import json
from importlib import import_module
from typing import Any

from skills.loader import load_enabled_skill_specs
from domain.scene import flatten_scene


def _understanding_node():
    return import_module("graph.understanding.node")


def _feature_flags(context: dict[str, Any]) -> dict[str, Any]:
    runtime_options = context.get("runtime_options", {}) or {}
    flags = (
        runtime_options.get("feature_flags")
        if isinstance(runtime_options, dict)
        else {}
    )
    return flags if isinstance(flags, dict) else {}


def _scene_entities_json(context: dict[str, Any]) -> str:
    return json.dumps(list(context.get("scene_entities", [])), ensure_ascii=False)


def _json_pretty(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def _runtime_options(context: dict[str, Any]) -> dict[str, Any]:
    options = context.get("runtime_options", {})
    return options if isinstance(options, dict) else {}


def _build_environment_closure(context: dict[str, Any]) -> list[dict[str, Any]]:
    """从 understanding context 的扁平环境构建“环境闭包”：
    对每个实体给出 位置(容器)/状态/是否在容器内/容器开闭，供理解层判断
    是否需要 Open/Close 等使能动作（解决“工具锁在关闭容器内却漏选 Open”的问题）。

    返回 [{name, location, container_open, states, is_container, relation}]。
    环境缺失或异常时返回 []（调用方回退到仅实体名，保持向后兼容）。
    """
    options = context.get("runtime_options")
    options = options if isinstance(options, dict) else {}
    environment = options.get("environment")
    if not isinstance(environment, dict):
        environment = context.get("environment")
    if not isinstance(environment, dict):
        environment = context.get("scene")
    if not isinstance(environment, dict) or not environment:
        return []
    is_flat = any(
        isinstance(info, dict)
        and any(key in info for key in ("direct_parent", "full_path", "is_container"))
        for info in environment.values()
    )
    if not is_flat:
        environment = flatten_scene(environment)
    closure: list[dict[str, Any]] = []
    try:
        for name, info in environment.items():
            if not isinstance(info, dict):
                continue
            parent = str(info.get("direct_parent") or "")
            states = info.get("states")
            states = states if isinstance(states, dict) else {}
            parent_info = environment.get(parent) if parent else None
            parent_states = (
                parent_info.get("states") if isinstance(parent_info, dict) else {}
            )
            parent_states = parent_states if isinstance(parent_states, dict) else {}
            is_open = parent_states.get("isOpen")
            # 只有父容器明确有 isOpen 状态时才给出开闭判定；无 isOpen 状态（台面/地板等）视为不适用(None)
            closure.append(
                {
                    "name": name,
                    "location": parent or "未知环境",
                    "container_open": is_open if is_open is not None else None,
                    "container_type": str(parent_info.get("type") or "")
                    if isinstance(parent_info, dict)
                    else "",
                    "states": states,
                    "is_container": bool(info.get("is_container")),
                    "relation": str(info.get("direct_relation") or ""),
                }
            )
    except Exception as exc:
        print(f"[理解层] 环境闭包构建失败，回退仅实体名: {exc}")
        return []
    closure.sort(key=lambda item: str(item.get("name", "")))
    return closure


def environment_closure_json(context: dict[str, Any]) -> str:
    closure = _build_environment_closure(context)
    if not closure:
        return ""
    return json.dumps(closure, ensure_ascii=False, indent=2, default=str)


def _available_skills_json() -> str:
    skills = []
    try:
        specs = load_enabled_skill_specs()
    except Exception:
        specs = []
    for spec in specs:
        skills.append(
            {
                "name": spec.name,
                "description": spec.description,
                "planning_contract": dict(getattr(spec, "planning_contract", {}) or {}),
            }
        )
    return json.dumps(skills, ensure_ascii=False, indent=2, default=str)


def build_understanding_system_inputs(
    context: dict[str, Any], result: dict[str, Any] | None = None
) -> dict[str, Any]:
    node = _understanding_node()
    flags = _feature_flags(context)
    playbook = (
        ""
        if not bool(flags.get("playbook_retrieval", True))
        else node.load_understanding_playbook()
    )
    options = _runtime_options(context)
    task_context = options.get("task_context", {})
    return {
        "valid_names_json": _scene_entities_json(context),
        "system_rules": node.load_system_rules(),
        "playbook": playbook,
        "task_context_json": _json_pretty(
            task_context if isinstance(task_context, dict) else {}
        ),
        "environment_closure_json": environment_closure_json(context),
        "available_skills_json": _available_skills_json(),
    }


UNDERSTANDING_PROMPT_INPUT_BUILDERS = {
    "understanding.system": build_understanding_system_inputs,
}
