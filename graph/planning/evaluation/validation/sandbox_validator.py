from __future__ import annotations

import copy
from typing import Any, Callable

from domain.sandbox import apply_sandbox_action
from graph.planning.evaluation.validation.failure import report_audit_failure
from graph.planning.evaluation.validation.native_action_validator import validate_todo_actions
from graph.planning.evaluation.validation.sandbox import prepare_sandbox_scene
from graph.planning.evaluation.validation.sandbox_validation_types import SandboxValidationContext, SandboxValidationResult
from graph.planning.evaluation.validation.todo_contract import validate_todo_contract
from graph.planning.evaluation.validation.todo_validator import validate_todo_steps
from graph.planning.evaluation.validation.trajectory import todo_action_trajectory, todo_trajectory
from graph.state import PlanningState
from skills.planning_catalog import load_planning_catalog


def run_sandbox_validation(
    *,
    state: PlanningState,
    sandbox_enabled: bool,
    todo_list: list[dict[str, Any]],
    intent: str,
    memory: dict,
    iters: int,
    max_iterations: int,
    feature_flags: dict | None,
    injected_rule_ids: list[str] | None,
    debug_events: list[dict[str, Any]],
    retrac_active: bool,
    sda_active: bool,
    apply_action: Callable[..., tuple[bool, str, str]] = apply_sandbox_action,
) -> SandboxValidationResult:
    sim_env, sim_robot = prepare_sandbox_scene(state)
    validated_steps: list[dict[str, Any]] = []
    validated_todo_actions: list[dict[str, Any]] = []
    validated_audit_steps: list[dict[str, Any]] = []
    use_todo_step_adapter = bool(str(state.get("todo_step_adapter_path") or "").strip())
    sandbox_start_env = copy.deepcopy(sim_env)
    sandbox_start_robot = copy.deepcopy(sim_robot)
    trajectory_records: list[dict[str, Any]] = []
    context = SandboxValidationContext(
        intent=intent,
        memory=memory,
        iters=iters,
        max_iterations=max_iterations,
        feature_flags=feature_flags,
        injected_rule_ids=injected_rule_ids,
        debug_events=debug_events,
        retrac_active=retrac_active,
        sda_active=sda_active,
        apply_action=apply_action,
    )

    todo_contract_catalog = load_planning_catalog()
    if todo_list and todo_contract_catalog.raw_specs:
        try:
            todo_list = validate_todo_contract(
                state=state,
                todo_list=todo_list,
                current_env=sandbox_start_env,
                skill_catalog=todo_contract_catalog,
            )
            context.debug_events.append(
                {
                    "layer": "todo_contract",
                    "type": "passed",
                    "todo_count": len(todo_list),
                }
            )
        except Exception as exc:
            failure = report_audit_failure(
                {
                    "step": 1,
                    "execution": {
                        "skill": "TODO_CONTRACT",
                        "parameters": {"error": str(exc)},
                    },
                },
                "todo_list 契约检查失败",
                f"重新生成满足当前 skill 动作契约的完整 todo_list: {exc}",
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
                debug_events=context.debug_events
                + [
                    {
                        "layer": "todo_contract",
                        "type": "rejected",
                        "error": repr(exc),
                    }
                ],
                validated_todo_actions=validated_todo_actions,
                todo_checkpoint_env=sandbox_start_env,
                todo_checkpoint_robot=sandbox_start_robot,
            )
            return SandboxValidationResult(
                sim_env=sim_env,
                sim_robot=sim_robot,
                sandbox_start_env=sandbox_start_env,
                sandbox_start_robot=sandbox_start_robot,
                todo_list=todo_list,
                validated_steps=validated_steps,
                validated_todo_actions=validated_todo_actions,
                validated_audit_steps=validated_audit_steps,
                trajectory_str=todo_action_trajectory(todo_list)
                if use_todo_step_adapter
                else todo_trajectory(todo_list),
                failure_payload=failure,
            )

    if use_todo_step_adapter:
        failure = None
        if sandbox_enabled and todo_list:
            failure = failure or validate_todo_actions(
                state=state,
                todo_list=todo_list,
                context=context,
                sim_env=sim_env,
                sim_robot=sim_robot,
                sandbox_start_env=sandbox_start_env,
                sandbox_start_robot=sandbox_start_robot,
                validated_steps=validated_steps,
                validated_todo_actions=validated_todo_actions,
                validated_audit_steps=validated_audit_steps,
                trajectory_records=trajectory_records,
            )
        return SandboxValidationResult(
            sim_env=sim_env,
            sim_robot=sim_robot,
            sandbox_start_env=sandbox_start_env,
            sandbox_start_robot=sandbox_start_robot,
            todo_list=todo_list,
            validated_steps=validated_steps,
            validated_todo_actions=validated_todo_actions,
            validated_audit_steps=validated_audit_steps,
            trajectory_str=todo_action_trajectory(todo_list),
            failure_payload=failure,
        )

    sda_success_state: dict[str, Any] | None = None
    if sandbox_enabled:
        todo_result = validate_todo_steps(
            todo_list=todo_list,
            context=context,
            sim_env=sim_env,
            sim_robot=sim_robot,
            sandbox_start_env=sandbox_start_env,
            sandbox_start_robot=sandbox_start_robot,
            validated_steps=validated_steps,
            trajectory_records=trajectory_records,
        )
        todo_list = todo_result.todo_list
        validated_steps = todo_result.validated_steps
        sim_env = todo_result.sim_env
        sim_robot = todo_result.sim_robot
        sda_success_state = todo_result.sda_success_state
        failure = todo_result.failure_payload
    else:
        failure = None

    return SandboxValidationResult(
        sim_env=sim_env,
        sim_robot=sim_robot,
        sandbox_start_env=sandbox_start_env,
        sandbox_start_robot=sandbox_start_robot,
        todo_list=todo_list,
        validated_steps=validated_steps,
        validated_todo_actions=validated_todo_actions,
        validated_audit_steps=validated_audit_steps,
        trajectory_str=todo_trajectory(todo_list),
        sda_success_state=sda_success_state,
        failure_payload=failure,
    )
