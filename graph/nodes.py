import copy
import re
from graph.state import GlobalState
from graph.planning.config import REPAIR_STRATEGY_RETRAC, active_repair_strategy
from re_trac import empty_checkpoint_state

try:
    from langchain_core.messages import AIMessage, HumanMessage
except Exception:  # pragma: no cover - fallback for lean test environments
    class _Message:  # type: ignore[no-redef]
        def __init__(self, content: str):
            self.content = content

    class AIMessage(_Message):
        pass

    class HumanMessage(_Message):
        pass

# 本文件里的函数都是 LangGraph 节点：
# 它们不直接“执行任务”，而是根据当前 GlobalState 生成一份“局部状态更新字典”，
# 再由图框架把这些更新合并回全局状态。

# 读取 feature flag 的小工具。
# 这里故意做了两层兜底：
# 1. feature_flags 缺失或不是 dict 时，直接回退到默认值；
# 2. 只有当指定开关显式出现在 feature_flags 中时，才覆盖默认值。
# 这样调用方可以在“不传该开关”和“显式关闭该开关”之间做区分。
def _feature_enabled(state: GlobalState, name: str, default: bool = True) -> bool:
    flags = state.get("feature_flags", {})
    if isinstance(flags, dict) and name in flags:
        return bool(flags[name])
    return default

# 把规划层当前产出的 todo_list 包装进 interrupt_signal，交给执行层消费。
# 这个节点本质上是“注入式派发”：
# 1. 保留 interrupt_signal 里原有的其他字段；
# 2. 追加 execution manager 真正关心的 new_todo_list / is_cancel / intent；
# 3. 把 execution_status 重新置为 running，驱动主图继续向执行链路前进。
# 注意：这里不会改 task_stack，只是把“要执行什么”放进中断载荷里。
def inject_and_execute_node(state: GlobalState) -> dict:
    new_todo = state.get("todo_list", [])
    interrupt_signal = state.get("interrupt_signal", {})
    is_cancel = state.get("is_cancel_all", False)
    intent = state.get("structured_task", {}).get("intent", "未知意图")

    updated_signal = {
        **interrupt_signal,
        "new_todo_list": new_todo,
        "is_cancel": is_cancel,
        "intent": intent,
    }
    trace = state.get("cognitive_planning_trace", {})
    behavior_tree = trace.get("behavior_tree", {}) if isinstance(trace, dict) else {}
    if isinstance(behavior_tree, dict) and behavior_tree.get("compiled") is True:
        updated_signal["behavior_tree"] = dict(behavior_tree)

    return {
        "interrupt_signal": updated_signal,
        "execution_status": "running",
    }


# 处理“用户发来全新指令并中断当前任务”的入口节点。
# 这里做的不是简单记录一条消息，而是把旧任务的理解/规划现场尽量清空：
# 1. raw_instruction 改成新的中断文本；
# 2. 旧 structured_task、todo_list、environment、审计结果、checkpoint 全部作废；
# 3. 通过追加一条带强提示的 HumanMessage，强制后续理解层只围绕新指令工作。
# 这样可以避免旧任务的 intent、约束和环境假设污染新一轮解析。
def handle_interrupt_node(state: GlobalState) -> dict:
    interrupt_signal = state.get("interrupt_signal", {})
    interrupt_text = interrupt_signal.get("text", "")

    wrapped_text = (
        f"【系统警报：用户紧急中断了前置任务，发布了全新指令！"
        f"请彻底抛弃历史意图，严格仅针对此新指令进行解析】\n新指令：{interrupt_text}"
    )

    return {
        "raw_instruction": interrupt_text,
        "structured_task": {},
        "clarification_question": "",
        "is_complete": False,
        "todo_list": [],
        "is_feasible": False,
        "iteration_count": 0,
        "feedback": "",
        "environment": {},
        "evaluator_findings": [],
        # 中断意味着旧任务的 checkpoint 也不再可信，因此一并清空。
        **empty_checkpoint_state(),
        # messages 使用 operator.add reducer，只返回本节点新增消息，避免重复累加历史。
        "messages": [HumanMessage(content=wrapped_text)],
    }


