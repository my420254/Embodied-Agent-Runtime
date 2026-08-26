# 具身智能体分层架构设计

本文记录当前关于 OurAgent 后续架构演进的设计结论，重点覆盖：

- 大脑、小脑与 `todo_list` 的边界
- 低级动作、工具、认知技能与知识图谱的关系
- 是否引入行为树或 PDDL
- 技能库在使用前如何构建、使用中如何更新
- KG、场景图、任务动态图与大模型接口
- SkillOpt 与 PiEvo 对本项目的借鉴方式

## 核心结论

OurAgent 应采用“知识图谱 + 技能库 + 小脑工具”的混合架构，而不是把所有能力都放进同一个 `skills/` 概念中。

推荐分层如下：

```text
用户目标
  ↓
大脑：理解目标、检索知识、选择认知技能、生成或修复计划
  ↓
认知技能库：提供可复用、可学习、可展开的任务过程
  ↓
Skill Expander：把认知技能展开为 primitive todo_list
  ↓
Sandbox / Evaluator：审计前提、后果、物理可行性和安全约束
  ↓
小脑：只执行低级 PrimitiveTool
  ↓
环境反馈、失败经验、成功轨迹
  ↓
知识图谱与技能库的离线更新
```

真实执行时，小脑只接收低级动作工具，不直接接收“做饭”“洗衣服”这类高层技能。

## 术语边界

### PrimitiveTool

PrimitiveTool 是小脑可直接执行的原子动作，也可以称为 ActionPrimitive 或 MotorPrimitive。

典型例子：

```text
NavigateTo
Pickup
Put
Open
Close
Slice
Clean
Heat
Cool
ToggleOn
ToggleOff
```

PrimitiveTool 的特点：

- 小脑直接执行
- 参数明确
- 有前提条件和后果
- 有 deterministic handler 或 executor backend
- 可以被 sandbox 校验
- 语义应稳定，不应由大脑在线随意改写

### CognitiveSkill

CognitiveSkill 是大脑可学习、可复用、可展开的程序性记忆。

典型例子：

```text
CutIngredient
MakeTea
CookRice
DoLaundry
CleanDiningTable
PrepareBreakfast
```

CognitiveSkill 的特点：

- 不直接由小脑执行
- 会展开成一组 PrimitiveTool
- 有适用条件、成功标准和失败处理策略
- 可以被 SkillOpt 一类方法优化
- 可以从成功轨迹、失败轨迹和 benchmark 中持续改进

### KnowledgeGraph

KnowledgeGraph 是语义记忆和检索入口，不是完整过程控制器。

适合放入 KG 的内容：

- 对象类型、稳定属性、类别层次和长期语义
- 工具和对象的 affordance
- 任务、技能、对象之间的关系
- 安全约束和用户偏好
- 技能适用条件、证据、成功率、反例

不适合只放入 KG 的内容：

- 完整任务展开流程
- 复杂 fallback 逻辑
- 可执行 prompt 或 planner policy
- 技能版本、评测结果和 rollback artifact

### KG Service 不是 KG Agent

本文所说的 KG 不是另一个带大模型的智能体，而是一个带 schema、查询、检索、校验和候选更新机制的知识服务。

推荐边界：

```text
Brain LLM
  ↓ 调用结构化工具
KG Service
  ├── Graph Store
  ├── Ontology / Schema
  ├── Relation Query
  ├── Constraint Retrieval
  ├── Skill Metadata Retrieval
  ├── Candidate Update Manager
  └── Validation / Commit Gate
```

KG Service 负责：

- 查对象语义
- 查操作约束
- 查 skill 适用条件
- 查工具需求
- 查用户偏好
- 查安全规则
- 做受控多跳检索
- 构建任务相关子图
- 记录 evidence
- 接收候选更新
- 验证后 commit

KG Service 不负责：

- 直接规划完整 `todo_list`
- 自主决定下一步动作
- 在线改写技能
- 无验证地新增规则
- 像 agent 一样自由推理

