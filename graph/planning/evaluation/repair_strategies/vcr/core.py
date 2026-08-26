from __future__ import annotations

import copy
from collections.abc import Callable, Mapping
from typing import Any

from .causal_checkpoint import select_vcr_repair_checkpoint


Action = dict[str, Any]
ApplyAction = Callable[[dict, dict, str, dict], tuple[bool, str, str]]
ApplyEffect = Callable[[dict, dict, str, dict], None]
GoalTest = Callable[[dict, dict], bool]
SegmentPlanner = Callable[[dict[str, Any]], dict[str, Any]]
SkillPlanningCatalog = Any

VCR_SCHEMA_VERSION = "vcr_v2"
MODE_VCR_COUNTERFACTUAL_REPAIR = "vcr_counterfactual_repair"
VCR_MULTI_INTERVAL_SCHEMA_VERSION = "vcr_multi_interval_v1"
# A zero gap disables causal-window merging. Positive values opt into merging
# overlapping windows and non-overlapping windows separated by that many actions.
DEFAULT_MERGE_GAP_ACTIONS = 0
DEFAULT_MAX_RETRIES = 2


def run_counterfactual_suffix(
    *,
    failed_step: dict,
    failure_env: dict,
    failure_robot: dict,
    suffix_steps: list,
    apply_action: ApplyAction,
    skill_profile: str | None = None,
    skill_handlers: Mapping[str, Any] | None = None,
    goal_test: GoalTest | None = None,
    apply_effect: ApplyEffect | None = None,
) -> dict[str, Any]:
    """Test whether the original suffix works if the failed action had applied.

    The failed action is *not* validated. Its effect comes from the registered
    skill handler's ``apply`` method, while every later action still goes
    through the real sandbox transition function. This keeps the hypothetical
    step explicit and prevents VCR from hardcoding skill effects.
    """
    failed_action = _action_from_step(failed_step)
    skill = failed_action.get("skill", "")
    handler = (skill_handlers or {}).get(skill)
    if handler is None:
        return _counterfactual_failure(
            "failed_skill_handler_unavailable",
            {
                "failed_action": copy.deepcopy(failed_action),
                "profile": skill_profile or "",
            },
        )

    shadow_env = copy.deepcopy(failure_env or {})
    shadow_robot = copy.deepcopy(failure_robot or {})
    try:
        # Deliberately bypass validate(): this is the counterfactual premise.
        if apply_effect is not None:
            apply_effect(
                shadow_env,
                shadow_robot,
                skill,
                copy.deepcopy(failed_action.get("parameters", {})),
            )
        else:
            handler.apply(
                shadow_env,
                shadow_robot,
                copy.deepcopy(failed_action.get("parameters", {})),
            )
    except Exception as exc:
        return _counterfactual_failure(
            "failed_action_effect_unavailable",
            {
                "failed_action": copy.deepcopy(failed_action),
                "effect_source": _handler_source(handler),
                "error": str(exc),
            },
        )

    state_after_failed_effect_env = copy.deepcopy(shadow_env)
    state_after_failed_effect_robot = copy.deepcopy(shadow_robot)
    executed_steps = [_compact_step(failed_step)]
    for raw_step in suffix_steps or []:
        action = _action_from_step(raw_step)
        if not action.get("skill"):
            return _counterfactual_failure(
                "malformed_suffix_step",
                {"step": copy.deepcopy(raw_step), "executed_steps": executed_steps},
            )
        ok, issue, fix = apply_action(
            shadow_env,
            shadow_robot,
            action["skill"],
            action["parameters"],
        )
        if not ok:
            return _counterfactual_failure(
                "shadow_suffix_failed",
                {
                    "step": _compact_step(raw_step),
                    "issue": issue,
                    "fix": fix,
                    "executed_steps": executed_steps,
                },
            )
        executed_steps.append(_compact_step(raw_step))

    if goal_test is not None:
        try:
            if not goal_test(shadow_env, shadow_robot):
                return _counterfactual_failure(
                    "counterfactual_task_not_completed",
                    {
                        "executed_steps": executed_steps,
                        "task_completion": _task_completion_payload(
                            goal_test,
                            "not_completed",
                        ),
                    },
                )
        except Exception as exc:
            return _counterfactual_failure(
                "shadow_goal_test_failed",
                {"error": str(exc), "executed_steps": executed_steps},
            )

    return {
        "success": True,
        "effect_source": _handler_source(handler),
        "executed_steps": executed_steps,
        "final_env": shadow_env,
        "final_robot": shadow_robot,
        "state_after_failed_effect_env": state_after_failed_effect_env,
        "state_after_failed_effect_robot": state_after_failed_effect_robot,
        "goal_evidence": _goal_evidence(goal_test),
        "task_completion": _task_completion_payload(goal_test, "completed"),
    }


def repair_after_counterfactual_failure(
    *,
    todo_list: list,
    validated_steps: list,
    failed_step: dict,
    issue_type: str,
    fix_advice: str,
    failure_env: dict,
    failure_robot: dict,
    trajectory_records: list[dict[str, Any]],
    sandbox_start_env: dict,
    sandbox_start_robot: dict,
    apply_action: ApplyAction,
    max_segment_actions: int = 24,
    max_backtrack_depth: int | None = None,
    merge_gap_actions: int = DEFAULT_MERGE_GAP_ACTIONS,
    max_retries: int = DEFAULT_MAX_RETRIES,
    skill_profile: str | None = None,
    skill_catalog: SkillPlanningCatalog | None = None,
    skill_closure: list[str] | None = None,
    skill_handlers: Mapping[str, Any] | None = None,
    goal_test: GoalTest | None = None,
    apply_effect: ApplyEffect | None = None,
    task_context: dict[str, Any] | None = None,
    segment_planner: SegmentPlanner | None = None,
) -> dict[str, Any]:
    """Repair one or more counterfactually discoverable failure intervals.

    A single failure follows the original VCR v2 path unchanged. When the
    counterfactual suffix exposes more failures, VCR builds causal windows and
    leaves them separate by default. A positive ``merge_gap_actions`` opts into
    merging overlapping and nearby windows. It repairs each remaining window
    and verifies both protected boundaries and the final full-plan replay. A
    rejected proposal is fed back to the planner until ``max_retries`` is
    exhausted.
    """
    steps = [copy.deepcopy(step) for step in (todo_list or []) if isinstance(step, dict)]
    failed_index = _step_index(steps, failed_step)
    if failed_index is None:
        return _repair_failure("failed_step_not_in_todo_list", {"failed_step": _compact_step(failed_step)})

    if skill_catalog is None:
        return _repair_failure("skill_catalog_required", {})
    if skill_handlers is None:
        return _repair_failure("skill_handlers_required", {})
    catalog = skill_catalog
    scan = _scan_counterfactual_failures(
        steps=steps,
        first_failed_index=failed_index,
        first_issue_type=issue_type,
        first_fix_advice=fix_advice,
        failure_env=failure_env,
        failure_robot=failure_robot,
        trajectory_records=trajectory_records,
        apply_action=apply_action,
        skill_profile=skill_profile,
        skill_handlers=skill_handlers,
        goal_test=goal_test,
        apply_effect=apply_effect,
    )
    if not scan.get("success") or len(scan.get("failures", [])) <= 1:
        return _repair_single_counterfactual_failure(
            todo_list=steps,
            validated_steps=validated_steps,
            failed_step=failed_step,
            issue_type=issue_type,
            fix_advice=fix_advice,
            failure_env=failure_env,
            failure_robot=failure_robot,
            trajectory_records=trajectory_records,
            sandbox_start_env=sandbox_start_env,
            sandbox_start_robot=sandbox_start_robot,
            apply_action=apply_action,
            max_segment_actions=max_segment_actions,
            max_backtrack_depth=max_backtrack_depth,
            max_retries=_nonnegative_int(max_retries, DEFAULT_MAX_RETRIES),
            skill_profile=skill_profile,
            skill_catalog=catalog,
            skill_closure=skill_closure,
            skill_handlers=skill_handlers,
            goal_test=goal_test,
            apply_effect=apply_effect,
            task_context=task_context,
            segment_planner=segment_planner,
        )

    return _repair_multiple_counterfactual_failures(
        steps=steps,
        scan=scan,
        sandbox_start_env=sandbox_start_env,
        sandbox_start_robot=sandbox_start_robot,
        apply_action=apply_action,
        max_segment_actions=max_segment_actions,
        max_backtrack_depth=max_backtrack_depth,
        merge_gap_actions=_nonnegative_int(merge_gap_actions, DEFAULT_MERGE_GAP_ACTIONS),
        max_retries=_nonnegative_int(max_retries, DEFAULT_MAX_RETRIES),
        skill_profile=skill_profile,
        skill_catalog=catalog,
        skill_closure=skill_closure,
        skill_handlers=skill_handlers,
        goal_test=goal_test,
        task_context=task_context,
        segment_planner=segment_planner,
    )


