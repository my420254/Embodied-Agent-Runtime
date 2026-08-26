# 架构说明

本文是 OurAgent 的架构总纲。它优先回答三个问题：

- 哪些模块拥有哪类决策权
- 数据和控制流如何穿过主框架
- 后续重构不能突破哪些边界

更细的认知技能、KG、TaskGraph 和 BehaviorTree 设计见
`docs/COGNITIVE_SKILL_ARCHITECTURE.md`；落地路线见
`docs/ARCHITECTURE_IMPROVEMENT_PLAN.md`。

## 架构目标

OurAgent 后续不应继续演化成“LLM 在各层自由做决定”的系统。目标架构应收敛为：

```text
User / Benchmark Case
  ↓
LangGraph Runtime Orchestrator
  ↓
Brain Planning Facade
  ├── baseline LLM planner
  └── cognitive planner: KG + Scene Graph + TaskGraph + SkillLibrary
  ↓
Safety / Sandbox / Evaluator
  ↓
Task Management
  ├── todo_list execution
  └── optional BehaviorTree execution
  ↓
PrimitiveTool Executor
  ↓
Runtime Scene Session + Trace / Evidence
```

核心优化方向：

- `graph/` 继续保留 LangGraph 编排角色，但不再承载动作语义和 benchmark 规则。
- `Brain Planning Facade` 统一屏蔽 baseline planner 与 cognitive planner 的差异，两条路径都必须输出同一份 `todo_list` 契约。
- `skills/` 仍是低级 PrimitiveTool 的唯一语义真理源。
- `cognitive/` 只提供高层认知规划服务，不直接执行动作。
- `benchmark/` 只做数据集适配、动作映射和评测报告，不污染主框架语义。

## 分层职责

### 1. Runtime Orchestrator

所属目录：

- `main.py`
- `graph/`

职责：

- 维护 LangGraph 主流程：Understanding、Planning、Task Management、Reflection。
- 处理跨阶段控制流：中断、插单、人类验收、反思重试。
- 在 feature flag 控制下选择 baseline path、cognitive path、BT execution path。
- 只读写 `GlobalState`，不发明动作语义。

禁止：

- 在 `graph/` 内维护第二套动作参数表。
- 在 `graph/` 内写 benchmark-specific evaluator 或 simulator。
- 让 planning normalizer 长期承担自动补动作策略。

### 2. Brain Planning Facade

所属目录：

- `graph/planning/`
- `cognitive/`
- `interfaces/`

职责：

- 将结构化任务、场景绑定、历史反馈和 feature flags 转成统一规划请求。
- 在 baseline LLM planner 与 cognitive planner 之间选择路径。
- 无论路径如何，最终输出标准 `todo_list`、`grounded_environment`、`cognitive_planning_trace` 和 evaluator 可消费的状态。

路径约束：

```text
baseline path:
  structured_task + scene grounding + prompt rules
  -> LLM planner
  -> todo_list

cognitive path:
  structured_task + Scene Graph + KG contract
  -> TaskGraph
  -> CognitiveSkill selection
  -> deterministic / LLM reasoner
  -> todo_list
```

两条路径都必须进入同一个 `evaluate_feasibility()` 审计入口。

当前 Planning 入口实现约束：

- `graph/planning/node.py` 只保留 `decompose_task()` 和 `build_planning_graph()` 两个主编排入口。
- `graph/planning/config.py` 是规划层 feature flag 的统一配置入口；默认值来自 `config/settings.json` 的 `planning.features`，运行态 `state.feature_flags` 只作为覆盖层。
- `graph/planning/grounding.py` 负责把 Understanding 输出的 `relevant_item_names` 与 `structured_task.required_item_names` 合并为场景 grounding 关键词；合并时优先保留 `relevant_item_names` 的相关性排序，再补齐结构化槽位实体。
- `graph/planning/llm_decomposer.py` 负责 baseline LLM planner 的 prompt 调用、JSON 解析和 todo_list 规范化。
- `graph/planning/cognitive_decomposer.py` 只负责 cognitive planning path 的技能 profile 上下文、BT recovery 上下文和 checkpoint suffix repair；它不再按 `operation_type` 维护任务族/动作白名单，动作空间只能来自 `config/skills.json` 当前 profile 与 `skills/*`。
- `graph/planning/satisfaction.py` 负责进入规划前的“任务是否已满足”判定；它只消费 `structured_task.goal_state` / `desired_state` / `target_state` 这类显式状态目标，不再根据 `operation_type` 维护动作白名单或猜测任务完成条件。
- `graph/planning/semantic.py` 负责规划层实体语义类型推断等纯辅助逻辑。
- `evaluate_feasibility()` 可以被测试或 benchmark 直接调用，因此也会先执行同一套规划配置归一化；沙盒验证仍可通过 `planning.features.sandbox_evaluator` 或运行态覆盖关闭；`state_diff_audit` 可在沙盒模拟后比较全部实体状态差异，再交给 LLM 判断差异是否属于任务目标或不可恢复的必要条件。

