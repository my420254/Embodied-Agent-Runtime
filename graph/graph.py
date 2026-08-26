# MemorySaver 是 LangGraph 自带的内存型 checkpointer。
# 这里把它挂到主图 compile() 上，作用不是“业务记忆”，而是让整张图在多次节点跳转、
# 中断恢复、验收反馈再入图等场景下，都能保留同一份状态快照。
# 换句话说，主图里 waiting_for_evaluation、task_stack、messages 这类跨节点状态，
# 依赖这个 checkpointer 才能在一次运行结束后继续被后续运行读到。
from langgraph.checkpoint.memory import MemorySaver

# StateGraph 用来声明“节点 + 边 + 条件路由”的状态机；
# START 和 END 是主图的隐式起点/终点标记。
# 本文件就是围绕这三个对象，把理解、规划、执行、反思四个子图装配成一张总控图。
from langgraph.graph import END, START, StateGraph

# GlobalState 是主图统一共享的状态结构契约。
# 主图上的节点和子图不会各自维护独立上下文，而是都从这份全局状态里读写自己关心的字段。
# 因此 StateGraph(GlobalState) 的含义是：主图中每一步迁移，本质上都是在更新 GlobalState。
from graph.state import GlobalState

# 这些是“跨模块辅助节点”，不是四大主流程子图的一部分。
# 它们主要负责在模块之间做状态改写和桥接：
# - ask_human_feedback_node: 在任务执行成功后挂起，向外层 UI 发出验收提示。
# - handle_interrupt_node: 用户中断当前任务并下发新指令时，清空旧理解现场并重启。
# - inject_and_execute_node: 把规划结果封装进 interrupt_signal，交给执行层以“插单”方式消费。
# - process_human_feedback_node: 把人类验收输入翻译成 fully_completed 或 failed。
# - retry_execution_node: 用反思层产出的 corrected_execution 替换当前待执行动作。
# - retry_planning_node: 将补救约束和修正提示灌回规划链路，重新生成 todo_list。
# - retry_understanding_node: 清空失效理解结果，并把修正提示追加回消息流，重新理解任务。
from graph.nodes import (
    ask_human_feedback_node, 
    handle_interrupt_node,
    inject_and_execute_node,
    process_human_feedback_node,
    retry_execution_node,
    retry_planning_node,
    retry_understanding_node,
)

# 这些是“主图级路由器”。
# 它们只读取 GlobalState 决定下一跳，不执行业务逻辑：
# - global_entry_router: 决定从理解入口开始，还是先处理挂起的人类验收反馈。
# - global_task_management_router: 根据 execution_status 决定执行完成后去验收、反思或处理中断。
# - global_planning_router: 决定规划结果是直接执行、注入执行，还是先进入反思。
# - global_reflection_router: 根据 next_routing 把反思结论映射到具体重试节点。
# - global_understanding_router: 判断理解结果是否完整，是否允许进入规划。
# - post_feedback_router: 在处理完人类反馈后，决定结束还是进入反思修复。
from graph.routes import (
    global_entry_router,
    global_task_management_router,
    global_planning_router,
    global_reflection_router,
    global_understanding_router,
    post_feedback_router,
)

# 四个 build_*_graph() 都返回“已编译好的子图”，主图把它们当成大节点挂上来：
# - build_planning_graph: 任务分解 + 可行性审计的循环子图。
# - build_reflection_graph: 失败分诊 + 分层反思 + 输出修复策略的子图。
# - build_task_management_graph: 任务栈管理、动作分类、动作模拟/执行的子图。
# - build_understanding_graph: 指令分析与澄清提问的子图。
from graph.planning.node import build_planning_graph
from graph.reflection.node import build_reflection_graph
from graph.task_management.node import build_task_management_graph
from graph.understanding.node import build_understanding_graph


