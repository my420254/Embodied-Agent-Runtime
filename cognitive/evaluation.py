from __future__ import annotations

import copy
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable


class AblationVariant(str, Enum):
    BASELINE_TODO = "baseline_todo"
    KG_CONTRACT = "kg_contract"
    KG_TASK_GRAPH = "kg_task_graph"
    KG_TASK_GRAPH_LIGHTWEIGHT = "kg_task_graph_lightweight"
    KG_TASK_GRAPH_REPAIR = "kg_task_graph_repair"
    BT_EXECUTION = "bt_execution"


@dataclass(frozen=True)
class CognitiveAblationCaseResult:
    case_id: str
    variant: str
    planning_legal: bool
    sandbox_passed: bool
    task_success: bool
    replan_count: int = 0
    hallucinated_action_count: int = 0
    kg_query_count: int = 0
    scene_query_count: int = 0
    token_cost: int = 0
    latency_ms: float = 0.0
    orchestration_route: str = "unknown"
    failure_explainable: bool = True
    failure_category: str = ""
    trace_id: str = ""
    behavior_tree_compiled: bool = False
    behavior_tree_node_count: int = 0
    behavior_tree_executed: bool = False
    behavior_tree_succeeded: bool = False
    behavior_tree_attempt_count: int = 0
    behavior_tree_action_event_count: int = 0
    behavior_tree_condition_event_count: int = 0
    behavior_tree_replan_request_count: int = 0
    bt_recovery_hint_consumed: bool = False
    bt_recovery_retry_budget_exhausted: bool = False
    execution_reflection_retry_count: int = 0
    reflection_retry_limit_reached: bool = False
    checkpoint_suffix_checked: bool = False
    checkpoint_suffix_aligned: bool = False
    checkpoint_suffix_prefix_reused: bool = False
    checkpoint_suffix_validated_step_count: int = 0
    checkpoint_suffix_step_count: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "variant": self.variant,
            "planning_legal": self.planning_legal,
            "sandbox_passed": self.sandbox_passed,
            "task_success": self.task_success,
            "replan_count": self.replan_count,
            "hallucinated_action_count": self.hallucinated_action_count,
            "kg_query_count": self.kg_query_count,
            "scene_query_count": self.scene_query_count,
            "token_cost": self.token_cost,
            "latency_ms": self.latency_ms,
            "orchestration_route": self.orchestration_route,
            "failure_explainable": self.failure_explainable,
            "failure_category": self.failure_category,
            "trace_id": self.trace_id,
            "behavior_tree_compiled": self.behavior_tree_compiled,
            "behavior_tree_node_count": self.behavior_tree_node_count,
            "behavior_tree_executed": self.behavior_tree_executed,
            "behavior_tree_succeeded": self.behavior_tree_succeeded,
            "behavior_tree_attempt_count": self.behavior_tree_attempt_count,
            "behavior_tree_action_event_count": self.behavior_tree_action_event_count,
            "behavior_tree_condition_event_count": self.behavior_tree_condition_event_count,
            "behavior_tree_replan_request_count": self.behavior_tree_replan_request_count,
            "bt_recovery_hint_consumed": self.bt_recovery_hint_consumed,
            "bt_recovery_retry_budget_exhausted": self.bt_recovery_retry_budget_exhausted,
            "execution_reflection_retry_count": self.execution_reflection_retry_count,
            "reflection_retry_limit_reached": self.reflection_retry_limit_reached,
            "checkpoint_suffix_checked": self.checkpoint_suffix_checked,
            "checkpoint_suffix_aligned": self.checkpoint_suffix_aligned,
            "checkpoint_suffix_prefix_reused": self.checkpoint_suffix_prefix_reused,
            "checkpoint_suffix_validated_step_count": self.checkpoint_suffix_validated_step_count,
            "checkpoint_suffix_step_count": self.checkpoint_suffix_step_count,
        }


@dataclass(frozen=True)
class CognitivePlanningEvalCase:
    case_id: str
    runtime_scene: dict[str, Any]
    state: dict[str, Any]
    variant: str = AblationVariant.KG_TASK_GRAPH.value
    allowed_skills: tuple[str, ...] = ()