### 3. Knowledge And Cognitive Services

所属目录：

- `cognitive/kg_service.py`
- `cognitive/scene_graph_service.py`
- `cognitive/task_graph_builder.py`
- `cognitive/skill_library.py`
- `cognitive/reasoner.py`
- `cognitive/safety.py`

职责：

- KG 保存长期语义、技能关系、affordance、约束、用户偏好和证据。
- Scene Graph 保存当前实例、位置、状态和机器人局部状态。
- TaskGraph 保存单次任务的临时工作记忆。
- CognitiveSkill / planning context 只能引用当前 skill profile 启用的 PrimitiveTool；任务分解由 LLM 根据技能说明组合动作，不在 Python 代码中预定义任务族动作序列。
- SafetyPolicyEngine 提供任务无关硬约束，不依赖 prompt。

边界：

- KG 不是 KG Agent，不自主规划完整任务。
- Scene Graph 不保存长期语义。
- TaskGraph 任务结束后可销毁，只将验证过的事实、偏好、经验和 evidence 提交回持久层。

### 4. PrimitiveTool Skills

所属目录：

- `skills/`
- `config/skills.json`

职责：

- `prompt.md` 给 planner 暴露动作合同。
- `handler.py` 负责程序化校验和 sandbox/runtime 状态推进。
- `skill.yaml` 绑定技能元数据和 handler。
- profile 决定不同 benchmark 或运行模式启用哪些 PrimitiveTool。

硬规则：

- 动作参数、前提、后果、失败原因和沙盒状态推进只能以 skill 三件套为准。
- 删除某个 skill 时，主框架应 fail-soft；只影响依赖该 skill 的 profile 或 benchmark。
- 论文动作名和 OurAgent skill 名不一致时，映射写入 `benchmark/<paper>/adapter.py`，不新增重复 skill。

### 5. Domain Runtime

所属目录：

- `domain/`
- `config/scene_state.py`

职责：

- scene 索引、压平、恢复和 session 管理。
- runtime session 和 sandbox session 的创建、克隆、快照与恢复。
- 为 skills、planning evaluator 和 execution 提供确定性 scene glue。

禁止：

- 在 `domain/` 维护第二套动作语义。
- 把 benchmark evaluator、LLM prompt、认知技能策略塞进 domain helper。

### 6. Execution Layer

所属目录：

- `execution/`
- `adapters/`
- `graph/task_management/`

职责：

- 按配置分发到 simulation 或 ROS backend。
- 消费已审计的 PrimitiveTool step。
- 在 BT execution path 中解释执行已编译 BehaviorTree。
- 回写 runtime scene、`env_state`、execution failure 和 runtime trace。

执行层不负责：

- 选择高层 CognitiveSkill。
- 解释 benchmark task semantics。
- 修复规划语义；失败只应编码为结构化状态，交给 planning repair 或 reflection。

### 7. Benchmark And Evaluation

所属目录：

- `benchmark/`
- `tests/`
- `deep_checks/`

职责：

- 接入论文和数据集：EAI、DELTA、ReAcTree、ALFRED、WAH 等。
- 做输入输出转换、动作名映射、官方 evaluator/simulator 桥接。
- 输出 cognitive eval artifact、rollup report、ablation summary。
- 通过 tests / smoke / deep checks 保护架构边界。

benchmark import 失败时必须隔离，不应拖垮全局主图。

## 数据与控制流

### 主任务流

```text
HumanMessage / Benchmark Case
  -> UnderstandingState.structured_task + relevant_item_names
  -> PlanningState.todo_list
  -> PlanningState.is_feasible
  -> ExecutionState.task_stack
  -> ExecutionResult / behavior_tree_execution
  -> Human Feedback or Reflection
```

### 语义理解实体筛选流

