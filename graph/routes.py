try:
    from langgraph.graph import END
except Exception:  # pragma: no cover - fallback for lean test environments
    END = "__end__"  # type: ignore[assignment]

from graph.state import GlobalState


# 本文件只负责“主图级别的路由决策”：
# 每个 router 都读取 GlobalState 中的少量关键字段，返回下一个节点名或 END。
# 它们不修改状态，也不做业务执行；职责仅限于决定主图下一步跳到哪里。

# 读取是否启用反思链路的辅助函数。
# 约定如下：
# 1. feature_flags["reflection"] 显式存在时，以该值为准；
# 2. 未显式配置时，默认关闭反思，让主流程先聚焦规划/执行闭环本身。
def reflection_enabled(state: GlobalState) -> bool:
    flags = state.get("feature_flags", {})
    if isinstance(flags, dict) and "reflection" in flags:
        return bool(flags["reflection"])
    return False


def _feature_enabled(state: GlobalState, name: str, default: bool = False) -> bool:
    flags = state.get("feature_flags", {})
    if isinstance(flags, dict) and name in flags:
        return bool(flags[name])
    return default


def _bt_direct_replan_budget(state: GlobalState) -> int:
    flags = state.get("feature_flags", {})
    raw_budget = flags.get("cognitive_bt_direct_replan_budget", 1) if isinstance(flags, dict) else 1
    try:
        budget = int(raw_budget)
    except (TypeError, ValueError):
        budget = 1
    return max(budget, 0)


def _bt_direct_replan_count(state: GlobalState) -> int:
    try:
        return int(state.get("bt_recovery_direct_replan_count") or state.get("direct_replan_count") or 0)
    except (TypeError, ValueError):
        return 0


def _bt_recovery_direct_replan_requested(state: GlobalState) -> bool:
    return bool(
        state.get("execution_status") == "failed"
        and state.get("next_routing") == "retry_planning"
        and state.get("failure_reason") == "behavior_tree_replan_requested"
        and _feature_enabled(state, "cognitive_bt_recovery_direct_replan")
        and _bt_direct_replan_count(state) < _bt_direct_replan_budget(state)
    )


def _execution_reflection_planning_repair_requested(state: GlobalState) -> bool:
    return bool(
        state.get("execution_status") == "failed"
        and state.get("next_routing") == "retry_planning"
        and state.get("failure_reason") == "invalid_corrected_execution"
    )


def _counterfactual_completion_deferred(state: GlobalState) -> bool:
    completion = state.get("counterfactual_task_completion")
    return bool(
        isinstance(completion, dict)
        and completion.get("status") == "not_completed"
        and completion.get("handled") is False
    )


# 主图入口路由。
# 正常情况下，任务都从 Understanding_Module 开始；
# 有两种例外：
# 1. 系统当前正挂在“等待人类验收反馈”的状态上，这时优先消费验收反馈；
# 2. 系统保留着 task_stack 且外部 CommandBus 送来了 interrupt_signal，
#    这时要回到任务管理层，让中断控制器决定恢复、插单、暂停或取消。
def global_entry_router(state: GlobalState) -> str:
    if state.get("waiting_for_evaluation"):
        return "Process_Human_Feedback"
    if state.get("task_stack") and state.get("interrupt_signal"):
        return "Task_Management_Module"
    return "Understanding_Module"


# 理解层出口路由。
# is_complete=False 表示当前还不能安全进入规划：
# 常见情况是需要向用户追问、或者理解层尚未产出可执行的 structured_task。
# 这时主图直接结束本轮，由外层系统把澄清问题展示给用户；等用户补充输入后再重新入图。
# 只有当理解层确认信息完整时，才进入 Planning_Module。
def global_understanding_router(state: GlobalState) -> str:
    if state.get("is_cancel_all"):
        return END
    if not state.get("is_complete"):
        return END
    return "Planning_Module"


