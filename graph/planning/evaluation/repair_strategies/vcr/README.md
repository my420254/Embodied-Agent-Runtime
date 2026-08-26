# VCR

VCR 位于 planning evaluation 的隔离修复策略目录中，内部按自身算法划分：

- `diagnosis.py`：根据完整 `todo_list`、统一模拟失败和反事实后缀结果确定替换窗口，并组装 LLM 输入。
- `assembly.py`：把 LLM 返回的替换窗口与固定前后缀拼成完整 `todo_list`。
- `core.py`：提供反事实后缀模拟及 VCR 算法函数；生产评估入口只复用诊断所需的反事实模拟。
- `causal_checkpoint.py`：只负责 VCR 的因果回滚点与窗口边界选择。

VCR 不在策略内部调用 LLM、重试或执行完整计划。评估层输出 diagnosis，规划子图调用 LLM，评估层再通过 assembly 拼装完整候选；规划子图随后把候选重新送入合法性检查、基础沙盒和后续审计。VCR 与 SDA、ReTrac 不互相导入。

每次 diagnosis 只发布最早的一个修复窗口。反事实分析可能发现多个失败窗口，
但较早窗口的动作会改变较晚窗口的入口状态，因此不能在同一次 LLM 输入中并行
修复。窗口动作经独立段验证后，被插回完整计划并重新回放；若后续仍失败，再以
已回放的真实状态生成下一次 diagnosis。这个顺序保证后续窗口不会依赖旧计划的
反事实快照。

反事实模拟执行完整个动作序列后，评估层先做二分任务完成度判定。
understanding 提供了可判定的显式目标时，使用确定性 `goal_test`；否则由
评估层将模拟前后状态差异和任务相关最终状态交给 LLM，只返回
`completed` 或 `not_completed`，不生成修复建议。`completed` 继续生成 VCR
修复窗口；`not_completed` 返回
`counterfactual_task_completion={"status": "not_completed", "handled": false}`，
并停在预留接口。该分支当前不自动重规划，也不执行原计划。

LLM 的结构化 payload 只有 `task_goal` 与一个 `repair_window`。`repair_window` 包含：

- `id`：唯一窗口标识。
- `position`：含起止步骤编号的原计划替换区间。
- `current_state`：窗口前的机器人状态，以及 understanding 已提取的相关实体状态。
- `target_state`：窗口后的相关目标状态，来自反事实轨迹的出口快照。LLM 的任务是用
  `skill_contracts` 从 `current_state` 规划到 `target_state`。
- `failure_obligations`：压缩后的根因动作、错误动作、错误动作执行前必须满足的前置
  条件，以及根因动作造成的相关状态变化。它只描述当前窗口内部的修复义务，不展开旧的
  多窗口因果链。
- `repair_strategies`：两种局部修法：保持根因动作并在错误动作前补足前置条件，或替换
  根因动作并重新达到错误动作前置条件。
- `skill_contracts`：理解层冻结的 `skill_closure` 中各技能的紧凑 `requires/effects`
  状态转移契约；VCR 只校验并消费该闭包，不自行推断、扩大或重算技能集合，也不再
  附加包含示例与重复说明的完整技能 Markdown。

提示词不包含额外候选实体、下一固定动作或动作数量上限；只明确替换段动作数量可变、每步
必须满足 `skill_contracts` 的前置条件，并要求按 `repair_strategies` 之一处理
`failure_obligations`。系统内部仍从反事实轨迹提取出口契约用于窗口段验证，但不把
delta 形式作为 LLM 的主目标。默认 LLM 路径的实体集合严格复用 understanding 的
`relevant_item_names`。理解层先把用户明确目标写入
`structured_task.goal_state`，并依据技能动作模型补齐目标写入技能的前置技能，形成
	`skill_closure`；实体事实来自当前请求的 `environment`。默认 LLM prompt 路径不做
	同房间扫描、承载物枚举、实体替换或技能扩张。
若出口契约引用了理解层未召回的实体，VCR 会终止诊断，而不是给 LLM 隐藏验收条件。
完整入口快照仍只保留在系统内部用于候选段验证。

反事实动作和正式评估共用 evaluation 提供的动作/效果语义接口，因此载体到任务目标的
效果对象规范化也不属于 VCR。VCR 只识别失败、回溯因果窗口并校验目标，不生成场景型
修复建议。

LLM 只返回 `{"repair_window_id": "window_1", "actions": [...]}`；系统只用
`actions` 替换该窗口。完整计划、错误对象和修复建议不进入首轮提示词。
`merge_gap_actions=0` 时每轮只发布最早失败对应的独立因果窗口，包括与其重叠的
其他窗口也不合并；补丁经真实 replay 后，后续错误基于新轨迹重新诊断。正数值仅用于
显式恢复重叠及邻近窗口合并。
候选段验证失败时，重试不再重复发送完整失败快照。同一 `failed_action` 只保留
一项 `validation_errors`，其中 `failed_action.action_index` 标出失败的段内位置，
每项 `causal_errors` 的 `root_action` 标出模拟器回溯到的状态来源，
`state_mismatches` 记录实际值与期望值，`rejected_sequences` 记录此前已失败的窗口内
动作序列。重试指令要求按同两种策略重写窗口，并避免重复任一已拒绝序列或其错误动作前缀。
根因动作只从本次窗口模拟实际观察到的状态写入
反查，不按技能名猜测；无法对应到窗口内写入时保留空根因。通用执行错误保留错误码和
错误类型，不伪造空状态谓词。字段只陈述验证事实，不生成动作顺序或修复建议。
复测日志同样使用 `prompt_repair_window` 与 `repair_window_summary`，不会再输出
`prompt_repair_windows`、`causal_groups` 或修复建议字段。

	策略由 evaluation 装配配置选择，planning state 不再声明独立 checkpoint repair 开关：

```json
{
  "planning": {
    "evaluation": {"repair_strategy": "vcr"}
  }
}
```

策略选择只读 `planning.evaluation.repair_strategy`；runtime state 和
`feature_flags` 不能覆盖 VCR/Re-Trac/SDA 的选择。
