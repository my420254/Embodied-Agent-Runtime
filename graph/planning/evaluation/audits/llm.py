# audits/llm.py - LLM audit and finding-curation adapters.
# LLM 通过函数参数注入；技能 prompt 由 EvaluationSkillSnapshot 传入调用方。
from __future__ import annotations

import copy
from typing import Any, Callable

# render_prompt / parse_json_from_llm 不被 patch，直接 top-level 引入。
from config.json_utils import parse_json_from_llm
from config.llms import llm_trace_context
from config.prompts import render_prompt

try:
    from langchain_core.messages import HumanMessage
except Exception:  # pragma: no cover - fallback for lean test environments
    class HumanMessage:  # type: ignore[no-redef]
        def __init__(self, content: str):
            self.content = content


def _run_state_diff_audit(
    *,
    intent: str,
    todo_list: list,
    simulated_steps: list,
    trajectory: str,
    state_diff: dict[str, Any],
    state_audit_context: dict[str, Any],
    get_planning_llm: Callable[[], Any],
) -> dict[str, Any]:
    prompt = render_prompt(
        "planning.state_diff_audit",
        intent=intent,
        todo_list_json=_json_dumps(_compact_action_sequence(todo_list)),
        action_plan_json=_json_dumps(_compact_action_sequence(todo_list)),
        simulated_steps_json=_json_dumps(_compact_action_sequence(simulated_steps)),
        trajectory=trajectory,
        state_diff_json=_json_dumps(state_diff),
        state_audit_context_json=_json_dumps(state_audit_context),
    )
    with llm_trace_context(
        process_name="final_state_audit",
        prompt_name="planning.state_diff_audit",
        call_stage="state_diff_audit",
    ):
        response = get_planning_llm().invoke([HumanMessage(content=prompt)])
    result = parse_json_from_llm(response.content)
    if not isinstance(result, dict) or not isinstance(result.get("is_passed"), bool):
        raise ValueError("状态差异审计输出缺少布尔字段 is_passed")
    return result


def _run_counterfactual_task_completion(
    *,
    intent: str,
    todo_list: list,
    state_diff: dict[str, Any],
    state_audit_context: dict[str, Any],
    get_planning_llm: Callable[[], Any],
) -> dict[str, Any]:
    """Judge only whether a counterfactual terminal state satisfies the task."""

    prompt = render_prompt(
        "planning.counterfactual_task_completion",
        intent=intent,
        todo_list_json=_json_dumps(_compact_action_sequence(todo_list)),
        action_plan_json=_json_dumps(_compact_action_sequence(todo_list)),
        state_diff_json=_json_dumps(state_diff),
        state_audit_context_json=_json_dumps(state_audit_context),
    )
    with llm_trace_context(
        process_name="counterfactual_task_completion",
        prompt_name="planning.counterfactual_task_completion",
        call_stage="counterfactual_task_completion",
    ):
        response = get_planning_llm().invoke([HumanMessage(content=prompt)])
    result = parse_json_from_llm(response.content)
    if not isinstance(result, dict) or not isinstance(
        result.get("task_completed"), bool
    ):
        raise ValueError("反事实任务完成度输出缺少布尔字段 task_completed")
    return {
        "task_completed": result["task_completed"],
        "evidence": str(result.get("evidence", "") or ""),
    }


def _compact_action_sequence(todo_list: list | None) -> list[dict[str, Any]]:
    compact_steps = []
    for step in todo_list or []:
        if not isinstance(step, dict):
            continue
        execution = step.get("execution", {})
        if isinstance(execution, dict) and execution:
            compact_steps.append(
                {
                    "step": step.get("step"),
                    "skill": execution.get("skill", ""),
                    "parameters": copy.deepcopy(execution.get("parameters", {})),
                }
            )
            continue
        if "action" in step:
            compact_steps.append(
                {
                    key: copy.deepcopy(value)
                    for key, value in step.items()
                    if key != "step"
                }
            )
            continue
        compact_steps.append({"step": step.get("step")})
    return compact_steps


def _run_semantic_audit(
    *,
    intent: str,
    trajectory: str,
    current_env_json: str,
    robot_state_json: str,
    navigation_contract: str,
    skills_markdown: str,
    get_planning_llm: Callable[[], Any],
) -> dict[str, Any]:
    prompt = render_prompt(
        "planning.audit",
        intent=intent,
        trajectory=trajectory,
        current_env_json=current_env_json,
        robot_state_json=robot_state_json,
        navigation_contract=navigation_contract,
        skills_markdown=skills_markdown,
    )
    with llm_trace_context(
        process_name="semantic_audit",
        prompt_name="planning.audit",
        call_stage="semantic_audit",
    ):
        response = get_planning_llm().invoke([HumanMessage(content=prompt)])
    result = parse_json_from_llm(response.content)
    if isinstance(result, dict) and isinstance(result.get("is_passed"), bool):
        return result

    retry_prompt = (
        "上一轮语义审计输出无法解析。必须只输出一个 JSON 对象，不要解释、不要 markdown、不要额外文本。"
        "格式严格为：{\"is_passed\": true, \"issue\": \"\", \"fix_advice\": \"\"}\n\n"
        f"任务目标：{intent}\n\n"
        f"动作轨迹：\n{trajectory}\n\n"
        f"导航契约：\n{navigation_contract}\n\n"
        "如果轨迹能完成任务且没有明确违反技能契约，输出 is_passed=true。"
    )
    with llm_trace_context(
        process_name="semantic_audit",
        prompt_name="planning.audit",
        call_stage="semantic_audit_retry",
    ):
        retry_response = get_planning_llm().invoke([HumanMessage(content=retry_prompt)])
    retry_result = parse_json_from_llm(retry_response.content)
    if not isinstance(retry_result, dict) or not isinstance(retry_result.get("is_passed"), bool):
        raise ValueError("语义审计输出缺少布尔字段 is_passed")
    return retry_result


def save_evaluator_finding_to_playbook(
    raw_issue: str,
    raw_fix: str,
    intent: str,
    step_detail: str,
    *,
    feature_flags: dict | None = None,
    get_planning_llm: Callable[[], Any],
):
    # 把一次具体的“失败原因 + 修复建议”交给 LLM 做经验抽象，再尝试写回 playbook。
    # 这里不直接把 raw_issue/raw_fix 生写进经验库，是为了避免经验规则过于偶然、碎片化。
    # curate_evaluator_finding 来自 ace.playbook，不被 patch，直接 top-level 引入。
    from ace.playbook import curate_evaluator_finding

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


def _json_dumps(data: Any) -> str:
    # 与 state_diff._json_dumps 相同实现；这里独立保留，避免 audit_llm 依赖纯逻辑子模块。
    import json

    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


__all__ = [
    "_run_counterfactual_task_completion",
    "_run_state_diff_audit",
    "_run_semantic_audit",
    "save_evaluator_finding_to_playbook",
]