def _repair_single_counterfactual_failure(
    *,
    todo_list: list,
    validated_steps: list,
    failed_step: dict,
    issue_type: str,
    fix_advice: str,
    failure_env: dict,
    failure_robot: dict,
    trajectory_records: list[dict[str, Any]],
    sandbox_start_env: dict,
    sandbox_start_robot: dict,
    apply_action: ApplyAction,
    max_segment_actions: int = 24,
    max_backtrack_depth: int | None = None,
    max_retries: int = DEFAULT_MAX_RETRIES,
    skill_profile: str | None = None,
    skill_catalog: SkillPlanningCatalog | None = None,
    skill_closure: list[str] | None = None,
    skill_handlers: Mapping[str, Any] | None = None,
    goal_test: GoalTest | None = None,
    apply_effect: ApplyEffect | None = None,
    task_context: dict[str, Any] | None = None,
    segment_planner: SegmentPlanner | None = None,
) -> dict[str, Any]:
    """Repair a failed step only when its original suffix is counterfactually viable.

    After shadow-validating the suffix, VCR selects a causal rollback checkpoint
    and asks the planning model for only the interval before the failed action.
    It then splices that interval into the immutable plan and replays the complete
    candidate in the sandbox. No local state-space search is performed.
    """
    steps = [copy.deepcopy(step) for step in (todo_list or []) if isinstance(step, dict)]
    failed_index = _step_index(steps, failed_step)
    if failed_index is None:
        return _repair_failure("failed_step_not_in_todo_list", {"failed_step": _compact_step(failed_step)})

    if skill_catalog is None:
        return _repair_failure("skill_catalog_required", {})
    if skill_handlers is None:
        return _repair_failure("skill_handlers_required", {})
    catalog = skill_catalog
    suffix_steps = steps[failed_index + 1 :]
    counterfactual = run_counterfactual_suffix(
        failed_step=failed_step,
        failure_env=failure_env,
        failure_robot=failure_robot,
        suffix_steps=suffix_steps,
        apply_action=apply_action,
        skill_profile=skill_profile,
        skill_handlers=skill_handlers,
        goal_test=goal_test,
        apply_effect=apply_effect,
    )
    if not counterfactual.get("success"):
        return _repair_failure(
            "counterfactual_suffix_not_viable",
            {"counterfactual": _without_final_state(counterfactual)},
        )

    checkpoint = select_vcr_repair_checkpoint(
        todo_list=steps,
        validated_steps=validated_steps,
        failed_step=failed_step,
        issue_type=issue_type,
        fix_advice=fix_advice,
        failure_env=failure_env,
        failure_robot=failure_robot,
        trajectory_records=trajectory_records,
        sandbox_start_env=sandbox_start_env,
        sandbox_start_robot=sandbox_start_robot,
        max_backtrack_depth=max_backtrack_depth,
        skill_profile=skill_profile,
        skill_catalog=catalog,
        skill_closure=skill_closure,
    )
    failed_step_num = _step_number(failed_step) or 0
    cause_step_num = int(checkpoint.get("rollback_step_num") or failed_step_num)
    causal_predicate = str(checkpoint.get("causal_predicate", "") or "")
    cause_index = _step_index_by_number(steps, cause_step_num)
    if cause_index is None:
        cause_index = failed_index

    local_source_steps = steps[cause_index:failed_index]
    terminal_contract = _suffix_effect_contract(
        checkpoint.get("checkpoint_env", {}),
        checkpoint.get("checkpoint_robot", {}),
        counterfactual["final_env"],
        counterfactual["final_robot"],
    )
    allowed_skill_names = sorted(skill_handlers)
    segment_request = _build_segment_request(
        task_context=task_context,
        checkpoint=checkpoint,
        failed_step=failed_step,
        issue_type=issue_type,
        fix_advice=fix_advice,
        original_interval=local_source_steps,
        suffix_steps=suffix_steps,
        counterfactual=counterfactual,
        terminal_contract=terminal_contract,
        catalog=catalog,
        allowed_skill_names=allowed_skill_names,
        max_segment_actions=max_segment_actions,
    )
    max_attempts = max_retries + 1
    retry_history: list[dict[str, Any]] = []
    last_failure_reason = "llm_segment_generation_failed"
    last_failure_details: dict[str, Any] = {}

    for attempt_number in range(1, max_attempts + 1):
        attempt_request, local_plan = _invoke_segment_planner(
            base_request=segment_request,
            attempt_number=attempt_number,
            max_attempts=max_attempts,
            retry_history=retry_history,
            segment_planner=segment_planner,
            skill_profile=skill_profile,
            max_segment_actions=max_segment_actions,
            allowed_skill_names=allowed_skill_names,
        )
        if not local_plan.get("success"):
            last_failure_reason = "llm_segment_generation_failed"
            last_failure_details = {
                "counterfactual": _without_final_state(counterfactual),
                "checkpoint": _compact_checkpoint(checkpoint),
                "local_plan": local_plan,
            }
            retry_history.append(
                _retry_record(
                    attempt_number,
                    last_failure_reason,
                    {
                        "planner_reason": local_plan.get("reason", ""),
                        "planner_details": copy.deepcopy(local_plan.get("details", {})),
                    },
                )
            )
            continue

        candidate_steps = _reindex_steps(
            steps[:cause_index]
            + [_step_from_action(action) for action in local_plan["actions"]]
            + steps[failed_index:]
        )
        replay = _replay_plan(
            candidate_steps,
            sandbox_start_env,
            sandbox_start_robot,
            apply_action,
        )
        if not replay.get("success"):
            last_failure_reason = "real_candidate_replay_failed"
            replay_summary = _without_final_state(replay)
            last_failure_details = {
                "counterfactual": _without_final_state(counterfactual),
                "checkpoint": _compact_checkpoint(checkpoint),
                "local_plan": local_plan,
                "replay": replay_summary,
            }
            retry_history.append(
                _retry_record(
                    attempt_number,
                    last_failure_reason,
                    {"replay": replay_summary},
                )
            )
            continue

        if terminal_contract and not _contract_holds(
            terminal_contract,
            replay["final_env"],
            replay["final_robot"],
        ):
            last_failure_reason = "counterfactual_terminal_contract_not_preserved"
            last_failure_details = {
                "counterfactual": _without_final_state(counterfactual),
                "checkpoint": _compact_checkpoint(checkpoint),
                "local_plan": local_plan,
                "terminal_contract": terminal_contract,
            }
            retry_history.append(
                _retry_record(attempt_number, last_failure_reason, {})
            )
            continue

        if goal_test is not None:
            try:
                goal_reached = goal_test(replay["final_env"], replay["final_robot"])
            except Exception as exc:
                return _repair_failure(
                    "real_candidate_goal_test_failed",
                    {
                        "error": str(exc),
                        "local_plan": local_plan,
                        "attempt_count": attempt_number,
                        "max_retries": max_retries,
                        "retry_history": copy.deepcopy(retry_history),
                    },
                )
            if not goal_reached:
                last_failure_reason = "real_candidate_goal_not_reached"
                last_failure_details = {
                    "counterfactual": _without_final_state(counterfactual),
                    "checkpoint": _compact_checkpoint(checkpoint),
                    "local_plan": local_plan,
                }
                retry_history.append(
                    _retry_record(attempt_number, last_failure_reason, {})
                )
                continue

        _attach_retry_stats(
            local_plan,
            attempt_number=attempt_number,
            max_retries=max_retries,
            retry_history=retry_history,
        )
        segment_request = attempt_request
        break
    else:
        return _repair_failure(
            last_failure_reason,
            _retry_exhausted_details(
                last_failure_details,
                max_retries=max_retries,
                retry_history=retry_history,
            ),
        )

    vcr_state = {
        "version": VCR_SCHEMA_VERSION,
        "mode": MODE_VCR_COUNTERFACTUAL_REPAIR,
        "failure": {
            "issue_type": issue_type,
            "fix_advice": fix_advice,
            "failed_step": _compact_step(failed_step),
        },
        "counterfactual": _without_final_state(counterfactual),
        "causal_rollback": {
            "selected_step": cause_step_num,
            "reason": checkpoint.get("reason", ""),
            "causal_predicate": causal_predicate,
            "causal_action": copy.deepcopy(checkpoint.get("causal_action")),
        },
        "state_dependency_graph": copy.deepcopy(checkpoint.get("state_dependency_graph", {})),
        "local_task": {
            "initial_state": {
                "environment": copy.deepcopy(checkpoint.get("checkpoint_env", {})),
                "robot": copy.deepcopy(checkpoint.get("checkpoint_robot", {})),
            },
            "goal": {
                "type": "failed_action_and_continuation_requirements",
                "action": _compact_step(failed_step),
            },
            "failure_requirement": copy.deepcopy(segment_request["failure_requirement"]),
            "continuation_requirements": copy.deepcopy(
                segment_request["protected_continuation"]["possible_conditions"]
            ),
            "replaced_original_steps": [_compact_step(step) for step in local_source_steps],
            "replacement_actions": [_step_from_action(action) for action in local_plan["actions"]],
            "repair_summary": local_plan.get("repair_summary", ""),
            "planner_stats": copy.deepcopy(local_plan.get("planner_stats", {})),
        },
        "final_verification": {
            "sandbox_replay": "passed",
            "goal_evidence": (
                counterfactual.get("goal_evidence", "")
                if goal_test is not None
                else "counterfactual_terminal_contract"
            ),
            "terminal_contract": terminal_contract,
        },
    }
    return {
        "success": True,
        "todo_list": candidate_steps,
        "validated_steps": candidate_steps,
        "checkpoint_env": replay["final_env"],
        "checkpoint_robot": replay["final_robot"],
        "trajectory_records": replay.get("trajectory_records", []),
        "vcr_state": vcr_state,
    }