@dataclass(frozen=True)
class CognitiveAblationSummary:
    variant: str
    case_count: int
    planning_legal_rate: float
    sandbox_pass_rate: float
    task_success_rate: float
    avg_replan_count: float
    avg_hallucinated_action_count: float
    avg_kg_query_count: float
    avg_scene_query_count: float
    avg_token_cost: float
    avg_latency_ms: float
    orchestration_route_counts: dict[str, int]
    orchestration_route_metrics: dict[str, dict[str, Any]]
    failure_explainability_rate: float
    failure_categories: dict[str, int]
    behavior_tree_compile_rate: float
    avg_behavior_tree_node_count: float
    behavior_tree_execution_rate: float
    behavior_tree_success_rate: float
    avg_behavior_tree_attempt_count: float
    avg_behavior_tree_action_event_count: float
    avg_behavior_tree_condition_event_count: float
    avg_behavior_tree_replan_request_count: float
    bt_recovery_hint_consumption_rate: float
    bt_recovery_retry_budget_exhaustion_rate: float
    avg_execution_reflection_retry_count: float
    reflection_retry_limit_rate: float
    checkpoint_suffix_check_rate: float
    checkpoint_suffix_alignment_rate: float
    checkpoint_suffix_prefix_reuse_rate: float
    avg_checkpoint_suffix_validated_step_count: float
    avg_checkpoint_suffix_step_count: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "variant": self.variant,
            "case_count": self.case_count,
            "planning_legal_rate": self.planning_legal_rate,
            "sandbox_pass_rate": self.sandbox_pass_rate,
            "task_success_rate": self.task_success_rate,
            "avg_replan_count": self.avg_replan_count,
            "avg_hallucinated_action_count": self.avg_hallucinated_action_count,
            "avg_kg_query_count": self.avg_kg_query_count,
            "avg_scene_query_count": self.avg_scene_query_count,
            "avg_token_cost": self.avg_token_cost,
            "avg_latency_ms": self.avg_latency_ms,
            "orchestration_route_counts": dict(self.orchestration_route_counts),
            "orchestration_route_metrics": {
                route: dict(metrics) for route, metrics in self.orchestration_route_metrics.items()
            },
            "failure_explainability_rate": self.failure_explainability_rate,
            "failure_categories": dict(self.failure_categories),
            "behavior_tree_compile_rate": self.behavior_tree_compile_rate,
            "avg_behavior_tree_node_count": self.avg_behavior_tree_node_count,
            "behavior_tree_execution_rate": self.behavior_tree_execution_rate,
            "behavior_tree_success_rate": self.behavior_tree_success_rate,
            "avg_behavior_tree_attempt_count": self.avg_behavior_tree_attempt_count,
            "avg_behavior_tree_action_event_count": self.avg_behavior_tree_action_event_count,
            "avg_behavior_tree_condition_event_count": self.avg_behavior_tree_condition_event_count,
            "avg_behavior_tree_replan_request_count": self.avg_behavior_tree_replan_request_count,
            "bt_recovery_hint_consumption_rate": self.bt_recovery_hint_consumption_rate,
            "bt_recovery_retry_budget_exhaustion_rate": self.bt_recovery_retry_budget_exhaustion_rate,
            "avg_execution_reflection_retry_count": self.avg_execution_reflection_retry_count,
            "reflection_retry_limit_rate": self.reflection_retry_limit_rate,
            "checkpoint_suffix_check_rate": self.checkpoint_suffix_check_rate,
            "checkpoint_suffix_alignment_rate": self.checkpoint_suffix_alignment_rate,
            "checkpoint_suffix_prefix_reuse_rate": self.checkpoint_suffix_prefix_reuse_rate,
            "avg_checkpoint_suffix_validated_step_count": self.avg_checkpoint_suffix_validated_step_count,
            "avg_checkpoint_suffix_step_count": self.avg_checkpoint_suffix_step_count,
        }


