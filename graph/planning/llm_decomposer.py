from __future__ import annotations

import copy
import inspect
from typing import Any

from config.json_utils import parse_json_from_llm
from config.llms import get_planning_llm, llm_trace_context
from config.module_loader import resolve_callable
from graph.planning.evaluation.outcomes.continuation import (
    EMPTY_FAILED_LESSONS_TEXT,
    strip_repeated_prefix,
)
from graph.planning.normalizer import (
    _format_task_environment_facts,
    _normalize_todo_list,
    environment_from_state,
    task_already_satisfied,
    task_context as get_task_context,
    task_source_text as get_task_source_text,
)
from graph.planning.prompts import build_planning_messages
from graph.planning.repair import (
    sda_current_state,
    sda_todo_action_prefix,
    sda_todo_prefix,
)
from graph.planning.config import (
    REPAIR_STRATEGY_SDA,
    active_repair_strategy,
    planning_feature_enabled,
)
from graph.state import PlanningState
from skills.action_codec import ensure_execution_shape


def _todo_parser_path(state: PlanningState) -> str:
    return str(state.get("todo_output_parser_path") or "").strip()


def _todo_completed_output(text: str) -> bool:
    parsed = parse_json_from_llm(text, fallback=None)
    if isinstance(parsed, dict):
        status = str(parsed.get("status", "") or "").strip().lower()
        if status == "completed":
            return True
        return not parsed
    if isinstance(parsed, list):
        return not parsed
    return False


def _todo_parser_kwargs(
    parser, *, state: PlanningState, prompt_text: str, current_env: dict
) -> dict:
    kwargs = {
        "env_state": current_env,
        "current_env": current_env,
        "prompt": prompt_text,
        "state": state,
    }
    try:
        signature = inspect.signature(parser)
    except (TypeError, ValueError):
        return {}
    accepts_var_kw = any(
        param.kind == inspect.Parameter.VAR_KEYWORD
        for param in signature.parameters.values()
    )
    if accepts_var_kw:
        return kwargs
    return {
        name: value for name, value in kwargs.items() if name in signature.parameters
    }


def _parse_todo_schema_planner_output(
    text: str,
    *,
    state: PlanningState,
    prompt_text: str,
    current_env: dict,
    allow_completed: bool = True,
) -> tuple[str, str, list[dict]]:
    if _todo_completed_output(text):
        if not allow_completed:
            raise ValueError("任务未确认完成时，todo_list 输出不能为空或 completed")
        return "completed", str(text or "").strip(), []
    parser = resolve_callable(
        _todo_parser_path(state),
        required=False,
        label="todo_output_parser",
    )
    if not callable(parser):
        raise ValueError("缺少 todo_output_parser，无法解析当前数据集的 todo_list")
    normalized, native_plan = parser(
        text,
        **_todo_parser_kwargs(
            parser, state=state, prompt_text=prompt_text, current_env=current_env
        ),
    )
    if not isinstance(native_plan, list):
        raise ValueError("todo_output_parser 必须返回动作列表")
    if not native_plan:
        raise ValueError("status=planned 时必须输出非空 todo_list 动作序列")
    return "planned", str(normalized or text or "").strip(), native_plan


def _reindex_todo_actions(native_actions: list[dict]) -> list[dict]:
    normalized: list[dict] = []
    for index, step in enumerate(native_actions or [], start=1):
        if not isinstance(step, dict):
            continue
        item = copy.deepcopy(step)
        item["step"] = index
        normalized.append(item)
    return normalized


def _todo_action_signature(step: dict[str, Any]) -> str:
    item = copy.deepcopy(step if isinstance(step, dict) else {})
    item.pop("step", None)
    try:
        return str(sorted(item.items()))
    except Exception:
        return str(item)