Understanding 模块的第一层职责不是直接规划动作，而是从“任务文本 + 场景实体清单”中筛出对任务有用的实体，并保证传给 Planning 的实体都来自当前场景。

输入：

```text
task: 用户任务文本
scene_entities: 当前 runtime scene 中可用实体名称清单
messages: 必要的对话上下文
```

LLM 只负责做语义相关性判断，输出相关实体，不输出无关实体。实体按四类组织：

```text
directly_related    直接相关：任务目标、必须操作对象、明确指定工具或容器
indirectly_related  间接相关：完成任务通常需要的工具、承载物、位置、状态依赖对象
possibly_related    可能相关：任务可能用到，但不是当前指令明确要求的备选对象
irrelevant          不相关：不应输出到结果中
```

输出顺序规则：

- 先按分类优先级排序：`directly_related -> indirectly_related -> possibly_related`。
- 每个分类内部再按相关性从高到低排序。
- `irrelevant` 不进入输出。
- 最终对外只暴露一份扁平排序列表，作为 `relevant_item_names`。

推荐中间结构：

```json
{
  "entity_relevance": {
    "directly_related": [
      {"name": "牛肉_1", "reason": "任务直接目标", "required": true, "score": 1.0}
    ],
    "indirectly_related": [
      {"name": "菜刀_1", "reason": "切牛肉所需工具", "required": true, "score": 0.92}
    ],
    "possibly_related": [
      {"name": "砧板_2", "reason": "可作为备用切割表面", "required": false, "score": 0.51}
    ]
  },
  "relevant_item_names": ["牛肉_1", "菜刀_1", "砧板_2"]
}
```

实体校验必须在 Understanding 内完成，Planning 不应再接收未经验证的实体名称。

校验规则：

- 将 LLM 输出的 `relevant_item_names` 与 `scene_entities` 比对。
- 如果所有实体都存在，直接输出排序后的实体清单给任务分解模块。
- 如果存在不在场景清单内的实体，记录为 `invalid_entity_names`。
- 如果还没有达到最大修复次数，向 LLM 反馈这些实体不存在，并要求 LLM 只做增量修复。
- 如果不存在实体是任务必须项，LLM 应检查场景清单中是否存在可替代实体。
- 如果不存在实体不是任务必须项，LLM 应删除该实体。
- 增量修复结果与上一轮有效实体清单合并后，再次做同样校验。
- 如果已经达到最大修复次数，系统不再反问 LLM，直接删除仍不存在的实体，将剩余已验证实体清单传给 Planning。

增量修复建议输出：

```json
{
  "remove": ["红色菜刀"],
  "replace": [
    {
      "missing": "红色菜刀",
      "replacement": "菜刀_1",
      "reason": "场景中没有红色菜刀，菜刀_1 是可用切割工具"
    }
  ],
  "add": [],
  "relevant_item_names_delta": ["菜刀_1"]
}
```

最大重试后的降级策略是 fail-soft：

```text
invalid entities after max retries
  -> drop invalid names
  -> keep validated relevant_item_names
  -> continue to Planning
```

只有当删除非法实体后没有任何可用的直接相关必需实体时，Understanding 才应设置 `needs_clarification=True`，向用户反问缺失的任务核心对象；否则应继续让 Planning 基于剩余实体尝试分解任务。

### 场景状态流

```text
seed scene
  -> runtime session
  -> sandbox clone
  -> evaluator checkpoint
  -> runtime execution update
  -> trace / optional dump
```

场景状态不再以 repo 中的 `default/runtime/sandbox` 三份常驻文件作为长期真值：

- `scenes/default/house.json` 是唯一基线 seed scene。
- runtime scene 在内存 session 中维护，是连续任务的环境事实来源。
- sandbox scene 从 runtime session 克隆，只用于规划审计。
- 可选 `state_diff_audit` 在 sandbox 模拟通过后，由代码遍历全部实体状态并生成前后差异，再让 LLM 审计这些差异是否正是任务目标或完成任务不可恢复的必要条件。
- dump 文件只用于调试，不是 canonical state。

核心接口：

- `load_seed_scene()`
- `new_runtime_session()`
- `clone_sandbox_session()`
- `snapshot_scene()`
- `restore_scene()`

### 失败修复流

```text
planning reject
  -> checkpoint + evaluator_findings
  -> replan from validated prefix

execution failure
  -> runtime checkpoint + failed step
  -> execution reflection or planning repair

human negative feedback
  -> understanding/planning reflection
  -> retry selected stage
```

