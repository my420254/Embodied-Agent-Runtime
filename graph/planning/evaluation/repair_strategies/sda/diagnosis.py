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

from .assembly import assemble_sda_plan
from .state_dependency import select_repair_checkpoint


@dataclass(frozen=True)
class SDARepairStrategy(RepairStrategy):
    max_backtrack_depth: int = 0
    name: str = "sda"

    def find_errors(self, context: RepairContext) -> RepairDiagnosis:
        checkpoint = select_repair_checkpoint(
            todo_list=context.todo_list,
            validated_steps=context.validated_steps,
            failed_step=context.failed_step,
            issue_type=context.issue_type,
            fix_advice=context.fix_advice,
            failure_env=context.failure_env,
            failure_robot=context.failure_robot,
            trajectory_records=context.trajectory_records,
            sandbox_start_env=context.sandbox_start_env,
            sandbox_start_robot=context.sandbox_start_robot,
            failure_kind="sandbox_failure",
            max_backtrack_depth=self.max_backtrack_depth,
            skill_profile=context.skill_profile,
            repair_catalog=context.skill_catalog,
        )
        rollback_step = int(checkpoint.get("rollback_step_num") or 0)
        steps = [
            copy.deepcopy(step)
            for step in context.todo_list
            if isinstance(step, dict)
        ]
        prompt = _build_prompt(context, checkpoint, steps)
        return RepairDiagnosis(
            strategy_name=self.name,
            prompt=prompt,
            merge_context={
                "validated_prefix": copy.deepcopy(checkpoint["validated_steps"]),
                "rollback_step": rollback_step,
            },
        )

    def reassemble(
        self,
        diagnosis: RepairDiagnosis,
        generated_todo_list: list[dict],
    ) -> RepairAssembly:
        return assemble_sda_plan(diagnosis, generated_todo_list)


def _build_prompt(
    context: RepairContext,
    checkpoint: dict,
    steps: list[dict],
) -> str:
    validated_prefix = checkpoint.get("validated_steps") or []
    root_cause_step = checkpoint.get("rollback_step_num")
    failed_step = _step_number(context.failed_step)
    validated_prefix_end = (
        _step_number(validated_prefix[-1]) if validated_prefix else None
    )
    payload = {
        "plan_intent": str(context.structured_task.get("intent", "") or ""),
        "complete_todo_list": steps,
        "repair_window": {
            "preserved_prefix_end_step": validated_prefix_end,
            "regenerate_start_step": root_cause_step,
            "regenerate_end_step": _step_number(steps[-1]) if steps else None,
        },
        "error_reason": {
            "failed_step": failed_step,
            "failed_action": copy.deepcopy(context.failed_step),
            "issue_type": context.issue_type,
            "fix_advice": context.fix_advice,
            "root_cause_step": root_cause_step,
            "root_cause_action": copy.deepcopy(
                checkpoint.get("causal_action")
                or checkpoint.get("rollback_step")
                or {}
            ),
            "causal_predicate": checkpoint.get("causal_predicate", ""),
            "causal_state_change": {
                "before": copy.deepcopy(checkpoint.get("causal_before")),
                "after": copy.deepcopy(checkpoint.get("causal_after")),
            },
            "causal_reason": checkpoint.get("reason", ""),
        },
        "repair_advice": {
            "choose_one_of": [
                {
                    "id": "replace_root_cause_action",
                    "instruction": (
                        f"原第 {root_cause_step} 步动作导致原第 {failed_step} 步不满足执行条件。"
                        f"不要原样沿用该根因动作；从第 {root_cause_step} 步生成新的动作安排，"
                        f"使后续计划满足失败动作要求：{context.fix_advice}。"
                    ),
                },
                {
                    "id": "keep_root_cause_and_restore_precondition",
                    "instruction": (
                        f"可以保留原第 {root_cause_step} 步动作，但在执行原第 {failed_step} 步动作"
                        f"或其等价动作之前，必须插入或重排动作，使其执行条件成立："
                        f"{context.fix_advice}。"
                    ),
                },
            ],
            "output_requirement": {
                "first_generated_step_replaces_original_step": root_cause_step,
                "generate_complete_suffix": True,
                "do_not_copy_invalid_suffix_unchanged": True,
            },
        },
    }
    return (
        "你是 SDA 因果后缀修复器。系统已从完整计划的实际失败轨迹中找到根本原因。"
        "保留 repair_window 指定的已验证前缀，丢弃 regenerate_start_step 及其后的旧计划，"
        "必须采用 repair_advice 中至少一种建议，从根因步骤开始重新生成完整后缀，"
        "修复 error_reason 并完成 plan_intent。"
        "不要复制已验证前缀。技能文档由重规划入口附加。"
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


__all__ = ["SDARepairStrategy"]
