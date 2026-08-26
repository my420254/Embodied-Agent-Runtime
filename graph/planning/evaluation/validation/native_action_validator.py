from __future__ import annotations

import copy
from typing import Any

from config.module_loader import resolve_callable
from graph.planning.config import sda_max_backtrack_depth
from graph.planning.evaluation.validation.debug_events import sync_debug_event_aliases
from graph.planning.evaluation.validation.failure import report_audit_failure
from graph.planning.evaluation.validation.sandbox_validation_types import SandboxValidationContext
from graph.planning.evaluation.validation.trajectory import step_number
from graph.state import PlanningState
from re_trac import build_failed_step_retrac_state
from SDA import select_repair_checkpoint


def validate_todo_actions(
    *,
    state: PlanningState,
    todo_list: list[dict[str, Any]],
    context: SandboxValidationContext,
    sim_env: dict[str, dict[str, Any]],
    sim_robot: dict[str, Any],
    sandbox_start_env: dict[str, dict[str, Any]],
    sandbox_start_robot: dict[str, Any],
    validated_steps: list[dict[str, Any]],
    validated_todo_actions: list[dict[str, Any]],
    validated_audit_steps: list[dict[str, Any]],
    trajectory_records: list[dict[str, Any]],
) -> dict[str, Any] | None:
    todo_step_to_skill = resolve_callable(
        str(state.get("todo_step_adapter_path") or ""),
        required=False,
        label="todo_step_adapter",
    )
    if todo_step_to_skill is None:
        return report_audit_failure(
            {},
            "序列验证失败",
            "当前 todo_list schema 未注册沙盒审计适配器",
            context.intent,
            context.memory,
            context.iters,
            [],
            sim_env,
            sim_robot,
            context.injected_rule_ids,
            context.max_iterations,
            context.feature_flags,
            attempted_steps=todo_list,
            debug_events=context.debug_events,
        )

    for todo_step in todo_list:
        try:
            act, params = todo_step_to_skill(todo_step, sim_robot)
        except Exception as exc:
            failed = report_audit_failure(
                todo_step,
                "todo_list 动作解析失败",
                f"无法解析该动作的技能参数: {exc}",
                context.intent,
                context.memory,
                context.iters,
                validated_steps,
                sim_env,
                sim_robot,
                context.injected_rule_ids,
                context.max_iterations,
                context.feature_flags,
                debug_events=context.debug_events,
                validated_todo_actions=validated_todo_actions,
                todo_checkpoint_env=sim_env,
                todo_checkpoint_robot=sim_robot,
                attempted_steps=todo_list,
            )
            return sync_debug_event_aliases(failed)

        audit_step = {
            **copy.deepcopy(todo_step),
            "execution": {"skill": act, "parameters": copy.deepcopy(params)},
        }
        current_audit_plan = validated_audit_steps + [copy.deepcopy(audit_step)]
        snap_env, snap_robot = copy.deepcopy(sim_env), copy.deepcopy(sim_robot)
        ok, issue_type, fix = context.apply_action(sim_env, sim_robot, act, params)
        context.debug_events.append(
            {
                "layer": "sandbox",
                "type": "step_check",
                "skill": act,
                "parameters": copy.deepcopy(params),
                "todo_step": copy.deepcopy(todo_step),
                "ok": bool(ok),
                "issue_type": issue_type,
                "fix": fix,
            }
        )
        if not ok:
            sda_checkpoint = None
            sda_validated_todo_prefix: list[dict[str, Any]] = []
            if context.sda_active:
                try:
                    sda_checkpoint = select_repair_checkpoint(
                        todo_list=current_audit_plan,
                        validated_steps=validated_audit_steps,
                        failed_step=audit_step,
                        issue_type=issue_type,
                        fix_advice=fix,
                        failure_env=snap_env,
                        failure_robot=snap_robot,
                        trajectory_records=trajectory_records,
                        sandbox_start_env=sandbox_start_env,
                        sandbox_start_robot=sandbox_start_robot,
                        failure_kind="todo_schema_sandbox_failure",
                        max_backtrack_depth=sda_max_backtrack_depth(),
                    )
                    rollback_step_num = int(sda_checkpoint.get("rollback_step_num") or audit_step.get("step") or 1)
                    sda_validated_todo_prefix = [
                        copy.deepcopy(item)
                        for item in (todo_list or [])
                        if isinstance(item, dict) and (step_number(item) or 0) < rollback_step_num
                    ]
                    sda_checkpoint["sda_state"]["todo_trajectory"] = {
                        "original_todo_list": copy.deepcopy(todo_list or []),
                        "validated_prefix": copy.deepcopy(sda_validated_todo_prefix),
                        "next_step_num": len(sda_validated_todo_prefix) + 1,
                    }
                    context.debug_events.append(
                        {
                            "layer": "sda",
                            "type": "todo_checkpoint_selected",
                            "failed_step": audit_step.get("step"),
                            "rollback_step_num": rollback_step_num,
                        }
                    )
                except Exception as exc:
                    context.debug_events.append(
                        {
                            "layer": "sda",
                            "type": "todo_checkpoint_exception",
                            "failed_step": audit_step.get("step"),
                            "error": repr(exc),
                        }
                    )
            failed = report_audit_failure(
                audit_step,
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
                debug_events=context.debug_events,
                validated_todo_actions=validated_todo_actions,
                todo_checkpoint_env=snap_env,
                todo_checkpoint_robot=snap_robot,
                attempted_steps=todo_list,
                re_trac_state=build_failed_step_retrac_state(
                    failure_kind="sandbox_intercept",
                    issue_type=issue_type,
                    issue=f"第 {audit_step.get('step', '?')} 步物理拦截: {issue_type}",
                    fix_advice=fix,
                    todo_list=current_audit_plan,
                    validated_steps=validated_audit_steps,
                    failed_step=audit_step,
                    sim_env=snap_env,
                    sim_robot=snap_robot,
                    validated_todo_actions=validated_todo_actions,
                    failed_todo_step=todo_step,
                )
                if context.retrac_active
                else {},
            )
            if sda_checkpoint:
                failed["sda_state"] = copy.deepcopy(sda_checkpoint.get("sda_state", {}))
                failed["validated_todo_actions"] = copy.deepcopy(sda_validated_todo_prefix)
                failed["todo_checkpoint_env"] = copy.deepcopy(sda_checkpoint.get("checkpoint_env", {}))
                failed["todo_checkpoint_robot"] = copy.deepcopy(sda_checkpoint.get("checkpoint_robot", {}))
            return sync_debug_event_aliases(failed)
        validated_todo_actions.append(copy.deepcopy(todo_step))
        validated_audit_steps.append(copy.deepcopy(audit_step))
        trajectory_records.append(
            {
                "step": copy.deepcopy(audit_step),
                "before_env": snap_env,
                "before_robot": snap_robot,
                "after_env": copy.deepcopy(sim_env),
                "after_robot": copy.deepcopy(sim_robot),
            }
        )
    plan_validator = resolve_callable(
        str(state.get("todo_list_validator_path") or ""),
        required=False,
        label="todo_list_validator",
    )
    if plan_validator is not None:
        result = plan_validator(
            state=state,
            todo_list=copy.deepcopy(todo_list),
            validated_todo_actions=copy.deepcopy(validated_todo_actions),
            trajectory_records=copy.deepcopy(trajectory_records),
            initial_env=copy.deepcopy(sandbox_start_env),
            initial_robot=copy.deepcopy(sandbox_start_robot),
            final_env=copy.deepcopy(sim_env),
            final_robot=copy.deepcopy(sim_robot),
        )
        if isinstance(result, dict) and result.get("is_passed") is False:
            issue_type = str(result.get("issue") or "todo_list 时序审计失败")
            fix = str(result.get("fix_advice") or "重新生成满足当前 benchmark 动作契约的完整计划")
            failed = report_audit_failure(
                {
                    "step": result.get("step") or "?",
                    "execution": {
                        "skill": "GOAL_CHECK",
                        "parameters": copy.deepcopy(result.get("details", {})),
                    },
                },
                issue_type,
                fix,
                context.intent,
                context.memory,
                context.iters,
                [],
                sandbox_start_env,
                sandbox_start_robot,
                context.injected_rule_ids,
                context.max_iterations,
                context.feature_flags,
                debug_events=context.debug_events
                + [
                    {
                        "layer": "todo_list_validator",
                        "type": "rejected",
                        "result": copy.deepcopy(result),
                    }
                ],
                validated_todo_actions=[],
                todo_checkpoint_env=sandbox_start_env,
                todo_checkpoint_robot=sandbox_start_robot,
                attempted_steps=todo_list,
            )
            return sync_debug_event_aliases(failed)
    return None
