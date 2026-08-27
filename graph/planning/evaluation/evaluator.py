"""Public entry points for candidate evaluation and repair assembly."""
from __future__ import annotations

import copy
import json
from dataclasses import replace
from typing import Any

from ace.playbook import learn_from_success, record_rule_feedback
from adapters.sandbox import apply_sandbox_action
from adapters.tracing import JsonlTraceRecorder
from config.llms import get_planning_llm
from config.settings import get_config
from graph.planning.config import with_planning_config
from graph.planning.normalizer import get_full_flat_house
from skills.planning_catalog import load_planning_catalog
from skills.registry import get_skill_handlers, load_enabled_skill_prompts

from .audits import llm as audit_llm
from .audits import run_evaluation_audits
from .composition import build_repair_registry, resolve_repair_strategy
from .dependencies import EvaluationDependencies
from .models import (
    CandidateRevision,
    EvaluationFailure,
    EvaluationFailureCode,
    EvaluationSession,
    REPAIR_REQUEST_VERSION,
    validate_evaluation_repair_request,
)
from .outcomes.handoff import CheckpointFailureHandoff
from .outcomes.reporter import EvaluationReporter
from .pipeline.candidate import evaluate_candidate
from .pipeline.simulation import _handler_failure_code
from .pipeline.session import (
    build_evaluation_context,
    create_evaluation_session,
    resolve_evaluation_modes,
)
from .repair_strategies.contracts import (
    RepairContext,
    RepairDiagnosis,
)
from .validation.checkpoint import _explicit_goal_test
from .validation.legality import build_legality_repair_prompt
from .validation.state_diff import _build_state_audit_context, _build_state_diff


REPAIR_CANDIDATE_REVISION_SOURCE = "evaluation_repair_candidate"


def save_evaluator_finding_to_playbook(*args, **kwargs):
    kwargs.setdefault("get_planning_llm", get_planning_llm)
    return audit_llm.save_evaluator_finding_to_playbook(*args, **kwargs)


def _failure_skill_name(failure: Any) -> str:
    """从失败的步骤提取动作对应的 skill 名（如 RIGHT_GRASP），供修复时针对性加载该 skill 的 prompt。"""
    try:
        step = getattr(failure, "step", {})
        if isinstance(step, dict):
            execution = step.get("execution", {})
            if isinstance(execution, dict):
                return str(execution.get("skill", "") or "").strip()
    except Exception:
        pass
    return ""


def _dependencies(strategy_name: str) -> EvaluationDependencies:
    return EvaluationDependencies(
        apply_sandbox_action=apply_sandbox_action,
        get_full_flat_house=get_full_flat_house,
        get_planning_llm=get_planning_llm,
        load_skill_catalog=load_planning_catalog,
        load_enabled_skill_prompts=load_enabled_skill_prompts,
        record_rule_feedback=record_rule_feedback,
        learn_from_success=learn_from_success,
        save_evaluator_finding=save_evaluator_finding_to_playbook,
        trace_recorder_factory=JsonlTraceRecorder,
        get_skill_handlers=get_skill_handlers,
        repair_registry=build_repair_registry(
            config_reader=get_config,
            strategy_name=strategy_name,
        ),
        failure_handoff=CheckpointFailureHandoff(),
    )


def evaluate_feasibility(
    state,
    dependencies: EvaluationDependencies | None = None,
):
    """Evaluate one complete candidate without invoking the planning model."""

    state = with_planning_config(state)
    if dependencies is None:
        dependencies = _dependencies(resolve_repair_strategy(get_config))
    context = build_evaluation_context(state, dependencies)
    modes = resolve_evaluation_modes(state, context.feature_flags, dependencies)
    reporter = EvaluationReporter(
        context,
        dependencies,
        modes.sandbox,
        repair_enabled=modes.repair_selection.strategy is not None,
    )

    if modes.repair_selection.error:
        return reporter.failure(
            EvaluationFailure(
                code=EvaluationFailureCode.CONFIGURATION,
                issue_type="修复模式配置冲突",
                fix_advice=modes.repair_selection.error,
                checkpoint_robot=copy.deepcopy(context.initial_robot),
            )
        )

    session = create_evaluation_session(context, modes, dependencies)
    if isinstance(session, EvaluationFailure):
        return reporter.failure(session)
    if modes.state_diff_audit and not modes.sandbox:
        return reporter.failure(
            EvaluationFailure(
                code=EvaluationFailureCode.CONFIGURATION,
                issue_type="状态差异审计配置异常",
                fix_advice=(
                    "state_diff_audit 依赖 sandbox_evaluator；"
                    "请同时启用沙盒模拟，或关闭状态差异审计。"
                ),
                checkpoint_env=session.validation_env,
                checkpoint_robot=context.initial_robot,
            )
        )

    segment_failure = _validate_repair_segments(
        session,
        _repair_candidate_transaction(context.state),
    )
    if segment_failure is not None:
        return _handle_candidate_failure(
            session,
            dependencies,
            reporter,
            segment_failure,
        )

    candidate_failure = evaluate_candidate(session)
    if candidate_failure is not None:
        return _handle_candidate_failure(
            session,
            dependencies,
            reporter,
            candidate_failure,
        )

    audit_outcome = run_evaluation_audits(session, dependencies)
    if isinstance(audit_outcome, CandidateRevision):
        session.apply_revision(audit_outcome)
        return reporter.revision(session, audit_outcome)
    if isinstance(audit_outcome, EvaluationFailure):
        if _repair_candidate_transaction(session.context.state):
            return _handle_candidate_failure(
                session,
                dependencies,
                reporter,
                audit_outcome,
            )
        return reporter.failure(audit_outcome)
    _mark_repair_candidate_accepted(session)
    return reporter.complete(session)


def assemble_repair_candidate(
    state,
    dependencies: EvaluationDependencies | None = None,
) -> dict[str, Any]:
    """Assemble planning-model output into a complete candidate todo list."""

    state = with_planning_config(state)
    if dependencies is None:
        dependencies = _dependencies(resolve_repair_strategy(get_config))
    request = state.get("evaluation_repair_request")
    generated = state.get("repair_todo_list")
    request_error = validate_evaluation_repair_request(request)
    if request_error:
        return _assembly_failure(state, request_error)
    if not isinstance(generated, list) or not any(
        isinstance(step, dict) for step in generated
    ):
        return _retry_repair_assembly_output(
            state,
            request,
            "规划层未返回可拼装的 repair_todo_list",
            generated_count=0,
        )

    generated_steps = [
        copy.deepcopy(step) for step in generated if isinstance(step, dict)
    ]
    segment_checks: list[dict[str, Any]] = []
    if request.get("assembly_mode") == "complete":
        complete_todo_list = _reindex(generated_steps)
        step_provenance = [
            {
                "source": "generated",
                "generated_action_index": index,
            }
            for index in range(1, len(complete_todo_list) + 1)
        ]
    else:
        strategy_name = str(request.get("strategy_name", ""))
        selection = dependencies.repair_registry.select(strategy_name)
        if selection.strategy is None:
            return _assembly_failure(
                state,
                selection.error or f"无法选择修复策略: {strategy_name}",
            )
        diagnosis = RepairDiagnosis(
            strategy_name=strategy_name,
            prompt=str(request.get("prompt", "")),
            merge_context=copy.deepcopy(request.get("merge_context") or {}),
        )
        try:
            assembly = selection.strategy.reassemble(diagnosis, generated_steps)
        except Exception as exc:
            return _assembly_failure(
                state,
                f"{strategy_name} 完整 todo_list 拼装异常: {exc}",
            )
        if not assembly.success or not assembly.todo_list:
            return _retry_repair_assembly_output(
                state,
                request,
                assembly.error or "修复策略未拼装出完整 todo_list",
                generated_count=len(generated_steps),
            )
        complete_todo_list = assembly.todo_list
        step_provenance = _normalized_step_provenance(
            assembly.step_provenance,
            len(complete_todo_list),
        )
        segment_checks = [
            copy.deepcopy(item)
            for item in assembly.segment_checks
            if isinstance(item, dict)
        ]

    history = _complete_repair_history(
        state.get("repair_history"),
        request,
        generated_count=len(generated_steps),
    )
    base_todo_list = request.get("original_todo_list")
    if not isinstance(base_todo_list, list):
        base_todo_list = state.get("todo_list") or []
    return {
        "todo_list": copy.deepcopy(complete_todo_list),
        "is_feasible": False,
        "feedback": "规划层重规划输出已拼装为完整 todo_list，等待重新评估。",
        "evaluation_repair_request": {},
        "repair_todo_list": [],
        "evaluation_recheck": True,
        "evaluation_revision_context": {
            "source": REPAIR_CANDIDATE_REVISION_SOURCE,
            "base_todo_list": copy.deepcopy(base_todo_list),
            "repair_request": copy.deepcopy(request),
            "generated_todo_list": copy.deepcopy(generated_steps),
            "step_provenance": copy.deepcopy(step_provenance),
            "segment_checks": segment_checks,
        },
        "repair_history": history,
        "planning_continuation": {},
        "repair_handoff": {},
    }


