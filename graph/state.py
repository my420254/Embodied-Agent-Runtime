# operator.add 被用作 LangGraph reducer，表示 messages 在状态合并时采用列表拼接，而不是后值覆盖前值。
import operator

# Annotated 用来给 messages 标记 reducer；TypedDict 用来声明各阶段状态字段的结构契约。
from typing import Annotated, Any, Dict, List, Optional, TypedDict


# 这个模块定义了主图和各子图共享的状态结构。
# 它不负责业务逻辑，只负责声明“每一层会读写哪些字段”。
class UnderstandingState(TypedDict):
    """指令理解模块状态。"""

    messages: Annotated[List[Any], operator.add] # 对话消息历史；理解层会从这里读取最近的人类输入，必要时也会向这里追加澄清问题。
    raw_instruction: str # 当前待理解的原始指令文本；通常直接来自用户输入或中断后的新指令。
    original_instruction: str # benchmark/framework 入口保留的原始任务文本；理解层 prompt 和 trace 用它防止中途改写。
    feature_flags: Dict[str, bool] # benchmark/framework 运行开关；理解层需要读取 allow_clarification 和异常是否应抛出。
    task_context: Dict[str, Any] # 外部任务源提供的紧凑上下文，例如可用实体名和原始任务定义；不承载完整场景图。
    task_input_payload: Dict[str, Any] # benchmark 原始输入中允许暴露给 understanding 的字段子集，只用于 prompt/trace。
    environment: Dict[str, Any] # 请求级环境；理解层只用它收集可见实体名，不做实体替换或环境裁剪。
    scene: Dict[str, Any] # 可选嵌套场景输入；入口未扁平化时可直接提供给理解层收集实体名。
    entity_catalog: List[str] # 外部入口给出的实体目录；优先作为理解 prompt 的合法实体表。
    is_complete: bool # 理解结果是否足够完整，可以继续进入规划层；不是“整个任务是否完成”。
    is_cancel_all: bool # 当前指令是否表达了“取消/终止当前任务”的意图。
    needs_clarification: bool # 理解层是否认为需要向用户反问；与 is_complete 保持互补但单独暴露，便于功能解耦。
    clarification_question: str # 当指令信息不足或检测到幻觉实体时，理解层生成的追问内容。
    relevant_item_names: List[str] # 从当前场景实体列表中筛出的、与任务文本相关的物品名称。
    skill_closure: List[str] # 理解层基于可用 skill 摘要一次性筛出的任务相关 skill 名称；代码只过滤非法名称，不自动补依赖。
    structured_task: Dict # 理解层产出的结构化任务对象，后续规划层会基于它做实体 grounding 和动作分解。
    entity_repair: Dict[str, Any] # 实体修复功能的审计元信息；记录是否启用、尝试次数和结果状态。
    goal_state_extract: Dict[str, Any] # 终态抽取功能的审计元信息；记录是否启用、来源和尝试次数。