可以有离线 KG Curator 使用 LLM 总结日志、抽取候选事实或合并重复规则，但它只能产生 candidate fact / candidate rule，不能直接污染正式 KG。

推荐写入流程：

```text
LLM propose
  ↓
schema normalize
  ↓
deduplicate
  ↓
sandbox / benchmark / human validation
  ↓
commit
```

## KG、Scene Graph 与 TaskGraph

KG、场景图和任务动态图必须分开。

```text
Persistent KG
  存长期知识、对象语义、技能关系、用户偏好、安全规则、历史证据

Runtime Scene Graph
  存当前房间、物体位置、开关状态、机器人持物、清洁状态等可变事实

TaskGraph
  每次任务临时构建，只包含本任务相关实体、技能、约束、目标、执行轨迹和中间假设
```

场景图额外维护，不在 KG 里。对象的位置和当前状态属于 Scene Graph，不属于 Persistent KG。

例如，KG 可以知道：

```text
牛肉 -> category -> raw_meat
raw_meat -> requires_tool -> knife
raw_meat -> requires_state -> clean_cutting_board
CutIngredient -> uses_primitive -> Slice
```

但 KG 不负责知道：

```text
牛肉_1 当前在冰箱_1
菜刀_1 当前在抽屉_1
砧板_1 当前 clean == false
机器人当前在厨房
```

这些事实由 Scene Graph 维护。

TaskGraph 是任务工作记忆。它从 KG 和 Scene Graph 中抽取当前任务需要的子集，用于规划、校验和重规划。

```text
用户目标
  ↓
从 Scene Graph 解析实例和状态
  ↓
从 KG 检索语义、约束、技能和安全规则
  ↓
构建 TaskGraph
  ↓
大脑基于 TaskGraph 生成计划
  ↓
执行反馈增量更新 TaskGraph
  ↓
任务结束后销毁 TaskGraph
  ↓
验证过的事实、偏好、经验提交回持久层
```

执行完任务后，TaskGraph 可以销毁，但不应全部丢弃：

```text
临时推理、中间假设 -> 丢弃
真实状态变化 -> 更新 Runtime Scene Graph
用户明确偏好 -> 写入 User Preference KG
成功/失败经验 -> 写入 Evidence / Skill History
可泛化规则 -> 进入 candidate principle，离线验证后再写入稳定 KG
```

## KG 边类型与 schema

核心边类型必须提前定义。大模型可以查询某个对象有哪些边，但不能随意发明边名并直接写入 KG。

原因是关系名如果完全开放，会快速产生语义重复：

```text
requires_tool
need_tool
must_have_tool
tool_required
需要工具
依赖工具
```

这些会破坏后续检索、规划和多跳推理。

推荐做法：

```text
核心关系 schema 提前定义
大模型通过接口查询对象已有边
大模型可以提出候选新边或候选新关系类型
系统负责映射、验证、合并或拒绝
```

核心关系至少包含：

```text
located_in          对象位于哪里，通常用于 Scene Graph
contains            容器包含什么，通常用于 Scene Graph
has_state           对象当前状态，通常用于 Scene Graph
category            对象类型
affords             对象支持什么操作
requires_tool       操作/技能需要什么工具
requires_state      操作/技能需要什么状态
precondition_of     某条件是谁的前提
effect_of           某动作产生什么后果
uses_primitive      认知技能使用哪些小脑工具
applicable_when     技能适用条件
conflicts_with      约束冲突
user_prefers        用户偏好
evidence_for        证据支持某事实或规则
counterexample_of   反例反驳某规则
```

内部建议使用英文 snake_case，文档和 prompt 中可以附中文解释。

大模型查询对象邻居时应使用 view / policy / budget 控制，不建议直接返回所有边：

```python
kg.get_neighbors("牛肉_1", view="planning")
kg.get_neighbors("牛肉_1", view="safety")
kg.get_neighbors("牛肉_1", view="operation:cut")
```

新关系类型必须走候选流程：