def _scan_counterfactual_failures(
    *,
    steps: list,
    first_failed_index: int,
    first_issue_type: str,
    first_fix_advice: str,
    failure_env: dict,
    failure_robot: dict,
    trajectory_records: list[dict[str, Any]],
    apply_action: ApplyAction,
    skill_profile: str | None,
    skill_handlers: Mapping[str, Any],
    goal_test: GoalTest | None,
    apply_effect: ApplyEffect | None = None,
) -> dict[str, Any]:
    """Continue past failures by applying registered effects and collect them."""
    handlers = skill_handlers
    env = copy.deepcopy(failure_env or {})
    robot = copy.deepcopy(failure_robot or {})
    records = copy.deepcopy(trajectory_records or [])
    failures: list[dict[str, Any]] = []
    states_before: dict[int, dict[str, Any]] = {}
    states_after: dict[int, dict[str, Any]] = {}
    executed_steps: list[dict[str, Any]] = []

    for index in range(first_failed_index, len(steps)):
        step = steps[index]
        action = _action_from_step(step)
        if not action.get("skill"):
            return _counterfactual_failure(
                "malformed_suffix_step",
                {"step": copy.deepcopy(step), "executed_steps": executed_steps},
            )

        before_env = copy.deepcopy(env)
        before_robot = copy.deepcopy(robot)
        states_before[index] = {
            "environment": copy.deepcopy(before_env),
            "robot": copy.deepcopy(before_robot),
        }
        record_count_before = len(records)

        if index == first_failed_index:
            ok = False
            issue = first_issue_type
            fix = first_fix_advice
        else:
            ok, issue, fix = apply_action(
                env,
                robot,
                action["skill"],
                action["parameters"],
            )

        counterfactual = not ok
        effect_source = ""
        if counterfactual:
            # A failing transition may have partially mutated its arguments.
            # Restore the real pre-action state before applying the premise.
            env = copy.deepcopy(before_env)
            robot = copy.deepcopy(before_robot)
            handler = handlers.get(action["skill"])
            if handler is None:
                return _counterfactual_failure(
                    "failed_skill_handler_unavailable",
                    {
                        "failed_action": copy.deepcopy(action),
                        "failed_step": _compact_step(step),
                        "profile": skill_profile or "",
                        "executed_steps": executed_steps,
                    },
                )
            try:
                if apply_effect is not None:
                    apply_effect(
                        env,
                        robot,
                        action["skill"],
                        copy.deepcopy(action["parameters"]),
                    )
                else:
                    handler.apply(env, robot, copy.deepcopy(action["parameters"]))
            except Exception as exc:
                return _counterfactual_failure(
                    "failed_action_effect_unavailable",
                    {
                        "failed_action": copy.deepcopy(action),
                        "failed_step": _compact_step(step),
                        "effect_source": _handler_source(handler),
                        "error": str(exc),
                        "executed_steps": executed_steps,
                    },
                )
            effect_source = _handler_source(handler)
            failures.append(
                {
                    "index": index,
                    "step": copy.deepcopy(step),
                    "issue_type": str(issue or ""),
                    "fix_advice": str(fix or ""),
                    "failure_env": copy.deepcopy(before_env),
                    "failure_robot": copy.deepcopy(before_robot),
                    "state_after_effect_env": copy.deepcopy(env),
                    "state_after_effect_robot": copy.deepcopy(robot),
                    "effect_source": effect_source,
                    "trajectory_count_before": record_count_before,
                }
            )

        after_env = copy.deepcopy(env)
        after_robot = copy.deepcopy(robot)
        states_after[index] = {
            "environment": copy.deepcopy(after_env),
            "robot": copy.deepcopy(after_robot),
        }
        records.append(
            {
                "step": copy.deepcopy(step),
                "before_env": before_env,
                "before_robot": before_robot,
                "after_env": after_env,
                "after_robot": after_robot,
                "counterfactual": counterfactual,
                "effect_source": effect_source,
            }
        )
        executed_steps.append(_compact_step(step))

    if goal_test is not None:
        try:
            if not goal_test(env, robot):
                return _counterfactual_failure(
                    "counterfactual_task_not_completed",
                    {
                        "executed_steps": executed_steps,
                        "failures": [_compact_scanned_failure(item) for item in failures],
                        "task_completion": _task_completion_payload(
                            goal_test,
                            "not_completed",
                        ),
                    },
                )
        except Exception as exc:
            return _counterfactual_failure(
                "shadow_goal_test_failed",
                {"error": str(exc), "executed_steps": executed_steps},
            )

    return {
        "success": True,
        "failures": failures,
        "trajectory_records": records,
        "states_before": states_before,
        "states_after": states_after,
        "executed_steps": executed_steps,
        "final_env": copy.deepcopy(env),
        "final_robot": copy.deepcopy(robot),
        "goal_evidence": _goal_evidence(goal_test),
        "task_completion": _task_completion_payload(goal_test, "completed"),
    }


