from __future__ import annotations

import copy
from typing import Any

from ace.playbook import record_rule_feedback
from config.llms import get_planning_llm
from config.module_loader import resolve_module
from config.settings import get_config
from graph.planning.evaluation.audits import llm as audit_llm
from graph.planning.evaluation.validation.debug_events import sync_debug_event_aliases
from graph.planning.evaluation.validation.state_diff import (
    _build_state_audit_context,
    _build_state_diff,
)
from graph.planning.config import (
    REPAIR_STRATEGY_RETRAC,
    REPAIR_STRATEGY_SDA,
    active_repair_strategy,
    planning_feature_enabled,
)
from graph.planning.normalizer import (
    task_context as get_task_context,
    task_source_text as get_task_source_text,
)
from graph.state import PlanningState
from re_trac import (
    build_failed_step_retrac_state,
    build_failure_finding,
    build_failure_payload,
    build_state_diff_retrac_state,
)


def _same_todo_action(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_value = copy.deepcopy(left if isinstance(left, dict) else {})
    right_value = copy.deepcopy(right if isinstance(right, dict) else {})
    left_value.pop("step", None)
    right_value.pop("step", None)
    return left_value == right_value


def _state_todo_action_prefix(state: PlanningState) -> list[dict[str, Any]]:
    direct_prefix = state.get("validated_todo_actions")
    if isinstance(direct_prefix, list) and direct_prefix:
        return copy.deepcopy(direct_prefix)
    sda_state = state.get("sda_state", {})
    if not isinstance(sda_state, dict):
        return []
    for section, key in (
        ("todo_trajectory", "validated_prefix"),
        ("trajectory", "validated_todo_prefix"),
    ):
        value = sda_state.get(section, {})
        if (
            isinstance(value, dict)
            and isinstance(value.get(key), list)
            and value.get(key)
        ):
            return copy.deepcopy(value[key])
    return []


def _merge_todo_action_prefix(
    prefix: list[dict[str, Any]], plan: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    if not prefix:
        return copy.deepcopy(plan or [])
    if not plan:
        return copy.deepcopy(prefix)
    if len(plan) >= len(prefix) and all(
        _same_todo_action(plan[index], item) for index, item in enumerate(prefix)
    ):
        return copy.deepcopy(plan)
    return copy.deepcopy(prefix) + copy.deepcopy(plan)


def _state_action_plan(state: PlanningState) -> list[dict[str, Any]]:
    action_plan = state.get("todo_list")
    return copy.deepcopy(action_plan) if isinstance(action_plan, list) else []


def is_state_diff_audit_enabled(feature_flags: dict | None) -> bool:
    return planning_feature_enabled(feature_flags, "state_diff_audit", default=False)


def diff_state(
    before_env: dict[str, dict[str, Any]],
    before_robot: dict[str, Any],
    after_env: dict[str, dict[str, Any]],
    after_robot: dict[str, Any],
) -> dict[str, Any]:
    return _build_state_diff(before_env, before_robot, after_env, after_robot)


def final_state_context(state: PlanningState) -> dict[str, Any]:
    structured_task = state.get("structured_task", {})
    if not isinstance(structured_task, dict):
        structured_task = {}
    task_context = get_task_context(state)
    if not isinstance(task_context, dict):
        task_context = {}
    raw_evaluation_context = state.get("evaluation_context", {})
    evaluation_context = (
        raw_evaluation_context if isinstance(raw_evaluation_context, dict) else {}
    )
    structured_goal_state = (
        structured_task.get("goal_state")
        or structured_task.get("desired_state")
        or structured_task.get("target_state")
        or {}
    )
    structured_final_state = structured_task.get("final_state") or {}
    external_goal_state = (
        task_context.get("external_goal_state")
        or task_context.get("final_state")
        or task_context.get("goal_state")
        or task_context.get("desired_state")
        or task_context.get("target_state")
        or structured_goal_state
    )
    external_goal_text = str(
        task_context.get("external_goal_text")
        or task_context.get("goal_text")
        or task_context.get("target_state_text")
        or ""
    )
    return {
        "task_context": copy.deepcopy(task_context),
        "evaluation_context": copy.deepcopy(evaluation_context),
        "structured_goal_state": copy.deepcopy(structured_goal_state),
        "structured_final_state": copy.deepcopy(structured_final_state),
        "external_goal_state": copy.deepcopy(
            external_goal_state if external_goal_state is not None else {}
        ),
        "external_goal_text": external_goal_text,
        "has_external_goal": bool(external_goal_state)
        or bool(structured_final_state)
        or bool(external_goal_text.strip()),
    }


def build_final_state_packet(
    state: PlanningState,
    *,
    trajectory: str,
    initial_env: dict[str, dict[str, Any]],
    initial_robot: dict[str, Any],
    final_env: dict[str, dict[str, Any]],
    final_robot: dict[str, Any],
    state_diff: dict[str, Any],
) -> dict[str, Any]:
    context = final_state_context(state)
    return {
        "task_source_text": get_task_source_text(state),
        "task_context": copy.deepcopy(context.get("task_context", {})),
        "evaluation_context": copy.deepcopy(context.get("evaluation_context", {})),
        "external_goal": {
            "has_external_goal": bool(context.get("has_external_goal", False)),
            "external_goal_state": copy.deepcopy(
                context.get("external_goal_state", {})
            ),
            "external_goal_text": context.get("external_goal_text", ""),
            "structured_goal_state": copy.deepcopy(
                context.get("structured_goal_state", {})
            ),
            "structured_final_state": copy.deepcopy(
                context.get("structured_final_state", {})
            ),
        },
        "initial": {
            "environment": copy.deepcopy(initial_env),
            "robot": copy.deepcopy(initial_robot),
        },
        "final": {
            "environment": copy.deepcopy(final_env),
            "robot": copy.deepcopy(final_robot),
        },
        "state_diff": copy.deepcopy(state_diff),
        "trajectory": trajectory,
        "action_plan": _state_todo_action_prefix(state) or _state_action_plan(state),
    }


def benchmark_final_state_compare(packet: dict[str, Any]) -> dict[str, Any]:
    module_name = str(
        get_config("files", "final_state_module", default="") or ""
    ).strip()
    if not module_name:
        return {
            "enabled": False,
            "status": "not_configured",
            "comparer_module": "",
        }
    module = resolve_module(
        module_name, required=True, label="benchmark final_state_module"
    )
    compare_fn = getattr(module, "compare_final_state", None)
    if not callable(compare_fn):
        raise AttributeError(
            f"{module_name}.compare_final_state is required by files.final_state_module"
        )
    result = compare_fn(copy.deepcopy(packet))
    if not isinstance(result, dict):
        raise ValueError(f"{module_name}.compare_final_state must return a JSON object")
    result.setdefault("enabled", True)
    result.setdefault("status", "recorded")
    result.setdefault("comparer_module", module_name)
    return result


def run_state_diff_audit(
    state: PlanningState,
    *,
    intent: str,
    trajectory: str,
    initial_env: dict[str, dict[str, Any]],
    initial_robot: dict[str, Any],
    final_env: dict[str, dict[str, Any]],
    final_robot: dict[str, Any],
    state_diff: dict[str, Any],
    simulated_steps: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    packet = build_final_state_packet(
        state,
        trajectory=trajectory,
        initial_env=initial_env,
        initial_robot=initial_robot,
        final_env=final_env,
        final_robot=final_robot,
        state_diff=state_diff,
    )
    benchmark_compare = benchmark_final_state_compare(packet)
    packet["benchmark_final_state_compare"] = copy.deepcopy(benchmark_compare)
    structured_task = state.get("structured_task", {})
    if not isinstance(structured_task, dict):
        structured_task = {}
    todo_or_steps = simulated_steps or _state_action_plan(state) or []
    audit_context = _build_state_audit_context(
        initial_env,
        initial_robot,
        final_env,
        final_robot,
        todo_or_steps if isinstance(todo_or_steps, list) else [],
        structured_task,
    )
    # Official/gold evaluation inputs stay in the deterministic checker and
    # reporting packet. They must never enter an LLM prompt or repair feedback.
    audit_context["task_context"] = copy.deepcopy(packet.get("task_context", {}))
    action_plan = _state_action_plan(state)

    llm_result = audit_llm._run_state_diff_audit(
        intent=intent,
        todo_list=action_plan,
        simulated_steps=simulated_steps or [],
        trajectory=trajectory,
        state_diff=state_diff,
        state_audit_context=audit_context,
        get_planning_llm=get_planning_llm,
    )
    if not isinstance(llm_result, dict):
        raise ValueError("公共状态差异审计输出必须是 JSON 对象")

    parsed = copy.deepcopy(llm_result)
    deterministic = (
        benchmark_compare.get("deterministic_goal_check", {})
        if isinstance(benchmark_compare, dict)
        else {}
    )
    if (
        isinstance(deterministic, dict)
        and deterministic.get("passed") is True
        and deterministic.get("authoritative_when_passed") is True
    ):
        parsed["is_passed"] = True
        parsed["issue"] = ""
        parsed["fix_advice"] = ""
        parsed["repair_mode"] = "continue_from_current"
        parsed["deterministic_goal_check"] = copy.deepcopy(deterministic)
    elif isinstance(deterministic, dict) and deterministic.get("passed") is False:
        parsed["is_passed"] = False
        parsed["issue"] = "benchmark deterministic goal check failed"
        parsed["fix_advice"] = (
            "最终状态未满足 benchmark 的确定性目标检查；"
            "请只依据原始任务指令、当前环境和 skill 契约重新规划。"
        )
        parsed["repair_mode"] = "reset_and_replan"
        parsed["deterministic_goal_check"] = copy.deepcopy(deterministic)
    repair_mode = str(
        parsed.get("repair_mode", "continue_from_current") or "continue_from_current"
    ).strip()
    if repair_mode not in {"continue_from_current", "reset_and_replan"}:
        repair_mode = "continue_from_current"
    parsed["repair_mode"] = repair_mode
    parsed["audit_method"] = "framework_llm_state_diff"
    parsed["state_audit_context"] = audit_context
    parsed["llm_result"] = llm_result
    parsed["benchmark_final_state_compare"] = copy.deepcopy(benchmark_compare)
    parsed["has_external_goal"] = bool(
        packet.get("external_goal", {}).get("has_external_goal", False)
    )
    parsed["final_state_packet"] = packet
    parsed["state_diff"] = state_diff
    return parsed


def build_sda_state_diff_repair_state(
    *,
    audit_result: dict[str, Any],
    issue: str,
    fix: str,
    todo_list: list[dict[str, Any]],
    validated_steps: list[dict[str, Any]],
    validated_todo_actions: list[dict[str, Any]],
    validated_audit_steps: list[dict[str, Any]],
    checkpoint_env: dict[str, dict[str, Any]],
    checkpoint_robot: dict[str, Any],
    reset_plan: bool,
    state_diff: dict[str, Any],
) -> dict[str, Any]:
    prefix_steps = (
        []
        if reset_plan
        else list(validated_steps or validated_audit_steps or todo_list or [])
    )
    prefix_todo_actions = (
        [] if reset_plan else list(validated_todo_actions or todo_list or [])
    )
    next_step_num = len(prefix_todo_actions or prefix_steps) + 1
    return {
        "version": "sda_v1",
        "mode": "sda_state_diff_repair",
        "repair_strategy": REPAIR_STRATEGY_SDA,
        "failure_kind": "state_diff_audit",
        "issue_type": issue,
        "failure": {
            "issue": f"最终态对比拦截: {issue}",
            "fix_advice": fix,
            "audit_result": copy.deepcopy(audit_result),
        },
        "trajectory": {
            "original_todo_list": copy.deepcopy(
                todo_list or validated_audit_steps or []
            ),
            "verified_prefix": copy.deepcopy(prefix_steps),
            "validated_prefix": copy.deepcopy(prefix_steps),
            "validated_todo_prefix": copy.deepcopy(prefix_todo_actions),
            "validated_step_count": len(prefix_todo_actions or prefix_steps),
            "next_step_num": next_step_num,
            "prefix_is_valid": True,
            "discarded_suffix": [],
        },
        "todo_trajectory": {
            "original_todo_list": copy.deepcopy(todo_list or []),
            "validated_prefix": copy.deepcopy(prefix_todo_actions),
            "next_step_num": len(prefix_todo_actions) + 1,
        },
        "current_simulated_state": {
            "robot": copy.deepcopy(checkpoint_robot),
            "environment": copy.deepcopy(checkpoint_env),
            "changed_state_diff": copy.deepcopy(state_diff),
            "note": "This is the sandbox state selected after final-state audit, not the real runtime scene.",
        },
        "frontier": {
            "type": "append_state_diff_recovery"
            if not reset_plan
            else "reset_and_replan_after_state_diff_audit",
            "next_step_num": next_step_num,
            "instruction": (
                "Continue from current_simulated_state and add only the missing recovery/goal-completion suffix."
                if not reset_plan
                else "Discard the failed plan and regenerate a complete plan from the initial sandbox state."
            ),
        },
    }


def build_state_diff_failure_payload(
    *,
    state: PlanningState,
    audit_result: dict[str, Any],
    intent: str,
    memory: dict,
    iters: int,
    max_iterations: int,
    feature_flags: dict | None,
    injected_rule_ids: list[str] | None,
    todo_list: list[dict[str, Any]],
    validated_steps: list[dict[str, Any]],
    validated_todo_actions: list[dict[str, Any]],
    validated_audit_steps: list[dict[str, Any]],
    sandbox_start_env: dict[str, dict[str, Any]],
    sandbox_start_robot: dict[str, Any],
    final_env: dict[str, dict[str, Any]],
    final_robot: dict[str, Any],
    state_diff: dict[str, Any],
    debug_events: list[dict[str, Any]],
) -> dict[str, Any]:
    repair_strategy = active_repair_strategy()
    record_retrac = repair_strategy == REPAIR_STRATEGY_RETRAC
    issue = str(audit_result.get("issue") or "最终态未满足")
    fix = str(audit_result.get("fix_advice") or "根据最终态审计意见修正动作序列")
    full_issue = f"最终态对比拦截: {issue}"
    repair_mode = str(audit_result.get("repair_mode") or "continue_from_current")
    reset_plan = repair_mode == "reset_and_replan"
    step_info = {
        "step": len(todo_list or validated_steps) + 1,
        "execution": {
            "skill": "FINAL_STATE_AUDIT",
            "parameters": {"repair_mode": repair_mode},
        },
    }
    finding = build_failure_finding(step_info=step_info, issue=full_issue, fix=fix)
    if reset_plan:
        checkpoint_env = copy.deepcopy(sandbox_start_env)
        checkpoint_robot = copy.deepcopy(sandbox_start_robot)
        payload_validated_steps: list[dict[str, Any]] = []
        payload_validated_todo_actions: list[dict[str, Any]] = []
        retrac_state = (
            build_failed_step_retrac_state(
                failure_kind="state_diff_audit_reset",
                issue_type=issue,
                issue=full_issue,
                fix_advice=fix,
                todo_list=todo_list or validated_audit_steps,
                validated_steps=[],
                failed_step=step_info,
                sim_env=checkpoint_env,
                sim_robot=checkpoint_robot,
            )
            if record_retrac
            else {}
        )
    else:
        checkpoint_env = copy.deepcopy(final_env)
        checkpoint_robot = copy.deepcopy(final_robot)
        payload_validated_steps = list(
            validated_steps or validated_audit_steps or todo_list or []
        )
        inherited_todo_prefix = _state_todo_action_prefix(state)
        current_todo_plan = list(validated_todo_actions or todo_list or [])
        payload_validated_todo_actions = _merge_todo_action_prefix(
            inherited_todo_prefix, current_todo_plan
        )
        retrac_state = (
            build_state_diff_retrac_state(
                issue_type=issue,
                issue=full_issue,
                fix_advice=fix,
                todo_list=todo_list or validated_audit_steps,
                validated_steps=payload_validated_steps or validated_audit_steps,
                validated_todo_actions=payload_validated_todo_actions,
                sim_env=checkpoint_env,
                sim_robot=checkpoint_robot,
                state_diff=state_diff,
                audit_result=audit_result,
            )
            if record_retrac
            else {}
        )

    sda_state = (
        build_sda_state_diff_repair_state(
            audit_result=audit_result,
            issue=issue,
            fix=fix,
            todo_list=todo_list,
            validated_steps=payload_validated_steps,
            validated_todo_actions=payload_validated_todo_actions,
            validated_audit_steps=validated_audit_steps,
            checkpoint_env=checkpoint_env,
            checkpoint_robot=checkpoint_robot,
            reset_plan=reset_plan,
            state_diff=state_diff,
        )
        if repair_strategy == REPAIR_STRATEGY_SDA
        else {}
    )

    payload = build_failure_payload(
        issue=full_issue,
        fix=fix,
        memory=memory,
        validated_steps=payload_validated_steps,
        checkpoint_env=checkpoint_env,
        checkpoint_robot=checkpoint_robot,
        validated_todo_actions=payload_validated_todo_actions,
        todo_checkpoint_env=checkpoint_env if todo_list else {},
        todo_checkpoint_robot=checkpoint_robot if todo_list else {},
        re_trac_state=retrac_state,
        finding=finding,
        record_retrac_memory=record_retrac,
    )
    payload.update(
        {
            "todo_list": [] if reset_plan else list(todo_list or []),
            "execution_status": "failed" if iters >= max_iterations else "running",
            "failed_action": "状态差异审计",
            "error_feedback": full_issue,
            "failure_layer": "planning",
            "failure_category": "state_diff_audit",
            "repair_strategy": repair_strategy,
            "sda_state": copy.deepcopy(sda_state),
            "state_diff_audit": {
                "passed": False,
                "result": copy.deepcopy(audit_result),
                "state_diff": copy.deepcopy(state_diff),
            },
            "planning_debug_events": list(debug_events or []),
        }
    )
    record_rule_feedback(
        "planning",
        injected_rule_ids,
        outcome="harmful",
        feature_flags=feature_flags,
    )
    return sync_debug_event_aliases(payload)