```python
kg.propose_relation_type(
    name="after_operation",
    domain="Operation",
    range="StateChange",
    reason="需要表达切生肉之后必须清洁刀具"
)
```

系统先尝试映射到已有关系；如果不能表达，再进入 candidate schema，经验证后才加入正式 schema。

## 大模型与 KG 的接口

大模型不应直接写 Cypher、SPARQL 或任意图查询语言。应通过 typed APIs 查询 KG。

推荐接口分为三类。

读取接口：

```python
kg.resolve_entities(text, scene_context)
kg.get_relevant_subgraph(goal, entities, budget)
kg.get_object_facts(object_id)
kg.get_affordances(object_id)
kg.get_skill_candidates(goal, entities)
kg.get_constraints(entity_ids, skill_ids)
kg.describe_schema(phase="planning")
kg.get_available_relations(entity_id, view="planning")
```

检查接口：

```python
kg.check_preconditions(action, params, task_graph_id)
kg.check_skill_applicability(skill_id, params, task_graph_id)
kg.explain_failure(action, params, state)
kg.find_missing_facts(task_graph_id)
kg.check_plan_dependencies(task_graph_id, todo_list)
```

写入接口：

```python
kg.record_observation(observation, provenance)
kg.propose_fact_update(candidate_fact, evidence_id)
kg.propose_rule_update(candidate_rule, evidence_ids)
kg.commit_validated_update(candidate_id)
```

写入接口必须区分 observation、candidate update 和 validated commit。大模型可以提出候选，但不能直接写正式 KG。

## 多轮查询与 TaskGraph 增量构建

大模型需要多次查询 KG 来丰富 TaskGraph，也需要受控多跳查找。

推荐循环：

```text
1. 解析用户目标，得到初始实体和意图
2. 构建 seed TaskGraph
3. 查询相关对象、状态、技能、约束
4. 生成候选 todo_list
5. 用 sandbox / KG 检查前提条件
6. 对缺失信息继续查询 KG 或 Scene Graph
7. 更新 TaskGraph
8. 重复，直到计划可执行或需要反问用户
```

多跳示例：

```text
牛肉_1 -> category -> raw_meat
raw_meat -> requires -> clean_cutting_board
raw_meat -> requires_tool -> knife
knife -> instance -> 菜刀_1
cutting_board -> instance -> 砧板_1
Clean -> can_make -> 砧板_1.clean = true
Slice -> requires -> ingredient_on_cutting_board
```

多跳不应无限扩张。建议：

```text
普通任务：max_hops = 2
复杂任务：max_hops = 3
高风险任务：额外查 safety / preference
节点预算：最多 50 个节点
边预算：最多 120 条边
```

规划阶段允许的关系可以限制为：

```text
located_in
contains
category
affords
requires
requires_tool
precondition
effect
conflicts_with
uses_primitive
applicable_when
user_prefers
```

大模型负责提出查询意图，KG Service 负责执行受控多跳、去重、剪枝、排序和置信度管理。

## 切牛肉任务的 KG 查询契约

针对“切牛肉”，大模型不应问 KG：

```text
牛肉在哪里？
菜刀在哪里？
砧板是否干净？
冰箱是否打开？
```

这些属于 Scene Graph。

大模型应问 KG：

```text
牛肉作为一种对象，在“切”这个任务下需要什么语义知识、工具角色、约束、前后条件和安全规则？
```

示例查询：

```json
{
  "query_type": "task_operation_contract",
  "task": {
    "operation": "cut",
    "target_name": "牛肉",
    "target_type_hint": "beef",
    "desired_result": {
      "form": "sliced",
      "cut_style": "片"
    },
    "domain": "food_preparation"
  },
  "need": [
    "canonical_target_type",
    "candidate_cognitive_skills",
    "required_roles",
    "preconditions_to_check_in_scene",
    "conditional_rules",
    "safety_constraints",
    "success_criteria",
    "scene_queries_needed"
  ]
}
```

KG 返回任务语义合同：