def analyze_counterfactual_failure_windows(
    *,
    steps: list,
    first_failed_index: int,
    first_issue_type: str,
    first_fix_advice: str,
    failure_env: dict,
    failure_robot: dict,
    trajectory_records: list[dict[str, Any]],
    sandbox_start_env: dict,
    sandbox_start_robot: dict,
    apply_action: ApplyAction,
    max_backtrack_depth: int | None,
    skill_profile: str | None,
    skill_catalog: SkillPlanningCatalog,
    skill_closure: list[str] | None = None,
    skill_handlers: Mapping[str, Any],
    goal_test: GoalTest | None = None,
    apply_effect: ApplyEffect | None = None,
) -> dict[str, Any]:
    """Find every counterfactual failure and its independent causal window."""

    scan = _scan_counterfactual_failures(
        steps=steps,
        first_failed_index=first_failed_index,
        first_issue_type=first_issue_type,
        first_fix_advice=first_fix_advice,
        failure_env=failure_env,
        failure_robot=failure_robot,
        trajectory_records=trajectory_records,
        apply_action=apply_action,
        skill_profile=skill_profile,
        skill_handlers=skill_handlers,
        goal_test=goal_test,
        apply_effect=apply_effect,
    )
    if not scan.get("success"):
        return scan
    windows = _build_causal_repair_windows(
        steps=steps,
        scan=scan,
        sandbox_start_env=sandbox_start_env,
        sandbox_start_robot=sandbox_start_robot,
        max_backtrack_depth=max_backtrack_depth,
        skill_profile=skill_profile,
        skill_catalog=skill_catalog,
        skill_closure=skill_closure,
    )
    if not windows:
        return _counterfactual_failure(
            "counterfactual_repair_windows_empty",
            {"failure_count": len(scan.get("failures", []))},
        )
    return {
        "success": True,
        "failures": scan["failures"],
        "windows": windows,
        "executed_steps": scan.get("executed_steps", []),
        "states_before": copy.deepcopy(scan.get("states_before", {})),
        "states_after": copy.deepcopy(scan.get("states_after", {})),
        "final_env": copy.deepcopy(scan.get("final_env", {})),
        "final_robot": copy.deepcopy(scan.get("final_robot", {})),
        "goal_evidence": scan.get("goal_evidence", ""),
        "task_completion": copy.deepcopy(scan.get("task_completion", {})),
    }


def merge_causal_repair_windows(
    windows: list[dict[str, Any]],
    merge_gap_actions: int = DEFAULT_MERGE_GAP_ACTIONS,
) -> list[dict[str, Any]]:
    """Keep windows separate by default; merge them only when explicitly enabled."""

    return _merge_repair_windows(
        windows,
        _nonnegative_int(merge_gap_actions, DEFAULT_MERGE_GAP_ACTIONS),
    )


