from __future__ import annotations

import copy

from ..contracts import RepairAssembly, RepairDiagnosis


def assemble_sda_plan(
    diagnosis: RepairDiagnosis,
    generated_todo_list: list[dict],
) -> RepairAssembly:
    if not generated_todo_list:
        return RepairAssembly(
            strategy_name=diagnosis.strategy_name,
            success=False,
            error="SDA 未生成可重组的因果后缀",
        )
    prefix = diagnosis.merge_context.get("validated_prefix", [])
    todo_list = _reindex(prefix + generated_todo_list)
    return RepairAssembly(
        strategy_name=diagnosis.strategy_name,
        success=True,
        todo_list=todo_list,
        step_provenance=(
            [
                {
                    "source": "original",
                    "original_step": step.get("step"),
                }
                for step in prefix
                if isinstance(step, dict)
            ]
            + [
                {
                    "source": "generated",
                    "generated_action_index": index,
                }
                for index, step in enumerate(generated_todo_list, start=1)
                if isinstance(step, dict)
            ]
        ),
    )


def _reindex(steps: list[dict]) -> list[dict]:
    return [
        {**copy.deepcopy(step), "step": index}
        for index, step in enumerate(steps, start=1)
        if isinstance(step, dict)
    ]


__all__ = ["assemble_sda_plan"]