def _handle_candidate_failure(
    session: EvaluationSession,
    dependencies: EvaluationDependencies,
    reporter: EvaluationReporter,
    failure: EvaluationFailure,
) -> dict[str, Any]:
    attempts = _repair_attempt_count(session.repair_history)
    transaction = _repair_candidate_transaction(session.context.state)
    if transaction:
        if _candidate_failure_after_repair_window(session, failure, transaction):
            return _accept_candidate_and_repair_followup(
                session,
                dependencies,
                reporter,
                failure,
                transaction,
                round_number=attempts + 1,
            )
        if attempts >= _repair_attempt_limit(session.context.feature_flags):
            return _reject_terminal_repair_candidate(
                session,
                reporter,
                failure,
                transaction,
            )
        return _retry_repair_candidate(
            session,
            reporter,
            failure,
            transaction,
            round_number=attempts + 1,
        )
    if attempts >= _repair_attempt_limit(session.context.feature_flags):
        return reporter.failure(failure)
    if failure.kind == "plan_legality":
        violations = failure.artifacts.get("plan_legality", {}).get(
            "violations",
            [],
        )
        request = {
            "version": REPAIR_REQUEST_VERSION,
            "round": attempts + 1,
            "stage": "legality",
            "assembly_mode": "complete",
            "strategy_name": "",
            "prompt": build_legality_repair_prompt(
                intent=session.context.intent,
                todo_list=session.todo_list,
                violations=violations,
                environment=session.validation_env,
            ),
            "merge_context": {},
            "original_todo_list": copy.deepcopy(session.todo_list),
            "violations": copy.deepcopy(violations),
        }
        return _publish_repair_request(session, reporter, failure, request)
    if failure.kind != "sandbox_failure":
        return reporter.failure(failure)

    strategy = session.modes.repair_selection.strategy
    if strategy is None:
        return reporter.failure(failure)
    context = _repair_context(session, failure, dependencies)
    try:
        diagnosis = strategy.find_errors(context)
    except Exception as exc:
        return reporter.failure(
            _repair_failure(
                session,
                failure,
                f"{strategy.name} 问题组装异常: {exc}",
            )
        )
    if diagnosis.disposition == "deferred":
        return _deferred_repair_result(session, diagnosis)
    if diagnosis.error or not diagnosis.prompt:
        return reporter.failure(
            _repair_failure(
                session,
                failure,
                diagnosis.error or "修复策略未生成重规划问题描述",
            )
        )

    request = {
        "version": REPAIR_REQUEST_VERSION,
        "round": attempts + 1,
        "stage": "sandbox",
        "assembly_mode": "strategy",
        "strategy_name": strategy.name,
        "skill_contract_mode": "compact" if strategy.name == "vcr" else "full",
        "prompt": diagnosis.prompt,
        "merge_context": copy.deepcopy(diagnosis.merge_context),
        "original_todo_list": copy.deepcopy(session.todo_list),
        "failure": {
            "step": failure.step.get("step"),
            "issue_type": failure.issue_type,
            "fix_advice": failure.fix_advice,
            "skill": _failure_skill_name(failure),
        },
    }
    return _publish_repair_request(session, reporter, failure, request)


def _accept_candidate_and_repair_followup(
    session: EvaluationSession,
    dependencies: EvaluationDependencies,
    reporter: EvaluationReporter,
    failure: EvaluationFailure,
    transaction: dict[str, Any],
    *,
    round_number: int,
) -> dict[str, Any]:
    """Commit a successful VCR window patch and diagnose the later failure.

    Candidate-level replay can fail after the repaired window.  In that case the
    repaired segment is not rejected; it becomes the new base plan and VCR should
    diagnose the later failure against the actual replayed trajectory.
    """

    session.repair_history = _mark_latest_candidate_result(
        session.repair_history,
        status="accepted",
    )
    strategy = session.modes.repair_selection.strategy
    if strategy is None:
        return reporter.failure(failure)
    context = _repair_context(session, failure, dependencies)
    try:
        diagnosis = strategy.find_errors(context)
    except Exception as exc:
        return reporter.failure(
            _repair_failure(
                session,
                failure,
                f"{strategy.name} 后续问题组装异常: {exc}",
            )
        )
    if diagnosis.disposition == "deferred":
        return _deferred_repair_result(session, diagnosis)
    if diagnosis.error or not diagnosis.prompt:
        return reporter.failure(
            _repair_failure(
                session,
                failure,
                diagnosis.error or "修复策略未生成后续重规划问题描述",
            )
        )

    request = {
        "version": REPAIR_REQUEST_VERSION,
        "round": round_number,
        "stage": "sandbox",
        "assembly_mode": "strategy",
        "strategy_name": strategy.name,
        "skill_contract_mode": "compact" if strategy.name == "vcr" else "full",
        "prompt": diagnosis.prompt,
        "merge_context": copy.deepcopy(diagnosis.merge_context),
        "original_todo_list": copy.deepcopy(session.todo_list),
        "failure": {
            "step": failure.step.get("step"),
            "issue_type": failure.issue_type,
            "fix_advice": failure.fix_advice,
        },
        "accepted_prior_repair": {
            "source": REPAIR_CANDIDATE_REVISION_SOURCE,
            "repair_request": copy.deepcopy(
                transaction.get("repair_request") or {}
            ),
        },
    }
    return _publish_repair_request(session, reporter, failure, request)


def _publish_repair_request(
    session: EvaluationSession,
    reporter: EvaluationReporter,
    failure: EvaluationFailure,
    request: dict[str, Any],
) -> dict[str, Any]:
    entry = {
        "round": request["round"],
        "stage": request["stage"],
        "status": "diagnosed",
        "generated_count": 0,
        "assembled": False,
    }
    if request["stage"] == "legality":
        entry["violations"] = copy.deepcopy(request.get("violations", []))
    else:
        entry["failure"] = copy.deepcopy(request.get("failure", {}))
    session.record_repair(entry)
    event = replace(
        failure,
        artifacts={
            **copy.deepcopy(failure.artifacts),
            "repair_history": copy.deepcopy(session.repair_history),
        },
    )
    result = reporter.failure(event)
    if result.get("execution_status") == "failed":
        return result
    result.update(
        {
            "todo_list": copy.deepcopy(session.todo_list),
            "evaluation_repair_request": copy.deepcopy(request),
            "repair_todo_list": [],
            "evaluation_recheck": False,
            "repair_history": copy.deepcopy(session.repair_history),
        }
    )
    return result