```json
{
  "canonical_target_type": "beef",
  "categories": [
    "food",
    "ingredient",
    "meat",
    "raw_meat",
    "cuttable_ingredient"
  ],
  "candidate_cognitive_skills": [
    {
      "skill_id": "cooking.cut_ingredient",
      "priority": 1,
      "reason": "beef is a cuttable ingredient"
    }
  ],
  "required_roles": [
    {
      "role": "target",
      "semantic_type": "beef"
    },
    {
      "role": "cutting_tool",
      "semantic_type": "knife",
      "constraints": [
        "clean",
        "food_safe"
      ]
    },
    {
      "role": "cutting_surface",
      "semantic_type": "cutting_board",
      "constraints": [
        "clean",
        "food_safe",
        "suitable_for_raw_meat"
      ]
    }
  ],
  "preconditions_to_check_in_scene": [
    {
      "predicate": "target_accessible",
      "args": ["target"]
    },
    {
      "predicate": "target_not_frozen",
      "args": ["target"]
    },
    {
      "predicate": "surface_clean",
      "args": ["cutting_surface"]
    },
    {
      "predicate": "tool_clean",
      "args": ["cutting_tool"]
    },
    {
      "predicate": "target_on_surface",
      "args": ["target", "cutting_surface"]
    },
    {
      "predicate": "robot_holding",
      "args": ["cutting_tool"]
    }
  ],
  "conditional_rules": [
    {
      "if": "target.frozen == true",
      "then": "must_thaw_before_cutting"
    },
    {
      "if": "cutting_surface.clean == false",
      "then": "clean_cutting_surface_before_use"
    },
    {
      "if": "target.category == raw_meat",
      "then": "avoid_cross_contamination"
    }
  ],
  "safety_constraints": [
    "raw_meat should not share an unclean cutting surface with ready-to-eat food",
    "knife and cutting surface should be cleaned after cutting raw meat",
    "cutting should happen only when target is placed on a stable cutting surface"
  ],
  "success_criteria": [
    {
      "predicate": "target_cut_style",
      "args": ["target", "sliced"]
    },
    {
      "predicate": "target_on_surface_or_container",
      "args": ["target"]
    }
  ],
  "scene_queries_needed": [
    {
      "query": "resolve_instance",
      "type": "beef",
      "role": "target"
    },
    {
      "query": "find_instance",
      "type": "knife",
      "role": "cutting_tool"
    },
    {
      "query": "find_instance",
      "type": "cutting_board",
      "role": "cutting_surface"
    },
    {
      "query": "check_state",
      "target": "target",
      "states": ["accessible", "frozen", "packaged"]
    },
    {
      "query": "check_state",
      "target": "cutting_surface",
      "states": ["clean"]
    },
    {
      "query": "check_state",
      "target": "cutting_tool",
      "states": ["clean"]
    }
  ]
}
```

大模型随后根据 `scene_queries_needed` 查询 Scene Graph，绑定真实实例和状态，再把这些事实作为查询上下文传给 KG 做规则实例化。

示例：

```json
{
  "query_type": "instantiate_operation_contract",
  "operation": "cut",
  "target_type": "beef",
  "desired_result": {
    "cut_style": "sliced"
  },
  "bound_roles": {
    "target": {
      "id": "牛肉_1",
      "type": "beef",
      "states": {
        "frozen": false,
        "packaged": false
      }
    },
    "cutting_tool": {
      "id": "菜刀_1",
      "type": "knife",
      "states": {
        "clean": true
      }
    },
    "cutting_surface": {
      "id": "砧板_1",
      "type": "cutting_board",
      "states": {
        "clean": false,
        "suitable_for_raw_meat": true
      }
    }
  }
}
```

KG 返回实例化约束，而不是位置事实：

