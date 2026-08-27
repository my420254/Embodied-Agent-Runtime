from __future__ import annotations

import copy
import importlib
from typing import Any

from graph.planning.config import sda_max_backtrack_depth, sda_max_subtree_actions
from graph.planning.evaluation.validation.debug_events import sync_debug_event_aliases
from graph.planning.evaluation.validation.failure import report_audit_failure
from graph.planning.normalizer import reindex_todo_steps
from graph.planning.evaluation.validation.sandbox_validation_types import SandboxValidationContext, TodoValidationResult
from graph.planning.evaluation.validation.trajectory import step_number
from re_trac import build_failed_step_retrac_state


def _select_sda_repair_checkpoint(**kwargs: Any) -> dict[str, Any]:
    module = importlib.import_module(
        "graph.planning.evaluation.repair_strategies.sda.state_dependency"
    )
    return module.select_repair_checkpoint(**kwargs)


def generate_adaptive_subtree(**kwargs: Any) -> dict[str, Any]:
    """精简展示版不再保留 legacy 顶层 SDA 自适应子树生成器。

    默认修复策略是 ReTrac，因此主流程不会进入这里。若后续要重新启用
    `repair_strategy=sda`，应把自适应子树生成能力迁移到
    `graph.planning.evaluation.repair_strategies.sda` 内部，而不是恢复顶层
    `SDA/` 目录。
    """

    del kwargs
    return {
        "success": False,
        "actions": [],
        "failure_reason": "SDA adaptive subtree generator is not included in the slim interview runtime.",
    }


