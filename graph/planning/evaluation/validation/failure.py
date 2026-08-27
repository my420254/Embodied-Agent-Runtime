from __future__ import annotations

import copy
import importlib

from langchain_core.messages import HumanMessage

from ace.playbook import curate_evaluator_finding, record_rule_feedback
from config.json_utils import parse_json_from_llm
from config.llms import get_planning_llm
from graph.planning.config import feature_enabled
from graph.planning.evaluation.validation.debug_events import append_debug_event, sync_debug_event_aliases
from graph.planning.config import REPAIR_STRATEGY_RETRAC, REPAIR_STRATEGY_SDA, active_repair_strategy
from re_trac import build_failure_finding, build_failure_payload, failed_lesson_occurrences


def _dataset_failure_diagnosis(
    issue_type: str,
    fix: str,
    step_info: dict,
    env: dict,
    robot: dict,
) -> dict:
    """Load an optional benchmark-local taxonomy without changing behavior."""
    try:
        from config.settings import get_config

        module_name = get_config("evaluation", "failure_policy", default="")
        if not module_name:
            module_name = get_config("planning", "evaluation", "failure_policy", default="")
        if not module_name:
            return {}
        policy = importlib.import_module(str(module_name))
        classifier = getattr(policy, "classify_failure", None)
        if not callable(classifier):
            return {}
        execution = step_info.get("execution", {})
        if not isinstance(execution, dict):
            execution = {}
        result = classifier(
            issue_type,
            fix,
            skill=execution.get("skill", ""),
            parameters=execution.get("parameters", {}),
            environment=env,
            robot=robot,
        )
        return result if isinstance(result, dict) else {}
    except Exception:
        # A reporting plugin must never make the evaluator fail.
        return {}


def save_evaluator_finding_to_playbook(
    raw_issue: str,
    raw_fix: str,
    intent: str,
    step_detail: str,
    *,
    feature_flags: dict | None = None,
):
    if not feature_enabled(feature_flags, "playbook_write", default=False):
        return

    def invoke_curator(prompt: str) -> dict:
        response = get_planning_llm().invoke([HumanMessage(content=prompt)])
        return parse_json_from_llm(response.content)

    curate_evaluator_finding(
        raw_issue,
        raw_fix,
        intent,
        step_detail,
        invoke_curator,
        feature_flags=feature_flags,
    )


def report_audit_failure(
    step_info: dict,
    issue_type: str,
    fix: str,
    intent: str,
    memory: dict,
    iters: int,
    validated_steps: list,
    env: dict,
    robot: dict,
    injected_rule_ids: list[str] | None = None,
    max_iterations: int | None = None,
    feature_flags: dict | None = None,
    attempted_steps: list | None = None,
    debug_events: list[dict] | None = None,
    validated_todo_actions: list | None = None,
    todo_checkpoint_env: dict | None = None,
    todo_checkpoint_robot: dict | None = None,
    re_trac_state: dict | None = None,
) -> dict:
    repair_strategy = active_repair_strategy()
    record_retrac = repair_strategy == REPAIR_STRATEGY_RETRAC
    track_repeated_failure = repair_strategy in {REPAIR_STRATEGY_RETRAC, REPAIR_STRATEGY_SDA}
    step_num = step_info.get("step", "?")
    skill_name = str(step_info.get("execution", {}).get("skill", "") or "").strip().upper()
    if skill_name == "GOAL_CHECK":
        full_issue = f"最终态检查拦截: {issue_type}"
    elif skill_name in {"TODO_CONTRACT", "PLAN_CONTRACT"}:
        full_issue = f"序列验证拦截: {issue_type}"
    else:
        full_issue = f"第 {step_num} 步物理拦截: {issue_type}"
    finding = build_failure_finding(step_info=step_info, issue=full_issue, fix=fix)
    repeated_same_failure = track_repeated_failure and failed_lesson_occurrences(memory, full_issue, fix) >= 1

    save_evaluator_finding_to_playbook(
        full_issue,
        fix,
        intent,
        str(step_info),
        feature_flags=feature_flags,
    )
    record_rule_feedback(
        "planning",
        injected_rule_ids,
        outcome="harmful",
        feature_flags=feature_flags,
    )

    result = build_failure_payload(
        issue=full_issue,
        fix=fix,
        memory=memory,
        validated_steps=validated_steps,
        checkpoint_env=env,
        checkpoint_robot=robot,
        validated_todo_actions=validated_todo_actions,
        todo_checkpoint_env=todo_checkpoint_env,
        todo_checkpoint_robot=todo_checkpoint_robot,
        re_trac_state=re_trac_state if record_retrac else {},
        finding=finding,
        record_retrac_memory=track_repeated_failure,
    )
    result["repair_strategy"] = repair_strategy
    result["execution_status"] = "running"
    result["failed_action"] = copy.deepcopy(step_info)
    result["error_feedback"] = full_issue
    result["failure_layer"] = "planning"
    result["failure_category"] = "sandbox_validation"
    diagnosis = _dataset_failure_diagnosis(issue_type, fix, step_info, env, robot)
    if diagnosis:
        result["dataset_failure_diagnosis"] = diagnosis
        result["failure_error_code"] = diagnosis.get("error_code", "")
    result["todo_list"] = list(attempted_steps or [])
    result["planning_debug_events"] = append_debug_event(
        {"planning_debug_events": list(debug_events or [])},
        {
            "layer": "planning_evaluator",
            "type": "audit_failure",
            "issue": full_issue,
            "fix": fix,
            "step_info": copy.deepcopy(step_info),
            "validated_steps_count": len(validated_steps or []),
            "validated_todo_actions_count": len(validated_todo_actions or []),
        },
    )
    if repeated_same_failure:
        result.update(
            {
                "execution_status": "failed",
                "failed_action": "任务规划",
                "error_feedback": "重复同类错误，终止沙盒拦截",
                "failure_layer": "planning",
            }
        )
        result["feedback"] = (
            f"{full_issue}\n{fix}\n"
            f"重复犯同类错误：{issue_type}，终止沙盒拦截。"
        )
        result["planning_debug_events"] = append_debug_event(
            {"planning_debug_events": list(result.get("planning_debug_events") or [])},
            {
                "layer": "planning_evaluator",
                "type": "stop_on_repeated_failure",
                "issue": full_issue,
                "fix": fix,
            },
        )
    if max_iterations is None:
        max_iterations = 10
    if iters >= max_iterations:
        failed_todo_list = (
            list(attempted_steps or [])
            if feature_enabled(feature_flags, "preserve_failed_todo_list", default=False)
            else []
        )
        result.update(
            {
                "execution_status": "failed",
                "todo_list": failed_todo_list,
                "failed_action": "任务规划",
                "error_feedback": "迭代次数超限",
                "failure_layer": "planning",
            }
        )
    return sync_debug_event_aliases(result)