```json
{
  "applicable_skill": "cooking.cut_ingredient",
  "resolved_constraints": [
    {
      "status": "satisfied",
      "constraint": "target_not_frozen",
      "evidence": "牛肉_1.frozen == false"
    },
    {
      "status": "satisfied",
      "constraint": "tool_clean",
      "evidence": "菜刀_1.clean == true"
    },
    {
      "status": "unsatisfied",
      "constraint": "surface_clean",
      "evidence": "砧板_1.clean == false",
      "required_fix": {
        "primitive": "Clean",
        "target": "砧板_1"
      }
    }
  ],
  "abstract_plan_skeleton": [
    {
      "goal": "make_target_accessible",
      "role": "target"
    },
    {
      "goal": "ensure_clean_surface",
      "role": "cutting_surface",
      "required_if": "cutting_surface.clean == false"
    },
    {
      "goal": "place_target_on_surface",
      "roles": ["target", "cutting_surface"]
    },
    {
      "goal": "hold_cutting_tool",
      "role": "cutting_tool"
    },
    {
      "goal": "cut_target",
      "primitive": "Slice",
      "params": {
        "target_item": "target",
        "cut_style": "sliced"
      }
    },
    {
      "goal": "post_cleaning_for_raw_meat",
      "required": true
    }
  ],
  "post_actions_recommended": [
    {
      "primitive": "Clean",
      "target": "菜刀_1",
      "reason": "knife used for raw meat"
    },
    {
      "primitive": "Clean",
      "target": "砧板_1",
      "reason": "cutting surface used for raw meat"
    }
  ]
}
```

最终边界：

```text
KG 管“规则和意义”
Scene Graph 管“当前事实和位置状态”
TaskGraph 管“本次任务工作记忆”
Brain LLM 通过 typed APIs 查询、补图、规划和修复
```

## Tool 与 Skill 的命名决策

现有 `skills/` 中的 `NavigateTo`、`Pickup`、`Put`、`Open` 等能力，从大脑视角看更像 tool，而不是后续希望学习的高级 skill。

建议逐步采用如下命名：

```text
Capability
├── PrimitiveTool
│   ├── NavigateTo
│   ├── Pickup
│   └── Put
└── CognitiveSkill
    ├── CutIngredient
    ├── MakeTea
    └── DoLaundry
```

为降低重构成本，短期可以保留现有 `skills/` 目录，但在 manifest 中增加 `kind` 字段：

```yaml
kind: primitive_tool
name: Pickup
handler: skills.Pickup.handler:PickupSkill
```

后续新增的高层技能使用独立目录：

```text
learned_skills/
  cooking/
    cut_ingredient/
    make_tea/
  laundry/
    do_laundry/
```

或长期统一为：

```text
capabilities/
  primitives/
  cognitive_skills/
```

## Todo List、行为树与 PDDL

### 当前阶段

继续让大脑生成结构化 `todo_list` 是合理的。

原因：

- LLM 生成动作序列更稳定
- 与当前 sandbox evaluator 和 skill handler 兼容
- 容易记录、评测、修复和回放
- 对家居服务中大量线性任务已经足够有效

建议增强 `todo_list` schema，而不是立即替换：

```json
{
  "step": 2,
  "execution": {
    "skill": "Pickup",
    "parameters": {
      "target_item": "苹果_1"
    }
  },
  "preconditions": [
    "robot_at_direct_parent(target_item)",
    "hand_empty",
    "item_accessible(target_item)"
  ],
  "expected_effects": [
    "robot_holding = target_item"
  ],
  "failure_policy": {
    "on_precondition_failed": "repair_plan",
    "max_retries": 1
  }
}
```

### 行为树

行为树适合作为运行时执行控制层，而不是一开始就作为 LLM 主输出。

推荐方式：

```text
CognitiveSkill
  ↓
todo_list
  ↓
todo_list -> BehaviorTree compiler
  ↓
小脑执行
```

行为树适合处理：

- 条件检查
- 重试
- fallback
- 中断恢复
- 动态环境变化

但不建议直接让 LLM 生成完整行为树。更稳妥的方式是系统把已经审计过的 `todo_list` 编译成行为树。

### PDDL

PDDL 适合封闭世界中的形式化规划和验证，但不适合作为当前家居服务 agent 的全局主表示。

