from __future__ import annotations

import json
from importlib import import_module
from typing import Any

from config.llms import llm_trace_context
from config.module_loader import call_configured_module_function
from domain.task_environment import build_task_environment_closure
from skills.loader import load_enabled_skill_names, load_enabled_skill_specs

from .base import FeatureContext, FeatureResult

try:
    from langchain_core.messages import SystemMessage
except Exception:  # pragma: no cover - fallback for lean test environments
    class _Message:  # type: ignore[no-redef]
        def __init__(self, content: str):
            self.content = content

    class SystemMessage(_Message):
        pass


def _understanding_node():
    return import_module("graph.understanding.node")


def _parse_llm_json(content: str) -> dict:
    node = _understanding_node()
    try:
        parsed = node.parse_json_from_llm(content, fallback={})
    except TypeError:
        parsed = node.parse_json_from_llm(content)
    except Exception:
        parsed = {}
    return parsed if isinstance(parsed, dict) else {}


def _available_skills_json() -> str:
    """给第二次调用提供全部启用的 skill 名称+描述（供模型准确选择）。"""
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
            }
        )
    return json.dumps(skills, ensure_ascii=False, indent=2, default=str)


def _environment_closure_from_context(context: FeatureContext) -> list[dict]:
    """从 context 构建“环境闭包”（供第二次调用选 skill 时判断使能动作）。

    优先复用 domain 的通用闭包逻辑 build_task_environment_closure：
    根据第一次调用产出的实体名（structured_task/relevant_item_names），从全量场景中
    查出任务闭包环境（实体 + 父路径 + 容器 descendants + 状态）——这正是 planning
    使用的同一份闭包语义，提前到 skill 选择阶段复用，保证“选 skill”和“规划”看到
    一致的环境视图。

    若场景不可用（如纯交互模式），回退到从扁平环境全量提取的简化闭包。
    """
    options = context.get("runtime_options", {})
    options = options if isinstance(options, dict) else {}
    environment = options.get("environment")
    if not isinstance(environment, dict):
        environment = context.get("environment")
    if not isinstance(environment, dict):
        environment = context.get("scene")

    # 优先走完整闭包逻辑：按实体名查任务环境闭包
    try:
        structured = context.get("_closure_structured_task") or {}
        if isinstance(structured, dict) and structured:
            scene_source = context.get("scene")
            if not isinstance(scene_source, dict):
                scene_source = options.get("scene")
            if not isinstance(scene_source, dict):
                scene_source = environment
            if isinstance(scene_source, dict) and scene_source:
                closure_env = build_task_environment_closure(
                    scene_source,
                    structured,
                    relevant_item_names=context.get("_closure_relevant_names"),
                )
                if isinstance(closure_env, dict) and closure_env:
                    return _format_closure_entries(closure_env)
    except Exception:
        pass

    # 回退：扁平环境全量提取
    if not isinstance(environment, dict) or not environment:
        return []
    try:
        return _format_closure_entries(environment)
    except Exception:
        return []


def _format_closure_entries(environment: dict) -> list[dict]:
    closure: list[dict[str, Any]] = []
    for name, info in environment.items():
        if not isinstance(info, dict):
            continue
        parent = str(info.get("direct_parent") or "")
        states = info.get("states")
        states = states if isinstance(states, dict) else {}
        parent_info = environment.get(parent) if parent else None
        parent_states = parent_info.get("states") if isinstance(parent_info, dict) else {}
        parent_states = parent_states if isinstance(parent_states, dict) else {}
        is_open = parent_states.get("isOpen")
        closure.append(
            {
                "name": name,
                "location": parent or "未知环境",
                "container_open": is_open if is_open is not None else None,
                "container_type": str(parent_info.get("type") or "") if isinstance(parent_info, dict) else "",
                "states": states,
                "is_container": bool(info.get("is_container")),
                "relation": str(info.get("direct_relation") or ""),
            }
        )
    closure.sort(key=lambda item: str(item.get("name", "")))
    return closure


def _build_prompt_inputs(context: FeatureContext, result: FeatureResult) -> dict:
    """组装第二次调用输入：任务指令 + 环境闭包 + 全部 skill 描述。"""
    task = str(context.get("task", "") or "")
    options = context.get("runtime_options", {})
    options = options if isinstance(options, dict) else {}
    original = str(options.get("original_instruction") or task)
    # 第一次调用已产出的结构化任务（实体等），作为 grounding 和闭包查询依据
    structured = result.get("structured_task", {})
    relevant_names = result.get("relevant_item_names", [])
    context["_closure_structured_task"] = structured
    context["_closure_relevant_names"] = (
        [str(name) for name in relevant_names if str(name or "").strip()]
        if isinstance(relevant_names, list)
        else []
    )
    closure = _environment_closure_from_context(context)
    return {
        "task_instruction": original or task,
        "task_context_json": json.dumps(options.get("task_context", {}), ensure_ascii=False, indent=2, default=str),
        "environment_closure_json": json.dumps(closure, ensure_ascii=False, indent=2, default=str) if closure else "",
        "structured_task_json": json.dumps(structured, ensure_ascii=False, indent=2, default=str),
        "available_skills_json": _available_skills_json(),
    }


def _always_include(context: FeatureContext) -> list[str]:
    settings = context.get("feature_settings", {})
    settings = settings if isinstance(settings, dict) else {}
    closure_settings = settings.get("skill_closure", {})
    closure_settings = closure_settings if isinstance(closure_settings, dict) else {}
    names = closure_settings.get("always_include", [])
    if not isinstance(names, list):
        return []
    return [str(name).strip() for name in names if str(name).strip()]