def result_from_planning_outputs(
    *,
    case_id: str,
    variant: str | AblationVariant,
    planned_state: dict[str, Any],
    evaluated_state: dict[str, Any],
    allowed_skills: Iterable[str] | None = None,
) -> CognitiveAblationCaseResult:
    trace = _trace_from_outputs(planned_state, evaluated_state)
    todo_list = evaluated_state.get("todo_list") or planned_state.get("todo_list") or []
    allowed = set(allowed_skills or [])
    hallucinated = _count_hallucinated_actions(todo_list, allowed) if allowed else 0
    sandbox = trace.get("sandbox", {}) if isinstance(trace.get("sandbox"), dict) else {}
    safety = trace.get("safety", {}) if isinstance(trace.get("safety"), dict) else {}
    metrics = trace.get("metrics", {}) if isinstance(trace.get("metrics"), dict) else {}
    planning_node = trace.get("planning_node", {}) if isinstance(trace.get("planning_node"), dict) else {}
    behavior_tree = trace.get("behavior_tree", {}) if isinstance(trace.get("behavior_tree"), dict) else {}
    behavior_tree_compiled = bool(behavior_tree.get("compiled") is True)
    behavior_tree_stats = behavior_tree.get("stats", {}) if isinstance(behavior_tree.get("stats"), dict) else {}
    behavior_tree_node_count = int(behavior_tree_stats.get("nodes") or 0)
    behavior_tree_attempts = _behavior_tree_execution_attempts(trace)
    behavior_tree_execution = _last_behavior_tree_execution(trace)
    behavior_tree_events = _behavior_tree_execution_events(trace, behavior_tree_execution)
    behavior_tree_executed = bool(behavior_tree_execution)
    behavior_tree_succeeded = bool(behavior_tree_execution.get("succeeded") is True)
    behavior_tree_attempt_count = len(behavior_tree_attempts) if behavior_tree_attempts else int(behavior_tree_executed)
    behavior_tree_action_event_count = _count_bt_events(behavior_tree_events, "Action")
    behavior_tree_condition_event_count = _count_bt_events(behavior_tree_events, "Condition")
    behavior_tree_replan_request_count = _count_bt_replan_requests(behavior_tree_events)
    bt_recovery = planning_node.get("bt_recovery", {}) if isinstance(planning_node.get("bt_recovery"), dict) else {}
    bt_recovery_retry_budget_exhausted = _bt_recovery_retry_budget_exhausted(evaluated_state, trace)
    execution_reflection_retry_count = _execution_reflection_retry_count(evaluated_state, trace)
    reflection_retry_limit_reached = _reflection_retry_limit_reached(evaluated_state, trace)
    checkpoint_suffix = (
        planning_node.get("checkpoint_suffix_repair", {})
        if isinstance(planning_node.get("checkpoint_suffix_repair"), dict)
        else {}
    )
    checkpoint_suffix_validated_step_count = int(checkpoint_suffix.get("validated_step_count") or 0)
    checkpoint_suffix_step_count = int(planning_node.get("suffix_step_count") or 0)
    variant_value = str(variant.value if isinstance(variant, AblationVariant) else variant)

    sandbox_passed = bool(evaluated_state.get("is_feasible") is True or sandbox.get("passed") is True)
    planning_legal = bool(safety.get("passed", bool(todo_list) and hallucinated == 0))
    if variant_value == AblationVariant.BT_EXECUTION.value:
        planning_legal = planning_legal and behavior_tree_compiled
    task_success = bool(evaluated_state.get("task_success", sandbox_passed))
    if (
        variant_value == AblationVariant.BT_EXECUTION.value
        and behavior_tree_executed
        and execution_reflection_retry_count == 0
    ):
        task_success = behavior_tree_succeeded
    failed = (
        not sandbox_passed
        or evaluated_state.get("is_feasible") is False
        or (variant_value == AblationVariant.BT_EXECUTION.value and not task_success)
    )

    return CognitiveAblationCaseResult(
        case_id=case_id,
        variant=variant_value,
        planning_legal=planning_legal,
        sandbox_passed=sandbox_passed,
        task_success=task_success,
        replan_count=max(
            int(evaluated_state.get("direct_replan_count") or 0),
            int(evaluated_state.get("iteration_count") or planned_state.get("iteration_count") or 1) - 1,
            0,
        ),
        hallucinated_action_count=hallucinated,
        kg_query_count=_kg_query_count(trace),
        scene_query_count=len(trace.get("scene_queries", []) or []),
        token_cost=int(metrics.get("token_cost", 0) or 0),
        latency_ms=float(metrics.get("latency_ms", 0.0) or 0.0),
        orchestration_route=_orchestration_route(trace, variant_value),
        failure_explainable=_failure_explainable(evaluated_state, sandbox) if failed else True,
        failure_category=_failure_category(evaluated_state, sandbox) if failed else "",
        trace_id=str(trace.get("trace_id", "")),
        behavior_tree_compiled=behavior_tree_compiled,
        behavior_tree_node_count=behavior_tree_node_count,
        behavior_tree_executed=behavior_tree_executed,
        behavior_tree_succeeded=behavior_tree_succeeded,
        behavior_tree_attempt_count=behavior_tree_attempt_count,
        behavior_tree_action_event_count=behavior_tree_action_event_count,
        behavior_tree_condition_event_count=behavior_tree_condition_event_count,
        behavior_tree_replan_request_count=behavior_tree_replan_request_count,
        bt_recovery_hint_consumed=bool(bt_recovery),
        bt_recovery_retry_budget_exhausted=bt_recovery_retry_budget_exhausted,
        execution_reflection_retry_count=execution_reflection_retry_count,
        reflection_retry_limit_reached=reflection_retry_limit_reached,
        checkpoint_suffix_checked=bool(checkpoint_suffix),
        checkpoint_suffix_aligned=bool(checkpoint_suffix.get("aligned") is True),
        checkpoint_suffix_prefix_reused=bool(checkpoint_suffix.get("reuse_validated_prefix") is True),
        checkpoint_suffix_validated_step_count=checkpoint_suffix_validated_step_count,
        checkpoint_suffix_step_count=checkpoint_suffix_step_count,
    )


def summarize_ablation_results(results: Iterable[CognitiveAblationCaseResult]) -> dict[str, CognitiveAblationSummary]:
    grouped: dict[str, list[CognitiveAblationCaseResult]] = {}
    for result in results:
        grouped.setdefault(result.variant, []).append(result)
    return {variant: _summarize_variant(variant, variant_results) for variant, variant_results in grouped.items()}


