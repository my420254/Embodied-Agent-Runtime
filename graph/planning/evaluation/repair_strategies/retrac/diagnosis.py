from __future__ import annotations

import copy
import json
from dataclasses import dataclass

from ..contracts import (
    RepairAssembly,
    RepairContext,
    RepairDiagnosis,
    RepairStrategy,
)

from .assembly import assemble_retrac_plan


@dataclass(frozen=True)
class ReTracRepairStrategy(RepairStrategy):
    name: str = "retrac"

    def find_errors(self, context: RepairContext) -> RepairDiagnosis:
        steps = [
            copy.deepcopy(step)
            for step in context.todo_list
            if isinstance(step, dict)
        ]
        prompt = _build_prompt(context, steps)
        return RepairDiagnosis(
            strategy_name=self.name,
            prompt=prompt,
            merge_context={
                "validated_prefix": copy.deepcopy(context.validated_steps),
            },
        )

    def reassemble(
        self,
        diagnosis: RepairDiagnosis,
        generated_todo_list: list[dict],
    ) -> RepairAssembly:
        return assemble_retrac_plan(diagnosis, generated_todo_list)


def _build_prompt(context: RepairContext, steps: list[dict]) -> str:
    validated_prefix_end = (
        _step_number(context.validated_steps[-1])
        if context.validated_steps
        else None
    )
    payload = {
        "plan_intent": str(context.structured_task.get("intent", "") or ""),
        "complete_todo_list": steps,
        "repair_window": {
            "preserved_prefix_end_step": validated_prefix_end,
            "regenerate_start_step": _step_number(context.failed_step),
            "regenerate_end_step": _step_number(steps[-1]) if steps else None,
        },
        "error_reason": {
            "failed_step": _step_number(context.failed_step),
            "issue_type": context.issue_type,
            "fix_advice": context.fix_advice,
        },
    }
    return (
        "你是 ReTrac 后缀修复器。已验证前缀必须保持不变，丢弃失败步骤及其后的旧后缀，"
        "请依据 plan_intent、完整计划副本、repair_window 和 error_reason，"
        "只生成从 regenerate_start_step 开始的新后缀，不要重复已验证前缀。"
        "技能文档由重规划入口附加。"
        "只输出 JSON：{\"todo_list\": [...]}。\n\n"
        + json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    )


def _step_number(step: dict | None) -> int | None:
    if not isinstance(step, dict):
        return None
    try:
        return int(step.get("step"))
    except (TypeError, ValueError):
        return None


__all__ = ["ReTracRepairStrategy"]