# 进入人类验收挂起点。
# 当前实现复用了 clarification_question 这个展示通道，把“验收提示语”发给外层 UI。
# waiting_for_evaluation=True 会让主图下一次优先进入 Process_Human_Feedback 节点。
def ask_human_feedback_node(state: GlobalState) -> dict:
    return {
        "waiting_for_evaluation": True,
        "clarification_question": (
            "\n" + "=" * 70 + "\n"
            "[人类验收环节] 机器人报告任务已完成。您对结果满意吗？\n"
            "  - 满意：直接回车 或 输入 'ok'\n"
            "  - 不满意：直接输入您的反馈"
            "\n" + "=" * 70
        ),
    }


# 处理验收阶段的人类反馈。
# 分两条路径：
# 1. 空输入或肯定词：视为验收通过，整体状态进入 fully_completed；
# 2. 其他内容：视为人类否决结果，转成一次“失败”，交给反思链路继续修复。
# 这里把 failure_layer 标成 understanding，不是说代码报错发生在理解层，
# 而是把“用户不满意”解释为“系统对需求理解仍有偏差”，从而优先走需求修正路线。
def process_human_feedback_node(state: GlobalState) -> dict:
    feedback = state.get("human_feedback", "").strip()

    # 空串和若干常见肯定表达都视为“验收通过”。
    if not feedback or feedback.lower() in ["ok", "好的", "满意", "yes", "y", "行"]:
        return {
            "waiting_for_evaluation": False,
            "execution_status": "fully_completed",
            "error_feedback": "",
            "failed_action": "",
            "human_feedback": "",
        }

    msgs = list(state.get("messages", []))
    commands = []
    for message in msgs:
        # 只提取人类来源的消息，拼出本轮指令史，供后续反思层回看上下文。
        if getattr(message, "type", "") == "human" or isinstance(message, HumanMessage):
            text = message.content
            # 中断消息在 handle_interrupt_node 中被包装过，这里剥掉系统前缀，只保留真实新指令。
            if "新指令：" in text:
                text = text.split("新指令：")[-1].strip()
            commands.append(text)

    history_str = "\n".join([f"指令 {i + 1}: {cmd}" for i, cmd in enumerate(commands)])

    # 这条输出只用于本地观测，不参与状态流转。
    print(f"\n[系统内部] 识别到负面反馈：「{feedback}」。正在自主唤醒反思层...")

    return {
        "waiting_for_evaluation": False,
        "execution_status": "failed",
        "failed_action": "执行完毕但遭人类否决",
        "error_feedback": f"【用户差评】: {feedback}",
        "failure_layer": "understanding",
        "reflection_retry_count": 0,
        "original_instruction": f"【本轮会话的完整指令史】\n{history_str}",
        "messages": [HumanMessage(content=f"【验收未通过，人类追加要求】: {feedback}")],
    }


# 执行层重试节点。
# corrected_execution 是反思层给出的“替代动作”；如果它有效，就直接替换任务栈顶、
# 且仅替换当前待执行的第一步(todo_list[0])，保持其余上下文不变。
# 这里使用 deepcopy，是为了避免原 task_stack 里的嵌套结构被原地修改。
def retry_execution_node(state: GlobalState) -> dict:
    corrected = state.get("corrected_execution", {})
    stack = copy.deepcopy(state.get("task_stack", []))

    if isinstance(corrected, dict) and corrected.get("skill") and stack and stack[-1].get("todo_list"):
        stack[-1]["todo_list"][0] = {"execution": corrected}
        stack[-1].pop("behavior_tree", None)
        stack[-1]["behavior_tree_executed"] = True
        return {
            "task_stack": stack,
            "execution_status": "running",
            "failed_action": "",
            "error_feedback": "",
        }

    return {
        "task_stack": stack,
        "execution_status": "failed",
        "failure_layer": "planning",
        "failed_action": state.get("failed_action", ""),
        "error_feedback": _invalid_corrected_execution_feedback(state),
        "corrected_plan_hint": _invalid_corrected_execution_plan_hint(state),
        "next_routing": "retry_planning",
        "failure_reason": "invalid_corrected_execution",
    }


def _invalid_corrected_execution_feedback(state: GlobalState) -> str:
    original = state.get("error_feedback", "")
    suffix = "执行反思请求 retry_execution 但未提供有效 corrected_execution，已转入规划修复。"
    return f"{original}\n{suffix}" if original else suffix