def _repair_context(
    session: EvaluationSession,
    failure: EvaluationFailure,
    dependencies: EvaluationDependencies | None = None,
) -> RepairContext:
    simulation = session.simulation

    def apply_action(
        env: dict,
        robot: dict,
        skill: str,
        parameters: dict,
    ) -> tuple[bool, str, str]:
        step = {
            "execution": {
                "skill": skill,
                "parameters": copy.deepcopy(parameters),
            }
        }
        execution = _repair_execution(session, step, env)
        return session.skills.apply_action(
            env,
            robot,
            execution["skill"],
            execution["parameters"],
        )

    def validate_action(
        env: dict,
        robot: dict,
        skill: str,
        parameters: dict,
    ) -> tuple[bool, str, str]:
        step = {
            "execution": {
                "skill": skill,
                "parameters": copy.deepcopy(parameters),
            }
        }
        execution = _repair_execution(session, step, env)
        handler = session.skill_handlers.get(execution["skill"])
        if handler is None:
            return (
                False,
                "调用无效动作",
                f"技能 {execution['skill']} 在当前 profile 中未启用或未定义",
            )
        return handler.validate(
            env,
            robot,
            execution["parameters"],
        )

    def apply_effect(
        env: dict,
        robot: dict,
        skill: str,
        parameters: dict,
    ) -> None:
        step = {
            "execution": {
                "skill": skill,
                "parameters": copy.deepcopy(parameters),
            }
        }
        execution = _repair_execution(session, step, env)
        handler = session.skill_handlers.get(execution["skill"])
        if handler is None:
            raise KeyError(f"skill handler unavailable: {execution['skill']}")
        handler.apply(env, robot, execution["parameters"])

    return RepairContext(
        todo_list=copy.deepcopy(session.todo_list),
        validated_steps=copy.deepcopy(simulation.validated_steps),
        failed_step=copy.deepcopy(failure.step),
        issue_type=failure.issue_type,
        fix_advice=failure.fix_advice,
        failure_env=copy.deepcopy(failure.checkpoint_env),
        failure_robot=copy.deepcopy(failure.checkpoint_robot),
        trajectory_records=copy.deepcopy(simulation.trajectory_records),
        sandbox_start_env=copy.deepcopy(simulation.start_env),
        sandbox_start_robot=copy.deepcopy(simulation.start_robot),
        structured_task=copy.deepcopy(session.context.structured_task),
        relevant_item_names=copy.deepcopy(
            session.context.state.get("relevant_item_names") or []
        ),
        environment=copy.deepcopy(session.context.state.get("environment") or {}),
        skill_profile=session.context.skill_profile,
        skill_catalog=session.skill_catalog,
        skill_handlers=session.skill_handlers,
        skill_prompts=session.skills.prompts,
        apply_action=apply_action,
        validate_action=validate_action,
        skill_closure=copy.deepcopy(
            session.context.state.get("skill_closure") or []
        ),
        goal_test=_counterfactual_goal_test(session, dependencies),
        apply_effect=apply_effect,
    )


def _repair_execution(
    session: EvaluationSession,
    step: dict[str, Any],
    env: dict[str, Any],
) -> dict[str, Any]:
    execution = step.get("execution", {})
    return execution if isinstance(execution, dict) else {}


def _counterfactual_goal_test(
    session: EvaluationSession,
    dependencies: EvaluationDependencies | None,
):
    explicit_goal_test = _explicit_goal_test(session.context.structured_task)
    if explicit_goal_test is not None:
        return explicit_goal_test

    planning_llm_factory = (
        dependencies.get_planning_llm
        if dependencies is not None
        else get_planning_llm
    )
    simulation = session.simulation

    def goal_test(final_env: dict, final_robot: dict) -> bool:
        state_diff = _build_state_diff(
            simulation.start_env,
            simulation.start_robot,
            final_env,
            final_robot,
        )
        state_context = _build_state_audit_context(
            simulation.start_env,
            simulation.start_robot,
            final_env,
            final_robot,
            session.todo_list,
            session.context.structured_task,
        )
        result = audit_llm._run_counterfactual_task_completion(
            intent=session.context.intent,
            todo_list=session.todo_list,
            state_diff=state_diff,
            state_audit_context=state_context,
            get_planning_llm=planning_llm_factory,
        )
        goal_test.completion_evidence = result.get("evidence", "")
        return result["task_completed"]

    goal_test.completion_source = "llm_state_diff"
    goal_test.completion_evidence = ""
    return goal_test


def _deferred_repair_result(
    session: EvaluationSession,
    diagnosis: RepairDiagnosis,
) -> dict[str, Any]:
    """Expose an unhandled strategy outcome without replanning or execution."""

    return {
        "todo_list": copy.deepcopy(session.todo_list),
        "is_feasible": False,
        "feedback": diagnosis.error,
        "feature_flags": dict(session.context.feature_flags or {}),
        "planning_continuation": {},
        "evaluation_repair_request": {},
        "repair_todo_list": [],
        "evaluation_recheck": False,
        "evaluation_revision_context": {},
        "repair_history": copy.deepcopy(session.repair_history),
        **copy.deepcopy(diagnosis.artifacts),
    }


def _repair_failure(
    session: EvaluationSession,
    failure: EvaluationFailure,
    reason: str,
) -> EvaluationFailure:
    return replace(
        failure,
        fix_advice=reason or failure.fix_advice,
        artifacts={
            **copy.deepcopy(failure.artifacts),
            "repair_history": copy.deepcopy(session.repair_history),
        },
    )


def _repair_attempt_count(history: Any) -> int:
    return sum(
        1
        for entry in (history or [])
        if isinstance(entry, dict)
        and entry.get("stage") in {"legality", "sandbox"}
    )


def _repair_attempt_limit(feature_flags: dict[str, Any] | None) -> int:
    raw = (
        feature_flags.get("evaluation_repair_attempts", 10)
        if isinstance(feature_flags, dict)
        else 10
    )
    try:
        return max(0, min(int(raw), 10))
    except (TypeError, ValueError):
        return 10


def _repair_candidate_transaction(state: dict[str, Any]) -> dict[str, Any]:
    revision = state.get("evaluation_revision_context")
    if not isinstance(revision, dict):
        return {}
    if revision.get("source") == REPAIR_CANDIDATE_REVISION_SOURCE:
        return revision
    nested = revision.get("repair_transaction")
    if (
        isinstance(nested, dict)
        and nested.get("source") == REPAIR_CANDIDATE_REVISION_SOURCE
    ):
        return nested
    return {}


def _validate_repair_segments(
    session: EvaluationSession,
    transaction: dict[str, Any],
) -> EvaluationFailure | None:
    if not transaction or not session.modes.sandbox:
        return None
    raw_segments = transaction.get("segment_checks")
    if not isinstance(raw_segments, list) or not raw_segments:
        return None

    accepted = []
    failures = []
    for raw_segment in raw_segments:
        if not isinstance(raw_segment, dict):
            continue
        outcome = _validate_repair_segment(session, raw_segment)
        if outcome.get("success"):
            accepted.append(
                {
                    "repair_window_id": outcome["repair_window_id"],
                    "steps": copy.deepcopy(outcome["steps"]),
                }
            )
        else:
            failures.append(outcome["failure"])
    if not failures:
        return None

    first = failures[0]
    feedback_failures = [
        _public_segment_failure(failure)
        for failure in failures
    ]
    return EvaluationFailure(
        code=EvaluationFailureCode.UNKNOWN,
        issue_type="VCR 窗口修复未通过独立验证",
        fix_advice="至少一个修复窗口未满足动作前置条件或出口契约",
        kind="repair_segment_validation",
        checkpoint_env=copy.deepcopy(first.get("checkpoint_environment", {})),
        checkpoint_robot=copy.deepcopy(first.get("checkpoint_robot", {})),
        artifacts={
            "repair_segment_validation": {
                "strategy_name": "vcr",
                "accepted": accepted,
                "failures": feedback_failures,
            }
        },
    )