def _repair_multiple_counterfactual_failures(
    *,
    steps: list,
    scan: dict[str, Any],
    sandbox_start_env: dict,
    sandbox_start_robot: dict,
    apply_action: ApplyAction,
    max_segment_actions: int,
    max_backtrack_depth: int | None,
    merge_gap_actions: int,
    max_retries: int,
    skill_profile: str | None,
    skill_catalog: SkillPlanningCatalog,
    skill_closure: list[str] | None,
    skill_handlers: Mapping[str, Any],
    goal_test: GoalTest | None,
    task_context: dict[str, Any] | None,
    segment_planner: SegmentPlanner | None,
) -> dict[str, Any]:
    windows = _build_multi_repair_windows(
        steps=steps,
        scan=scan,
        sandbox_start_env=sandbox_start_env,
        sandbox_start_robot=sandbox_start_robot,
        max_backtrack_depth=max_backtrack_depth,
        merge_gap_actions=merge_gap_actions,
        skill_profile=skill_profile,
        skill_catalog=skill_catalog,
        skill_closure=skill_closure,
    )
    if not windows:
        return _repair_failure("counterfactual_repair_windows_empty", {})

    allowed_skill_names = sorted(skill_handlers)
    planned_windows: list[dict[str, Any]] = []
    scan_summary = _compact_counterfactual_scan(scan)

    for window_index, window in enumerate(windows):
        next_start_index = windows[window_index + 1]["start_index"] if window_index + 1 < len(windows) else len(steps)
        anchor_index = window["anchor_index"]
        anchor_failure = max(window["failures"], key=lambda item: int(item["index"]))
        protected_steps = steps[anchor_index + 1 : next_start_index]

        if next_start_index < len(steps):
            expected_boundary = scan.get("states_before", {}).get(next_start_index)
        else:
            expected_boundary = {
                "environment": copy.deepcopy(scan.get("final_env", {})),
                "robot": copy.deepcopy(scan.get("final_robot", {})),
            }
        if not isinstance(expected_boundary, dict):
            return _repair_failure(
                "counterfactual_boundary_state_missing",
                {"window_index": window_index + 1, "next_start_index": next_start_index},
            )

        counterfactual = {
            "success": True,
            "effect_source": anchor_failure.get("effect_source", ""),
            "executed_steps": [_compact_step(anchor_failure["step"])]
            + [_compact_step(step) for step in protected_steps],
            "state_after_failed_effect_env": copy.deepcopy(anchor_failure.get("state_after_effect_env", {})),
            "state_after_failed_effect_robot": copy.deepcopy(anchor_failure.get("state_after_effect_robot", {})),
            "final_env": copy.deepcopy(expected_boundary.get("environment", {})),
            "final_robot": copy.deepcopy(expected_boundary.get("robot", {})),
            "goal_evidence": "protected_boundary" if next_start_index < len(steps) else scan.get("goal_evidence", ""),
        }
        terminal_contract = _suffix_effect_contract(
            window["checkpoint"].get("checkpoint_env", {}),
            window["checkpoint"].get("checkpoint_robot", {}),
            counterfactual["final_env"],
            counterfactual["final_robot"],
        )
        failure_requirements = [
            _failure_requirement(item, skill_catalog)
            for item in sorted(window["failures"], key=lambda value: int(value["index"]))
        ]
        original_interval = steps[window["start_index"] : anchor_index + 1]
        base_request = _build_segment_request(
            task_context=task_context,
            checkpoint=window["checkpoint"],
            failed_step=anchor_failure["step"],
            issue_type=anchor_failure["issue_type"],
            fix_advice=anchor_failure["fix_advice"],
            original_interval=original_interval,
            suffix_steps=protected_steps,
            counterfactual=counterfactual,
            terminal_contract=terminal_contract,
            catalog=skill_catalog,
            allowed_skill_names=allowed_skill_names,
            max_segment_actions=max_segment_actions,
            failure_requirements=failure_requirements,
            repair_window={
                "window_index": window_index + 1,
                "window_count": len(windows),
                "original_start_step": _step_number(steps[window["start_index"]]),
                "anchor_failed_step": _step_number(steps[anchor_index]),
                "failure_count": len(window["failures"]),
                "merged": len(window["source_windows"]) > 1,
                "replace_anchor_failed_step": True,
                "merge_reasons": list(window.get("merge_reasons", [])),
                "merge_gap_actions": merge_gap_actions,
                "next_protected_boundary_step": (
                    _step_number(steps[next_start_index]) if next_start_index < len(steps) else None
                ),
            },
            boundary_state=expected_boundary,
        )
        max_attempts = max_retries + 1
        retry_history: list[dict[str, Any]] = []
        last_failure_reason = "llm_segment_generation_failed"
        last_failure_details: dict[str, Any] = {}

        for attempt_number in range(1, max_attempts + 1):
            request, local_plan = _invoke_segment_planner(
                base_request=base_request,
                attempt_number=attempt_number,
                max_attempts=max_attempts,
                retry_history=retry_history,
                segment_planner=segment_planner,
                skill_profile=skill_profile,
                max_segment_actions=max_segment_actions,
                allowed_skill_names=allowed_skill_names,
            )
            if not local_plan.get("success"):
                last_failure_reason = "llm_segment_generation_failed"
                last_failure_details = {
                    "counterfactual": scan_summary,
                    "checkpoint": _compact_checkpoint(window["checkpoint"]),
                    "local_plan": local_plan,
                    "repair_window": copy.deepcopy(request["repair_window"]),
                }
                retry_history.append(
                    _retry_record(
                        attempt_number,
                        last_failure_reason,
                        {
                            "planner_reason": local_plan.get("reason", ""),
                            "planner_details": copy.deepcopy(local_plan.get("details", {})),
                        },
                    )
                )
                continue

            local_candidate = [_step_from_action(action) for action in local_plan["actions"]] + [
                copy.deepcopy(step) for step in protected_steps
            ]
            local_replay = _replay_plan(
                local_candidate,
                window["checkpoint"].get("checkpoint_env", {}),
                window["checkpoint"].get("checkpoint_robot", {}),
                apply_action,
            )
            if not local_replay.get("success"):
                last_failure_reason = "real_candidate_replay_failed"
                replay_summary = _without_final_state(local_replay)
                last_failure_details = {
                    "counterfactual": scan_summary,
                    "checkpoint": _compact_checkpoint(window["checkpoint"]),
                    "local_plan": local_plan,
                    "repair_window": copy.deepcopy(request["repair_window"]),
                    "replay": replay_summary,
                }
                retry_history.append(
                    _retry_record(
                        attempt_number,
                        last_failure_reason,
                        {"replay": replay_summary},
                    )
                )
                continue

            if next_start_index < len(steps):
                if not _state_snapshots_equal(
                    expected_boundary.get("environment", {}),
                    expected_boundary.get("robot", {}),
                    local_replay["final_env"],
                    local_replay["final_robot"],
                ):
                    last_failure_reason = "protected_boundary_not_preserved"
                    boundary_details = {
                        "expected_robot": copy.deepcopy(expected_boundary.get("robot", {})),
                        "actual_robot": copy.deepcopy(local_replay.get("final_robot", {})),
                        "environment_matches": expected_boundary.get("environment", {})
                        == local_replay.get("final_env", {}),
                    }
                    last_failure_details = {
                        "counterfactual": scan_summary,
                        "repair_window": copy.deepcopy(request["repair_window"]),
                        **boundary_details,
                    }
                    retry_history.append(
                        _retry_record(attempt_number, last_failure_reason, boundary_details)
                    )
                    continue
            elif terminal_contract and not _contract_holds(
                terminal_contract,
                local_replay["final_env"],
                local_replay["final_robot"],
            ):
                last_failure_reason = "counterfactual_terminal_contract_not_preserved"
                last_failure_details = {
                    "counterfactual": scan_summary,
                    "repair_window": copy.deepcopy(request["repair_window"]),
                    "local_plan": local_plan,
                    "terminal_contract": terminal_contract,
                }
                retry_history.append(
                    _retry_record(attempt_number, last_failure_reason, {})
                )
                continue

            if next_start_index >= len(steps) and goal_test is not None:
                try:
                    goal_reached = goal_test(
                        local_replay["final_env"],
                        local_replay["final_robot"],
                    )
                except Exception as exc:
                    return _repair_failure(
                        "real_candidate_goal_test_failed",
                        {
                            "error": str(exc),
                            "local_plan": local_plan,
                            "repair_window": copy.deepcopy(request["repair_window"]),
                            "attempt_count": attempt_number,
                            "max_retries": max_retries,
                            "retry_history": copy.deepcopy(retry_history),
                        },
                    )
                if not goal_reached:
                    last_failure_reason = "real_candidate_goal_not_reached"
                    last_failure_details = {
                        "counterfactual": scan_summary,
                        "repair_window": copy.deepcopy(request["repair_window"]),
                        "local_plan": local_plan,
                    }
                    retry_history.append(
                        _retry_record(attempt_number, last_failure_reason, {})
                    )
                    continue

            _attach_retry_stats(
                local_plan,
                attempt_number=attempt_number,
                max_retries=max_retries,
                retry_history=retry_history,
            )
            break
        else:
            return _repair_failure(
                last_failure_reason,
                _retry_exhausted_details(
                    last_failure_details,
                    max_retries=max_retries,
                    retry_history=retry_history,
                ),
            )

        planned_windows.append(
            {
                **copy.deepcopy(window),
                "request": request,
                "local_plan": local_plan,
                "terminal_contract": terminal_contract,
                "next_start_index": next_start_index,
            }
        )

    candidate_steps = _assemble_multi_interval_candidate(steps, planned_windows)
    replay = _replay_plan(candidate_steps, sandbox_start_env, sandbox_start_robot, apply_action)
    if not replay.get("success"):
        return _repair_failure(
            "real_candidate_replay_failed",
            {
                "counterfactual": scan_summary,
                "repair_windows": [_compact_planned_window(item) for item in planned_windows],
                "replay": _without_final_state(replay),
            },
        )

    final_contract = planned_windows[-1]["terminal_contract"]
    if final_contract and not _contract_holds(final_contract, replay["final_env"], replay["final_robot"]):
        return _repair_failure(
            "counterfactual_terminal_contract_not_preserved",
            {
                "counterfactual": scan_summary,
                "repair_windows": [_compact_planned_window(item) for item in planned_windows],
                "terminal_contract": final_contract,
            },
        )
    if goal_test is not None:
        try:
            if not goal_test(replay["final_env"], replay["final_robot"]):
                return _repair_failure(
                    "real_candidate_goal_not_reached",
                    {
                        "counterfactual": scan_summary,
                        "repair_windows": [_compact_planned_window(item) for item in planned_windows],
                    },
                )
        except Exception as exc:
            return _repair_failure(
                "real_candidate_goal_test_failed",
                {"error": str(exc), "repair_windows": [_compact_planned_window(item) for item in planned_windows]},
            )

    primary = planned_windows[0]
    first_failure = min(scan["failures"], key=lambda item: int(item["index"]))
    primary_task = _local_task_state(primary)
    vcr_state = {
        "version": VCR_SCHEMA_VERSION,
        "mode": MODE_VCR_COUNTERFACTUAL_REPAIR,
        "multi_interval_version": VCR_MULTI_INTERVAL_SCHEMA_VERSION,
        "failure": {
            "issue_type": first_failure["issue_type"],
            "fix_advice": first_failure["fix_advice"],
            "failed_step": _compact_step(first_failure["step"]),
        },
        "counterfactual": scan_summary,
        "causal_rollback": {
            "selected_step": primary["checkpoint"].get("rollback_step_num"),
            "reason": primary["checkpoint"].get("reason", ""),
            "causal_predicate": primary["checkpoint"].get("causal_predicate", ""),
            "causal_action": copy.deepcopy(primary["checkpoint"].get("causal_action")),
        },
        "state_dependency_graph": copy.deepcopy(primary["checkpoint"].get("state_dependency_graph", {})),
        "local_task": primary_task,
        "repair_windows": [_window_state_payload(item) for item in planned_windows],
        "protected_segments": _protected_segment_spans(steps, planned_windows),
        "planner_stats": {
            "window_count": len(planned_windows),
            "counterfactual_failure_count": len(scan.get("failures", [])),
            "replacement_action_count": sum(len(item["local_plan"]["actions"]) for item in planned_windows),
            "attempt_count": sum(
                int(item["local_plan"].get("planner_stats", {}).get("attempt_count", 1))
                for item in planned_windows
            ),
            "retry_count": sum(
                int(item["local_plan"].get("planner_stats", {}).get("retry_count", 0))
                for item in planned_windows
            ),
            "max_retries_per_window": max_retries,
        },
        "final_verification": {
            "sandbox_replay": "passed",
            "goal_evidence": scan.get("goal_evidence", ""),
            "terminal_contract": final_contract,
        },
    }
    return {
        "success": True,
        "todo_list": candidate_steps,
        "validated_steps": candidate_steps,
        "checkpoint_env": replay["final_env"],
        "checkpoint_robot": replay["final_robot"],
        "trajectory_records": replay.get("trajectory_records", []),
        "vcr_state": vcr_state,
    }