# 规划层出口路由。
# 分支优先级是有意设计过的：
# 1. 先看 execution_status=="failed"。这通常意味着规划-审计循环在子图内部已经宣告失败，
#    例如达到重试上限或出现不可恢复问题，此时应优先交给反思层，而不是继续执行。
# 2. 再看是否存在“带文本的新中断 + 非空 task_stack”。
#    这代表当前并不是冷启动执行，而是在已有执行栈上插入一份新的 todo_list，
#    所以要先经过 Inject_And_Execute，把规划结果封装进 interrupt_signal。
# 3. 其余情况都走常规执行入口 Task_Management_Module。
def global_planning_router(state: GlobalState) -> str:
    # The interactive console can run in plan-only mode. Keep that decision in
    # the input payload because planning config normalizes feature_flags.
    task_input_payload = state.get("task_input_payload", {})
    if isinstance(task_input_payload, dict) and task_input_payload.get("plan_only"):
        return END
    if _feature_enabled(state, "plan_only"):
        return END
    if state.get("execution_status") == "fully_completed":
        return END
    if _counterfactual_completion_deferred(state):
        return END
    # 规划层达到重试上限时会标记 failed，并交给反思层处理。
    if state.get("execution_status") == "failed":
        return "Reflection_Module" if reflection_enabled(state) else END

    interrupt_signal = state.get("interrupt_signal")
    # 这里要求 task_stack 非空，是为了区分“已有任务执行中途插单”和“首次执行主任务”。
    # 前者需要注入式派发，后者直接进入 Task_Management_Module 即可。
    if interrupt_signal and interrupt_signal.get("text") and state.get("task_stack"):
        return "Inject_And_Execute"
    return "Task_Management_Module"


# 任务管理层出口路由。
# 这里负责把执行阶段的几种终态映射到主图后续动作：
# 1. failed -> 进入反思层（如果启用），否则直接结束；
# 2. interrupted 且中断里确实带了新文本 -> 走 Handle_Interrupt，清空旧理解现场后重启；
# 3. success -> 不直接 END，而是先进入 Ask_Human_Feedback，让人类做最终验收；
# 4. 其他状态默认结束当前轮次。
# 注意“失败优先于中断、成功”，因为一旦 execution_status 已是 failed，就应该先处理失败闭环。
def global_task_management_router(state: GlobalState) -> str:
    status = state.get("execution_status")
    if status == "failed":
        if _bt_recovery_direct_replan_requested(state):
            return "Retry_Planning"
        if _execution_reflection_planning_repair_requested(state):
            return "Retry_Planning"
        return "Reflection_Module" if reflection_enabled(state) else END
    if status == "interrupted":
        if state.get("interrupt_signal", {}).get("text"):
            return "Handle_Interrupt"
    if status == "success":
        return "Ask_Human_Feedback"
    return END


# 人类验收反馈处理后的路由。
# Process_Human_Feedback 节点本身已经把“满意/不满意”翻译成 execution_status：
# 1. 满意 -> fully_completed，此处直接 END；
# 2. 不满意 -> failed，此处再决定是否进入反思层。
# 因此这个 router 只需要读 execution_status，不必重复解析 human_feedback 文本。
def post_feedback_router(state: GlobalState) -> str:
    if state.get("execution_status") == "failed":
        return "Reflection_Module" if reflection_enabled(state) else END
    return END


# 反思层出口路由。
# Reflection_Module 不直接决定具体跳到哪个重试节点，而是把结论写进 next_routing。
# 这里再把抽象的策略名映射成主图里的具体节点名：
# - retry_execution -> Retry_Execution
# - retry_planning -> Retry_Planning
# - retry_understanding -> Retry_Understanding
# 未识别的 next_routing 一律回退到 END，避免错误字符串把主图导向未知节点。
def global_reflection_router(state: GlobalState) -> str:
    next_routing = state.get("next_routing", "end")
    routing_map = {
        "retry_execution": "Retry_Execution",
        "retry_planning": "Retry_Planning",
        "retry_understanding": "Retry_Understanding",
    }
    return routing_map.get(next_routing, END)
