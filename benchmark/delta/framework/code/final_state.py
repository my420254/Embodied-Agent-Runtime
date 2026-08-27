from __future__ import annotations

from typing import Any

from benchmark.framework_final_state import build_local_compare


def compare_final_state(packet: dict[str, Any]) -> dict[str, Any]:
    task_context = packet.get("task_context", {})
    task_context = task_context if isinstance(task_context, dict) else {}
    goal_projection = {
        "instruction": task_context.get("instruction", ""),
        "domain": task_context.get("domain", ""),
        "visible_delta_predicates": task_context.get("delta_env_state_predicates", []),
        "loadable_containers": task_context.get("loadable_containers", []),
    }
    return build_local_compare(
        packet,
        benchmark="DELTA",
        environment_format="DELTA scene_graph 转成 benchmark 本地扁平环境，保留 delta_predicate/delta_affordance 属性",
        action_format="DELTA 官方原生动作 JSON 对象",
        official_evaluator="planning 结束后调用 DELTA PDDL/VAL；评测答案字段不进入 understanding/planning/final_state audit",
        task_context_fields=[
            "dataset",
            "task_name",
            "domain",
            "instruction",
            "scene_graph_cache_path",
            "delta_env_state_predicates",
            "delta_accessible_items",
            "loadable_containers",
            "task_environment_mode",
        ],
        goal_projection=goal_projection,
        fairness_notes=[
            "本 comparer 不读取评测答案字段、官方目标字段或参考代价字段。",
            "DELTA 官方目标只在 planning 结束后的官方评测中使用。",
        ],
    )


__all__ = ["compare_final_state"]