def _validate_repair_segment(
    session: EvaluationSession,
    segment: dict[str, Any],
) -> dict[str, Any]:
    window_id = str(segment.get("segment_id", "") or "").strip()
    steps = [
        copy.deepcopy(step)
        for step in (segment.get("steps") or [])
        if isinstance(step, dict)
    ]
    environment = copy.deepcopy(segment.get("entry_environment") or {})
    robot = copy.deepcopy(segment.get("entry_robot") or {})
    observed_state_writes: list[dict[str, Any]] = []
    if not window_id or not steps or not isinstance(environment, dict) or not isinstance(robot, dict):
        return {
            "success": False,
            "failure": {
                "repair_window_id": window_id,
                "validation_stage": "segment_definition",
                "issue_type": "窗口验证上下文不完整",
                "failed_preconditions": [
                    {
                        "code": "configuration",
                        "required_condition": "窗口必须包含入口快照、出口契约和替换动作",
                    }
                ],
                "checkpoint_environment": environment,
                "checkpoint_robot": robot,
            },
        }

    for index, step in enumerate(steps, start=1):
        execution = step.get("execution", {})
        if not isinstance(execution, dict) or not execution:
            return _segment_action_failure(
                session,
                window_id,
                steps,
                index,
                EvaluationFailure(
                    code=EvaluationFailureCode.FORMAT_ERROR,
                    issue_type="输出格式异常",
                    fix_advice="必须提供符合规范的 execution 字典",
                    step=copy.deepcopy(step),
                    checkpoint_env=copy.deepcopy(environment),
                    checkpoint_robot=copy.deepcopy(robot),
                ),
                observed_state_writes,
            )
        before_environment = copy.deepcopy(environment)
        before_robot = copy.deepcopy(robot)
        skill = str(execution.get("skill", "") or "")
        ok, issue_type, fix_advice = session.skills.apply_action(
            environment,
            robot,
            skill,
            execution.get("parameters", {}),
        )
        if not ok:
            return _segment_action_failure(
                session,
                window_id,
                steps,
                index,
                EvaluationFailure(
                    code=_handler_failure_code(issue_type, skill),
                    issue_type=issue_type,
                    fix_advice=fix_advice,
                    step=copy.deepcopy(step),
                    checkpoint_env=before_environment,
                    checkpoint_robot=before_robot,
                ),
                observed_state_writes,
            )
        writes = _segment_state_writes(
            before_environment,
            before_robot,
            environment,
            robot,
        )
        observed_state_writes.append(
            {
                "action_index": index,
                "action": _compact_candidate_step(step),
                "writes": writes,
            }
        )

    mismatches = _segment_contract_mismatches(
        environment,
        robot,
        segment.get("exit_contract"),
    )
    if mismatches:
        return {
            "success": False,
            "failure": {
                "repair_window_id": window_id,
                "validation_stage": "exit_contract",
                "issue_type": "窗口出口契约未满足",
                "failed_preconditions": mismatches,
                "state_at_segment_exit": {
                    "robot": _compact_robot_state(robot),
                },
                "local_segment_path": _segment_local_path(
                    steps,
                    failed_index=len(steps),
                ),
                "observed_root_actions": _observed_root_actions(
                    observed_state_writes,
                    mismatches,
                ),
                "checkpoint_environment": environment,
                "checkpoint_robot": robot,
            },
        }
    return {
        "success": True,
        "repair_window_id": window_id,
        "steps": steps,
    }


def _segment_action_failure(
    session: EvaluationSession,
    window_id: str,
    steps: list[dict[str, Any]],
    action_index: int,
    failure: EvaluationFailure,
    observed_state_writes: list[dict[str, Any]],
) -> dict[str, Any]:
    failed_preconditions = _candidate_failed_preconditions(session, failure)
    return {
        "success": False,
        "failure": {
            "repair_window_id": window_id,
            "validation_stage": "segment_action",
            "segment_action_index": action_index,
            "failed_action": _compact_candidate_step(failure.step),
            "issue_type": failure.issue_type,
            "failed_preconditions": failed_preconditions,
            "observed_root_actions": _observed_root_actions(
                observed_state_writes,
                failed_preconditions,
            ),
            "state_before_failure": _compact_candidate_state(failure),
            "local_segment_path": _segment_local_path(
                steps,
                failed_index=action_index,
            ),
            "checkpoint_environment": copy.deepcopy(failure.checkpoint_env),
            "checkpoint_robot": copy.deepcopy(failure.checkpoint_robot),
        },
    }


def _segment_state_values(
    environment: dict[str, Any],
    robot: dict[str, Any],
) -> dict[str, Any]:
    values = {
        f"robot.robot.{key}": copy.deepcopy(value)
        for key, value in robot.items()
    }
    for entity, raw_info in environment.items():
        if not isinstance(raw_info, dict):
            values[f"entity.{entity}.value"] = copy.deepcopy(raw_info)
            continue
        for key, value in raw_info.items():
            if key == "states":
                continue
            values[f"entity.{entity}.{key}"] = copy.deepcopy(value)
        states = raw_info.get("states", {})
        if isinstance(states, dict):
            for key, value in states.items():
                values[f"state.{entity}.{key}"] = copy.deepcopy(value)
    return values


def _segment_state_writes(
    before_environment: dict[str, Any],
    before_robot: dict[str, Any],
    after_environment: dict[str, Any],
    after_robot: dict[str, Any],
) -> list[dict[str, Any]]:
    before = _segment_state_values(before_environment, before_robot)
    after = _segment_state_values(after_environment, after_robot)
    writes = []
    for predicate in sorted(set(before) | set(after)):
        before_value = before.get(predicate)
        after_value = after.get(predicate)
        if before_value == after_value:
            continue
        writes.append(
            {
                "predicate": predicate,
                "before": copy.deepcopy(before_value),
                "after": copy.deepcopy(after_value),
            }
        )
    return writes


def _canonical_vcr_predicate(predicate: str) -> str:
    if predicate.startswith("robot.robot."):
        return predicate
    if predicate.startswith("robot."):
        return "robot.robot." + predicate.removeprefix("robot.")
    return predicate