# 组装整张主控图。
# 这张图的职责不是做具体任务理解或具体动作执行，而是：
# 1. 规定四个核心阶段的进入顺序；
# 2. 处理中断、验收、反思重试等“跨阶段控制流”；
# 3. 为整张图挂上统一的状态 checkpointer。
def build_main_graph():
    # 用 GlobalState 声明整张主图的共享状态类型。
    workflow = StateGraph(GlobalState)

    # 四个主流程子图。
    # 它们分别对应：理解 -> 规划 -> 执行管理 -> 失败反思。
    # 从主图视角看，这四个子图都像“大节点”，但内部各自还有更细的节点和路由。
    workflow.add_node("Understanding_Module", build_understanding_graph())
    workflow.add_node("Planning_Module", build_planning_graph())
    workflow.add_node("Task_Management_Module", build_task_management_graph())
    workflow.add_node("Reflection_Module", build_reflection_graph())

    # 跨模块辅助节点。
    # 这些节点负责处理子图之间不好直接内聚的控制逻辑，例如：
    # - 中断后重置现场
    # - 规划结果注入执行层
    # - 人类验收挂起与回流
    # - 反思后的三种重试入口
    workflow.add_node("Handle_Interrupt", handle_interrupt_node)
    workflow.add_node("Inject_And_Execute", inject_and_execute_node)
    workflow.add_node("Ask_Human_Feedback", ask_human_feedback_node)
    workflow.add_node("Process_Human_Feedback", process_human_feedback_node)
    workflow.add_node("Retry_Execution", retry_execution_node)
    workflow.add_node("Retry_Planning", retry_planning_node)
    workflow.add_node("Retry_Understanding", retry_understanding_node)

    # 主图入口：
    # - 正常情况从 Understanding_Module 开始；
    # - 如果当前状态显示“正等待人类验收反馈”，则直接进入 Process_Human_Feedback。
    workflow.add_conditional_edges(START, global_entry_router)

    # 理解层出口：
    # - 理解完成 -> 进入规划层；
    # - 理解未完成 -> 直接结束本轮，通常由外层把 clarification_question 展示给用户。
    # 第一个参数是理解层这个“大节点”，第二个参数是路由器，第三个参数是路由规则字典。第三个参数是根据 global_understanding_router 的返回值来决定下一跳的： 
    # 返回 END 就结束本轮，返回 "Planning_Module" 就进入规划层。
    workflow.add_conditional_edges(
        "Understanding_Module",
        global_understanding_router,
        {
            END: END,
            "Planning_Module": "Planning_Module",
        },
    )

    # 规划层出口：
    # - 规划/审计失败 -> 反思层；
    # - 当前是“已有任务上的插入式规划” -> 先走 Inject_And_Execute；
    # - 其他正常情况 -> 进入任务管理/执行层。
    workflow.add_conditional_edges(
        "Planning_Module",
        global_planning_router,
        {
            END: END,
            "Reflection_Module": "Reflection_Module",
            "Inject_And_Execute": "Inject_And_Execute",
            "Task_Management_Module": "Task_Management_Module",
        },
    )
    # 注入节点本身不执行任务，只负责把新 todo_list 写入 interrupt_signal，
    # 处理完后统一流向 Task_Management_Module。
    workflow.add_edge("Inject_And_Execute", "Task_Management_Module")

    # 执行管理层出口：
    # - BT recovery 请求直接重规划 -> Retry_Planning（实验开关控制）；
    # - 其他失败 -> 反思；
    # - 被中断且收到新指令 -> 处理中断；
    # - 成功 -> 请求人类验收；
    # - 其余状态 -> 结束本轮。
    workflow.add_conditional_edges(
        "Task_Management_Module",
        global_task_management_router,
        {
            END: END,
            "Reflection_Module": "Reflection_Module",
            "Retry_Planning": "Retry_Planning",
            "Handle_Interrupt": "Handle_Interrupt",
            "Ask_Human_Feedback": "Ask_Human_Feedback",
        },
    )

    # Ask_Human_Feedback 节点会把 waiting_for_evaluation 置为 True，并输出验收提示。
    # 这里立刻 END 是刻意设计：
    # 当前轮执行到此为止，等外层收集到人类输入后，再从 START 重进主图，
    # 由 global_entry_router 把流程切到 Process_Human_Feedback。
    workflow.add_edge("Ask_Human_Feedback", END)

    # Process_Human_Feedback 负责把“满意/不满意”翻译成 execution_status。
    # 这里再根据 post_feedback_router 决定：
    # - 人类否决 -> 进入反思层
    # - 人类认可 -> 结束整轮任务
    workflow.add_conditional_edges(
        "Process_Human_Feedback",
        post_feedback_router,
        {
            "Reflection_Module": "Reflection_Module",
            END: END,
        },
    )

    # 处理中断节点会清空旧理解现场，并把新指令写回 raw_instruction/messages，
    # 所以它后面必须重新进入 Understanding_Module，而不是直接回执行层。
    workflow.add_edge("Handle_Interrupt", "Understanding_Module")

    # 反思层出口：
    # 反思子图内部会产出 next_routing，主图在这里把它映射到三种重试路径：
    # - Retry_Execution: 只替换当前动作，继续执行
    # - Retry_Planning: 保留任务语义但重新规划
    # - Retry_Understanding: 连任务理解都作废，回到最前面重做
    workflow.add_conditional_edges(
        "Reflection_Module",
        global_reflection_router,
        {
            END: END,
            "Retry_Execution": "Retry_Execution",
            "Retry_Planning": "Retry_Planning",
            "Retry_Understanding": "Retry_Understanding",
        },
    )

    # 三条重试路径各自回到对应的主流程阶段。
    # 这样反思层只负责“产出修复决策”，真正执行修复仍交给原始业务链路。
    workflow.add_edge("Retry_Execution", "Task_Management_Module")
    workflow.add_edge("Retry_Planning", "Planning_Module")
    workflow.add_edge("Retry_Understanding", "Understanding_Module")

    # 给主图挂上统一的内存型 checkpointer。
    # compile() 之后返回的是可直接运行的 LangGraph 图对象，而不是 StateGraph 定义本身。
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)
