import copy
from typing import Any

from ace.playbook import learn_from_success, record_rule_feedback
from graph.state import PlanningState
from graph.planning.config import (
    max_planning_iterations,
)
from graph.planning.evaluation import flags as evaluation_flags
from graph.planning.evaluation.validation.debug_events import sync_debug_event_aliases
from graph.planning.evaluation.validation.feature_records import (
    final_state_feature_record,
    sandbox_feature_record,
    sda_feature_record,
    skipped_feature_record,
)
from graph.planning.evaluation.validation.failure import report_audit_failure
from graph.planning.evaluation.validation.final_state import (
    build_final_state_packet,
    build_state_diff_failure_payload,
    diff_state,
    is_state_diff_audit_enabled,
    run_state_diff_audit,
)
from graph.planning.config import (
    REPAIR_STRATEGY_RETRAC,
    REPAIR_STRATEGY_SDA,
    active_repair_strategy,
    repair_strategy_event,
)
from re_trac import coerce_memory
from graph.planning.evaluation.validation.sandbox import prepare_sandbox_scene
from graph.planning.evaluation.validation.sandbox_validator import run_sandbox_validation
from graph.planning.normalizer import (
    planning_debug_events as get_planning_debug_events,
    task_context as get_task_context,
)


def _with_feature_records(payload: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    payload["planning_feature_records"] = copy.deepcopy(records)
    return payload


def _with_final_runtime_state(payload: dict[str, Any], env: dict[str, Any], robot: dict[str, Any]) -> dict[str, Any]:
    payload["environment"] = copy.deepcopy(env)
    payload["env_state"] = copy.deepcopy(robot)
    return payload


def _clear_failure_fields(payload: dict[str, Any]) -> dict[str, Any]:
    payload.update(
        {
            "failed_action": {},
            "error_feedback": "",
            "failure_layer": "",
            "failure_category": "",
            "todo_parse_error": "",
        }
    )
    return payload


def evaluate_feasibility(state: PlanningState) -> PlanningState:
    feature_flags = state.get("feature_flags", {})
    todo_list = state.get("todo_list", [])
    planner_status = str(state.get("planner_status", "planned")).strip().lower()
    st_task = state.get("structured_task", {})
    iters = state.get("iteration_count", 1)
    max_iterations = max_planning_iterations()
    intent = st_task.get("intent", "")
    memory = coerce_memory(state.get("re_trac_memory"))
    injected_rule_ids = state.get("injected_playbook_rule_ids", [])
    debug_events = get_planning_debug_events(state)
    sandbox_enabled = evaluation_flags.is_sandbox_evaluator_enabled(state)
    state_diff_audit_enabled = is_state_diff_audit_enabled(feature_flags)
    repair_strategy = active_repair_strategy()
    retrac_active = repair_strategy == REPAIR_STRATEGY_RETRAC
    sda_active = repair_strategy == REPAIR_STRATEGY_SDA
    memory = memory if (retrac_active or sda_active) else coerce_memory()
    state_diff_audit_result: dict[str, Any] | None = None
    feature_records = list(state.get("planning_feature_records") or [])
    debug_events.append(repair_strategy_event())

    if not isinstance(todo_list, list):
        todo_list = []
    if planner_status == "completed":
        feature_records.append(
            skipped_feature_record(
                "sandbox",
                enabled=sandbox_enabled,
                reason="planner_completed_without_actions",
                config={"todo_step_adapter_path": state.get("todo_step_adapter_path", "")},
            )
        )
        feature_records.append(
            skipped_feature_record(
                "sda",
                enabled=sda_active,
                reason="planner_completed_without_actions",
                config={"repair_strategy": repair_strategy},
            )
        )
        sandbox_start_env, sandbox_start_robot = prepare_sandbox_scene(state)
        sim_env = copy.deepcopy(sandbox_start_env)
        sim_robot = copy.deepcopy(sandbox_start_robot)
        state_diff = diff_state(sandbox_start_env, sandbox_start_robot, sim_env, sim_robot)
        if state_diff_audit_enabled:
            try:
                state_diff_audit_result = run_state_diff_audit(
                    state,
                    intent=intent,
                    trajectory="[]",
                    simulated_steps=[],
                    initial_env=sandbox_start_env,
                    initial_robot=sandbox_start_robot,
                    final_env=sim_env,
                    final_robot=sim_robot,
                    state_diff=state_diff,
                )
                debug_events.append(
                    {
                        "layer": "state_diff_audit",
                        "type": "passed" if bool(state_diff_audit_result.get("is_passed")) else "rejected",
                        "result": copy.deepcopy(state_diff_audit_result),
                    }
                )
            except Exception as exc:
                state_diff_audit_result = {
                    "is_passed": False,
                    "issue": "已完成状态审计异常",
                    "fix_advice": f"规划器声明已完成，但最终态审计无法稳定执行: {exc}",
                    "repair_mode": "reset_and_replan",
                    "exception": repr(exc),
                    "final_state_packet": build_final_state_packet(
                        state,
                        trajectory="[]",
                        initial_env=sandbox_start_env,
                        initial_robot=sandbox_start_robot,
                        final_env=sim_env,
                        final_robot=sim_robot,
                        state_diff=state_diff,
                    ),
                    "state_diff": state_diff,
                }
                debug_events.append(
                    {
                        "layer": "state_diff_audit",
                        "type": "exception",
                        "error": repr(exc),
                    }
                )

            if not bool((state_diff_audit_result or {}).get("is_passed")):
                feature_records.append(
                    final_state_feature_record(
                        enabled=True,
                        status="failed",
                        state_diff=state_diff,
                        audit_result=state_diff_audit_result,
                        sandbox_start_env=sandbox_start_env,
                        sandbox_start_robot=sandbox_start_robot,
                        final_env=sim_env,
                        final_robot=sim_robot,
                        simulated_steps=[],
                        task_context=get_task_context(state),
                        structured_task=st_task,
                    )
                )
                failed = build_state_diff_failure_payload(
                    state=state,
                    audit_result=state_diff_audit_result or {},
                    intent=intent,
                    memory=memory,
                    iters=iters,
                    max_iterations=max_iterations,
                    feature_flags=feature_flags,
                    injected_rule_ids=injected_rule_ids,
                    todo_list=[],
                    validated_steps=[],
                    validated_todo_actions=[],
                    validated_audit_steps=[],
                    sandbox_start_env=sandbox_start_env,
                    sandbox_start_robot=sandbox_start_robot,
                    final_env=sim_env,
                    final_robot=sim_robot,
                    state_diff=state_diff,
                    debug_events=debug_events,
                )
                return sync_debug_event_aliases(_with_feature_records(failed, feature_records))

            feature_records.append(
                final_state_feature_record(
                    enabled=True,
                    status="passed",
                    state_diff=state_diff,
                    audit_result=state_diff_audit_result,
                    sandbox_start_env=sandbox_start_env,
                    sandbox_start_robot=sandbox_start_robot,
                    final_env=sim_env,
                    final_robot=sim_robot,
                    simulated_steps=[],
                    task_context=get_task_context(state),
                    structured_task=st_task,
                )
            )
        else:
            feature_records.append(
                skipped_feature_record(
                    "final_state",
                    enabled=False,
                    reason="planner_completed_without_actions",
                    config={"state_diff_audit": state_diff_audit_enabled},
                )
            )
        return sync_debug_event_aliases(_with_final_runtime_state(_clear_failure_fields({
            "todo_list": todo_list,
            "validated_steps": [],
            "validated_todo_actions": [],
            "todo_checkpoint_env": copy.deepcopy(sim_env),
            "todo_checkpoint_robot": copy.deepcopy(sim_robot),
            "checkpoint_env": copy.deepcopy(sim_env),
            "checkpoint_robot": copy.deepcopy(sim_robot),
            "is_feasible": True,
            "execution_status": "fully_completed",
            "feedback": state.get("feedback", "规划器判断当前任务已完成。"),
            "evaluator_findings": [],
            "planner_status": planner_status,
            "planning_debug_events": debug_events + [{"layer": "planning_evaluator", "type": "planner_completed_without_actions"}],
            "state_diff_audit": {
                "passed": True,
                "result": copy.deepcopy(state_diff_audit_result or {}),
                "state_diff": copy.deepcopy(state_diff),
            } if state_diff_audit_enabled else {},
            "planning_feature_records": feature_records,
            "re_trac_state": {},
            "planning_continuation": {},
            "sda_state": {},
        }), sim_env, sim_robot))

    if not todo_list:
        feature_records.append(
            skipped_feature_record(
                "sandbox",
                enabled=sandbox_enabled,
                reason="planner_returned_no_actions",
                config={"todo_step_adapter_path": state.get("todo_step_adapter_path", "")},
            )
        )
        feature_records.append(
            skipped_feature_record(
                "sda",
                enabled=sda_active,
                reason="planner_returned_no_actions",
                config={"repair_strategy": repair_strategy},
            )
        )
        sandbox_start_env, sandbox_start_robot = prepare_sandbox_scene(state)
        parse_error = str(state.get("todo_parse_error") or "").strip()
        if parse_error:
            issue_type = "todo_list 输出解析失败"
            fix = f"输出必须是满足当前数据集动作契约的 JSON 序列，解析错误详情: {parse_error}"
        else:
            issue_type = "序列验证失败"
            fix = "必须输出标准动作序列"
        failed = report_audit_failure(
            {},
            issue_type,
            fix,
            intent,
            memory,
            iters,
            [],
            sandbox_start_env,
            sandbox_start_robot,
            injected_rule_ids,
            max_iterations,
            feature_flags,
            attempted_steps=todo_list,
            debug_events=debug_events,
        )
        failed["planning_feature_records"] = copy.deepcopy(feature_records)
        return sync_debug_event_aliases(_with_final_runtime_state(failed, sandbox_start_env, sandbox_start_robot))

    debug_event_start = len(debug_events)
    sandbox_result = run_sandbox_validation(
        state=state,
        sandbox_enabled=sandbox_enabled,
        todo_list=todo_list,
        intent=intent,
        memory=memory,
        iters=iters,
        max_iterations=max_iterations,
        feature_flags=feature_flags,
        injected_rule_ids=injected_rule_ids,
        debug_events=debug_events,
        retrac_active=retrac_active,
        sda_active=sda_active,
    )
    sandbox_debug_events = debug_events[debug_event_start:]
    feature_records.append(
        sandbox_feature_record(
            sandbox_enabled=sandbox_enabled,
            state=state,
            todo_list=todo_list,
            sandbox_result=sandbox_result,
            debug_events=sandbox_debug_events,
        )
    )
    feature_records.append(
        sda_feature_record(
            sda_active=sda_active,
            repair_strategy=repair_strategy,
            sandbox_result=sandbox_result,
            failure_payload=sandbox_result.failure_payload,
            debug_events=sandbox_debug_events,
        )
    )
    if sandbox_result.failure_payload is not None:
        failed_payload = _with_feature_records(sandbox_result.failure_payload, feature_records)
        return sync_debug_event_aliases(failed_payload)

    sim_env = sandbox_result.sim_env
    sim_robot = sandbox_result.sim_robot
    sandbox_start_env = sandbox_result.sandbox_start_env
    sandbox_start_robot = sandbox_result.sandbox_start_robot
    todo_list = sandbox_result.todo_list
    validated_steps = sandbox_result.validated_steps
    validated_todo_actions = sandbox_result.validated_todo_actions
    validated_audit_steps = sandbox_result.validated_audit_steps
    trajectory_str = sandbox_result.trajectory_str
    sda_success_state = sandbox_result.sda_success_state

    state_diff = diff_state(sandbox_start_env, sandbox_start_robot, sim_env, sim_robot)
    if state_diff_audit_enabled:
        try:
            state_diff_audit_result = run_state_diff_audit(
                state,
                intent=intent,
                trajectory=trajectory_str,
                simulated_steps=validated_todo_actions or validated_steps or validated_audit_steps,
                initial_env=sandbox_start_env,
                initial_robot=sandbox_start_robot,
                final_env=sim_env,
                final_robot=sim_robot,
                state_diff=state_diff,
            )
            debug_events.append(
                {
                    "layer": "state_diff_audit",
                    "type": "passed" if bool(state_diff_audit_result.get("is_passed")) else "rejected",
                    "result": copy.deepcopy(state_diff_audit_result),
                }
            )
        except Exception as exc:
            state_diff_audit_result = {
                "is_passed": False,
                "issue": "状态差异审计异常",
                "fix_advice": f"状态差异审计未能稳定输出 JSON 或调用失败: {exc}",
                "repair_mode": "reset_and_replan",
                "exception": repr(exc),
                "final_state_packet": build_final_state_packet(
                    state,
                    trajectory=trajectory_str,
                    initial_env=sandbox_start_env,
                    initial_robot=sandbox_start_robot,
                    final_env=sim_env,
                    final_robot=sim_robot,
                    state_diff=state_diff,
                ),
                "state_diff": state_diff,
            }
            debug_events.append(
                {
                    "layer": "state_diff_audit",
                    "type": "exception",
                    "error": repr(exc),
                }
            )
        if not bool(state_diff_audit_result.get("is_passed")):
            feature_records.append(
                final_state_feature_record(
                    enabled=True,
                    status="failed",
                    state_diff=state_diff,
                    audit_result=state_diff_audit_result,
                    sandbox_start_env=sandbox_start_env,
                    sandbox_start_robot=sandbox_start_robot,
                    final_env=sim_env,
                    final_robot=sim_robot,
                    simulated_steps=validated_todo_actions or validated_steps or validated_audit_steps,
                    task_context=get_task_context(state),
                    structured_task=st_task,
                )
            )
            failed = build_state_diff_failure_payload(
                state=state,
                audit_result=state_diff_audit_result,
                intent=intent,
                memory=memory,
                iters=iters,
                max_iterations=max_iterations,
                feature_flags=feature_flags,
                injected_rule_ids=injected_rule_ids,
                todo_list=todo_list,
                validated_steps=validated_steps,
                validated_todo_actions=validated_todo_actions,
                validated_audit_steps=validated_audit_steps,
                sandbox_start_env=sandbox_start_env,
                sandbox_start_robot=sandbox_start_robot,
                final_env=sim_env,
                final_robot=sim_robot,
                state_diff=state_diff,
                debug_events=debug_events,
            )
            return sync_debug_event_aliases(_with_feature_records(failed, feature_records))
        feature_records.append(
            final_state_feature_record(
                enabled=True,
                status="passed",
                state_diff=state_diff,
                audit_result=state_diff_audit_result,
                sandbox_start_env=sandbox_start_env,
                sandbox_start_robot=sandbox_start_robot,
                final_env=sim_env,
                final_robot=sim_robot,
                simulated_steps=validated_todo_actions or validated_steps or validated_audit_steps,
                task_context=get_task_context(state),
                structured_task=st_task,
            )
        )
    else:
        feature_records.append(
            final_state_feature_record(
                enabled=False,
                status="disabled",
                state_diff=state_diff,
                audit_result=None,
                sandbox_start_env=sandbox_start_env,
                sandbox_start_robot=sandbox_start_robot,
                final_env=sim_env,
                final_robot=sim_robot,
                simulated_steps=validated_todo_actions or validated_steps or validated_audit_steps,
                task_context=get_task_context(state),
                structured_task=st_task,
            )
        )

    learned_plan = todo_list
    record_rule_feedback("planning", injected_rule_ids, outcome="helpful", feature_flags=feature_flags)
    if bool((feature_flags or {}).get("playbook_write", False)):
        learn_from_success("planning", intent, learned_plan, feature_flags=feature_flags)
    return sync_debug_event_aliases(_with_final_runtime_state(_clear_failure_fields({
        "todo_list": todo_list,
        "validated_steps": validated_steps,
        "validated_todo_actions": validated_todo_actions,
        "todo_checkpoint_env": copy.deepcopy(sim_env),
        "todo_checkpoint_robot": copy.deepcopy(sim_robot),
        "checkpoint_env": copy.deepcopy(sim_env),
        "checkpoint_robot": copy.deepcopy(sim_robot),
        "is_feasible": True,
        "execution_status": "completed",
        "feedback": (
            "规划合法，SDA 自适应动作子树已完成 sandbox 修复。"
            if sda_success_state
            else "规划合法，验证环节闭环。"
        ),
        "evaluator_findings": [],
        "planner_status": planner_status,
        "repair_strategy": repair_strategy,
        "planning_debug_events": debug_events
        + [
            {
                "layer": "planning_evaluator",
                "type": "audit_passed",
                "validated_steps_count": len(validated_steps),
                "validated_todo_actions_count": len(validated_todo_actions),
            }
        ],
        "sda_state": copy.deepcopy(sda_success_state or {}),
        "re_trac_state": {},
        "planning_continuation": {},
        "state_diff_audit": {
            "passed": True,
            "result": copy.deepcopy(state_diff_audit_result or {}),
            "state_diff": copy.deepcopy(state_diff),
        } if state_diff_audit_enabled else {},
        "planning_feature_records": feature_records,
    }), sim_env, sim_robot))