def _observed_root_actions(
    observed_state_writes: list[dict[str, Any]],
    preconditions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    roots = []
    for precondition in preconditions:
        if not isinstance(precondition, dict):
            continue
        predicate = str(precondition.get("predicate", "") or "")
        if not predicate:
            continue
        canonical = _canonical_vcr_predicate(predicate)
        actual_is_known = "actual_value" in precondition
        actual_value = precondition.get("actual_value")
        root_action = {}
        for event in reversed(observed_state_writes):
            if not isinstance(event, dict):
                continue
            matching_write = next(
                (
                    write
                    for write in event.get("writes", [])
                    if isinstance(write, dict)
                    and write.get("predicate") == canonical
                    and (
                        not actual_is_known
                        or write.get("after") == actual_value
                    )
                ),
                None,
            )
            if matching_write is None:
                continue
            action = event.get("action")
            action = action if isinstance(action, dict) else {}
            root_action = {
                "action_index": event.get("action_index"),
                "skill": str(action.get("skill", "") or ""),
                "parameters": copy.deepcopy(
                    action.get("parameters", {})
                    if isinstance(action.get("parameters"), dict)
                    else {}
                ),
            }
            break
        roots.append(
            {
                "predicate": predicate,
                "root_action": root_action,
            }
        )
    return roots


def _public_segment_failure(failure: dict[str, Any]) -> dict[str, Any]:
    """Keep internal sandbox snapshots out of the next LLM repair prompt."""
    return {
        key: copy.deepcopy(value)
        for key, value in failure.items()
        if key not in {"checkpoint_environment", "checkpoint_robot"}
    }


def _segment_contract_mismatches(
    environment: dict[str, Any],
    robot: dict[str, Any],
    raw_contract: Any,
) -> list[dict[str, Any]]:
    contracts = raw_contract if isinstance(raw_contract, list) else []
    mismatches = []
    for contract in contracts:
        if not isinstance(contract, dict):
            continue
        predicate = str(contract.get("predicate", "") or "")
        required_value = copy.deepcopy(contract.get("required_value"))
        actual_value = _contract_actual_value(environment, robot, predicate)
        if actual_value != required_value:
            mismatches.append(
                {
                    "predicate": predicate,
                    "required_value": required_value,
                    "actual_value": actual_value,
                }
            )
    return mismatches


def _contract_actual_value(
    environment: dict[str, Any],
    robot: dict[str, Any],
    predicate: str,
) -> Any:
    if predicate.startswith("robot.robot."):
        return robot.get(predicate.removeprefix("robot.robot."))
    if predicate.startswith("entity."):
        body = predicate.removeprefix("entity.")
        entity, separator, field = body.rpartition(".")
        if separator:
            info = environment.get(entity, {})
            return info.get(field) if isinstance(info, dict) else None
    if predicate.startswith("state."):
        parts = predicate.split(".", 2)
        if len(parts) == 3:
            info = environment.get(parts[1], {})
            states = info.get("states", {}) if isinstance(info, dict) else {}
            return states.get(parts[2]) if isinstance(states, dict) else None
    return None


def _segment_local_path(
    steps: list[dict[str, Any]],
    *,
    failed_index: int,
) -> list[dict[str, Any]]:
    start = max(1, failed_index - 2)
    end = min(len(steps), failed_index + 1)
    path = []
    for index in range(start, end + 1):
        item = _compact_candidate_step(steps[index - 1])
        item["segment_action_index"] = index
        item["is_failed_action"] = index == failed_index
        path.append(item)
    return path


def _compact_robot_state(robot: dict[str, Any]) -> dict[str, Any]:
    return {
        key: copy.deepcopy(robot.get(key))
        for key in ("robot_location", "robot_holding")
        if key in robot
    }


def _retry_repair_candidate(
    session: EvaluationSession,
    reporter: EvaluationReporter,
    failure: EvaluationFailure,
    transaction: dict[str, Any],
    *,
    round_number: int,
) -> dict[str, Any]:
    request = copy.deepcopy(transaction.get("repair_request") or {})
    request_error = validate_evaluation_repair_request(request)
    if request_error:
        return _reject_terminal_repair_candidate(
            session,
            reporter,
            replace(
                failure,
                fix_advice=f"候选事务中的修复请求无效: {request_error}",
            ),
            transaction,
        )

    base_todo_list = transaction.get("base_todo_list")
    if not isinstance(base_todo_list, list):
        base_todo_list = request.get("original_todo_list")
    if not isinstance(base_todo_list, list):
        base_todo_list = []

    feedback = _repair_candidate_feedback(session, failure, transaction)
    progress = _repair_segment_progress(failure)
    failures = _candidate_failures_for_retry(request, feedback)
    failure_memory = _candidate_failure_memory(request, feedback)
    base_prompt = str(request.get("base_prompt") or request.get("prompt") or "")
    merge_context = copy.deepcopy(request.get("merge_context") or {})
    if progress:
        merge_context = _merge_segment_progress(merge_context, progress)
    active_window_ids = merge_context.get("active_window_ids")
    accepted_window_ids = sorted(
        (merge_context.get("accepted_window_steps") or {}).keys()
    )
    request.update(
        {
            "round": round_number,
            "base_prompt": base_prompt,
            "prompt": _candidate_retry_prompt(
                base_prompt,
                failures,
                active_window_ids=active_window_ids,
                accepted_window_ids=accepted_window_ids,
                strategy_name=str(request.get("strategy_name", "") or ""),
                failure_memory=failure_memory,
            ),
            "candidate_failures": failures,
            "candidate_failure_memory": failure_memory,
            "merge_context": merge_context,
            "original_todo_list": copy.deepcopy(base_todo_list),
            "failure": {
                "step": failure.step.get("step"),
                "issue_type": failure.issue_type,
                "fix_advice": failure.fix_advice,
            },
        }
    )
    session.todo_list = copy.deepcopy(base_todo_list)
    session.repair_history = _mark_latest_candidate_result(
        session.repair_history,
        status="rejected",
        failure=feedback,
    )
    return _publish_repair_request(session, reporter, failure, request)


def _reject_terminal_repair_candidate(
    session: EvaluationSession,
    reporter: EvaluationReporter,
    failure: EvaluationFailure,
    transaction: dict[str, Any],
) -> dict[str, Any]:
    base_todo_list = transaction.get("base_todo_list")
    if not isinstance(base_todo_list, list):
        base_todo_list = []
    feedback = _repair_candidate_feedback(session, failure, transaction)
    history = _mark_latest_candidate_result(
        session.repair_history,
        status="rejected",
        failure=feedback,
    )
    event = replace(
        failure,
        todo_list=copy.deepcopy(base_todo_list),
        artifacts={
            **copy.deepcopy(failure.artifacts),
            "repair_history": copy.deepcopy(history),
        },
    )
    result = reporter.failure(event)
    result.update(
        {
            "todo_list": copy.deepcopy(base_todo_list),
            "evaluation_repair_request": {},
            "repair_todo_list": [],
            "evaluation_recheck": False,
            "evaluation_revision_context": {},
            "repair_history": history,
        }
    )
    return result


def _candidate_failure_after_repair_window(
    session: EvaluationSession,
    failure: EvaluationFailure,
    transaction: dict[str, Any],
) -> bool:
    if failure.kind == "repair_segment_validation":
        return False
    failed_index = _candidate_step_index(session.todo_list, failure.step)
    if failed_index is None:
        return False
    provenance = _normalized_step_provenance(
        transaction.get("step_provenance"),
        len(session.todo_list),
    )
    current = provenance[failed_index]
    if current.get("source") != "original":
        return False
    return any(
        item.get("source") in {"generated", "accepted_window"}
        for item in provenance[:failed_index]
    )


def _candidate_failure_feedback(
    session: EvaluationSession,
    failure: EvaluationFailure,
    transaction: dict[str, Any],
) -> dict[str, Any]:
    failed_index = _candidate_step_index(session.todo_list, failure.step)
    provenance = _normalized_step_provenance(
        transaction.get("step_provenance"),
        len(session.todo_list),
    )
    location = {"complete_plan_step": failure.step.get("step")}
    if failed_index is not None:
        location.update(copy.deepcopy(provenance[failed_index]))
    return {
        "failed_step": failure.step.get("step"),
        "failed_action": _compact_candidate_step(failure.step),
        "candidate_location": location,
        "issue_type": failure.issue_type,
        "failed_preconditions": _candidate_failed_preconditions(
            session,
            failure,
        ),
        "state_before_failure": _compact_candidate_state(failure),
        "local_candidate_path": _candidate_local_path(
            session.todo_list,
            provenance,
            failed_index,
        ),
    }


def _repair_candidate_feedback(
    session: EvaluationSession,
    failure: EvaluationFailure,
    transaction: dict[str, Any],
) -> dict[str, Any]:
    progress = _repair_segment_progress(failure)
    if not progress:
        return _candidate_failure_feedback(session, failure, transaction)
    return {
        "validation_scope": "independent_repair_windows",
        "accepted_window_ids": [
            item["repair_window_id"]
            for item in progress["accepted"]
        ],
        "failed_windows": copy.deepcopy(progress["failures"]),
    }


def _repair_segment_progress(failure: EvaluationFailure) -> dict[str, Any]:
    raw = failure.artifacts.get("repair_segment_validation", {})
    if not isinstance(raw, dict) or raw.get("strategy_name") != "vcr":
        return {}
    accepted = [
        copy.deepcopy(item)
        for item in raw.get("accepted", [])
        if isinstance(item, dict)
        and str(item.get("repair_window_id", "") or "").strip()
        and isinstance(item.get("steps"), list)
    ]
    failures = [
        copy.deepcopy(item)
        for item in raw.get("failures", [])
        if isinstance(item, dict)
        and str(item.get("repair_window_id", "") or "").strip()
    ]
    return {"accepted": accepted, "failures": failures} if failures else {}


def _merge_segment_progress(
    merge_context: dict[str, Any],
    progress: dict[str, Any],
) -> dict[str, Any]:
    merged = copy.deepcopy(merge_context)
    accepted_steps = merged.get("accepted_window_steps", {})
    accepted_steps = (
        copy.deepcopy(accepted_steps)
        if isinstance(accepted_steps, dict)
        else {}
    )
    for item in progress["accepted"]:
        accepted_steps[str(item["repair_window_id"])] = copy.deepcopy(item["steps"])
    active_window_ids = [
        str(item["repair_window_id"])
        for item in progress["failures"]
    ]
    for window_id in active_window_ids:
        accepted_steps.pop(window_id, None)
    merged["accepted_window_steps"] = accepted_steps
    merged["active_window_ids"] = active_window_ids
    return merged


def _candidate_retry_prompt(
    base_prompt: str,
    failures: list[dict[str, Any]],
    *,
    active_window_ids: Any = None,
    accepted_window_ids: list[str] | None = None,
    strategy_name: str = "",
    failure_memory: list[dict[str, Any]] | None = None,
) -> str:
    is_vcr = strategy_name == "vcr"
    instruction = (
        "保持 task_goal、repair_window 的入口状态、出口契约和窗口边界不变，"
        "validation_errors 只陈述验证事实，不包含修复建议。"
        "请按 repair_window.repair_strategies 中的一种方法重写完整窗口 actions："
        "保持 root_action 时必须在 failed_action 前补足前置条件，"
        "或替换 root_action 并重新达到 failed_action 前置条件。"
        "确保每个 failed_action 执行前的状态"
        "不再出现 state_mismatches 中的 actual，而满足 expected；"
        "validation_errors 中的 rejected_sequences 是之前已失败的完整窗口动作序列，"
        "不要重复任一 rejected_sequence，也不要重复其 failed_action 前的同一动作前缀；"
        "causal_errors 的 root_action 是模拟器回溯到的状态来源动作。"
        if is_vcr
        else "保持原始修复范围，根据候选失败反馈修正失败路径。"
    )
    active = (
        [str(window_id) for window_id in active_window_ids]
        if isinstance(active_window_ids, list)
        else []
    )
    accepted = [str(window_id) for window_id in (accepted_window_ids or [])]
    if active:
        instruction = (
            "已采纳窗口不得改写或输出；只输出 active_repair_window_ids 中窗口的 actions。"
            + instruction
        )
    candidate_feedback = {
        "status": (
            "rejected_during_repair_window_validation"
            if is_vcr
            else "rejected_after_complete_plan_evaluation"
        ),
        "instruction": instruction,
    }
    if is_vcr:
        candidate_feedback["validation_errors"] = copy.deepcopy(
            failure_memory or []
        )
    else:
        candidate_feedback["failures"] = failures
    retry_payload = {"candidate_feedback": candidate_feedback}
    if active:
        retry_payload["candidate_feedback"]["active_repair_window_ids"] = active
        retry_payload["candidate_feedback"]["accepted_repair_window_ids"] = accepted
    return (
        base_prompt.rstrip()
        + "\n\n"
        + json.dumps(retry_payload, ensure_ascii=False, indent=2, default=str)
    )


def _candidate_failures_for_retry(
    request: dict[str, Any],
    feedback: dict[str, Any],
) -> list[dict[str, Any]]:
    previous = request.get("candidate_failures")
    failures = [
        copy.deepcopy(item)
        for item in (previous if isinstance(previous, list) else [])
        if isinstance(item, dict)
    ]
    failures.append(copy.deepcopy(feedback))
    limit = 1 if str(request.get("strategy_name", "") or "") == "vcr" else 2
    return failures[-limit:]


def _candidate_failure_memory(
    request: dict[str, Any],
    feedback: dict[str, Any],
) -> list[dict[str, Any]]:
    if str(request.get("strategy_name", "") or "") != "vcr":
        return []
    raw_memory = request.get("candidate_failure_memory")
    memory = [
        copy.deepcopy(item)
        for item in (raw_memory if isinstance(raw_memory, list) else [])
        if isinstance(item, dict)
    ]
    for constraint in _compact_vcr_failure_constraints(feedback):
        identity = _vcr_constraint_identity(constraint)
        previous = next(
            (
                item
                for item in memory
                if _vcr_constraint_identity(item) == identity
            ),
            None,
        )
        memory = [
            item for item in memory if _vcr_constraint_identity(item) != identity
        ]
        memory.append(_merge_vcr_constraint(previous, constraint))
    return memory[-8:]


def _compact_vcr_failure_constraints(feedback: dict[str, Any]) -> list[dict[str, Any]]:
    failed_windows = feedback.get("failed_windows")
    if not isinstance(failed_windows, list):
        failed_windows = [feedback]
    constraints = []
    for failure in failed_windows:
        if not isinstance(failure, dict):
            continue
        failed_action = failure.get("failed_action")
        failed_action = failed_action if isinstance(failed_action, dict) else {}
        error_fact = {
            "code": "",
            "issue_type": str(failure.get("issue_type", "") or ""),
        }
        causal_errors: list[dict[str, Any]] = []
        for precondition in failure.get("failed_preconditions", []):
            if not isinstance(precondition, dict):
                continue
            if not error_fact["code"]:
                error_fact["code"] = str(precondition.get("code", "") or "")
            predicate = str(precondition.get("predicate", "") or "")
            if not predicate:
                continue
            mismatch = {
                "state": _compact_vcr_state_key(
                    predicate
                ),
            }
            if "actual_value" in precondition:
                mismatch["actual"] = copy.deepcopy(precondition.get("actual_value"))
            if "required_value" in precondition:
                mismatch["expected"] = copy.deepcopy(precondition.get("required_value"))
            causal_root = _vcr_observed_root_cause(failure, precondition)
            matching_error = next(
                (
                    error
                    for error in causal_errors
                    if error.get("root_action") == causal_root
                ),
                None,
            )
            if matching_error is None:
                matching_error = {
                    "root_action": causal_root,
                    "state_mismatches": [],
                }
                causal_errors.append(matching_error)
            if mismatch not in matching_error["state_mismatches"]:
                matching_error["state_mismatches"].append(mismatch)
        constraint = {
            "repair_window_id": str(
                failure.get("repair_window_id", "") or ""
            ),
            "failed_action": {
                "action_index": failure.get("segment_action_index"),
                "skill": str(failed_action.get("skill", "") or ""),
                "parameters": copy.deepcopy(
                    failed_action.get("parameters", {})
                    if isinstance(failed_action.get("parameters"), dict)
                    else {}
                ),
            },
            "causal_errors": causal_errors,
        }
        rejected_sequence = _compact_vcr_rejected_sequence(failure)
        if rejected_sequence:
            constraint["rejected_sequences"] = [rejected_sequence]
        if error_fact["code"] or error_fact["issue_type"]:
            constraint["error"] = error_fact
        if (causal_errors or "error" in constraint) and constraint not in constraints:
            constraints.append(constraint)
    return constraints


def _vcr_observed_root_cause(
    failure: dict[str, Any],
    precondition: dict[str, Any],
) -> dict[str, Any]:
    predicate = str(precondition.get("predicate", "") or "")
    roots = failure.get("observed_root_actions")
    for item in roots if isinstance(roots, list) else []:
        if not isinstance(item, dict) or item.get("predicate") != predicate:
            continue
        root_action = item.get("root_action")
        if isinstance(root_action, dict):
            return copy.deepcopy(root_action)
    return {}


def _merge_vcr_constraint(
    previous: dict[str, Any] | None,
    current: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(previous, dict):
        return copy.deepcopy(current)
    merged = copy.deepcopy(current)
    causal_errors: list[dict[str, Any]] = []
    for source in (previous.get("causal_errors"), current.get("causal_errors")):
        for error in source if isinstance(source, list) else []:
            if not isinstance(error, dict):
                continue
            root_action = error.get("root_action")
            matching_error = next(
                (
                    item
                    for item in causal_errors
                    if item.get("root_action") == root_action
                ),
                None,
            )
            if matching_error is None:
                matching_error = {
                    "root_action": copy.deepcopy(root_action),
                    "state_mismatches": [],
                }
                causal_errors.append(matching_error)
            for mismatch in error.get("state_mismatches", []):
                if (
                    isinstance(mismatch, dict)
                    and mismatch not in matching_error["state_mismatches"]
                ):
                    matching_error["state_mismatches"].append(copy.deepcopy(mismatch))
    merged["causal_errors"] = causal_errors
    merged["rejected_sequences"] = _merge_vcr_rejected_sequences(
        previous,
        current,
    )
    return merged


def _compact_vcr_rejected_sequence(failure: dict[str, Any]) -> dict[str, Any]:
    path = failure.get("local_segment_path")
    if not isinstance(path, list):
        return {}
    actions = []
    failed_action_index = None
    for raw_action in path:
        if not isinstance(raw_action, dict):
            continue
        try:
            action_index = int(raw_action.get("segment_action_index"))
        except (TypeError, ValueError):
            action_index = len(actions) + 1
        action = {
            "action_index": action_index,
            "skill": str(raw_action.get("skill", "") or ""),
            "parameters": copy.deepcopy(
                raw_action.get("parameters", {})
                if isinstance(raw_action.get("parameters"), dict)
                else {}
            ),
        }
        if bool(raw_action.get("is_failed_action")):
            action["is_failed_action"] = True
            failed_action_index = action_index
        actions.append(action)
    if not actions:
        return {}
    return {
        "actions": actions,
        "failed_action_index": failed_action_index,
    }


def _merge_vcr_rejected_sequences(
    previous: dict[str, Any] | None,
    current: dict[str, Any],
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    for source in (
        (previous or {}).get("rejected_sequences"),
        current.get("rejected_sequences"),
    ):
        for sequence in source if isinstance(source, list) else []:
            if not isinstance(sequence, dict):
                continue
            identity = json.dumps(
                sequence,
                ensure_ascii=False,
                sort_keys=True,
                default=str,
            )
            if all(
                json.dumps(
                    item,
                    ensure_ascii=False,
                    sort_keys=True,
                    default=str,
                )
                != identity
                for item in merged
            ):
                merged.append(copy.deepcopy(sequence))
    return merged[-4:]


def _vcr_constraint_identity(constraint: dict[str, Any]) -> str:
    failed_action = constraint.get("failed_action", constraint.get("action"))
    failed_action = failed_action if isinstance(failed_action, dict) else {}
    identity = {
        "repair_window_id": constraint.get("repair_window_id"),
        "failed_action": {
            "skill": failed_action.get("skill"),
            "parameters": failed_action.get("parameters"),
        },
    }
    return json.dumps(identity, ensure_ascii=False, sort_keys=True, default=str)


def _compact_vcr_state_key(predicate: str) -> str:
    if predicate.startswith("robot.robot."):
        return predicate.removeprefix("robot.robot.")
    if predicate.startswith("robot."):
        return predicate.removeprefix("robot.")
    return predicate


def _normalized_step_provenance(raw: Any, count: int) -> list[dict[str, Any]]:
    if isinstance(raw, list) and len(raw) == count and all(
        isinstance(item, dict) for item in raw
    ):
        return copy.deepcopy(raw)
    return [{"source": "unknown"} for _ in range(count)]


def _candidate_step_index(
    todo_list: list[dict[str, Any]],
    failed_step: dict[str, Any],
) -> int | None:
    number = failed_step.get("step") if isinstance(failed_step, dict) else None
    for index, step in enumerate(todo_list):
        if isinstance(step, dict) and step.get("step") == number:
            return index
    for index, step in enumerate(todo_list):
        if step == failed_step:
            return index
    return None


def _compact_candidate_step(step: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(step, dict):
        return {}
    execution = step.get("execution", {})
    if not isinstance(execution, dict):
        return {"step": step.get("step")}
    return {
        "step": step.get("step"),
        "skill": str(execution.get("skill", "") or ""),
        "parameters": copy.deepcopy(execution.get("parameters", {})),
    }


def _candidate_local_path(
    todo_list: list[dict[str, Any]],
    provenance: list[dict[str, Any]],
    failed_index: int | None,
) -> list[dict[str, Any]]:
    if failed_index is None:
        return []
    start = max(0, failed_index - 2)
    end = min(len(todo_list), failed_index + 2)
    path = []
    for index in range(start, end):
        item = _compact_candidate_step(todo_list[index])
        item.update(copy.deepcopy(provenance[index]))
        item["is_failed_action"] = index == failed_index
        path.append(item)
    return path


def _compact_candidate_state(failure: EvaluationFailure) -> dict[str, Any]:
    robot = failure.checkpoint_robot
    environment = failure.checkpoint_env
    result: dict[str, Any] = {
        "robot": {
            key: copy.deepcopy(robot.get(key))
            for key in ("robot_location", "robot_holding")
            if isinstance(robot, dict) and key in robot
        },
        "entities": {},
    }
    execution = (
        failure.step.get("execution", {})
        if isinstance(failure.step, dict)
        else {}
    )
    parameters = (
        execution.get("parameters", {}) if isinstance(execution, dict) else {}
    )
    parameter_values = parameters.values() if isinstance(parameters, dict) else []
    names = [
        str(value)
        for value in parameter_values
        if isinstance(value, str) and value
    ]
    holding = (
        str(robot.get("robot_holding", "") or "")
        if isinstance(robot, dict)
        else ""
    )
    if holding and holding != "空" and holding not in names:
        names.append(holding)
    for name in names:
        info = environment.get(name, {}) if isinstance(environment, dict) else {}
        if not isinstance(info, dict):
            continue
        facts = {
            key: copy.deepcopy(info[key])
            for key in ("type", "direct_parent", "is_container")
            if key in info
        }
        states = info.get("states", {})
        if isinstance(states, dict) and states:
            facts["states"] = copy.deepcopy(states)
        result["entities"][name] = facts
    if not result["robot"]:
        result.pop("robot")
    if not result["entities"]:
        result.pop("entities")
    return result


def _candidate_failed_preconditions(
    session: EvaluationSession,
    failure: EvaluationFailure,
) -> list[dict[str, Any]]:
    execution = (
        failure.step.get("execution", {})
        if isinstance(failure.step, dict)
        else {}
    )
    skill = (
        str(execution.get("skill", "") or "")
        if isinstance(execution, dict)
        else ""
    )
    catalog_get = getattr(session.skill_catalog, "get", None)
    spec = catalog_get(skill) if callable(catalog_get) else None
    code = failure.code.value
    required: dict[str, Any] = {
        "code": code,
        "required_condition": failure.fix_advice,
    }
    robot = failure.checkpoint_robot
    environment = failure.checkpoint_env

    if failure.code == EvaluationFailureCode.ARM_STATE:
        required_value = "空"
        if spec is not None and spec.can_place_item:
            required_value = spec.item_value(execution)
        required.update(
            {
                "predicate": "robot.robot_holding",
                "required_value": required_value,
                "actual_value": (
                    robot.get("robot_holding")
                    if isinstance(robot, dict)
                    else None
                ),
            }
        )
    elif failure.code == EvaluationFailureCode.NAVIGATION_PRECONDITION:
        target = ""
        if spec is not None:
            location_key = (
                spec.location_param
                or spec.destination_param
                or spec.device_param
                or spec.target_param
            )
            target = spec.param_value(execution, location_key)
        required.update(
            {
                "predicate": "robot.robot_location",
                "required_value": target or failure.fix_advice,
                "actual_value": (
                    robot.get("robot_location")
                    if isinstance(robot, dict)
                    else None
                ),
            }
        )
    elif failure.code == EvaluationFailureCode.CONTAINER_STATE and spec is not None:
        target = (
            spec.destination_value(execution)
            or spec.target_value(execution)
            or spec.device_value(execution)
        )
        state_key = spec.container_state_key or spec.state_key or "isOpen"
        required_value = (
            spec.container_state_value
            if spec.container_state_key
            else spec.state_value
            if spec.state_key
            else True
        )
        info = environment.get(target, {}) if isinstance(environment, dict) else {}
        states = info.get("states", {}) if isinstance(info, dict) else {}
        required.update(
            {
                "predicate": (
                    f"state.{target}.{state_key}"
                    if target
                    else "container_state"
                ),
                "required_value": required_value,
                "actual_value": states.get(state_key) if isinstance(states, dict) else None,
            }
        )
    elif failure.code == EvaluationFailureCode.DEVICE_STATE and spec is not None:
        target = spec.device_value(execution)
        state_key = spec.device_state_key or spec.state_key or "isToggled"
        required_value = (
            spec.device_state_value
            if spec.device_state_key
            else spec.state_value
            if spec.state_key
            else True
        )
        info = environment.get(target, {}) if isinstance(environment, dict) else {}
        states = info.get("states", {}) if isinstance(info, dict) else {}
        required.update(
            {
                "predicate": (
                    f"state.{target}.{state_key}"
                    if target
                    else "device_state"
                ),
                "required_value": required_value,
                "actual_value": states.get(state_key) if isinstance(states, dict) else None,
            }
        )
    return [required]


def _mark_latest_candidate_result(
    raw_history: Any,
    *,
    status: str,
    failure: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    history = [
        copy.deepcopy(entry)
        for entry in (raw_history or [])
        if isinstance(entry, dict)
    ]
    for entry in reversed(history):
        if entry.get("status") == "assembled" and entry.get("assembled") is True:
            entry["status"] = status
            if failure:
                entry["candidate_failure"] = copy.deepcopy(failure)
            break
    return history


def _mark_repair_candidate_accepted(session: EvaluationSession) -> None:
    if not _repair_candidate_transaction(session.context.state):
        return
    session.repair_history = _mark_latest_candidate_result(
        session.repair_history,
        status="accepted",
    )


def _complete_repair_history(
    raw_history: Any,
    request: dict[str, Any],
    *,
    generated_count: int,
) -> list[dict[str, Any]]:
    history = [
        copy.deepcopy(entry)
        for entry in (raw_history or [])
        if isinstance(entry, dict)
    ]
    for entry in reversed(history):
        if (
            entry.get("round") == request.get("round")
            and entry.get("stage") == request.get("stage")
            and entry.get("status") == "diagnosed"
        ):
            entry.update(
                {
                    "status": "assembled",
                    "generated_count": generated_count,
                    "assembled": True,
                }
            )
            break
    return history


def _assembly_failure(state: dict, error: str) -> dict[str, Any]:
    return {
        "todo_list": copy.deepcopy(state.get("todo_list") or []),
        "is_feasible": False,
        "execution_status": "failed",
        "failed_action": "任务规划",
        "error_feedback": error,
        "feedback": error,
        "failure_layer": "planning",
        "failure_category": "repair_assembly",
        "evaluation_repair_request": {},
        "repair_todo_list": [],
        "evaluation_recheck": False,
        "evaluation_revision_context": {},
        "repair_history": copy.deepcopy(state.get("repair_history") or []),
    }


def _retry_repair_assembly_output(
    state: dict[str, Any],
    request: dict[str, Any],
    error: str,
    *,
    generated_count: int,
) -> dict[str, Any]:
    """Retry malformed LLM repair output within the normal repair budget."""
    history = [
        copy.deepcopy(entry)
        for entry in (state.get("repair_history") or [])
        if isinstance(entry, dict)
    ]
    attempts = _repair_attempt_count(history)
    base_todo_list = request.get("original_todo_list")
    if not isinstance(base_todo_list, list):
        base_todo_list = state.get("todo_list") or []

    feedback = _repair_assembly_feedback(request, error)
    history = _mark_repair_assembly_rejected(
        history,
        request,
        generated_count=generated_count,
        feedback=feedback,
    )
    if attempts >= _repair_attempt_limit(state.get("feature_flags")):
        result = _assembly_failure(state, error)
        result.update(
            {
                "todo_list": copy.deepcopy(base_todo_list),
                "repair_history": history,
            }
        )
        return result

    failures = _candidate_failures_for_retry(request, feedback)
    failure_memory = _candidate_failure_memory(request, feedback)
    base_prompt = str(request.get("base_prompt") or request.get("prompt") or "")
    merge_context = copy.deepcopy(request.get("merge_context") or {})
    if feedback["active_window_ids"]:
        merge_context["active_window_ids"] = copy.deepcopy(
            feedback["active_window_ids"]
        )
    active_window_ids = merge_context.get("active_window_ids")
    accepted_window_ids = sorted(
        (merge_context.get("accepted_window_steps") or {}).keys()
    )
    retry_request = copy.deepcopy(request)
    retry_request.update(
        {
            "round": attempts + 1,
            "base_prompt": base_prompt,
            "prompt": _candidate_retry_prompt(
                base_prompt,
                failures,
                active_window_ids=active_window_ids,
                accepted_window_ids=accepted_window_ids,
                strategy_name=str(request.get("strategy_name", "") or ""),
                failure_memory=failure_memory,
            ),
            "candidate_failures": failures,
            "candidate_failure_memory": failure_memory,
            "merge_context": merge_context,
            "original_todo_list": copy.deepcopy(base_todo_list),
        }
    )
    history.append(
        {
            "round": retry_request["round"],
            "stage": retry_request["stage"],
            "status": "diagnosed",
            "generated_count": 0,
            "assembled": False,
            "failure": copy.deepcopy(retry_request.get("failure", {})),
        }
    )
    return {
        "todo_list": copy.deepcopy(base_todo_list),
        "is_feasible": False,
        "feedback": "重规划输出无法拼装，已请求按窗口反馈重新生成。",
        "evaluation_repair_request": retry_request,
        "repair_todo_list": [],
        "evaluation_recheck": False,
        "evaluation_revision_context": {},
        "repair_history": history,
        "planning_continuation": {},
        "repair_handoff": {},
    }


def _repair_assembly_feedback(
    request: dict[str, Any],
    error: str,
) -> dict[str, Any]:
    merge_context = request.get("merge_context") or {}
    active_window_ids = merge_context.get("active_window_ids")
    repair_windows = merge_context.get("repair_windows") or []
    if not isinstance(active_window_ids, list):
        active_window_ids = [
            item.get("window_id")
            for item in repair_windows
            if isinstance(item, dict) and str(item.get("window_id", "") or "").strip()
        ]
    active = [str(window_id) for window_id in active_window_ids]
    return {
        "validation_scope": "repair_assembly",
        "issue_type": "重规划窗口输出不完整",
        "assembly_error": error,
        "active_window_ids": active,
        "failed_preconditions": [
            {
                "code": "repair_window_coverage",
                "required_condition": "必须为每个活动 repair_window_id 输出至少一个动作",
                "actual_value": active,
            }
        ],
    }


def _mark_repair_assembly_rejected(
    raw_history: list[dict[str, Any]],
    request: dict[str, Any],
    *,
    generated_count: int,
    feedback: dict[str, Any],
) -> list[dict[str, Any]]:
    history = copy.deepcopy(raw_history)
    for entry in reversed(history):
        if (
            entry.get("round") == request.get("round")
            and entry.get("stage") == request.get("stage")
            and entry.get("status") == "diagnosed"
        ):
            entry.update(
                {
                    "status": "rejected",
                    "generated_count": generated_count,
                    "assembled": False,
                    "candidate_failure": copy.deepcopy(feedback),
                }
            )
            break
    return history


def _reindex(steps: list[dict]) -> list[dict]:
    return [
        {**copy.deepcopy(step), "step": index}
        for index, step in enumerate(steps, start=1)
        if isinstance(step, dict)
    ]


__all__ = ["assemble_repair_candidate", "evaluate_feasibility"]