def _strip_repeated_todo_prefix(
    prefix: list[dict[str, Any]],
    candidate_steps: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not prefix or not candidate_steps:
        return copy.deepcopy(candidate_steps or [])
    if len(candidate_steps) < len(prefix):
        return copy.deepcopy(candidate_steps or [])
    if all(
        _todo_action_signature(candidate_steps[index])
        == _todo_action_signature(prefix[index])
        for index in range(len(prefix))
    ):
        return copy.deepcopy(candidate_steps[len(prefix) :])
    return copy.deepcopy(candidate_steps)


def _todo_action_prefix_from_retrac(state: PlanningState) -> list[dict[str, Any]]:
    retrac_state = state.get("re_trac_state", {})
    if not isinstance(retrac_state, dict):
        return []
    todo_trajectory = retrac_state.get("todo_trajectory", {})
    if isinstance(todo_trajectory, dict):
        prefix = todo_trajectory.get("validated_prefix")
        if isinstance(prefix, list) and prefix:
            return _reindex_todo_actions(prefix)
    trajectory = retrac_state.get("trajectory", {})
    if isinstance(trajectory, dict):
        prefix = trajectory.get("validated_todo_prefix")
        if isinstance(prefix, list) and prefix:
            return _reindex_todo_actions(prefix)
    return []


def _retrac_current_state(
    state: PlanningState,
    *,
    fallback_env: dict[str, Any],
    fallback_robot: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    retrac_state = state.get("re_trac_state", {})
    current = (
        retrac_state.get("current_simulated_state", {})
        if isinstance(retrac_state, dict)
        else {}
    )
    if not isinstance(current, dict):
        return fallback_env, fallback_robot
    env = current.get("environment")
    robot = current.get("robot")
    return (
        copy.deepcopy(env if isinstance(env, dict) and env else fallback_env),
        copy.deepcopy(robot if isinstance(robot, dict) and robot else fallback_robot),
    )


def _current_state_satisfied_reason(
    *,
    structured_task: dict[str, Any],
    current_env: dict[str, Any],
    current_robot: dict[str, Any],
    task_context: dict[str, Any],
) -> str:
    if task_context.get("ambiguous_goal_entities"):
        return ""
    try:
        return task_already_satisfied(
            structured_task,
            current_env,
            current_robot,
            task_context=task_context,
        )
    except Exception:
        return ""


def _parse_todo_planner_output(text: str) -> tuple[str, list]:
    parsed = parse_json_from_llm(text, fallback={})
    if isinstance(parsed, list):
        return "planned", parsed
    if not isinstance(parsed, dict):
        raise ValueError("规划层输出必须是 JSON 对象或数组")
    status = str(parsed.get("status", "planned")).strip().lower()
    if status not in {"planned", "completed"}:
        raise ValueError("规划层输出的 status 只能是 planned 或 completed")
    sequence = parsed.get("todo_list")
    if sequence is None:
        sequence = parsed.get("skill_sequence")
    if sequence is None:
        sequence = parsed.get("actions")
    if sequence is None:
        sequence = []
    if not isinstance(sequence, list):
        raise ValueError("规划层输出的动作序列必须是列表")
    if status == "planned" and not sequence:
        raise ValueError("status=planned 时必须输出非空动作序列")
    if status == "completed" and sequence:
        raise ValueError("status=completed 时动作序列必须为空")
    return status, sequence


def run_llm_decomposition(
    state: PlanningState,
    *,
    llm_provider=get_planning_llm,
) -> PlanningState:
    st_task = state.get("structured_task", {})
    st_task = st_task if isinstance(st_task, dict) else {}
    intent = str(st_task.get("intent", "") or "").strip()
    iters = int(state.get("iteration_count", 0) or 0) + 1
    feature_flags = state.get("feature_flags", {})
    env_state = state.get(
        "env_state", {"robot_location": "未知", "robot_holding": "空"}
    )
    env_state = env_state if isinstance(env_state, dict) else {}
    environment = environment_from_state(state)
    task_context = get_task_context(state)
    task_source_text = get_task_source_text(state)
    configured_todo_parser = bool(_todo_parser_path(state))

    if not intent:
        return {
            "todo_list": [],
            "iteration_count": iters,
            "feedback": "缺少任务意图，无法生成动作序列。",
        }

    ambiguous_goal_entities = (
        task_context.get("ambiguous_goal_entities", [])
        if isinstance(task_context, dict)
        else []
    )
    satisfied_reason = (
        ""
        if ambiguous_goal_entities
        else task_already_satisfied(
            st_task,
            environment,
            env_state,
            task_context=task_context,
        )
    )
    if satisfied_reason:
        return {
            "todo_list": [],
            "planner_status": "completed",
            "iteration_count": iters,
            "environment": environment,
            "env_state": env_state,
            "is_feasible": True,
            "execution_status": "fully_completed",
            "feedback": satisfied_reason,
        }

    continuation = state.get("planning_continuation", {})
    continuation = continuation if isinstance(continuation, dict) else {}
    # retrac 的交互 sandbox 失败回路把已验证前缀写在 state 顶层（build_failure_payload
    # 只写 validated_steps/checkpoint_env/checkpoint_robot，从不投影 planning_continuation）。
    # 非 parser 路径此前只读 continuation，continuation 恒为空 -> 前缀恒为空 -> 每轮从头重规划。
    # 故在 continuation 缺省时回退到顶层，与 validated_todo_actions 一直读顶层保持一致；
    # parser/benchmark 路径另有 _todo_action_prefix_from_retrac + _retrac_current_state 兜底，不受影响。
    continuation_validated_steps = continuation.get("validated_steps")
    if continuation_validated_steps is None and not configured_todo_parser:
        continuation_validated_steps = state.get("validated_steps", [])
    validated_steps = [
        copy.deepcopy(step)
        for step in (continuation_validated_steps or [])
        if isinstance(step, dict)
    ]
    validated_todo_actions = [
        copy.deepcopy(step)
        for step in state.get("validated_todo_actions", [])
        if isinstance(step, dict)
    ]
    if configured_todo_parser and not validated_todo_actions:
        validated_todo_actions = _todo_action_prefix_from_retrac(state)
    current_robot = continuation.get("current_robot") or env_state
    current_env = continuation.get("current_env") or environment
    if not configured_todo_parser and not continuation:
        # 与 validated_steps 配套的断点态同样写在顶层；续写必须从断点恢复，而非退回原始场景。
        current_robot = state.get("checkpoint_robot") or current_robot
        current_env = state.get("checkpoint_env") or current_env
    if configured_todo_parser and not continuation:
        current_env, current_robot = _retrac_current_state(
            state,
            fallback_env=current_env,
            fallback_robot=current_robot,
        )
    if active_repair_strategy() == REPAIR_STRATEGY_SDA:
        sda_state = state.get("sda_state", {})
        if isinstance(sda_state, dict):
            if not validated_steps:
                validated_steps = sda_todo_prefix(sda_state)
            if not validated_todo_actions:
                validated_todo_actions = sda_todo_action_prefix(sda_state)
            if not continuation:
                current_env, current_robot = sda_current_state(
                    sda_state,
                    fallback_env=environment,
                    fallback_robot=env_state,
                )
    next_step_num = int(
        continuation.get("next_step_num")
        or len(validated_todo_actions if configured_todo_parser else validated_steps)
        + 1
    )
    repair_handoff = continuation.get("repair_handoff", {})
    repair_handoff = repair_handoff if isinstance(repair_handoff, dict) else {}
    if not repair_handoff:
        if active_repair_strategy() == REPAIR_STRATEGY_SDA:
            repair_handoff = state.get("sda_state", {})
        else:
            repair_handoff = state.get("re_trac_state", {})
        repair_handoff = repair_handoff if isinstance(repair_handoff, dict) else {}

    messages, injected_rule_ids = build_planning_messages(
        current_robot=current_robot,
        current_env=current_env,
        navigation_contract="",
        task_environment_facts=_format_task_environment_facts(current_env),
        task_context=task_context,
        task_source_text=task_source_text,
        names_info=st_task.get("required_item_names", {})
        if isinstance(st_task.get("required_item_names", {}), dict)
        else {},
        understanding_final_state=(
            st_task.get("final_state", {})
            if isinstance(st_task.get("final_state", {}), dict)
            else {}
        ),
        skill_closure=state.get("skill_closure", []),
        failed_lessons=continuation.get("failed_lessons", EMPTY_FAILED_LESSONS_TEXT),
        intent=intent,
        feedback=str(state.get("feedback", "") or ""),
        validated_steps=validated_todo_actions
        if configured_todo_parser
        else validated_steps,
        next_step_num=next_step_num,
        repair_handoff=repair_handoff,
        feature_flags=feature_flags,
    )

    call_stage = (
        "planning_repair"
        if (
            validated_steps
            or validated_todo_actions
            or repair_handoff
            or state.get("feedback")
        )
        else "planning_initial"
    )
    with llm_trace_context(
        process_name="planning",
        prompt_name="planning.main_system",
        call_stage=call_stage,
        planning_iteration=int(state.get("iteration_count", 0) or 0) + 1,
    ):
        response = llm_provider().invoke(messages)
    raw_output = str(getattr(response, "content", "") or "")
    parse_error_feedback = ""
    planner_status = "planned"
    todo_list: list[dict] = []

    if configured_todo_parser:
        try:
            planner_status, parsed_native_output, parsed_native_plan = (
                _parse_todo_schema_planner_output(
                    raw_output,
                    state=state,
                    prompt_text=task_source_text,
                    current_env=current_env,
                    allow_completed=False,
                )
            )
            if validated_todo_actions:
                parsed_native_plan = _strip_repeated_todo_prefix(
                    validated_todo_actions,
                    parsed_native_plan,
                )
            todo_list = _reindex_todo_actions(
                validated_todo_actions + parsed_native_plan
            )
            raw_output = parsed_native_output
            if planner_status == "completed" and task_context.get(
                "ambiguous_goal_entities"
            ):
                planner_status = "planned"
                if not parsed_native_plan:
                    parse_error_feedback = (
                        "重复类别目标未绑定具体实例，禁止空计划完成。"
                    )
        except Exception as exc:
            if validated_todo_actions and _todo_completed_output(raw_output):
                state_diff_audit_enabled = planning_feature_enabled(
                    feature_flags,
                    "state_diff_audit",
                    default=False,
                )
                satisfied_reason = _current_state_satisfied_reason(
                    structured_task=st_task,
                    current_env=current_env,
                    current_robot=current_robot,
                    task_context=task_context,
                )
                if state_diff_audit_enabled or satisfied_reason:
                    planner_status = "planned"
                    todo_list = _reindex_todo_actions(validated_todo_actions)
                else:
                    parse_error_feedback = (
                        "todo_list 续写为空，但当前状态未被目标检查确认完成；"
                        "必须输出后续动作或启用最终态审计。"
                    )
                    print(f"[规划层] {parse_error_feedback}")
            else:
                parse_error_feedback = f"todo_list 输出解析失败: {exc}"
                print(f"[规划层] {parse_error_feedback}")
    else:
        try:
            planner_status, parsed_todo = _parse_todo_planner_output(raw_output)
            filtered_new_list = []
            for index, raw_step in enumerate(parsed_todo):
                step = ensure_execution_shape(raw_step)
                if not isinstance(step, dict):
                    step = {"raw_step": raw_step}
                step["step"] = next_step_num + index
                filtered_new_list.append(step)
            if validated_steps:
                filtered_new_list = strip_repeated_prefix(
                    validated_steps, filtered_new_list
                )
                for index, step in enumerate(filtered_new_list):
                    step["step"] = next_step_num + index
            todo_list = _normalize_todo_list(
                validated_steps + filtered_new_list,
                env_state,
                skill_profile=state.get("skill_profile"),
                flat_house=environment,
            )
        except Exception as exc:
            parse_error_feedback = f"规划层输出解析失败: {exc}"
            print(f"[规划层] {parse_error_feedback}")

    result: dict[str, Any] = {
        "todo_list": todo_list,
        "iteration_count": iters,
        "environment": environment,
        "env_state": env_state,
        "injected_playbook_rule_ids": injected_rule_ids,
        "planner_status": planner_status,
        "todo_llm_output": raw_output if configured_todo_parser else "",
        "todo_parse_error": "",
        # 透传给 decompose 输出块，供 renderer 如实显示“已锁定前 N 步 / RE-TRAC 防错记录”。
        # planning 是子图，主图 get_state() 在子图运行中看不到其内部 validated_steps，
        # 因此必须由本节点回吐；evaluate 会基于 todo_list 重新沙盒验证并覆盖 validated_steps，不受影响。
        "validated_steps": [copy.deepcopy(step) for step in validated_steps],
        "re_trac_memory": state.get("re_trac_memory", {}),
    }
    if parse_error_feedback:
        result["feedback"] = parse_error_feedback
        result["is_feasible"] = False
        result["todo_parse_error"] = (
            parse_error_feedback if configured_todo_parser else ""
        )
    elif not todo_list:
        if planner_status == "completed":
            result["feedback"] = "规划器判断当前任务已完成。"
            result["execution_status"] = "fully_completed"
            result["is_feasible"] = True
        else:
            result["feedback"] = "规划层未生成任何有效动作序列。"
    return result


__all__ = ["run_llm_decomposition"]