# PlanningState 只描述规划与审计阶段真正需要读写的字段。
class PlanningState(TypedDict):
    """任务分解与规划模块状态。"""

    feature_flags: Dict[str, bool] # 实验或消融开关；用于控制 playbook、沙盒审计等能力，不承载 repair strategy。
    structured_task: Dict # 来自理解层的结构化任务，是规划层生成 todo_list 的核心输入。
    relevant_item_names: List[str] # 理解层输出的按相关性排序实体列表；规划 grounding 会优先按该顺序解析场景实体。
    skill_closure: List[str] # 理解层选择的 skill 名称列表；规划 prompt 只注入这些 skill 的契约，空列表表示回退到当前 settings 启用的全部 skill。
    environment: Dict[str, Any] # 请求级任务环境；benchmark 或运行入口准备好后，planning/evaluator 从头到尾只读这一份。
    env_state: Dict[str, Any] # 机器人局部控制状态，如当前位置、当前手持物；规划规范化和审计都要参考它。
    task_input_payload: Dict[str, Any] # 任务原始输入负载；benchmark 入口需在进入 graph 前转成这个标准字段。
    task_context: Dict[str, Any] # 任务目标上下文；显式最终态、约束或 evaluator 额外输入都放这里。
    environment_source: Dict[str, Any] # 环境来源说明，只用于审计/trace，不进入 LLM 决策。
    entity_catalog: List[str] # benchmark 解析出的实体目录；用于 prompt 和 environment grounding 的补充说明。
    understanding_stage_executed: bool # 该规划请求前是否执行过 understanding；trace/report 需要依赖这个标记。

    todo_list: List[Dict] # 规划层生成或修正后的动作序列；step 结构由当前 skill/prompt 的动作契约决定。
    todo_output_parser_path: str # 当前数据集 todo_list 输出解析 hook 路径。
    todo_step_adapter_path: str # todo_list step 到沙盒 handler 参数的审计 hook 路径。
    todo_list_validator_path: str # 可选的 todo_list 整序列审计 hook 路径。
    is_feasible: bool # 沙盒审计后的可行性结论；True 表示当前 todo_list 可以放行到执行层。
    feedback: str # 规划或审计给出的反馈文本；可能是修正建议、计划级审计意见，或“任务已满足”的终态说明。
    iteration_count: int # 当前规划-审计循环已进行了多少轮，用于限制重试次数。
    evaluator_findings: List[Dict] # 沙盒审计产生的结构化发现列表；供反思层、Re-Trac 和记忆沉淀使用。
    injected_playbook_rule_ids: List[str] # 本轮 prompt 检索并注入给规划器的经验规则 ID；用于后续 helpful/harmful 反馈回写。
    planner_status: str # 规划器显式返回的状态 planned/completed。
    todo_llm_output: str # 规划层按当前数据集 todo_list 契约输出的原始文本。
    todo_parse_error: str # todo_list 解析失败文本。

    execution_status: str # 规划阶段借用的统一流程状态；当迭代超限等严重错误发生时，会标记为 failed。
    failed_action: str # 规划或审计失败时记录的失败动作/失败阶段名称。
    error_feedback: str # 规划或审计失败时的错误原因文本。
    failure_layer: str # 当前失败属于哪一层；当前主路径里规划失败通常写 planning。

    validated_steps: List[Dict] # 已经被沙盒验证通过的动作前缀；用于失败后从断点继续规划，而不是从头生成整条序列。
    validated_todo_actions: List[Dict] # 已通过审计的原样 todo_list 前缀；用于失败后的续写。
    checkpoint_env: Dict[str, Any] # validated_steps 执行后的沙盒环境检查点；供续写修复时恢复上下文。
    checkpoint_robot: Dict[str, Any] # validated_steps 执行后的机器人状态检查点；与 checkpoint_env 配套使用。
    todo_checkpoint_env: Dict[str, Any] # validated_todo_actions 执行后的沙盒环境检查点。
    todo_checkpoint_robot: Dict[str, Any] # validated_todo_actions 执行后的机器人状态检查点。
    repair_memory: Dict[str, List[str]] # evaluation repair 的策略无关短期失败记忆。
    repair_handoff: Dict[str, Any] # evaluation repair 的 checkpoint 续写上下文。
    planning_continuation: Dict[str, Any] # evaluation 投影给下一轮规划的续写上下文。
    evaluation_repair_request: Dict[str, Any] # evaluation 生成、planning 模型消费的重规划请求。
    repair_todo_list: List[Dict] # planning 模型针对 evaluation request 生成的待拼装动作。
    evaluation_recheck: bool # 当前 todo_list 是否跳过模型调用直接重新进入 evaluation。
    evaluation_revision_context: Dict[str, Any] # 修复候选事务上下文，供 assembly/reevaluate 提交或回滚。
    repair_history: List[Dict[str, Any]] # evaluation repair 跨节点记录。
    re_trac_memory: Dict[str, List[str]] # 单轮任务内的短期失败记忆；记录“刚刚踩过的坑”，帮助后续规划避开同类错误。
    re_trac_state: Dict[str, Any] # Re-TRAC 压缩状态；记录已验证轨迹、当前模拟状态、失败模式和下一步续写 frontier。
    sda_state: Dict[str, Any] # SDA 状态依赖诊断结果；记录因果回滚点、冲突谓词和被丢弃的子轨迹。
    repair_strategy: str # 当前唯一启用的序列修复策略：none/retrac/sda/vcr；由 settings 控制。
    state_diff_audit: Dict[str, Any] # 状态差异审计结果；由框架公共 LLM state-diff audit 判断 sandbox 前后状态是否符合任务目标。
    counterfactual_task_completion: Dict[str, Any] # 反事实末态 completed/not_completed 判定。
    planning_feature_records: List[Dict[str, Any]] # 规划侧功能记录；按 sandbox / SDA / final-state 等功能记录配置、输入、输出摘要。
    planning_debug_events: List[Dict[str, Any]] # planning/evaluator 调试事件。