原因：

- 家居环境对象开放
- 状态观测不完整
- 自然语言任务模糊
- PDDL domain 维护成本高
- LLM 生成 PDDL 的错误成本高

PDDL 更适合作为局部工具：

- 在明确子领域中做形式化搜索
- 校验单臂、容器、可达性等硬约束
- 为 sandbox evaluator 提供补充约束

推荐组合：

```text
LLM 生成 todo_list
系统编译为行为树执行
PDDL 或 handler 做局部形式化验证
```

## 认知技能与知识图谱的关系

认知技能应封装为 skill artifact，同时在知识图谱中注册、索引和关联。

```text
KnowledgeGraph 负责知道“有哪些技能、什么时候适用、需要什么对象和工具”
CognitiveSkill 负责知道“具体怎么做、怎么展开、失败怎么办”
```

例如 `CutIngredient`：

KG 中记录：

```text
胡萝卜 -> category -> vegetable
牛肉 -> category -> raw_meat
raw_meat -> requires -> clean_cutting_board
raw_meat -> after_cut -> clean_knife
CutIngredient -> uses -> Slice
CutIngredient -> requires -> knife
```

Skill 中记录：

```yaml
kind: cognitive_skill
id: cooking.cut_ingredient
parameters:
  ingredient: object
  cut_style: string
uses_primitives:
  - NavigateTo
  - Pickup
  - Put
  - Slice
  - Clean
success_criteria:
  - ingredient.state == cut
kg_queries:
  - get_object_category(ingredient)
  - get_required_tool(ingredient, cut_style)
  - get_safety_constraints(ingredient)
```

## 技能粒度

技能粒度不能太粗，也不能为每个对象都创建一个技能。

推荐原则：

```text
只是对象约束不同 -> 放入 KG
流程结构明显不同 -> 单独 CognitiveSkill
频繁复用且需要独立优化 -> 单独 CognitiveSkill
```

例如，`切肉` 不应一开始就注册成独立技能。更合理的起点是：

```text
CutIngredient(ingredient, cut_style)
```

由 KG 区分：

```text
ingredient = 胡萝卜 -> vegetable
ingredient = 牛肉 -> raw_meat
ingredient = 冷冻肉 -> frozen_meat
```

如果后续发现 `切肉` 的流程足够复杂、足够常用，再升级为：

```text
CutIngredient
├── CutVegetable
├── CutFruit
└── CutMeat
```

同理，`做饭` 不建议一开始做成巨大技能，而应视为 TaskFamily 或 Domain：

```text
Cooking
├── CutIngredient
├── WashIngredient
├── CookRice
├── FryEgg
├── BoilWater
└── PrepareMeal(recipe)
```

`洗衣服` 可以作为高层技能，但也应拆解为子技能：

```text
DoLaundry
├── CollectClothes
├── SortClothes
├── LoadWasher
├── AddDetergent
├── StartWasher
├── DryClothes
└── FoldClothes
```

## 技能库使用前如何构建

上线前不要试图覆盖所有家务场景，应先构建最小可用技能库。

### 1. 固定 PrimitiveTool

先稳定小脑工具：

```text
NavigateTo
Pickup
Put
Open
Close
Slice
Clean
Heat
Cool
ToggleOn
ToggleOff
```

每个 PrimitiveTool 必须有：

- 参数 schema
- 前置条件
- 后果
- handler 或 executor backend
- sandbox 单元测试
- prompt 中的动作合同

### 2. 构建对象和动作知识图谱

KG 至少要覆盖：

- 对象类别
- 对象状态
- 工具需求
- 可操作 affordance
- 安全约束
- 用户偏好
- skill 与对象、工具、子技能的关系

### 3. 构建种子 CognitiveSkill

优先构建可复用中间技能：

```text
CutIngredient
WashIngredient
BoilWater
MakeTea
CookRice
DoLaundry
CleanTable
```

每个 CognitiveSkill 至少包含：