def _invalid_corrected_execution_plan_hint(state: GlobalState) -> str:
    failed_step = _failed_step_from_task_stack(state.get("task_stack", []))
    if failed_step is not None and _behavior_tree_context_present(state):
        return (
            "BehaviorTree recovery requested repair_plan; "
            f"execution reflection omitted valid corrected_execution; replan from failed step {failed_step}."
        )
    return "执行反思未提供可执行 corrected_execution，请重新规划当前失败动作。"


def _behavior_tree_context_present(state: GlobalState) -> bool:
    execution = state.get("behavior_tree_execution", {})
    if isinstance(execution, dict) and execution:
        return True
    trace = state.get("cognitive_planning_trace", {})
    if not isinstance(trace, dict):
        return False
    if isinstance(trace.get("behavior_tree_execution"), dict) and trace.get("behavior_tree_execution"):
        return True
    attempts = trace.get("behavior_tree_execution_attempts", [])
    return bool(isinstance(attempts, list) and any(isinstance(attempt, dict) for attempt in attempts))


def _failed_step_from_task_stack(task_stack: list) -> int | None:
    if not isinstance(task_stack, list) or not task_stack:
        return None
    current = task_stack[-1]
    if not isinstance(current, dict):
        return None
    todo_list = current.get("todo_list", [])
    if not isinstance(todo_list, list) or not todo_list:
        return None
    first = todo_list[0]
    if not isinstance(first, dict):
        return None
    try:
        step = int(first.get("step"))
    except (TypeError, ValueError):
        step = None
    if isinstance(step, int) and step > 0:
        return step
    return None


def _failed_step_from_bt_events(events: object) -> int | None:
    if not isinstance(events, list):
        return None
    for event in events:
        if not isinstance(event, dict):
            continue
        node_id = event.get("node_id")
        if not isinstance(node_id, str):
            continue
        match = re.match(r"step_(\d+)_", node_id)
        if match:
            try:
                step = int(match.group(1))
            except (TypeError, ValueError):
                return None
            return step if step > 0 else None
    return None


# 规划层重试节点。
# 它负责把反思层给出的“补救信息”重新灌回 structured_task，并重置规划相关现场：
# 1. 把 new_constraints 合并进原约束；
# 2. 用 corrected_plan_hint / feasibility_fix / correction_strategy 生成下一轮 planning feedback；
# 3. 清空上一轮 todo_list、审计结果、工具恢复计划；
# 4. 按当前 repair strategy 决定是否保留 Re-Trac 所需的已验证前缀。
# 另外会把 task_stack 栈顶弹掉，避免旧计划对应的执行现场继续悬挂在栈里。
def retry_planning_node(state: GlobalState) -> dict:
    new_constraints = state.get("new_constraints", [])
    structured_task = dict(state.get("structured_task", {}))
    existing = list(structured_task.get("constraints", []))
    # 这里做的是集合并集语义：去重后写回，避免同一约束被重复追加。
    structured_task["constraints"] = list(set(existing + new_constraints))

    if new_constraints:
        old_intent = structured_task.get("intent", "")
        # 在 intent 上补一小段文字，主要用于调试/可观测性，不改变结构化任务主体。
        if "补救" not in old_intent:
            structured_task["intent"] = f"{old_intent} (追加补救: {new_constraints[0]})"

    stack = list(state.get("task_stack", []))
    if stack:
        stack.pop()

    feedback = (
        state.get("corrected_plan_hint")
        or state.get("feasibility_fix")
        or state.get("correction_strategy")
        or ""
    )
    checkpoint_state = empty_checkpoint_state()
    # 只有当前策略是 Re-Trac，且状态里确实已有断点信息时，才沿用这些检查点。
    # 否则按“从头重新规划”处理，避免把过期断点错误带入下一轮。
    if active_repair_strategy() == REPAIR_STRATEGY_RETRAC and (
        state.get("validated_steps")
        or state.get("validated_todo_actions")
        or state.get("checkpoint_env")
        or state.get("checkpoint_robot")
        or state.get("todo_checkpoint_env")
        or state.get("todo_checkpoint_robot")
    ):
        checkpoint_state = {
            "validated_steps": copy.deepcopy(state.get("validated_steps", [])),
            "validated_todo_actions": copy.deepcopy(state.get("validated_todo_actions", [])),
            "checkpoint_env": copy.deepcopy(state.get("checkpoint_env", {})),
            "checkpoint_robot": copy.deepcopy(state.get("checkpoint_robot", {})),
            "todo_checkpoint_env": copy.deepcopy(state.get("todo_checkpoint_env", {})),
            "todo_checkpoint_robot": copy.deepcopy(state.get("todo_checkpoint_robot", {})),
            "re_trac_state": copy.deepcopy(state.get("re_trac_state", {})),
            "planning_continuation": copy.deepcopy(state.get("planning_continuation", {})),
        }
    bt_replan_state = _bt_recovery_direct_replan_state(state)

    return {
        "structured_task": structured_task,
        "todo_list": [],
        "is_feasible": False,
        "iteration_count": 0,
        "feedback": feedback,
        "failed_action": "",
        "error_feedback": "",
        "task_stack": stack,
        "execution_status": "running",
        "next_routing": "",
        "failure_reason": "",
        "corrected_execution": {},
        "correction_strategy": "",
        "evaluator_findings": [],
        "repair_handoff": {},
        "planning_continuation": {},
        "evaluation_repair_request": {},
        "repair_todo_list": [],
        "evaluation_recheck": False,
        "evaluation_revision_context": {},
        "repair_history": [],
        **checkpoint_state,
        **bt_replan_state,
    }