def validate_todo_steps(
    *,
    todo_list: list[dict[str, Any]],
    context: SandboxValidationContext,
    sim_env: dict[str, dict[str, Any]],
    sim_robot: dict[str, Any],
    sandbox_start_env: dict[str, dict[str, Any]],
    sandbox_start_robot: dict[str, Any],
    validated_steps: list[dict[str, Any]],
    trajectory_records: list[dict[str, Any]],
) -> TodoValidationResult:
    sda_success_state: dict[str, Any] | None = None
    for step in todo_list:
        execution = step.get("execution", {})
        if not execution or not isinstance(execution, dict):
            return TodoValidationResult(
                todo_list=todo_list,
                validated_steps=validated_steps,
                sim_env=sim_env,
                sim_robot=sim_robot,
                failure_payload=report_audit_failure(
                    step,
                    "输出格式异常",
                    "必须提供符合规范的 execution 字典",
                    context.intent,
                    context.memory,
                    context.iters,
                    validated_steps,
                    sim_env,
                    sim_robot,
                    context.injected_rule_ids,
                    context.max_iterations,
                    context.feature_flags,
                    attempted_steps=todo_list,
                    debug_events=context.debug_events,
                ),
            )

        act = execution.get("skill", "")
        params = execution.get("parameters", {})
        snap_env, snap_robot = copy.deepcopy(sim_env), copy.deepcopy(sim_robot)
        ok, issue_type, fix = context.apply_action(sim_env, sim_robot, act, params)
        context.debug_events.append(
            {
                "layer": "sandbox",
                "type": "step_check",
                "skill": act,
                "parameters": copy.deepcopy(params),
                "ok": bool(ok),
                "issue_type": issue_type,
                "fix": fix,
            }
        )
        if not ok:
            sda_checkpoint = None
            if context.sda_active:
                try:
                    sda_checkpoint = _select_sda_repair_checkpoint(
                        todo_list=todo_list,
                        validated_steps=validated_steps,
                        failed_step=step,
                        issue_type=issue_type,
                        fix_advice=fix,
                        failure_env=snap_env,
                        failure_robot=snap_robot,
                        trajectory_records=trajectory_records,
                        sandbox_start_env=sandbox_start_env,
                        sandbox_start_robot=sandbox_start_robot,
                        failure_kind="sandbox_failure",
                        max_backtrack_depth=sda_max_backtrack_depth(),
                    )
                    discarded_suffix = [
                        copy.deepcopy(item)
                        for item in (todo_list or [])
                        if isinstance(item, dict)
                        and (step_number(item) or 0) >= int(sda_checkpoint.get("rollback_step_num") or 0)
                    ]
                    adaptive_subtree = generate_adaptive_subtree(
                        discarded_suffix=discarded_suffix,
                        checkpoint_env=sda_checkpoint["checkpoint_env"],
                        checkpoint_robot=sda_checkpoint["checkpoint_robot"],
                        apply_action=lambda env, robot, skill, parameters: context.apply_action(
                            env,
                            robot,
                            skill,
                            parameters,
                        ),
                        max_actions=sda_max_subtree_actions(),
                    )
                    sda_checkpoint["sda_state"]["adaptive_subtree"] = copy.deepcopy(
                        {
                            key: value
                            for key, value in adaptive_subtree.items()
                            if key not in {"final_env", "final_robot"}
                        }
                    )
                    if adaptive_subtree.get("success"):
                        repaired_todo = reindex_todo_steps(
                            list(sda_checkpoint["validated_steps"] or [])
                            + list(adaptive_subtree.get("actions", []) or [])
                        )
                        todo_list = repaired_todo
                        validated_steps = repaired_todo
                        sim_env = copy.deepcopy(adaptive_subtree.get("final_env") or sim_env)
                        sim_robot = copy.deepcopy(adaptive_subtree.get("final_robot") or sim_robot)
                        context.debug_events.append(
                            {
                                "layer": "sda",
                                "type": "repair_success",
                                "failed_step": step.get("step"),
                                "rollback_step_num": sda_checkpoint.get("rollback_step_num"),
                                "generated_action_count": len(adaptive_subtree.get("actions", []) or []),
                            }
                        )
                        sda_success_state = copy.deepcopy(sda_checkpoint.get("sda_state", {}))
                        break
                    context.debug_events.append(
                        {
                            "layer": "sda",
                            "type": "repair_failed",
                            "failed_step": step.get("step"),
                            "rollback_step_num": sda_checkpoint.get("rollback_step_num"),
                            "failure_reason": adaptive_subtree.get("failure_reason", ""),
                        }
                    )
                except Exception as exc:
                    context.debug_events.append(
                        {
                            "layer": "sda",
                            "type": "repair_exception",
                            "failed_step": step.get("step"),
                            "error": repr(exc),
                        }
                    )
            failed = report_audit_failure(
                step,
                issue_type,
                fix,
                context.intent,
                context.memory,
                context.iters,
                validated_steps,
                snap_env,
                snap_robot,
                context.injected_rule_ids,
                context.max_iterations,
                context.feature_flags,
                attempted_steps=todo_list,
                debug_events=context.debug_events,
                re_trac_state=build_failed_step_retrac_state(
                    failure_kind="sandbox_intercept",
                    issue_type=issue_type,
                    issue=f"第 {step.get('step', '?')} 步物理拦截: {issue_type}",
                    fix_advice=fix,
                    todo_list=todo_list,
                    validated_steps=validated_steps,
                    failed_step=step,
                    sim_env=snap_env,
                    sim_robot=snap_robot,
                )
                if context.retrac_active
                else {},
            )
            if sda_checkpoint:
                failed["sda_state"] = copy.deepcopy(sda_checkpoint.get("sda_state", {}))
            return TodoValidationResult(
                todo_list=todo_list,
                validated_steps=validated_steps,
                sim_env=sim_env,
                sim_robot=sim_robot,
                sda_success_state=sda_success_state,
                failure_payload=sync_debug_event_aliases(failed),
            )
        validated_steps.append(step)
        trajectory_records.append(
            {
                "step": copy.deepcopy(step),
                "before_env": snap_env,
                "before_robot": snap_robot,
                "after_env": copy.deepcopy(sim_env),
                "after_robot": copy.deepcopy(sim_robot),
            }
        )
    return TodoValidationResult(
        todo_list=todo_list,
        validated_steps=validated_steps,
        sim_env=sim_env,
        sim_robot=sim_robot,
        sda_success_state=sda_success_state,
    )