def run_cognitive_planning_eval_cases(
    cases: Iterable[CognitivePlanningEvalCase],
    *,
    sandbox_evaluator: bool | None = True,
) -> list[CognitiveAblationCaseResult]:
    from config.scene_state import (
        get_runtime_session,
        get_sandbox_session,
        set_runtime_session,
        set_sandbox_session,
    )
    from graph.planning import evaluator
    from graph.planning.node import decompose_task
    from graph.nodes import retry_execution_node, retry_planning_node
    from graph.reflection import node as reflection_node
    from graph.routes import global_task_management_router
    from graph.task_management import node as task_management_node
    from skills.loader import load_enabled_skill_names

    runtime_backup = get_runtime_session()
    sandbox_backup = get_sandbox_session()
    sandbox_flag_backup = evaluator.ENABLE_SANDBOX_EVALUATOR
    results: list[CognitiveAblationCaseResult] = []
    try:
        if sandbox_evaluator is not None:
            evaluator.ENABLE_SANDBOX_EVALUATOR = sandbox_evaluator
        for case in cases:
            set_runtime_session(copy.deepcopy(case.runtime_scene))
            set_sandbox_session(copy.deepcopy(case.runtime_scene))
            variant = _variant_value(case.variant)
            state = _state_for_ablation_variant(copy.deepcopy(case.state), variant)
            planned = _baseline_todo_planned_state(state) if variant == AblationVariant.BASELINE_TODO.value else decompose_task(state)
            evaluated = evaluator.evaluate_feasibility({**state, **planned})
            if variant == AblationVariant.BT_EXECUTION.value and _eval_sandbox_passed(planned, evaluated):
                evaluated = _execute_behavior_tree_eval_case(
                    state={**state, **planned, **evaluated},
                    evaluated_state=evaluated,
                    task_management_node=task_management_node,
                )
                manager_route = global_task_management_router(evaluated)
                if manager_route == "Retry_Planning":
                    if not _bt_direct_replan_budget_allows(evaluated):
                        evaluated = _mark_bt_direct_replan_budget_exhausted(evaluated)
                        allowed = case.allowed_skills or tuple(load_enabled_skill_names())
                        results.append(
                            result_from_planning_outputs(
                                case_id=case.case_id,
                                variant=variant,
                                planned_state=planned,
                                evaluated_state=evaluated,
                                allowed_skills=allowed,
                            )
                        )
                        continue
                    retry_state = {**state, **evaluated, **retry_planning_node(evaluated)}
                    retry_planned = decompose_task(retry_state)
                    retry_evaluated = evaluator.evaluate_feasibility({**retry_state, **retry_planned})
                    retry_evaluated = _execute_behavior_tree_eval_case(
                        state={**retry_state, **retry_planned, **retry_evaluated},
                        evaluated_state=retry_evaluated,
                        task_management_node=task_management_node,
                    )
                    retry_manager_route = global_task_management_router(retry_evaluated)
                    evaluated = _merge_direct_replan_eval_result(evaluated, retry_evaluated)
                    evaluated = _record_bt_direct_replan_budget_decision(evaluated, exhausted=False)
                    planned = retry_planned
                    if retry_manager_route == "Reflection_Module" and _feature_enabled(
                        retry_evaluated,
                        "cognitive_bt_execution_reflection_retry",
                    ):
                        evaluated = _execute_execution_reflection_eval_case(
                            state={**retry_state, **retry_planned},
                            evaluated_state=evaluated,
                            reflection_node=reflection_node,
                            retry_execution_node=retry_execution_node,
                            retry_planning_node=retry_planning_node,
                            task_management_node=task_management_node,
                            decompose_task=decompose_task,
                            planning_evaluator=evaluator,
                        )
                elif manager_route == "Reflection_Module" and _feature_enabled(
                    evaluated,
                    "cognitive_bt_execution_reflection_retry",
                ):
                    evaluated = _execute_execution_reflection_eval_case(
                        state={**state, **planned},
                        evaluated_state=evaluated,
                        reflection_node=reflection_node,
                        retry_execution_node=retry_execution_node,
                        retry_planning_node=retry_planning_node,
                        task_management_node=task_management_node,
                        decompose_task=decompose_task,
                        planning_evaluator=evaluator,
                    )
            allowed = case.allowed_skills or tuple(load_enabled_skill_names())
            results.append(
                result_from_planning_outputs(
                    case_id=case.case_id,
                    variant=variant,
                    planned_state=planned,
                    evaluated_state=evaluated,
                    allowed_skills=allowed,
                )
            )
    finally:
        evaluator.ENABLE_SANDBOX_EVALUATOR = sandbox_flag_backup
        set_runtime_session(runtime_backup)
        set_sandbox_session(sandbox_backup)
    return results


def _variant_value(variant: str | AblationVariant) -> str:
    return str(variant.value if isinstance(variant, AblationVariant) else variant)


def _state_for_ablation_variant(state: dict[str, Any], variant: str) -> dict[str, Any]:
    enriched = copy.deepcopy(state)
    feature_flags = dict(enriched.get("feature_flags") or {})
    if variant == AblationVariant.BASELINE_TODO.value:
        feature_flags["cognitive_planning"] = False
        feature_flags["cognitive_bt_compile"] = False
        feature_flags["cognitive_bt_execute"] = False
        feature_flags["checkpoint_repair"] = False
    elif variant == AblationVariant.KG_TASK_GRAPH_REPAIR.value:
        feature_flags["cognitive_planning"] = True
        feature_flags["checkpoint_repair"] = True
    elif variant == AblationVariant.KG_TASK_GRAPH_LIGHTWEIGHT.value:
        feature_flags["cognitive_planning"] = True
        feature_flags["cognitive_lightweight_path"] = True
    elif variant == AblationVariant.BT_EXECUTION.value:
        feature_flags["cognitive_planning"] = True
        feature_flags["cognitive_bt_compile"] = True
        feature_flags["cognitive_bt_execute"] = True
        feature_flags.setdefault("cognitive_bt_recovery_direct_replan", True)
    elif variant in {AblationVariant.KG_CONTRACT.value, AblationVariant.KG_TASK_GRAPH.value}:
        feature_flags["cognitive_planning"] = True
    enriched["feature_flags"] = feature_flags
    return enriched