def _build_multi_repair_windows(
    *,
    steps: list,
    scan: dict[str, Any],
    sandbox_start_env: dict,
    sandbox_start_robot: dict,
    max_backtrack_depth: int | None,
    merge_gap_actions: int,
    skill_profile: str | None,
    skill_catalog: SkillPlanningCatalog,
    skill_closure: list[str] | None,
) -> list[dict[str, Any]]:
    windows = _build_causal_repair_windows(
        steps=steps,
        scan=scan,
        sandbox_start_env=sandbox_start_env,
        sandbox_start_robot=sandbox_start_robot,
        max_backtrack_depth=max_backtrack_depth,
        skill_profile=skill_profile,
        skill_catalog=skill_catalog,
        skill_closure=skill_closure,
    )
    return _merge_repair_windows(windows, merge_gap_actions)


def _build_causal_repair_windows(
    *,
    steps: list,
    scan: dict[str, Any],
    sandbox_start_env: dict,
    sandbox_start_robot: dict,
    max_backtrack_depth: int | None,
    skill_profile: str | None,
    skill_catalog: SkillPlanningCatalog,
    skill_closure: list[str] | None,
) -> list[dict[str, Any]]:
    windows: list[dict[str, Any]] = []
    all_records = scan.get("trajectory_records", [])
    for failure in sorted(scan.get("failures", []), key=lambda item: int(item["index"])):
        failure_index = int(failure["index"])
        checkpoint = select_vcr_repair_checkpoint(
            todo_list=steps,
            validated_steps=steps[:failure_index],
            failed_step=failure["step"],
            issue_type=failure["issue_type"],
            fix_advice=failure["fix_advice"],
            failure_env=failure["failure_env"],
            failure_robot=failure["failure_robot"],
            trajectory_records=all_records[: int(failure["trajectory_count_before"])],
            sandbox_start_env=sandbox_start_env,
            sandbox_start_robot=sandbox_start_robot,
            max_backtrack_depth=max_backtrack_depth,
            skill_profile=skill_profile,
            skill_catalog=skill_catalog,
            skill_closure=skill_closure,
        )
        cause_number = int(checkpoint.get("rollback_step_num") or (_step_number(failure["step"]) or 0))
        cause_index = _step_index_by_number(steps, cause_number)
        if cause_index is None or cause_index > failure_index:
            cause_index = failure_index
        windows.append(
            {
                "start_index": cause_index,
                "anchor_index": failure_index,
                "failures": [copy.deepcopy(failure)],
                "checkpoint": checkpoint,
                "source_windows": [
                    {
                        "start_index": cause_index,
                        "anchor_index": failure_index,
                    }
                ],
                "merge_reasons": [],
            }
        )
    return windows


def _merge_repair_windows(windows: list[dict[str, Any]], merge_gap_actions: int) -> list[dict[str, Any]]:
    ordered = sorted(
        windows,
        key=lambda item: (int(item["start_index"]), int(item["anchor_index"])),
    )
    if merge_gap_actions <= 0:
        return [copy.deepcopy(window) for window in ordered]

    merged: list[dict[str, Any]] = []
    for raw_window in ordered:
        window = copy.deepcopy(raw_window)
        if not merged:
            merged.append(window)
            continue
        current = merged[-1]
        protected_gap = int(window["start_index"]) - int(current["anchor_index"]) - 1
        overlaps = int(window["start_index"]) <= int(current["anchor_index"])
        nearby = (
            not overlaps
            and protected_gap <= merge_gap_actions
        )
        if not overlaps and not nearby:
            merged.append(window)
            continue

        current["anchor_index"] = max(int(current["anchor_index"]), int(window["anchor_index"]))
        current["failures"].extend(copy.deepcopy(window["failures"]))
        current["failures"].sort(key=lambda item: int(item["index"]))
        current["source_windows"].extend(copy.deepcopy(window["source_windows"]))
        reason = "overlapping_causal_windows" if overlaps else f"nearby_gap_{max(0, protected_gap)}"
        if reason not in current["merge_reasons"]:
            current["merge_reasons"].append(reason)
    return merged


def _failure_requirement(failure: dict[str, Any], catalog: SkillPlanningCatalog) -> dict[str, Any]:
    return {
        "failed_step": _compact_step(failure.get("step")),
        "sandbox_issue": str(failure.get("issue_type", "") or ""),
        "sandbox_fix": str(failure.get("fix_advice", "") or ""),
        "skill_contract": _step_skill_contract(failure.get("step"), catalog),
    }