失败必须结构化记录：

- `failure_layer`
- `failure_reason`
- `failed_action`
- `error_feedback`
- `evaluator_findings`
- `validated_steps`
- `checkpoint_env`
- `checkpoint_robot`
- `cognitive_planning_trace`

## 依赖方向

允许的稳定方向：

```text
main -> graph
graph -> interfaces / config
graph -> cognitive public facades
graph -> skills registry
graph -> domain runtime glue
graph -> execution dispatcher
benchmark -> graph public entry points
benchmark -> skills/domain/execution public contracts
tests -> all public contracts
```

不允许的方向：

```text
skills -> graph
domain -> graph
execution -> graph
cognitive -> benchmark
graph -> benchmark internals
benchmark -> graph private nodes
```

如果为了兼容旧路径短期违反依赖方向，必须满足：

- 用 feature flag 隔离。
- 在 `ARCHITECTURE_IMPROVEMENT_PLAN.md` 记录迁移目标。
- 有测试覆盖旧路径与新路径的行为一致性。

## Feature Flag 策略

feature flag 只能用于切换能力，不应用于隐藏长期架构分叉。

配置入口：

```text
config/settings.json
  planning.features
    -> graph.planning.config.with_planning_config()
    -> PlanningState.feature_flags
```

优先级：

```text
state.feature_flags 显式覆盖
  > config/settings.json: planning.features
  > 代码内保守默认值
```

当前建议分组：

```text
planning path:
  cognitive_planning
  cognitive_lightweight_path

validation:
  sandbox_evaluator
  checkpoint_repair
  semantic_audit
  state_diff_audit

execution:
  cognitive_bt_compile
  cognitive_bt_execute
  cognitive_bt_recovery_direct_replan
  cognitive_bt_execution_reflection_retry

learning:
  playbook_retrieval
  playbook_write
  candidate_rules
  cognitive_trace_write

repair:
  reflection
```

上线新 feature flag 时必须同时说明：

- 默认值。
- 关闭时是否回退到旧路径。
- 是否影响 benchmark 结果可比性。
- 应由哪类测试覆盖。

## Trace 与证据治理

每次规划和执行都应能回答：

- 为什么选择该 path。
- 查询了哪些 KG / Scene Graph 信息。
- 哪些规则影响了计划。
- 哪些步骤由 normalizer、SafetyPolicyEngine 或 evaluator 修改/拦截。
- 失败时使用了哪个 checkpoint 和 validated prefix。
- 经验写入是否只是 candidate，是否经过验证后 commit。

最低 trace 字段：

```text
orchestration_route
selected_skill_ids
kg_query
kg_facts_used
scene_instances_bound
task_graph_stats
plan_summary
safety
sandbox
state_diff_audit
behavior_tree_execution
trace_storage
```

LLM 只能提出 candidate update。正式 KG、规则或技能更新必须经过：

```text
propose -> normalize -> deduplicate -> validate -> commit
```

并记录：

- provenance
- confidence
- timestamp
- ttl
- evidence_ids
- validation status

## 设计收敛原则

后续修改按以下优先级判断：

1. 先保护 `skills/` 作为 PrimitiveTool 语义真理源。
2. 再保护 `GlobalState`、`TodoList`、`PlanStep`、`ValidationResult` 等 typed contracts。
3. 再保护 benchmark 隔离和可复现实验。
4. 最后才优化 prompt、模板、normalizer 和交互体验。

如果某个改动能提高单个 benchmark 分数，但会让动作语义复制到 `graph/`、`domain/` 或 `benchmark/`，该改动不应合入。

## 重构规范

- 文档必须与代码同步；代码边界改变时，这份文档必须同步修正。
- `domain/` 不是 helper 垃圾桶，只保留确定性 scene/session/runtime glue。
- `deep_checks/` 可以作为模型连通性、主图端到端、benchmark smoke test 的主要验证入口。
- 新增 benchmark 必须先写 adapter 边界，再接 runner 和 metrics。
- 新增 CognitiveSkill 必须能展开为现有 PrimitiveTool，不能绕过 `skills/`。
- 新增 PrimitiveTool 必须包含 prompt、handler、metadata 和 profile 配置。
- 新增 learning / memory 写入路径必须默认 candidate-only，不能直接污染正式知识库。