def _baseline_todo_planned_state(state: dict[str, Any]) -> dict[str, Any]:
    todo_list = copy.deepcopy(state.get("todo_list") or [])
    return {
        "todo_list": todo_list,
        "iteration_count": int(state.get("iteration_count") or 0) + 1,
        "environment": copy.deepcopy(state.get("environment") or {}),
        "env_state": copy.deepcopy(state.get("env_state") or {}),
        "injected_playbook_rule_ids": [],
        "cognitive_planning_trace": {
            "planning_node": {
                "variant": AblationVariant.BASELINE_TODO.value,
                "cognitive_planning": False,
                "raw_step_count": len(todo_list),
                "normalized_step_count": len(todo_list),
            },
            "plan_summary": {
                "source_skill_id": "baseline_todo",
                "step_count": len(todo_list),
                "skills": [
                    step.get("execution", {}).get("skill", "")
                    for step in todo_list
                    if isinstance(step, dict) and isinstance(step.get("execution"), dict)
                ],
            },
            "safety": {"passed": bool(todo_list), "layer": "baseline_todo"},
            "orchestration": {"path": AblationVariant.BASELINE_TODO.value, "reason": "supplied_todo_list"},
        },
    }


def _eval_sandbox_passed(planned_state: dict[str, Any], evaluated_state: dict[str, Any]) -> bool:
    trace = _trace_from_outputs(planned_state, evaluated_state)
    sandbox = trace.get("sandbox", {}) if isinstance(trace.get("sandbox"), dict) else {}
    return bool(evaluated_state.get("is_feasible") is True or sandbox.get("passed") is True)


def _execute_behavior_tree_eval_case(
    *,
    state: dict[str, Any],
    evaluated_state: dict[str, Any],
    task_management_node: Any,
) -> dict[str, Any]:
    managed = task_management_node.task_manager_node(state)
    execution_state = {**state, **managed}
    if task_management_node.route_after_manager(execution_state) != "behavior_tree_execute":
        return evaluated_state

    executed = task_management_node.execute_behavior_tree_node(execution_state)
    after_execution = {**execution_state, **executed}
    completed = task_management_node.task_manager_node(after_execution)
    final_state = {**state, **evaluated_state, **managed, **executed, **completed}
    behavior_tree_execution = final_state.get("behavior_tree_execution", {})
    final_state["cognitive_planning_trace"] = _record_behavior_tree_execution_attempt(
        final_state.get("cognitive_planning_trace", {}),
        behavior_tree_execution,
    )
    final_state["task_success"] = bool(
        final_state.get("execution_status") == "success"
        and isinstance(behavior_tree_execution, dict)
        and behavior_tree_execution.get("succeeded") is True
    )
    return final_state


def _merge_direct_replan_eval_result(first: dict[str, Any], retry: dict[str, Any]) -> dict[str, Any]:
    return {
        **_merge_behavior_tree_followup_eval_result(first, retry),
        "direct_replan_count": int(first.get("direct_replan_count") or 0) + 1,
    }


def _merge_behavior_tree_followup_eval_result(first: dict[str, Any], retry: dict[str, Any]) -> dict[str, Any]:
    first_trace = first.get("cognitive_planning_trace", {})
    retry_trace = retry.get("cognitive_planning_trace", {})
    merged_trace = dict(retry_trace) if isinstance(retry_trace, dict) else {}
    attempts = []
    if isinstance(first_trace, dict):
        attempts.extend(_behavior_tree_execution_attempts(first_trace))
    if isinstance(retry_trace, dict):
        attempts.extend(_behavior_tree_execution_attempts(retry_trace))
    if attempts:
        merged_trace["behavior_tree_execution_attempts"] = attempts
    return {
        **retry,
        "cognitive_planning_trace": merged_trace,
    }


def _bt_direct_replan_budget(state: dict[str, Any]) -> int:
    flags = state.get("feature_flags", {})
    raw_budget = flags.get("cognitive_bt_direct_replan_budget", 1) if isinstance(flags, dict) else 1
    try:
        budget = int(raw_budget)
    except (TypeError, ValueError):
        budget = 1
    return max(budget, 0)


def _bt_direct_replan_used(state: dict[str, Any]) -> int:
    try:
        return int(state.get("bt_recovery_direct_replan_count") or state.get("direct_replan_count") or 0)
    except (TypeError, ValueError):
        return 0


def _bt_direct_replan_budget_allows(state: dict[str, Any]) -> bool:
    return _bt_direct_replan_used(state) < _bt_direct_replan_budget(state)