class ExecutionState(TypedDict):
    """任务管理模块状态。"""

    feature_flags: Dict[str, bool] # 执行层实验开关；例如 cognitive_bt_execute 控制是否用 BehaviorTree 执行已编译计划。
    todo_list: List[Dict] # 来自规划层的待执行动作序列；首次进入任务管理层时会被压入 task_stack。
    raw_instruction: str # 当前任务对应的原始用户指令；主要用于新任务入栈时保留描述。
    structured_task: Dict # 当前任务的结构化表达；用于给任务栈里的 instruction 提供语义名称。
    task_stack: List[Dict[str, Any]] # 任务栈；支持主任务、插入任务、中断恢复等执行控制。
    env_state: Dict[str, Any] # 执行层维护的机器人局部状态镜像，如位置、手持物、最近动作带来的局部变化。
    interrupt_signal: Optional[Dict[str, Any]] # 中断载荷；既可表示用户新指令，也可表示规划层注入的新 todo_list。
    current_action_category: str # 当前动作所属控制域，例如底盘控制、机械臂控制、IoT 硬件交互。
    allow_interrupt_input: bool # 执行动作之间是否允许读取交互式中断输入；主要给本地控制台调试使用。
    execution_status: str # 执行层当前状态，如 running / success / failed / interrupted / paused / cancelled。
    failed_action: str # 执行失败时记录的具体动作字符串。
    error_feedback: str # 执行失败时返回的错误详情。
    failure_layer: str # 当前失败属于 execution、planning、understanding 等哪一层；执行层出错时通常写 execution。
    failed_subtask_context: str # 预留给更细粒度失败现场描述的字段；当前项目里实际写入较少。
    cognitive_planning_trace: Dict[str, Any] # 规划层认知 trace；执行层可读取其中的 BehaviorTree artifact。
    behavior_tree_execution: Dict[str, Any] # BT executor 输出的运行事件和最终状态，用于 trace/debug。
    messages: Annotated[List[Any], operator.add] # 执行层追加的消息，例如中断指令、系统提示等。


class ReflectionState(TypedDict):
    """分层反思与经验提炼模块状态。"""

    feature_flags: Dict[str, bool] # 反思层同样会读取实验开关，例如是否允许写 playbook。
    original_instruction: str # 失败分析要回看的原始任务指令或完整指令史。
    failed_action: str # 触发反思的失败动作或失败节点。
    error_feedback: str # 失败时的错误文本，是反思 prompt 的核心输入之一。
    failure_layer: str # 失败属于 understanding / planning / feasibility / execution 哪一层，用于分诊。
    failed_subtask_context: str # 失败发生时的子任务上下文；当前主要作为反思层扩展字段保留。
    env_state: Dict[str, Any] # 失败发生时的机器人局部状态；反思执行错误时会参考它。
    messages: Annotated[List[Any], operator.add] # 对话上下文与系统消息；理解层反思会从中抽取最近消息片段。
    task_stack: List[Dict[str, Any]] # 失败发生时的任务栈快照；规划/执行反思会借此恢复失败现场。
    structured_task: Dict # 当前结构化任务；反思层需要基于它分析理解偏差或规划偏差。
    environment: Dict[str, Any] # 当前请求级任务环境；规划反思时用于解释为什么动作不成立。
    evaluator_findings: List[Dict] # 沙盒审计留下的结构化发现；可行性反思尤其依赖它。
    injected_playbook_rule_ids: List[str] # 本轮规划曾注入的经验规则 ID；用于后续记录 helpful/harmful 反馈。

    determined_reflection_layer: str # 分诊台最终确定进入哪一层反思节点，例如 layer2_planning。
    reflection_retry_count: int # 已进行过多少轮反思；达到上限后会停止自动修复。

    corrected_understanding: str # 反思层生成的“修正后理解结果”文本，主要用于理解层失败后的补救。
    understanding_fix: str # 给理解层的修正提示，会作为系统修正消息追加回消息流。
    new_constraints: List[str] # 规划反思生成的新硬约束；下一轮规划会把它们并入 structured_task.constraints。
    corrected_plan_hint: str # 针对规划层的局部修正方向，通常会进入下一轮 planning 的 feedback。
    feasibility_fix: str # 针对“被审计器反复拦截”的系统性修复方向。
    planning_lesson: str # 从规划/可行性失败中提炼出的经验法则文本。
    corrected_execution: Dict[str, Any] # 执行反思给出的替代动作；若可直接替换当前动作，就写在这里。
    alternative_tools: List[str] # 执行反思识别出的可替代工具列表。

    clarification_question: str # 理解层反思可能重新触发澄清时要回写的问题文本。
    correction_strategy: str # 反思层给出的总体修正策略摘要；retry_planning 等节点会优先从这里取反馈。
    misunderstanding_analysis: str # 对误解成因的分析文本；当前主要作为反思输出的保留字段。
    next_routing: str # 反思结束后要跳向哪条重试路径，例如 retry_planning / retry_execution。
    extracted_experience: str # 本轮失败提炼出的经验摘要，用于调试或后续沉淀。
    failure_level: str # 人类可读的失败层级标签，如 Layer2_任务分解层；主要用于输出和记录。


