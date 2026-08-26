from __future__ import annotations

import copy
from typing import Any

from graph.planning.normalizer import normalize_todo_list, reindex_todo_actions
from graph.planning.config import (
    REPAIR_STRATEGY_RETRAC,
    REPAIR_STRATEGY_SDA,
    active_repair_strategy,
)
from graph.state import PlanningState
from re_trac import EMPTY_FAILED_LESSONS_TEXT, planning_context


def sda_compact_step_to_todo(step: dict | None) -> dict | None:
    if not isinstance(step, dict):
        return None
    if isinstance(step.get("execution"), dict):
        return copy.deepcopy(step)
    skill = str(step.get("skill", "") or "")
    if not skill:
        return None
    return {
        "step": step.get("step"),
        "execution": {
            "skill": skill,
            "parameters": copy.deepcopy(step.get("parameters", {}) or {}),
        },
    }


def sda_todo_prefix(sda_state: dict[str, Any]) -> list[dict]:
    trajectory = sda_state.get("trajectory", {}) if isinstance(sda_state, dict) else {}
    if not isinstance(trajectory, dict):
        return []
    raw_prefix = (
        trajectory.get("validated_prefix")
        or trajectory.get("verified_prefix")
        or trajectory.get("validated_steps")
        or []
    )
    prefix = []
    for step in raw_prefix if isinstance(raw_prefix, list) else []:
        converted = sda_compact_step_to_todo(step if isinstance(step, dict) else None)
        if converted:
            prefix.append(converted)
    return normalize_todo_list(prefix)


def sda_todo_action_prefix(sda_state: dict[str, Any]) -> list[dict]:
    if not isinstance(sda_state, dict):
        return []
    todo_trajectory = sda_state.get("todo_trajectory", {})
    if isinstance(todo_trajectory, dict):
        raw_prefix = todo_trajectory.get("validated_prefix") or []
        if raw_prefix:
            return reindex_todo_actions(raw_prefix if isinstance(raw_prefix, list) else [])
    trajectory = sda_state.get("trajectory", {})
    if isinstance(trajectory, dict):
        raw_prefix = trajectory.get("validated_todo_prefix") or []
        return reindex_todo_actions(raw_prefix if isinstance(raw_prefix, list) else [])
    return []


def sda_current_state(
    sda_state: dict[str, Any],
    *,
    fallback_env: dict,
    fallback_robot: dict,
) -> tuple[dict, dict]:
    current = sda_state.get("current_simulated_state", {}) if isinstance(sda_state, dict) else {}
    if not isinstance(current, dict):
        return copy.deepcopy(fallback_env), copy.deepcopy(fallback_robot)
    env = current.get("environment")
    robot = current.get("robot")
    return (
        copy.deepcopy(env if isinstance(env, dict) else fallback_env),
        copy.deepcopy(robot if isinstance(robot, dict) else fallback_robot),
    )


def build_repair_context(
    *,
    state: PlanningState,
    feature_flags: dict,
    resolved_env: dict,
    env_state: dict,
) -> dict[str, Any]:
    repair_strategy = active_repair_strategy()
    if repair_strategy == REPAIR_STRATEGY_RETRAC:
        trace = planning_context(
            state=state,
            resolved_env=resolved_env,
            fallback_robot=env_state,
        )
        trace["repair_state"] = copy.deepcopy(trace.get("re_trac_state", {}))
    elif repair_strategy == REPAIR_STRATEGY_SDA:
        sda_state = state.get("sda_state", {})
        if not isinstance(sda_state, dict):
            sda_state = {}
        sda_current_env, sda_current_robot = sda_current_state(
            sda_state,
            fallback_env=resolved_env,
            fallback_robot=env_state,
        )
        sda_validated_steps = sda_todo_prefix(sda_state)
        sda_validated_todo_actions = sda_todo_action_prefix(sda_state)
        trace = {
            "validated_steps": sda_validated_steps,
            "validated_todo_actions": sda_validated_todo_actions,
            "current_env": sda_current_env,
            "current_robot": sda_current_robot,
            "next_step_num": len(sda_validated_steps) + 1,
            "failed_lessons": EMPTY_FAILED_LESSONS_TEXT,
            "re_trac_state": {},
            "repair_state": copy.deepcopy(sda_state),
        }
    else:
        trace = {
            "validated_steps": [],
            "validated_todo_actions": [],
            "current_env": resolved_env,
            "current_robot": env_state,
            "next_step_num": 1,
            "failed_lessons": EMPTY_FAILED_LESSONS_TEXT,
            "re_trac_state": {},
            "repair_state": {},
        }
    trace["repair_strategy"] = repair_strategy
    repair_state = trace.get("repair_state")
    if not isinstance(repair_state, dict):
        repair_state = {}
    trace["repair_state"] = {
        "repair_strategy": repair_strategy,
        **copy.deepcopy(repair_state),
    }
    return trace
