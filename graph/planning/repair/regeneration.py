from __future__ import annotations

import copy
from collections.abc import Callable
from typing import Any


class PlanningRegenerationError(RuntimeError):
    """Typed failure while invoking or parsing the repair planning model."""

    def __init__(self, category: str, message: str):
        super().__init__(message)
        self.category = category


def regenerate_todo_list(
    prompt: str,
    skill_profile: str | None,
    skills_markdown: str,
    *,
    planning_llm_factory: Callable[[], Any],
    parse_json: Callable[..., Any],
    ensure_shape: Callable[[dict], dict],
    message_factory: Callable[..., Any],
) -> list[dict[str, Any]]:
    """Invoke the planning model for one evaluator-requested repair plan."""

    try:
        skill_context = (
            f"\n\n【当前 profile 可用技能契约】\n{skills_markdown}"
            if skills_markdown.strip()
            else ""
        )
        request = (
            f"{prompt}{skill_context}\n\n"
            "必须只输出 JSON，不要 markdown 或解释。"
        )
        response = planning_llm_factory().invoke([message_factory(content=request)])
    except Exception as exc:
        raise PlanningRegenerationError(
            "model_invocation",
            f"规划修复模型调用失败: {exc}",
        ) from exc

    try:
        parsed = parse_json(getattr(response, "content", ""), fallback={})
    except Exception as exc:
        raise PlanningRegenerationError(
            "model_output",
            f"规划修复模型输出解析失败: {exc}",
        ) from exc

    if isinstance(parsed, dict):
        raw_steps = parsed.get("todo_list")
        if not isinstance(raw_steps, list):
            raw_steps = parsed.get("replacement_todo_list")
        if not isinstance(raw_steps, list):
            raw_steps = parsed.get("actions")
    else:
        raw_steps = parsed
    if not isinstance(raw_steps, list):
        raise PlanningRegenerationError(
            "model_output",
            "规划修复模型未返回动作数组",
        )
    generated = [
        ensure_shape(copy.deepcopy(step))
        for step in raw_steps
        if isinstance(step, dict)
    ]
    if not generated:
        raise PlanningRegenerationError(
            "model_output",
            "规划修复模型返回了空的 todo_list",
        )
    return generated


__all__ = ["PlanningRegenerationError", "regenerate_todo_list"]
