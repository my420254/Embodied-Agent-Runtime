from __future__ import annotations

import copy

try:
    from langchain_core.messages import HumanMessage
except Exception:  # pragma: no cover - fallback for lean test environments
    class HumanMessage:  # type: ignore[no-redef]
        def __init__(self, content: str):
            self.content = content

from config.json_utils import parse_json_from_llm
from config.llms import get_planning_llm
from graph.planning.config import get_planning_max_iterations, with_planning_config
from graph.planning.evaluation.evaluator import (
    assemble_repair_candidate,
)
from graph.planning.evaluation.validation.native_evaluator import (
    evaluate_feasibility as evaluate_todo_feasibility,
)
from graph.planning.evaluation.models import validate_evaluation_repair_request
from graph.planning.llm_decomposer import run_llm_decomposition
from graph.planning.repair import PlanningRegenerationError, regenerate_todo_list
from graph.state import PlanningState
from skills.action_codec import ensure_execution_shape
from skills.registry import load_enabled_skill_prompts, load_skill_prompts_for

def _terminal_cancel_result(iters: int) -> dict:
    return {
        "todo_list": [],
        "evaluation_repair_request": {},
        "repair_todo_list": [],
        "evaluation_recheck": False,
        "evaluation_revision_context": {},
        "iteration_count": iters,
        "execution_status": "fully_completed",
        "is_feasible": True,
        "feedback": "任务已取消，无需执行动作。",
    }


def _iteration_limit_result(iters: int) -> dict:
    return {
        "todo_list": [],
        "evaluation_repair_request": {},
        "repair_todo_list": [],
        "evaluation_recheck": False,
        "evaluation_revision_context": {},
        "iteration_count": iters,
        "is_feasible": False,
        "execution_status": "failed",
        "failed_action": "任务规划",
        "error_feedback": "迭代次数超限",
        "failure_layer": "planning",
    }


def _repair_model_failure(
    iters: int,
    error: PlanningRegenerationError,
    todo_list: list[dict],
) -> dict:
    return {
        "todo_list": copy.deepcopy(todo_list),
        "repair_todo_list": [],
        "evaluation_repair_request": {},
        "evaluation_recheck": False,
        "evaluation_revision_context": {},
        "iteration_count": iters,
        "is_feasible": False,
        "execution_status": "failed",
        "failed_action": "任务规划",
        "error_feedback": str(error),
        "feedback": str(error),
        "failure_layer": "planning",
        "failure_category": error.category,
    }


def decompose_task(state: PlanningState) -> PlanningState:
    """Planning graph entry node.

    Root-level planning owns request orchestration; model decomposition lives in
    llm_decomposer.py, and evaluation repair requests are consumed here.
    """

    state = with_planning_config(state)
    st_task = state.get("structured_task", {})
    st_task = st_task if isinstance(st_task, dict) else {}
    intent = str(st_task.get("intent", "") or "").strip()
    iters = int(state.get("iteration_count", 0) or 0) + 1
    feature_flags = state.get("feature_flags", {})
    planning_config = state.get("planning_config", {})

    if any(keyword in intent for keyword in ("终止", "取消", "结束")):
        return {
            **_terminal_cancel_result(iters),
            "feature_flags": feature_flags,
            "planning_config": planning_config,
        }

    if iters > get_planning_max_iterations():
        return {
            **_iteration_limit_result(iters),
            "feature_flags": feature_flags,
            "planning_config": planning_config,
        }

    request = state.get("evaluation_repair_request")
    if isinstance(request, dict) and request:
        result = _decompose_evaluation_repair(state, request, iters)
    else:
        result = run_llm_decomposition(state, llm_provider=get_planning_llm)

    result["feature_flags"] = feature_flags
    result["planning_config"] = planning_config
    result.setdefault("evaluation_repair_request", {})
    result.setdefault("repair_todo_list", [])
    result.setdefault("evaluation_recheck", False)
    result.setdefault("evaluation_revision_context", {})
    result.setdefault("environment_source", copy.deepcopy(state.get("environment_source") or {}))
    result.setdefault("counterfactual_task_completion", {})
    return result