def _bt_recovery_direct_replan_state(state: GlobalState) -> dict:
    if state.get("failure_reason") != "behavior_tree_replan_requested":
        return {}
    try:
        used = int(state.get("bt_recovery_direct_replan_count") or state.get("direct_replan_count") or 0) + 1
    except (TypeError, ValueError):
        used = 1
    return {
        "bt_recovery_direct_replan_count": used,
        "cognitive_planning_trace": _record_bt_recovery_direct_replan_budget(state, used),
    }


def _record_bt_recovery_direct_replan_budget(state: GlobalState, used: int) -> dict:
    trace = state.get("cognitive_planning_trace", {})
    if not isinstance(trace, dict):
        trace = {}
    events = trace.get("bt_recovery_retry_budget", [])
    if not isinstance(events, list):
        events = []
    events.append(
        {
            "budget": _bt_direct_replan_budget(state),
            "used": used,
            "exhausted": used >= _bt_direct_replan_budget(state),
            "route": "Retry_Planning",
            "stage": "retry_planning",
        }
    )
    return {**trace, "bt_recovery_retry_budget": events}


def _bt_direct_replan_budget(state: GlobalState) -> int:
    flags = state.get("feature_flags", {})
    raw_budget = flags.get("cognitive_bt_direct_replan_budget", 1) if isinstance(flags, dict) else 1
    try:
        budget = int(raw_budget)
    except (TypeError, ValueError):
        budget = 1
    return max(budget, 0)


# 理解层重试节点。
# 用法是“保留消息流中的修正提示，但清空已经失效的任务解析结果”，让理解层重新开始：
# 1. 把 understanding_fix / clarification_question 作为新增 AIMessage 追加到 messages；
# 2. 清空 structured_task、todo_list、task_stack、environment 等派生状态；
# 3. checkpoint 也一并清空，因为旧检查点对应的是旧理解下的任务世界。
def retry_understanding_node(state: GlobalState) -> dict:
    clarification = state.get("clarification_question", "")
    understanding_fix = state.get("understanding_fix", "")
    new_messages = []

    if understanding_fix:
        new_messages.append(AIMessage(content=f"[系统修正提示] {understanding_fix}"))
    if clarification:
        new_messages.append(AIMessage(content=clarification))

    return {
        # messages 使用 operator.add reducer，只追加新增修正提示。
        "messages": new_messages,
        "structured_task": {},
        "is_complete": False,
        "todo_list": [],
        "task_stack": [],
        "is_feasible": False,
        "iteration_count": 0,
        "execution_status": "running",
        "failed_action": "",
        "error_feedback": "",
        "environment": {},
        "evaluator_findings": [],
        **empty_checkpoint_state(),
    }