- 参数
- 适用条件
- KG 查询
- primitive tools 白名单
- 展开策略
- 成功标准
- 失败策略
- 评测用例

### 4. 建立 Skill Registry

Skill Registry 负责：

- 动态加载 PrimitiveTool 和 CognitiveSkill
- 按 `kind` 分 namespace
- 只向小脑暴露 PrimitiveTool
- 向大脑暴露 CognitiveSkill 的检索信息
- 记录版本、状态、证据和评测结果

### 5. 建立评测集

没有评测用例的 CognitiveSkill 不应上线。

例如 `CutIngredient` 至少需要：

```text
切苹果
切胡萝卜
切生肉
切冷冻肉
没有刀
砧板脏
机器人手里已有物体
```

## 技能状态流转

CognitiveSkill 应使用显式生命周期：

```text
draft -> candidate -> validated -> deployed -> deprecated
```

约束：

- 真实执行只读取 `deployed`
- `candidate` 只能在 sandbox 或 benchmark 中使用
- 新版本不能覆盖旧版本
- 每次 promote 必须有验证集结果
- 每个 deployed 版本必须可回滚

## 使用过程中的更新流程

运行时不要直接修改已部署技能。

正确流程：

```text
真实任务执行
  ↓
记录轨迹、失败、成功、用户反馈
  ↓
写入 evidence / history
  ↓
离线生成 candidate patch
  ↓
在训练集跑
  ↓
在验证集跑
  ↓
分数提升才 promote
  ↓
旧版本保留，可回滚
```

也就是：

```text
online 只收集证据
offline 才更新技能
validated 后再部署
```

每次执行后应记录：

```json
{
  "skill_id": "cooking.cut_ingredient",
  "version": "0.1.0",
  "task": "切牛肉",
  "context": {
    "ingredient": "牛肉_1",
    "state": "raw",
    "tool": "菜刀_1"
  },
  "expanded_todo_list": [],
  "success": false,
  "failure_reason": "砧板未清洁",
  "fix_hint": "切生肉前需要确认砧板清洁或使用专用砧板"
}
```

根据结果更新两类资产：

```text
KG 更新：新增或调整对象、工具、安全约束、反例
Skill 更新：修改展开策略、失败策略、成功标准或适用条件
```

## SkillOpt 的借鉴方式

SkillOpt 的核心启发是：把 skill 文档视为 frozen model 外部的可训练状态，通过离线 rollout、候选编辑和验证集门控来优化技能文本。

对 OurAgent 最有价值的部分：

- 把 CognitiveSkill 和 planning playbook 当作可优化文本 artifact
- 使用候选 patch，而不是在线直接覆盖
- 训练集生成候选，验证集决定是否接受
- 只部署验证通过的 `best_skill`
- 部署后不增加推理时调用

推荐用于：

- 优化 `CognitiveSkill.expansion`
- 优化 planning playbook
- 优化 profile 级 skill pack
- 从 benchmark 轨迹中改进技能展开策略

不建议用于：

- 自动修改低级 PrimitiveTool handler
- 在线真实执行中直接改技能
- 跳过 sandbox/validation 的自我改写

## PiEvo 的借鉴方式

PiEvo 的核心启发是：维护一个可演化的 principle space，并根据不确定性和异常结果主动选择实验、扩展原则。

对 OurAgent 最有价值的部分：

- 把 playbook 规则和 KG 约束视为 principles
- 每条 principle 记录 belief、uncertainty、evidence、counterexamples
- 使用异常驱动新增原则，而不是每次失败都写经验
- 主动选择最能验证或推翻当前原则的 benchmark case

推荐用于：

- 管理 KG 中的家居操作原则
- 管理 planning playbook 的置信度
- 指导 benchmark case 采样
- 判断哪些技能需要拆分、合并或升级

不建议照搬：

- 完整 GP/Bayesian optimization 架构
- 用多 agent 框架替换当前 LangGraph
- 把科学发现流程原样套到家居动作规划

## 推荐模块划分

