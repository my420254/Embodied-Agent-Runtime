"""Build request-scoped context, modes, and mutable evaluation sessions."""
from __future__ import annotations

import copy
from typing import Any

from graph.planning.config import get_planning_max_iterations
from graph.state import PlanningState
from .. import flags
from ..dependencies import EvaluationDependencies
from ..models import (
    EvaluationContext,
    EvaluationFailure,
    EvaluationFailureCode,
    EvaluationModes,
    EvaluationSession,
    SimulationResult,
)
from ..validation.checkpoint import _apply_checkpoint_env
from .skills import load_skill_snapshot


def build_evaluation_context(
    state: PlanningState,
    dependencies: EvaluationDependencies,
) -> EvaluationContext:
    feature_flags = state.get("feature_flags", {})
    structured_task = state.get("structured_task", {})
    return EvaluationContext(
        state=state,
        feature_flags=feature_flags,
        skill_profile=state.get("skill_profile"),
        initial_robot=state.get(
            "env_state",
            {"robot_location": "未知", "robot_holding": "空"},
        ),
        structured_task=structured_task,
        iteration_count=state.get("iteration_count", 1),
        max_iterations=get_planning_max_iterations(),
        intent=structured_task.get("intent", ""),
        memory=dependencies.failure_handoff.load_memory(state),
        injected_rule_ids=state.get("injected_playbook_rule_ids", []),
    )


def resolve_evaluation_modes(
    state: PlanningState,
    feature_flags: dict[str, Any],
    dependencies: EvaluationDependencies,
) -> EvaluationModes:
    sandbox = flags.is_sandbox_evaluator_enabled(state)
    state_diff_audit = flags._feature_enabled(
        feature_flags,
        "state_diff_audit",
        default=False,
    )
    repair_selection = dependencies.repair_registry.select()
    return EvaluationModes(
        sandbox=sandbox,
        state_diff_audit=state_diff_audit,
        repair_selection=repair_selection,
        reuse_validated_prefix=False,
    )


def create_evaluation_session(
    context: EvaluationContext,
    modes: EvaluationModes,
    dependencies: EvaluationDependencies,
) -> EvaluationSession | EvaluationFailure:
    try:
        validation_env = _request_validation_env(context.state, dependencies)
    except Exception as exc:
        return EvaluationFailure(
            code=EvaluationFailureCode.SCENE_LOAD,
            issue_type="评估场景加载失败",
            fix_advice=f"无法读取请求级场景快照: {exc}",
            kind="evaluation_setup",
            checkpoint_env=copy.deepcopy(
                context.state.get("environment") or {}
            ),
            checkpoint_robot=copy.deepcopy(context.initial_robot),
            todo_list=copy.deepcopy(context.state.get("todo_list") or []),
            artifacts={
                "scene_load": {
                    "passed": False,
                    "error": str(exc),
                }
            },
        )
    if not isinstance(validation_env, dict) or not validation_env:
        return EvaluationFailure(
            code=EvaluationFailureCode.SCENE_LOAD,
            issue_type="评估场景格式异常",
            fix_advice=(
                "planning evaluation 需要请求级平坦环境；请传 environment。"
            ),
            kind="evaluation_setup",
            checkpoint_robot=copy.deepcopy(context.initial_robot),
            todo_list=copy.deepcopy(context.state.get("todo_list") or []),
            artifacts={
                "scene_load": {
                    "passed": False,
                    "error": f"unexpected type: {type(validation_env).__name__}",
                }
            },
        )

    todo_list = copy.deepcopy(context.state.get("todo_list", []))
    prefix_steps = [
        copy.deepcopy(step)
        for step in (context.state.get("validated_steps") or [])
        if isinstance(step, dict)
    ]
    validated_steps = copy.deepcopy(prefix_steps) if modes.reuse_validated_prefix else []
    sim_robot = (
        copy.deepcopy(context.state.get("checkpoint_robot") or context.initial_robot)
        if modes.reuse_validated_prefix
        else copy.deepcopy(context.initial_robot)
    )
    todo_steps = (
        copy.deepcopy(todo_list[len(prefix_steps) :])
        if modes.reuse_validated_prefix
        else copy.deepcopy(todo_list)
    )
    start_env = copy.deepcopy(validation_env)
    simulation_env = copy.deepcopy(start_env)
    if modes.reuse_validated_prefix:
        simulation_env = _apply_checkpoint_env(
            simulation_env,
            context.state.get("checkpoint_env") or {},
            sim_robot,
        )
    simulation = SimulationResult(
        todo_list=copy.deepcopy(todo_list),
        todo_steps=todo_steps,
        validated_steps=validated_steps,
        final_env=copy.deepcopy(simulation_env),
        final_robot=copy.deepcopy(sim_robot),
        start_env=start_env,
        start_robot=copy.deepcopy(context.initial_robot),
        repair_base_env=copy.deepcopy(simulation_env),
        repair_base_robot=copy.deepcopy(sim_robot),
    )
    repair_history = copy.deepcopy(
        context.state.get("repair_history") or []
    )
    return EvaluationSession(
        context=context,
        modes=modes,
        todo_list=todo_list,
        prefix_steps=prefix_steps,
        skills=load_skill_snapshot(context.skill_profile, dependencies),
        validation_env=validation_env,
        simulation=simulation,
        repair_history=repair_history,
        pending_recovery_actions=_pending_recovery_actions(context.state),
    )


def _request_validation_env(
    state: PlanningState,
    dependencies: EvaluationDependencies,
) -> dict[str, Any]:
    environment = state.get("environment")
    if isinstance(environment, dict) and environment:
        return copy.deepcopy(dependencies.get_full_flat_house(environment))

    raise ValueError("missing request-level planning environment")


def _pending_recovery_actions(state: PlanningState) -> list[dict]:
    if not state.get("evaluation_recheck"):
        return []
    revision = state.get("evaluation_revision_context")
    if not isinstance(revision, dict) or revision.get("source") != "state_diff_recovery":
        return []
    artifacts = revision.get("artifacts")
    actions = artifacts.get("recovery_actions") if isinstance(artifacts, dict) else None
    if isinstance(actions, list):
        return copy.deepcopy(
            [action for action in actions if isinstance(action, dict)]
        )
    return []


__all__ = [
    "build_evaluation_context",
    "create_evaluation_session",
    "resolve_evaluation_modes",
]