def _assemble_multi_interval_candidate(steps: list, planned_windows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    assembled: list[dict[str, Any]] = []
    cursor = 0
    for window in planned_windows:
        start_index = int(window["start_index"])
        anchor_index = int(window["anchor_index"])
        assembled.extend(copy.deepcopy(steps[cursor:start_index]))
        assembled.extend(_step_from_action(action) for action in window["local_plan"]["actions"])
        cursor = anchor_index + 1
    assembled.extend(copy.deepcopy(steps[cursor:]))
    return _reindex_steps(assembled)


def _state_snapshots_equal(
    expected_env: dict,
    expected_robot: dict,
    actual_env: dict,
    actual_robot: dict,
) -> bool:
    return expected_env == actual_env and expected_robot == actual_robot


def _compact_scanned_failure(failure: dict[str, Any]) -> dict[str, Any]:
    return {
        "step": _compact_step(failure.get("step")),
        "issue_type": str(failure.get("issue_type", "") or ""),
        "fix_advice": str(failure.get("fix_advice", "") or ""),
        "effect_source": str(failure.get("effect_source", "") or ""),
    }


def _compact_counterfactual_scan(scan: dict[str, Any]) -> dict[str, Any]:
    failures = [_compact_scanned_failure(item) for item in scan.get("failures", [])]
    return {
        "success": True,
        "effect_source": failures[0].get("effect_source", "") if failures else "",
        "effect_sources": [item.get("effect_source", "") for item in failures],
        "executed_steps": copy.deepcopy(scan.get("executed_steps", [])),
        "failures": failures,
        "failure_count": len(failures),
        "goal_evidence": scan.get("goal_evidence", ""),
    }


def _local_task_state(window: dict[str, Any]) -> dict[str, Any]:
    request = window["request"]
    local_plan = window["local_plan"]
    return {
        "initial_state": {
            "environment": copy.deepcopy(window["checkpoint"].get("checkpoint_env", {})),
            "robot": copy.deepcopy(window["checkpoint"].get("checkpoint_robot", {})),
        },
        "goal": {
            "type": "failure_window_and_boundary_requirements",
            "action": copy.deepcopy(request["failure_requirement"]["failed_step"]),
        },
        "failure_requirement": copy.deepcopy(request["failure_requirement"]),
        "failure_requirements": copy.deepcopy(request.get("failure_requirements", [])),
        "continuation_requirements": copy.deepcopy(
            request["protected_continuation"]["possible_conditions"]
        ),
        "replaced_original_steps": copy.deepcopy(request["original_replaced_interval"]),
        "replacement_actions": [_step_from_action(action) for action in local_plan["actions"]],
        "repair_summary": local_plan.get("repair_summary", ""),
        "planner_stats": copy.deepcopy(local_plan.get("planner_stats", {})),
    }


def _compact_planned_window(window: dict[str, Any]) -> dict[str, Any]:
    return {
        "repair_window": copy.deepcopy(window["request"].get("repair_window", {})),
        "checkpoint": _compact_checkpoint(window["checkpoint"]),
        "failures": [_compact_scanned_failure(item) for item in window["failures"]],
        "local_plan": copy.deepcopy(window["local_plan"]),
    }


def _window_state_payload(window: dict[str, Any]) -> dict[str, Any]:
    payload = _compact_planned_window(window)
    payload["local_task"] = _local_task_state(window)
    payload["boundary_contract"] = {
        "next_start_step": window["request"]["repair_window"].get("next_protected_boundary_step"),
        "terminal_contract": copy.deepcopy(window["terminal_contract"]),
    }
    return payload


def _protected_segment_spans(steps: list, planned_windows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    cursor = 0
    for window in planned_windows:
        start_index = int(window["start_index"])
        if cursor < start_index:
            spans.append(
                {
                    "start_step": _step_number(steps[cursor]),
                    "end_step": _step_number(steps[start_index - 1]),
                }
            )
        cursor = int(window["anchor_index"]) + 1
    if cursor < len(steps):
        spans.append(
            {
                "start_step": _step_number(steps[cursor]),
                "end_step": _step_number(steps[-1]),
            }
        )
    return spans


def _nonnegative_int(value: Any, default: int) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return max(0, int(default))


def _build_segment_request(
    *,
    task_context: dict[str, Any] | None,
    checkpoint: dict[str, Any],
    failed_step: dict,
    issue_type: str,
    fix_advice: str,
    original_interval: list,
    suffix_steps: list,
    counterfactual: dict[str, Any],
    terminal_contract: list[dict[str, Any]],
    catalog: SkillPlanningCatalog,
    allowed_skill_names: list[str],
    max_segment_actions: int,
    failure_requirements: list[dict[str, Any]] | None = None,
    repair_window: dict[str, Any] | None = None,
    boundary_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    primary_failure_requirement = {
        "failed_step": _compact_step(failed_step),
        "sandbox_issue": issue_type,
        "sandbox_fix": fix_advice,
        "skill_contract": _step_skill_contract(failed_step, catalog),
    }
    all_failure_requirements = copy.deepcopy(failure_requirements or [primary_failure_requirement])
    if all_failure_requirements:
        primary_failure_requirement = copy.deepcopy(all_failure_requirements[-1])
    return {
        "task_context": copy.deepcopy(task_context or {}),
        "repair_window": copy.deepcopy(repair_window or {}),
        "cause_checkpoint": {
            "selected_step": checkpoint.get("rollback_step_num"),
            "causal_predicate": checkpoint.get("causal_predicate", ""),
            "environment": copy.deepcopy(checkpoint.get("checkpoint_env", {})),
            "robot": copy.deepcopy(checkpoint.get("checkpoint_robot", {})),
        },
        "failure_requirement": primary_failure_requirement,
        "failure_requirements": all_failure_requirements,
        "original_replaced_interval": [_compact_step(step) for step in original_interval],
        "protected_continuation": {
            "suffix_steps": [_compact_step(step) for step in suffix_steps],
            "possible_conditions": [
                {
                    "step": _compact_step(step),
                    "skill_contract": _step_skill_contract(step, catalog),
                }
                for step in suffix_steps
            ],
            "expected_state_after_failed_action": {
                "environment": copy.deepcopy(counterfactual.get("state_after_failed_effect_env", {})),
                "robot": copy.deepcopy(counterfactual.get("state_after_failed_effect_robot", {})),
            },
            "terminal_contract": copy.deepcopy(terminal_contract),
            "boundary_state": copy.deepcopy(boundary_state or {}),
        },
        "constraints": {
            "allowed_skill_names": list(allowed_skill_names),
            "max_segment_actions": max_segment_actions,
            "output_scope": (
                "actions_replacing_entire_repair_window_including_anchor_failed_step"
                if (repair_window or {}).get("replace_anchor_failed_step") is True
                else "actions_inside_repair_window_before_anchor_failed_step_only"
            ),
        },
    }


def _invoke_segment_planner(
    *,
    base_request: dict[str, Any],
    attempt_number: int,
    max_attempts: int,
    retry_history: list[dict[str, Any]],
    segment_planner: SegmentPlanner | None,
    skill_profile: str | None,
    max_segment_actions: int,
    allowed_skill_names: list[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    request = copy.deepcopy(base_request)
    request["retry_context"] = {
        "attempt_number": attempt_number,
        "max_attempts": max_attempts,
        "is_retry": attempt_number > 1,
        "previous_failures": copy.deepcopy(retry_history),
    }
    try:
        raw_plan = (
            segment_planner(copy.deepcopy(request))
            if segment_planner is not None
            else {
                "success": False,
                "reason": "segment_planner_required",
                "details": {},
            }
        )
    except Exception as exc:
        raw_plan = {
            "success": False,
            "reason": "segment_planner_exception",
            "details": {"error": str(exc)},
        }
    local_plan = _normalize_segment_plan(
        raw_plan,
        allowed_skill_names=allowed_skill_names,
        max_segment_actions=max_segment_actions,
    )
    return request, local_plan


def _retry_record(attempt_number: int, reason: str, details: dict[str, Any]) -> dict[str, Any]:
    return {
        "attempt_number": attempt_number,
        "reason": reason,
        "details": copy.deepcopy(details),
    }


def _attach_retry_stats(
    local_plan: dict[str, Any],
    *,
    attempt_number: int,
    max_retries: int,
    retry_history: list[dict[str, Any]],
) -> None:
    planner_stats = local_plan.setdefault("planner_stats", {})
    planner_stats["attempt_count"] = attempt_number
    planner_stats["retry_count"] = attempt_number - 1
    planner_stats["max_retries"] = max_retries
    if retry_history:
        planner_stats["retry_failures"] = [
            {
                "attempt_number": item.get("attempt_number"),
                "reason": item.get("reason", ""),
            }
            for item in retry_history
        ]


def _retry_exhausted_details(
    details: dict[str, Any],
    *,
    max_retries: int,
    retry_history: list[dict[str, Any]],
) -> dict[str, Any]:
    result = copy.deepcopy(details)
    result["attempt_count"] = len(retry_history)
    result["max_retries"] = max_retries
    result["retry_history"] = copy.deepcopy(retry_history)
    return result


def _step_skill_contract(step: dict | None, catalog: SkillPlanningCatalog) -> dict[str, Any]:
    action = _action_from_step(step)
    spec = catalog.get(action["skill"])
    if not spec:
        return {}
    return {
        "requires_empty_hand": spec.requires_empty_hand,
        "resolved_arguments": {
            "target": spec.target_value(action),
            "item": spec.item_value(action),
            "destination": spec.destination_value(action),
            "location": spec.location_value(action),
            "device": spec.device_value(action),
        },
        "required_states": {
            "container": (
                {"key": spec.container_state_key, "value": spec.container_state_value}
                if spec.container_state_key
                else None
            ),
            "device": (
                {"key": spec.device_state_key, "value": spec.device_state_value}
                if spec.device_state_key
                else None
            ),
        },
        "declared_effects": {
            "target_state": (
                {"key": spec.state_key, "value": spec.state_value}
                if spec.state_key
                else None
            ),
            "item_state": (
                {"key": spec.effect_state_key, "value": spec.effect_state_value}
                if spec.effect_state_key
                else None
            ),
        },
    }


def _normalize_segment_plan(
    raw_plan: Any,
    *,
    allowed_skill_names: list[str],
    max_segment_actions: int,
) -> dict[str, Any]:
    if not isinstance(raw_plan, dict):
        return {
            "success": False,
            "reason": "segment_plan_not_object",
            "details": {"output_type": type(raw_plan).__name__},
        }
    if raw_plan.get("success") is not True:
        return {
            "success": False,
            "reason": str(raw_plan.get("reason", "segment_planner_failed") or "segment_planner_failed"),
            "details": copy.deepcopy(raw_plan.get("details", {})),
        }

    raw_actions = raw_plan.get("actions")
    if not isinstance(raw_actions, list):
        return {"success": False, "reason": "segment_actions_not_list", "details": {}}
    if len(raw_actions) > max_segment_actions:
        return {
            "success": False,
            "reason": "segment_action_limit_exceeded",
            "details": {"count": len(raw_actions), "max_segment_actions": max_segment_actions},
        }

    allowed = set(allowed_skill_names)
    actions: list[Action] = []
    for index, raw_action in enumerate(raw_actions):
        action = (
            _action_from_step(raw_action)
            if isinstance(raw_action, dict) and "execution" in raw_action
            else {
                "skill": str(raw_action.get("skill", "") or "") if isinstance(raw_action, dict) else "",
                "parameters": copy.deepcopy(raw_action.get("parameters", {}))
                if isinstance(raw_action, dict) and isinstance(raw_action.get("parameters", {}), dict)
                else {},
            }
        )
        if not action["skill"]:
            return {
                "success": False,
                "reason": "segment_action_missing_skill",
                "details": {"index": index},
            }
        if action["skill"] not in allowed:
            return {
                "success": False,
                "reason": "segment_action_skill_not_enabled",
                "details": {"index": index, "skill": action["skill"]},
            }
        actions.append(action)

    planner_stats = raw_plan.get("planner_stats", {})
    if not isinstance(planner_stats, dict):
        planner_stats = {}
    planner_stats = copy.deepcopy(planner_stats)
    planner_stats.setdefault("planner", "injected_segment_planner")
    planner_stats["replacement_length"] = len(actions)
    return {
        "success": True,
        "actions": actions,
        "repair_summary": str(raw_plan.get("repair_summary", "") or ""),
        "planner_stats": planner_stats,
    }


def _replay_plan(
    steps: list,
    initial_env: dict,
    initial_robot: dict,
    apply_action: ApplyAction,
) -> dict[str, Any]:
    env = copy.deepcopy(initial_env or {})
    robot = copy.deepcopy(initial_robot or {})
    trajectory_records: list[dict[str, Any]] = []
    for step in steps:
        action = _action_from_step(step)
        if not action.get("skill"):
            return {"success": False, "reason": "malformed_candidate_step", "step": _compact_step(step)}
        before_env = copy.deepcopy(env)
        before_robot = copy.deepcopy(robot)
        ok, issue, fix = apply_action(env, robot, action["skill"], action["parameters"])
        if not ok:
            return {
                "success": False,
                "reason": "candidate_step_failed",
                "step": _compact_step(step),
                "issue": issue,
                "fix": fix,
            }
        trajectory_records.append(
            {
                "step": copy.deepcopy(step),
                "before_env": before_env,
                "before_robot": before_robot,
                "after_env": copy.deepcopy(env),
                "after_robot": copy.deepcopy(robot),
            }
        )
    return {
        "success": True,
        "final_env": env,
        "final_robot": robot,
        "trajectory_records": trajectory_records,
    }


def _suffix_effect_contract(
    before_env: dict,
    before_robot: dict,
    after_env: dict,
    after_robot: dict,
) -> list[dict[str, Any]]:
    """Capture durable suffix effects when no explicit task goal is available.

    Robot position is intentionally omitted: navigation is a transient
    operational state, not a task effect. Other robot state plus entity state
    and containment changes remain part of the compatibility contract.
    """
    before_robot_effects = {
        key: copy.deepcopy(value)
        for key, value in (before_robot or {}).items()
        if key != "robot_location"
    }
    after_robot_effects = {
        key: copy.deepcopy(value)
        for key, value in (after_robot or {}).items()
        if key != "robot_location"
    }
    before = _leaf_values({"environment": before_env or {}, "robot": before_robot_effects})
    after = _leaf_values({"environment": after_env or {}, "robot": after_robot_effects})
    contract = []
    for path in sorted(set(before) | set(after)):
        existed_before = path in before
        existed_after = path in after
        if existed_before and existed_after and before[path] == after[path]:
            continue
        contract.append(
            {
                "path": list(path),
                "exists": existed_after,
                "expected": copy.deepcopy(after.get(path)),
            }
        )
    return contract


def _contract_holds(contract: list[dict[str, Any]], env: dict, robot: dict) -> bool:
    values = _leaf_values({"environment": env or {}, "robot": robot or {}})
    for fact in contract:
        path = tuple(fact.get("path", []))
        exists = path in values
        if exists != bool(fact.get("exists")):
            return False
        if exists and values[path] != fact.get("expected"):
            return False
    return True


def _leaf_values(value: Any, prefix: tuple[str, ...] = ()) -> dict[tuple[str, ...], Any]:
    if isinstance(value, dict):
        flattened: dict[tuple[str, ...], Any] = {}
        for key, item in value.items():
            flattened.update(_leaf_values(item, prefix + (str(key),)))
        if not value and prefix:
            flattened[prefix] = {}
        return flattened
    return {prefix: copy.deepcopy(value)}


def _counterfactual_failure(reason: str, details: dict[str, Any]) -> dict[str, Any]:
    return {"success": False, "reason": reason, "details": details}


def _repair_failure(reason: str, details: dict[str, Any]) -> dict[str, Any]:
    return {
        "success": False,
        "mode": MODE_VCR_COUNTERFACTUAL_REPAIR,
        "failure_reason": reason,
        "failure_details": details,
    }


def _goal_evidence(goal_test: GoalTest | None) -> str:
    if goal_test is None:
        return "counterfactual_actions_completed"
    return str(getattr(goal_test, "completion_source", "explicit_goal") or "explicit_goal")


def _task_completion_payload(
    goal_test: GoalTest | None,
    status: str,
) -> dict[str, Any]:
    payload = {
        "status": status,
        "evidence_source": _goal_evidence(goal_test),
    }
    evidence = str(getattr(goal_test, "completion_evidence", "") or "")
    if evidence:
        payload["evidence"] = evidence
    return payload


def _handler_source(handler: Any) -> str:
    return f"{handler.__class__.__module__}.{handler.__class__.__name__}.apply"


def _action_from_step(step: dict | None) -> Action:
    execution = step.get("execution", {}) if isinstance(step, dict) else {}
    if not isinstance(execution, dict):
        return {"skill": "", "parameters": {}}
    params = execution.get("parameters", {})
    return {
        "skill": str(execution.get("skill", "") or ""),
        "parameters": copy.deepcopy(params) if isinstance(params, dict) else {},
    }


def _step_from_action(action: Action) -> dict[str, Any]:
    return {
        "execution": {
            "skill": str(action.get("skill", "") or ""),
            "parameters": copy.deepcopy(action.get("parameters", {}) or {}),
        }
    }


def _compact_step(step: dict | None) -> dict[str, Any]:
    compact = _step_from_action(_action_from_step(step))
    if isinstance(step, dict) and _step_number(step) is not None:
        compact["step"] = _step_number(step)
    return compact


def _step_number(step: dict | None) -> int | None:
    if not isinstance(step, dict):
        return None
    try:
        return int(step.get("step"))
    except (TypeError, ValueError):
        return None


def _step_index(steps: list, target: dict | None) -> int | None:
    target_num = _step_number(target)
    for index, step in enumerate(steps):
        if step is target:
            return index
        if target_num is not None and _step_number(step) == target_num:
            return index
    return None


def _step_index_by_number(steps: list, number: int) -> int | None:
    for index, step in enumerate(steps):
        if _step_number(step) == number:
            return index
    return None


def _reindex_steps(steps: list) -> list[dict[str, Any]]:
    reindexed = []
    for number, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            continue
        normalized = _step_from_action(_action_from_step(step))
        normalized["step"] = number
        reindexed.append(normalized)
    return reindexed


def _compact_checkpoint(checkpoint: dict[str, Any]) -> dict[str, Any]:
    return {
        "rollback_step_num": checkpoint.get("rollback_step_num"),
        "reason": checkpoint.get("reason", ""),
        "causal_predicate": checkpoint.get("causal_predicate", ""),
        "rollback_step": copy.deepcopy(checkpoint.get("rollback_step", {})),
    }


def _without_final_state(result: dict[str, Any]) -> dict[str, Any]:
    return {
        key: copy.deepcopy(value)
        for key, value in result.items()
        if key
        not in {
            "final_env",
            "final_robot",
            "state_after_failed_effect_env",
            "state_after_failed_effect_robot",
        }
    }