后续可以逐步形成三个管理器：

```text
ToolRegistry
  管 PrimitiveTool，面向小脑执行，稳定、强校验

SkillLibrary
  管 CognitiveSkill，面向大脑检索和展开，版本化、可验证、可回滚

KnowledgeGraph Service
  管对象语义、关系、约束、skill 索引、经验统计和原则置信度

Runtime Scene Graph
  管对象实例、位置、状态和机器人当前状态

TaskGraph Builder
  按任务从 KG 和 Scene Graph 抽取相关子图，形成临时工作记忆
```

调用流程：

```text
1. 大脑理解用户目标
2. 查询 Scene Graph 解析对象实例、位置和当前状态
3. 查询 KG 获取对象语义、技能关系、偏好和约束
4. 构建 TaskGraph
5. 从 SkillLibrary 检索候选 CognitiveSkill
6. 选择或组合 CognitiveSkill
7. 展开为 primitive todo_list
8. Sandbox/Evaluator 审计
9. 小脑执行 PrimitiveTool
10. 记录结果
11. 销毁 TaskGraph，并离线更新 KG 与 SkillLibrary
```

## 落地路线

### 阶段一：术语和 schema 收敛

- 给现有 `skills/*/skill.yaml` 增加 `kind: primitive_tool`
- 新增 CognitiveSkill schema
- 明确小脑只执行 PrimitiveTool
- 明确 CognitiveSkill 必须展开为 `todo_list`

### 阶段二：最小认知技能库

- 新增 `learned_skills/`
- 实现 `CutIngredient`、`MakeTea`、`DoLaundry` 等种子技能
- 每个技能配评测用例
- 建立 skill 状态流转

### 阶段三：KG 与 SkillRegistry 联动

- KG 注册 skill node
- skill node 指向 artifact path
- KG 存对象 affordance、约束、证据和反例
- 大脑通过 KG typed APIs 检索技能和约束

### 阶段三点五：Scene Graph 与 TaskGraph

- 明确 Scene Graph 维护对象实例、位置、状态和机器人状态
- 明确 Persistent KG 不存当前场景状态
- 实现 `build_task_graph(goal)`，从 KG 和 Scene Graph 抽取任务相关子图
- 支持多轮查询增量丰富 TaskGraph
- 任务结束后销毁 TaskGraph，只提交验证过的事实、偏好和经验

### 阶段四：执行层增强

- 保持大脑输出 `todo_list`
- 增加 `preconditions`、`expected_effects`、`failure_policy`
- 实现 `todo_list -> BehaviorTree` 编译器
- 用行为树管理执行时 retry、fallback 和中断恢复

### 阶段五：离线自优化

- 记录成功/失败轨迹
- 生成 candidate skill patch
- 用 benchmark/sandbox 做训练集和验证集
- 只 promote 验证提升的技能版本
- 引入 SkillOpt 式文本优化和 PiEvo 式 principle 管理

## 安全边界

家居服务任务涉及刀具、热源、水、电器和人体周边环境，因此必须保留硬边界：

- PrimitiveTool handler 不允许在线自动改写
- CognitiveSkill 不能绕过 sandbox
- `candidate` 技能不能进入真实执行
- 涉及刀具、热源、电器的技能需要更高验证门槛
- 所有 deployed skill 必须可回滚
- 用户偏好和安全禁忌必须进入 KG，并在规划时强制检索

## 当前推荐决策

短期不推翻现有 `todo_list` 架构。

当前最合理的演进方向是：

```text
保留 todo_list 作为大脑到小脑之间的规划契约
把现有低级 skills 重命名或标注为 PrimitiveTool
新增 CognitiveSkill 作为大脑可学习的高层过程
用 KG 管理对象语义、约束、索引和证据
用 Scene Graph 管理对象实例、位置和当前状态
用 TaskGraph 承载每次任务的临时工作记忆
用 sandbox/evaluator 审计所有展开结果
用离线验证门控更新技能库
后续再把 todo_list 编译成行为树执行
```