def _closure_settings(context: FeatureContext) -> dict:
    settings = context.get("feature_settings", {})
    settings = settings if isinstance(settings, dict) else {}
    closure_settings = settings.get("skill_closure", {})
    return closure_settings if isinstance(closure_settings, dict) else {}


def _validate_selection(
    context: FeatureContext,
    *,
    selected: list[str],
    prompt_inputs: dict,
) -> dict:
    settings = _closure_settings(context)
    validator_module = str(settings.get("validator_module") or "").strip()
    if not validator_module:
        return {"valid": True, "issue": ""}
    try:
        verdict = call_configured_module_function(
            ("understanding", "features", "settings", "skill_closure", "validator_module"),
            validator_module,
            "validate_selection",
            selected=selected,
            environment_closure_json=prompt_inputs.get("environment_closure_json", ""),
            task_instruction=prompt_inputs.get("task_instruction", ""),
            task_context_json=prompt_inputs.get("task_context_json", ""),
            label="skill closure validator",
        )
    except Exception as exc:
        # A configured validator is part of the benchmark contract. Fail closed so
        # experiments cannot silently continue with an unchecked skill closure.
        return {"valid": False, "issue": f"技能闭包校验器执行失败: {exc}"}
    if not isinstance(verdict, dict):
        return {"valid": False, "issue": "技能闭包校验器返回格式无效"}
    return {
        "valid": bool(verdict.get("valid", False)),
        "issue": str(verdict.get("issue") or "技能闭包未覆盖任务所需的状态前提"),
    }


def filter_skill_selection(
    *,
    proposed_skill_names: list[str],
    available_skill_names: list[str],
) -> list[str]:
    """按 enabled skills 过滤模型提议的 skill_closure。

    兼容两种命名格式：yaml 的 name 可能是带空格的显示名（如 "go to"），
    而 load_enabled_skill_names 返回目录名（如 "go_to"）。统一把空格↔下划线归一化后匹配，
    保证 ALFRED 等数据集的下划线 skill 名也能正确过滤。
    """
    def _norm(value: str) -> str:
        return str(value or "").strip().lower().replace("_", " ").replace("-", " ")

    ordered_available = list(dict.fromkeys(str(name) for name in available_skill_names if name))
    available_norm = {_norm(name): name for name in ordered_available}
    selected = []
    seen = set()
    for name in proposed_skill_names:
        text = str(name or "").strip()
        if not text:
            continue
        key = _norm(text)
        matched = available_norm.get(key)
        if matched is not None and matched not in seen:
            selected.append(matched)
            seen.add(matched)
    return selected


def run(context: FeatureContext, result: FeatureResult) -> FeatureResult:
    if (
        result.get("stop_pipeline")
        or result.get("is_cancel_all")
        or not result.get("is_complete")
    ):
        return {"skill_closure": []}

    node = _understanding_node()
    prompt_inputs = _build_prompt_inputs(context, result)
    system_prompt = node.render_prompt(
        "understanding.skill_selection",
        **prompt_inputs,
    )
    valid_messages = [msg for msg in context.get("messages", []) if hasattr(msg, "content")]
    if len(valid_messages) > 4:
        valid_messages = valid_messages[-4:]

    with llm_trace_context(
        process_name="understanding",
        prompt_name="understanding.skill_selection",
        call_stage="skill_closure",
    ):
        response = node.get_understanding_llm().invoke([SystemMessage(content=system_prompt)] + valid_messages)
    try:
        available = load_enabled_skill_names()
    except Exception:
        available = []

    settings = _closure_settings(context)
    max_retries = max(0, int(settings.get("max_validation_retries", 0) or 0))
    validation_history = []
    current_response = response
    selected: list[str] = []
    for attempt in range(max_retries + 1):
        parsed = _parse_llm_json(current_response.content)
        proposed = parsed.get("skill_closure", []) if isinstance(parsed, dict) else []
        if not isinstance(proposed, list):
            proposed = []
        proposed_names = [str(name) for name in proposed if name]
        for name in _always_include(context):
            if name not in proposed_names:
                proposed_names.append(name)
        selected = filter_skill_selection(
            proposed_skill_names=proposed_names,
            available_skill_names=available,
        )
        verdict = _validate_selection(
            context,
            selected=selected,
            prompt_inputs=prompt_inputs,
        )
        validation_history.append(
            {
                "attempt": attempt + 1,
                "selected": list(selected),
                "valid": bool(verdict["valid"]),
                "issue": str(verdict["issue"]),
            }
        )
        if verdict["valid"] or attempt >= max_retries:
            break
        retry_prompt = (
            f"{system_prompt}\n\n"
            "上一次输出未通过数据集动作契约校验。代码不会替你增加任何 skill；"
            "请依据可用 skill 描述重新选择完整闭包。\n"
            f"issue: {verdict['issue']}"
        )
        with llm_trace_context(
            process_name="understanding",
            prompt_name="understanding.skill_selection",
            call_stage="skill_closure_validation_retry",
        ):
            current_response = node.get_understanding_llm().invoke(
                [SystemMessage(content=retry_prompt)] + valid_messages
            )

    final_valid = bool(validation_history[-1]["valid"]) if validation_history else True
    return {
        "skill_closure": selected if final_valid else [],
        "skill_closure_valid": final_valid,
        "skill_closure_validation": validation_history,
    }


__all__ = ["filter_skill_selection", "run"]