def _decompose_evaluation_repair(
    state: PlanningState,
    request: dict,
    iters: int,
) -> PlanningState:
    original_todo = state.get("todo_list") or []
    request_error = validate_evaluation_repair_request(request)
    if request_error:
        return {
            "todo_list": copy.deepcopy(original_todo),
            "repair_todo_list": [],
            "evaluation_repair_request": copy.deepcopy(request),
            "execution_status": "failed",
            "is_feasible": False,
            "failed_action": "任务规划",
            "error_feedback": request_error,
            "failure_layer": "planning",
            "failure_category": "repair_request",
            "iteration_count": iters,
        }

    skill_profile = state.get("skill_profile")
    try:
        repair_todo = _regenerate_evaluation_repair(request, skill_profile)
    except PlanningRegenerationError as exc:
        return _repair_model_failure(iters, exc, original_todo)

    return {
        "todo_list": copy.deepcopy(original_todo),
        "repair_todo_list": repair_todo,
        "evaluation_repair_request": copy.deepcopy(request),
        "is_feasible": False,
        "evaluation_recheck": False,
        "evaluation_revision_context": {},
        "iteration_count": iters,
    }


def _regenerate_evaluation_repair(
    request: dict,
    skill_profile: str | None = None,
) -> list[dict]:
    skills_markdown = _repair_skills_markdown(request, skill_profile)
    return regenerate_todo_list(
        str(request.get("prompt", "")),
        skill_profile,
        skills_markdown,
        planning_llm_factory=get_planning_llm,
        parse_json=parse_json_from_llm,
        ensure_shape=lambda step: ensure_execution_shape(step, skill_profile),
        message_factory=HumanMessage,
    )


def _repair_skills_markdown(request: dict, skill_profile: str | None) -> str:
    if request.get("skill_contract_mode") == "compact":
        return ""
    # 1) 优先加载被拦截动作对应 skill 的针对性 prompt（RE-TRAC 按失败 skill 给文档，
    #    模型才知道该动作的前置/状态/持物前提，而不是全量技能表稀释注意力）
    failed_skill = ""
    failure = request.get("failure", {})
    if isinstance(failure, dict):
        failed_skill = str(failure.get("skill", "") or "").strip()
    if failed_skill:
        try:
            targeted = load_skill_prompts_for([failed_skill])
            if targeted.strip():
                return targeted
        except Exception:
            pass
    # 2) request 显式带上的技能文档
    for key in ("skills_markdown", "skill_contracts_markdown", "skill_prompts"):
        value = request.get(key)
        if isinstance(value, str):
            return value
    # 3) 兜底：全量 enabled skill prompts
    return load_enabled_skill_prompts(skill_profile)


def evaluate_candidate(state: PlanningState) -> PlanningState:
    return evaluate_todo_feasibility(state)


def _counterfactual_completion_deferred(state: PlanningState) -> bool:
    completion = state.get("counterfactual_task_completion")
    return bool(
        isinstance(completion, dict)
        and completion.get("status") == "not_completed"
        and completion.get("handled") is False
    )


def _after_decompose(state: PlanningState) -> str:
    if state.get("execution_status") in {"fully_completed", "failed"}:
        return "end"
    if state.get("evaluation_repair_request") and state.get("repair_todo_list"):
        return "assemble_repair"
    return "evaluate"


def _after_assemble(state: PlanningState) -> str:
    return "end" if state.get("execution_status") == "failed" else "evaluate"


def _after_evaluate(state: PlanningState) -> str:
    if (
        state.get("is_feasible")
        or state.get("execution_status") == "failed"
        or _counterfactual_completion_deferred(state)
    ):
        return "end"
    if state.get("evaluation_recheck"):
        return "evaluate"
    return "decompose"


def build_planning_graph():
    try:
        from langgraph.graph import END, StateGraph
    except Exception as exc:  # pragma: no cover - fail-soft import boundary
        raise RuntimeError("langgraph is required to build the planning graph") from exc

    workflow = StateGraph(PlanningState)
    workflow.add_node("decompose", decompose_task)
    workflow.add_node("assemble_repair", assemble_repair_candidate)
    workflow.add_node("evaluate", evaluate_candidate)
    workflow.set_entry_point("decompose")
    workflow.add_conditional_edges(
        "decompose",
        _after_decompose,
        {
            "end": END,
            "assemble_repair": "assemble_repair",
            "evaluate": "evaluate",
        },
    )
    workflow.add_conditional_edges(
        "assemble_repair",
        _after_assemble,
        {
            "end": END,
            "evaluate": "evaluate",
        },
    )
    workflow.add_conditional_edges(
        "evaluate",
        _after_evaluate,
        {
            "end": END,
            "evaluate": "evaluate",
            "decompose": "decompose",
        },
    )
    return workflow.compile()


__all__ = [
    "build_planning_graph",
    "decompose_task",
    "evaluate_candidate",
    "_regenerate_evaluation_repair",
]