class GlobalState(TypedDict):
    """贯穿主图和各子图的全局状态。"""

    feature_flags: Dict[str, bool] # 全局实验开关；不同模块都会读取它来决定启用哪些能力。
    waiting_for_evaluation: bool # 当前是否停在“等待人类验收反馈”的挂起点；若为 True，主图入口会直接走 Process_Human_Feedback。
    human_feedback: str # 人类在验收阶段输入的反馈文本；可能表示认可，也可能表示差评和追加要求。
    messages: Annotated[List[Any], operator.add] # 全局消息流；贯穿理解、规划、执行、反思的对话与系统消息历史。

    raw_instruction: str # 当前活跃指令文本；中断后会被替换成新指令。
    is_complete: bool # 理解层是否已给出足够完整的任务表达；不是“任务执行完成”。
    is_cancel_all: bool # 当前任务是否被识别为取消/终止意图。
    needs_clarification: bool # 理解层是否需要向用户反问。
    clarification_question: str # 当前待向用户展示的澄清或验收问题。
    relevant_item_names: List[str] # 理解层从场景中筛出的任务相关实体名称列表。
    skill_closure: List[str] # 理解层选择的任务相关 skill 名称列表。
    structured_task: Dict # 当前任务的结构化表达，是各层共享的核心任务对象。
    entity_repair: Dict[str, Any] # 理解层实体修复审计元信息。
    goal_state_extract: Dict[str, Any] # 理解层终态抽取审计元信息。
    original_instruction: str # 用于反思和审计回看的原始任务文本或完整指令史。

    environment: Dict[str, Any] # 请求级任务环境；规划、审计、反思层都会使用同一份数据。
    task_input_payload: Dict[str, Any] # 任务原始输入负载；benchmark 入口需在进入 graph 前转成这个标准字段。
    task_context: Dict[str, Any] # 任务目标上下文，如最终状态、约束或 evaluator 额外输入。
    environment_source: Dict[str, Any] # 环境来源说明，只用于审计/trace。
    entity_catalog: List[str] # benchmark 解析出的实体目录。
    understanding_stage_executed: bool # 当前结果前是否实际执行过 understanding。

    todo_list: List[Dict] # 当前生效的动作序列；step 结构由当前 skill/prompt 的动作契约决定。
    todo_output_parser_path: str # 当前数据集 todo_list 输出解析 hook 路径。
    todo_step_adapter_path: str # todo_list step 到沙盒 handler 参数的审计 hook 路径。
    todo_list_validator_path: str # 可选的 todo_list 整序列审计 hook 路径。
    cognitive_planning_trace: Dict[str, Any] # 认知规划 trace；包括 KG/Scene/TaskGraph/Safety/Sandbox/BehaviorTree 信息。
    is_feasible: bool # 最近一次规划审计结论。
    feedback: str # 规划/审计给出的反馈文字，可能用于下一轮迭代继续修复。
    iteration_count: int # 规划-审计循环次数。
    evaluator_findings: List[Dict] # 审计器结构化发现列表。
    planner_status: str # 规划器显式返回的 planned/completed 状态。
    todo_llm_output: str # 规划层按当前数据集 todo_list 契约输出的原始文本。
    todo_parse_error: str # todo_list 解析失败文本。

    validated_steps: List[Dict] # 已通过审计的动作前缀，用于 checkpoint repair 和续写式重规划。
    validated_todo_actions: List[Dict] # 已通过审计的原样 todo_list 前缀。
    checkpoint_env: Dict[str, Any] # validated_steps 执行后的环境检查点。
    checkpoint_robot: Dict[str, Any] # validated_steps 执行后的机器人检查点。
    todo_checkpoint_env: Dict[str, Any] # validated_todo_actions 执行后的沙盒环境检查点。
    todo_checkpoint_robot: Dict[str, Any] # validated_todo_actions 执行后的机器人状态检查点。
    repair_memory: Dict[str, List[str]] # evaluation repair 的策略无关短期失败记忆。
    repair_handoff: Dict[str, Any] # evaluation repair 的 checkpoint 续写上下文。
    planning_continuation: Dict[str, Any] # evaluation 投影给下一轮规划的续写上下文。
    evaluation_repair_request: Dict[str, Any] # evaluation 生成、planning 子图消费的重规划请求。
    repair_todo_list: List[Dict] # planning 模型针对 evaluation request 生成的重规划输出。
    evaluation_recheck: bool # 当前 todo_list 是否直接重新进入 evaluation。
    evaluation_revision_context: Dict[str, Any] # 修复候选事务上下文。
    repair_history: List[Dict[str, Any]] # evaluation repair 跨节点记录。
    re_trac_memory: Dict[str, List[str]] # 单轮任务内的短期失败记忆。
    sda_state: Dict[str, Any] # SDA 状态依赖诊断结果；供规划重试和 trace/debug 使用。
    state_diff_audit: Dict[str, Any] # 状态差异审计结果。
    counterfactual_task_completion: Dict[str, Any] # 反事实末态 completed/not_completed 判定。
    planning_feature_records: List[Dict[str, Any]] # 规划侧功能记录。
    planning_debug_events: List[Dict[str, Any]] # planning/evaluator 调试事件。

    task_stack: List[Dict[str, Any]] # 执行层任务栈；支持中断、新任务压栈和恢复旧任务。
    env_state: Dict[str, Any] # 机器人局部状态镜像。
    interrupt_signal: Optional[Dict[str, Any]] # 中断载荷或规划注入载荷。
    current_action_category: str # 当前动作的控制域分类。
    allow_interrupt_input: bool # 是否允许在动作间隙读取交互式中断输入。
    execution_status: str # 当前整体执行状态，如 running / success / failed / interrupted / paused / cancelled / fully_completed。
    failed_action: str # 最近一次失败对应的动作或阶段名。
    error_feedback: str # 最近一次失败的错误文本。
    failure_layer: str # 最近一次失败属于哪一层，供反思路由使用。
    failed_subtask_context: str # 最近一次失败的子任务上下文描述；当前多为预留字段。
    behavior_tree_execution: Dict[str, Any] # BT executor 运行结果；当 cognitive_bt_execute 开启时由执行层写入。

    determined_reflection_layer: str # 分诊台决定进入的反思层节点名。
    reflection_retry_count: int # 当前任务已自动反思了多少轮。
    failure_level: str # 人类可读的失败层级标签。
    correction_strategy: str # 反思层给出的总体修正策略摘要。

    corrected_understanding: str # 反思层修正后的理解结果文本。
    understanding_fix: str # 反思层给理解层的修正提示。
    new_constraints: List[str] # 反思层补充给规划层的新硬约束。
    corrected_plan_hint: str # 反思层给规划层的局部修正提示。
    feasibility_fix: str # 反思层针对系统性可行性问题给出的修正方向。
    planning_lesson: str # 从规划/审计失败中提炼的经验法则文本。
    corrected_execution: Dict[str, Any] # 反思层给执行层的替代动作。
    alternative_tools: List[str] # 反思层识别出的备选工具列表。
    misunderstanding_analysis: str # 对误解成因的分析文本。
    next_routing: str # 反思结束后主图下一步该走的重试方向。
    extracted_experience: str # 本轮失败提炼出的经验摘要。