def _mark_bt_direct_replan_budget_exhausted(state: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(state)
    enriched["bt_recovery_retry_budget_exhausted"] = True
    enriched["cognitive_planning_trace"] = _record_bt_direct_replan_budget_decision(enriched, exhausted=True).get(
        "cognitive_planning_trace",
        {},
    )
    enriched["task_success"] = False
    return enriched


def _record_bt_direct_replan_budget_decision(state: dict[str, Any], *, exhausted: bool) -> dict[str, Any]:
    enriched = dict(state)
    trace = enriched.get("cognitive_planning_trace", {})
    if not isinstance(trace, dict):
        trace = {}
    budget_events = trace.get("bt_recovery_retry_budget", [])
    if not isinstance(budget_events, list):
        budget_events = []
    budget_events.append(
        {
            "budget": _bt_direct_replan_budget(enriched),
            "used": _bt_direct_replan_used(enriched),
            "exhausted": bool(exhausted),
            "route": "Retry_Planning",
        }
    )
    enriched["cognitive_planning_trace"] = {**trace, "bt_recovery_retry_budget": budget_events}
    if exhausted:
        enriched["bt_recovery_retry_budget_exhausted"] = True
    return enriched


def _execute_execution_reflection_eval_case(
    *,
    state: dict[str, Any],
    evaluated_state: dict[str, Any],
    reflection_node: Any,
    retry_execution_node: Any,
    retry_planning_node: Any,
    task_management_node: Any,
    decompose_task: Any,
    planning_evaluator: Any,
    followup_planning_repair_budget: int = 1,
) -> dict[str, Any]:
    from graph.routes import global_reflection_router, global_task_management_router

    reflection_state = {**state, **evaluated_state}
    triage = reflection_node.failure_triage_node(reflection_state)
    attempt: dict[str, Any] = {
        "determined_reflection_layer": triage.get("determined_reflection_layer", ""),
        "limit_reached": triage.get("determined_reflection_layer") == "end",
    }
    if attempt["limit_reached"]:
        return _merge_execution_reflection_eval_result(
            evaluated_state,
            {**reflection_state, **triage},
            attempt,
            retry_count=0,
        )

    if triage.get("determined_reflection_layer") != "layer4_execution":
        return _merge_execution_reflection_eval_result(
            evaluated_state,
            {**reflection_state, **triage},
            attempt,
            retry_count=0,
        )

    reflected = reflection_node.layer4_execution_reflection_node({**reflection_state, **triage})
    reflected_state = {**reflection_state, **triage, **reflected}
    next_route = global_reflection_router(reflected_state)
    attempt.update(
        {
            "next_routing": reflected.get("next_routing", ""),
            "graph_route": next_route,
            "has_corrected_execution": bool(
                isinstance(reflected.get("corrected_execution"), dict)
                and reflected.get("corrected_execution", {}).get("skill")
            ),
        }
    )
    if next_route != "Retry_Execution":
        return _merge_execution_reflection_eval_result(
            evaluated_state,
            reflected_state,
            attempt,
            retry_count=0,
        )

    retried = retry_execution_node(reflected_state)
    retry_state = {**reflected_state, **retried}
    if retry_state.get("execution_status") != "running":
        if retry_state.get("next_routing") == "retry_planning":
            repair_state = {**retry_state, **retry_planning_node(retry_state)}
            repair_planned = decompose_task(repair_state)
            repair_evaluated = planning_evaluator.evaluate_feasibility({**repair_state, **repair_planned})
            if _eval_sandbox_passed(repair_planned, repair_evaluated):
                repair_evaluated = _execute_behavior_tree_eval_case(
                    state={**repair_state, **repair_planned, **repair_evaluated},
                    evaluated_state=repair_evaluated,
                    task_management_node=task_management_node,
                )
            merged = _merge_behavior_tree_followup_eval_result(evaluated_state, repair_evaluated)
            merged = _merge_execution_reflection_eval_result(
                merged,
                merged,
                attempt,
                retry_count=0,
            )
            repair_manager_route = global_task_management_router(repair_evaluated)
            if (
                followup_planning_repair_budget > 0
                and repair_manager_route == "Reflection_Module"
                and _feature_enabled(repair_evaluated, "cognitive_bt_execution_reflection_retry")
            ):
                return _execute_execution_reflection_eval_case(
                    state={**repair_state, **repair_planned},
                    evaluated_state=merged,
                    reflection_node=reflection_node,
                    retry_execution_node=retry_execution_node,
                    retry_planning_node=retry_planning_node,
                    task_management_node=task_management_node,
                    decompose_task=decompose_task,
                    planning_evaluator=planning_evaluator,
                    followup_planning_repair_budget=followup_planning_repair_budget - 1,
                )
            return merged
        return _merge_execution_reflection_eval_result(
            evaluated_state,
            retry_state,
            attempt,
            retry_count=0,
        )

    classified = task_management_node.task_classification_node(retry_state)
    simulated = task_management_node.simulate_action_node({**retry_state, **classified})
    managed = task_management_node.task_manager_node({**retry_state, **classified, **simulated})
    final_state = {**retry_state, **classified, **simulated, **managed}
    final_state["task_success"] = bool(final_state.get("execution_status") == "success")
    return _merge_execution_reflection_eval_result(
        evaluated_state,
        final_state,
        attempt,
        retry_count=1,
    )


def _merge_execution_reflection_eval_result(
    base: dict[str, Any],
    current: dict[str, Any],
    attempt: dict[str, Any],
    *,
    retry_count: int,
) -> dict[str, Any]:
    trace = _record_execution_reflection_attempt(
        current.get("cognitive_planning_trace") or base.get("cognitive_planning_trace") or {},
        attempt,
    )
    return {
        **base,
        **current,
        "cognitive_planning_trace": trace,
        "execution_reflection_retry_count": int(base.get("execution_reflection_retry_count") or 0) + retry_count,
        "reflection_retry_limit_reached": bool(
            base.get("reflection_retry_limit_reached") or attempt.get("limit_reached") is True
        ),
    }


def _record_behavior_tree_execution_attempt(trace: Any, execution: Any) -> dict[str, Any]:
    enriched = dict(trace) if isinstance(trace, dict) else {}
    if not isinstance(execution, dict) or not execution:
        return enriched
    attempts = _behavior_tree_execution_attempts(enriched)
    attempts.append(dict(execution))
    enriched["behavior_tree_execution_attempts"] = attempts
    return enriched


def _record_execution_reflection_attempt(trace: Any, attempt: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(trace) if isinstance(trace, dict) else {}
    attempts = enriched.get("execution_reflection_attempts", [])
    if not isinstance(attempts, list):
        attempts = []
    attempts.append(dict(attempt))
    enriched["execution_reflection_attempts"] = attempts
    return enriched


def _summarize_variant(variant: str, results: list[CognitiveAblationCaseResult]) -> CognitiveAblationSummary:
    count = len(results)
    failed = [result for result in results if not result.sandbox_passed or not result.task_success]
    checkpoint_checked = [result for result in results if result.checkpoint_suffix_checked]
    return CognitiveAblationSummary(
        variant=variant,
        case_count=count,
        planning_legal_rate=_rate(result.planning_legal for result in results),
        sandbox_pass_rate=_rate(result.sandbox_passed for result in results),
        task_success_rate=_rate(result.task_success for result in results),
        avg_replan_count=_avg(result.replan_count for result in results),
        avg_hallucinated_action_count=_avg(result.hallucinated_action_count for result in results),
        avg_kg_query_count=_avg(result.kg_query_count for result in results),
        avg_scene_query_count=_avg(result.scene_query_count for result in results),
        avg_token_cost=_avg(result.token_cost for result in results),
        avg_latency_ms=_avg(result.latency_ms for result in results),
        orchestration_route_counts=_orchestration_route_counts(results),
        orchestration_route_metrics=_orchestration_route_metrics(results),
        failure_explainability_rate=1.0 if not failed else _rate(result.failure_explainable for result in failed),
        failure_categories=_failure_category_counts(failed),
        behavior_tree_compile_rate=_rate(result.behavior_tree_compiled for result in results),
        avg_behavior_tree_node_count=_avg(result.behavior_tree_node_count for result in results),
        behavior_tree_execution_rate=_rate(result.behavior_tree_executed for result in results),
        behavior_tree_success_rate=_rate(result.behavior_tree_succeeded for result in results),
        avg_behavior_tree_attempt_count=_avg(result.behavior_tree_attempt_count for result in results),
        avg_behavior_tree_action_event_count=_avg(result.behavior_tree_action_event_count for result in results),
        avg_behavior_tree_condition_event_count=_avg(result.behavior_tree_condition_event_count for result in results),
        avg_behavior_tree_replan_request_count=_avg(result.behavior_tree_replan_request_count for result in results),
        bt_recovery_hint_consumption_rate=_rate(result.bt_recovery_hint_consumed for result in results),
        bt_recovery_retry_budget_exhaustion_rate=_rate(
            result.bt_recovery_retry_budget_exhausted for result in results
        ),
        avg_execution_reflection_retry_count=_avg(
            result.execution_reflection_retry_count for result in results
        ),
        reflection_retry_limit_rate=_rate(result.reflection_retry_limit_reached for result in results),
        checkpoint_suffix_check_rate=_rate(result.checkpoint_suffix_checked for result in results),
        checkpoint_suffix_alignment_rate=_rate(result.checkpoint_suffix_aligned for result in checkpoint_checked),
        checkpoint_suffix_prefix_reuse_rate=_rate(result.checkpoint_suffix_prefix_reused for result in checkpoint_checked),
        avg_checkpoint_suffix_validated_step_count=_avg(
            result.checkpoint_suffix_validated_step_count for result in checkpoint_checked
        ),
        avg_checkpoint_suffix_step_count=_avg(result.checkpoint_suffix_step_count for result in checkpoint_checked),
    )


def _trace_from_outputs(planned_state: dict[str, Any], evaluated_state: dict[str, Any]) -> dict[str, Any]:
    trace = evaluated_state.get("cognitive_planning_trace") or planned_state.get("cognitive_planning_trace") or {}
    return trace if isinstance(trace, dict) else {}


def _feature_enabled(state: dict[str, Any], name: str, default: bool = False) -> bool:
    flags = state.get("feature_flags", {})
    if isinstance(flags, dict) and name in flags:
        return bool(flags[name])
    return default


def _last_behavior_tree_execution(trace: dict[str, Any]) -> dict[str, Any]:
    attempts = _behavior_tree_execution_attempts(trace)
    if attempts:
        return attempts[-1]
    execution = trace.get("behavior_tree_execution", {})
    return dict(execution) if isinstance(execution, dict) else {}


def _behavior_tree_execution_attempts(trace: dict[str, Any]) -> list[dict[str, Any]]:
    attempts = trace.get("behavior_tree_execution_attempts", [])
    if not isinstance(attempts, list):
        return []
    return [dict(attempt) for attempt in attempts if isinstance(attempt, dict)]


def _behavior_tree_execution_events(trace: dict[str, Any], execution: dict[str, Any]) -> list[Any]:
    attempts = _behavior_tree_execution_attempts(trace)
    if attempts:
        events: list[Any] = []
        for attempt in attempts:
            attempt_events = attempt.get("events", [])
            if isinstance(attempt_events, list):
                events.extend(attempt_events)
        return events
    events = execution.get("events", [])
    return events if isinstance(events, list) else []


def _execution_reflection_attempts(trace: dict[str, Any]) -> list[dict[str, Any]]:
    attempts = trace.get("execution_reflection_attempts", [])
    if not isinstance(attempts, list):
        return []
    return [dict(attempt) for attempt in attempts if isinstance(attempt, dict)]


def _bt_recovery_retry_budget_exhausted(evaluated_state: dict[str, Any], trace: dict[str, Any]) -> bool:
    if evaluated_state.get("bt_recovery_retry_budget_exhausted") is True:
        return True
    budget_events = trace.get("bt_recovery_retry_budget", [])
    if not isinstance(budget_events, list):
        return False
    return any(isinstance(event, dict) and event.get("exhausted") is True for event in budget_events)


def _execution_reflection_retry_count(evaluated_state: dict[str, Any], trace: dict[str, Any]) -> int:
    explicit = evaluated_state.get("execution_reflection_retry_count")
    if explicit is not None:
        return int(explicit or 0)
    return sum(
        1
        for attempt in _execution_reflection_attempts(trace)
        if attempt.get("graph_route") == "Retry_Execution"
    )


def _reflection_retry_limit_reached(evaluated_state: dict[str, Any], trace: dict[str, Any]) -> bool:
    if evaluated_state.get("reflection_retry_limit_reached") is True:
        return True
    return any(attempt.get("limit_reached") is True for attempt in _execution_reflection_attempts(trace))


def _count_hallucinated_actions(todo_list: list[dict[str, Any]], allowed_skills: set[str]) -> int:
    count = 0
    for step in todo_list:
        execution = step.get("execution", {}) if isinstance(step, dict) else {}
        skill = execution.get("skill") if isinstance(execution, dict) else None
        if skill and skill not in allowed_skills:
            count += 1
    return count


def _kg_query_count(trace: dict[str, Any]) -> int:
    if trace.get("kg_query") or trace.get("kg_query_type"):
        return 1
    return 0


def _orchestration_route(trace: dict[str, Any], variant: str) -> str:
    orchestration = trace.get("orchestration", {})
    if isinstance(orchestration, dict):
        route = str(orchestration.get("path") or "").strip()
        if route:
            return route
    if variant == AblationVariant.BASELINE_TODO.value:
        return AblationVariant.BASELINE_TODO.value
    return "unknown"


def _count_bt_events(events: list[Any], node_type: str) -> int:
    return sum(1 for event in events if isinstance(event, dict) and event.get("node_type") == node_type)


def _count_bt_replan_requests(events: list[Any]) -> int:
    count = 0
    for event in events:
        action_result = event.get("action_result", {}) if isinstance(event, dict) else {}
        if isinstance(action_result, dict) and action_result.get("replan_requested") is True:
            count += 1
    return count


def _failure_explainable(evaluated_state: dict[str, Any], sandbox: dict[str, Any]) -> bool:
    signals = (
        evaluated_state.get("feedback"),
        evaluated_state.get("error_feedback"),
        sandbox.get("issue_type"),
        sandbox.get("fix"),
    )
    return any(bool(signal) for signal in signals)


def _failure_category(evaluated_state: dict[str, Any], sandbox: dict[str, Any]) -> str:
    category = sandbox.get("failure_category") or evaluated_state.get("failure_category") or ""
    if category:
        return str(category)
    try:
        from graph.planning.failure_taxonomy import classify_planning_failure

        return classify_planning_failure(
            str(evaluated_state.get("feedback") or evaluated_state.get("error_feedback") or ""),
            str(evaluated_state.get("fix") or ""),
        ).value
    except Exception:
        return ""


def _failure_category_counts(results: list[CognitiveAblationCaseResult]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for result in results:
        if result.failure_category:
            counts[result.failure_category] = counts.get(result.failure_category, 0) + 1
    return counts


def _orchestration_route_counts(results: list[CognitiveAblationCaseResult]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for result in results:
        route = result.orchestration_route or "unknown"
        counts[route] = counts.get(route, 0) + 1
    return dict(sorted(counts.items()))


def _orchestration_route_metrics(results: list[CognitiveAblationCaseResult]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[CognitiveAblationCaseResult]] = {}
    for result in results:
        grouped.setdefault(result.orchestration_route or "unknown", []).append(result)
    metrics: dict[str, dict[str, Any]] = {}
    for route, route_results in grouped.items():
        metrics[route] = {
            "case_count": len(route_results),
            "planning_legal_rate": _rate(result.planning_legal for result in route_results),
            "sandbox_pass_rate": _rate(result.sandbox_passed for result in route_results),
            "task_success_rate": _rate(result.task_success for result in route_results),
            "avg_kg_query_count": _avg(result.kg_query_count for result in route_results),
            "avg_scene_query_count": _avg(result.scene_query_count for result in route_results),
            "avg_latency_ms": _avg(result.latency_ms for result in route_results),
        }
    return {route: metrics[route] for route in sorted(metrics)}


def _rate(values: Iterable[bool]) -> float:
    values_list = list(values)
    if not values_list:
        return 0.0
    return sum(1 for value in values_list if value) / len(values_list)


def _avg(values: Iterable[float]) -> float:
    values_list = list(values)
    if not values_list:
        return 0.0
    return sum(float(value) for value in values_list) / len(values_list)
