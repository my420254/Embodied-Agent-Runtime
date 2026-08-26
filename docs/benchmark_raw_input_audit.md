# Benchmark Raw Input Audit

本文档用于核对 framework 路径当前到底把什么作为模型输入来源。核心边界：

- 不允许把论文 action sequencing 阶段生成的中间提示词、摘要、目标展开文本当作输入。
- 允许使用数据集原始任务字段、原始初始环境、以及我们从原始字段转换出的 `scene_override` / `task_environment_facts`。
- 仍然会使用我们自己的 prompt 模板调用模型；被丢弃的是论文仓库预生成的 `llm_prompt` 字段，不是 OurAgent 的 prompt。

## 当前流程

1. Benchmark adapter 读取原始数据集文件，生成 `case_input` 和 `reference`。
2. `task_environment.py` 从原始初始环境构造 OurAgent scene：
   - `scene_override`: 完整 benchmark-local 场景，只作为事实源和 understanding 实体目录。
   - `understanding_environment_facts`: 从完整场景转换出的全量环境事实，给 understanding 读取。
3. understanding 使用我们自己的 `config/prompts.json` 或 benchmark-local `config/prompts.json`，输入是原始任务字段、raw goal 字段、全量环境事实，输出 `structured_task`；其中 `required_item_names` / `relevant_item_names` 只能是实体名称。
4. planning 入口调用 `build_task_environment`：用 understanding 选出的实体名称到 `scene_override` 里查闭包，生成 `task_environment_override`。
5. sandbox 使用同一份 `sandbox_environment_override` 作为可执行初始环境；不会再绕过裁剪结果直接使用 full scene。
6. final-state inference 是 understanding feature：从公平输入里推断 `structured_task.goal_state`；如果 raw goal 已经在数据集里，就作为原始任务目标输入 understanding。
7. planning 使用我们自己的 planning prompt，把 `structured_task`、机器人状态、裁剪环境事实、技能契约渲染成提示词，再让模型输出动作。

因此，`framework 路径丢弃 EAI llm_prompt` 的含义是：不使用 EAI 论文 action sequencing prompt cache 里那段已经整合了对象、初始状态、目标状态、动作格式说明的长 prompt。OurAgent 仍然会构造自己的 prompt，只是 prompt 内容来自原始数据和我们的适配器。

## 环境闭包规则

- `scene_override` 是完整世界，只给 understanding 看，用来从全量环境中识别任务实体。
- understanding 输出的 `required_item_names` / `relevant_item_names` 必须只包含实体名，不包含状态、坐标或动作。
- `build_task_environment` 是 planning 侧模块：它拿这些实体名回查完整世界，补齐父路径、直接父节点、以及被明确选中容器的子树，返回 `task_environment_override`。
- `sandbox_environment_override` 与 `task_environment_override` 同源，sandbox 用它作为初始可执行环境，skill 只在这个任务闭包环境里修改状态。
- 如果 understanding 没有输出任何可匹配实体，裁剪环境会为空；这会暴露实体抽取失败，而不是悄悄退回 full scene。

## 一眼结论

| 数据集 | 当前环境来源 | 当前任务来源 | 当前是否使用论文中间 prompt | 需要确认的问题 |
|---|---|---|---|---|
| DELTA | `/data/zmy/DELTA/data/scene_graph.py` | `data/example.py` 的 `goal` 自然语言 | 否 | `delta_env_state` 是原始领域说明，当前没有喂给模型；是否应作为原始任务补充输入需要确认 |
| EAI BEHAVIOR | raw `behavior_bddl_info.initial_condition` + `name_category` | raw identifier humanized task name + raw `goal_condition` | 否 | `goal_option` 是巨大展开参考，只保留在 reference/eval，不进入 framework case input；`required_item_names` 必须输出 `candle.n.01_1` 这类可执行环境实体名，不允许 `candle_0` prompt 别名 |
| EAI VirtualHome | raw PDDL `:objects` + `:init` | raw task name / id2task + raw PDDL `:goal` | 否 | `:goal` 可用于 understanding 推断 `structured_task.goal_state`，但不直接作为 planning 动作答案 |
| ReActree WAH | raw `init_graph` nodes/edges/states | raw `nl_instructions` + raw `task_goal` | 否 | `task_goal` 可用于 understanding 推断目标状态；sandbox 仍按裁剪环境和 skill 效果执行 |
| ReActree ALFRED | raw ALFRED task 初始化后的 simulator observation/object metadata | raw annotation `task_desc` + task path metadata | 否 | 环境需要启动 ALFRED simulator 得到初始观测，不来自论文 prompt |

## DELTA 样例

当前模型侧允许字段：

```text
task_id, instruction, profile, domain, scene_name, scene_graph
```

样例 case：

```json
{
  "case_id": "clean:allensville",
  "instruction": "Identify and dispose the possible rubbish (e.g. food residue, drink bottles/cans etc.), mop the floor in living room and kitchen, note that all mops should be clean after mopping each room. The mop should be clean in the end, and the battery should be full.",
  "domain": "clean",
  "scene_name": "allensville",
  "scene_graph_rooms": [
    "bathroom_1",
    "bathroom_2",
    "bedroom_1",
    "bedroom_2",
    "corridor_1",
    "corridor_2",
    "corridor_3",
    "dining_room",
    "kitchen",
    "living_room",
    "lobby"
  ],
  "scene_entity_count_after_conversion": 58
}
```

原始但当前不喂给模型的字段示例：

```json
{
  "delta_env_state_sample": [
    "item_is_mop(<item>): <item> is mop.",
    "item_is_sink(<item>): <item> is sink.",
    "item_is_rubbish_bin(<item>): <item> is rubbish_bin.",
    "item_is_robot_hub(<item>): <item> is robot_hub.",
    "item_disposed(<item>): <item> is disposed."
  ],
  "item_keep_sample_oracle_pruned_only": [
    "sink_1",
    "sink_2",
    "mop",
    "cola_can",
    "banana_peel"
  ],
  "subgoal_pddl_sample_eval_only": [
    "(:goal (item_disposed cola_can))",
    "(:goal (item_disposed banana_peel))"
  ]
}
```

判断：`scene_graph` 是原始环境，合规；`item_keep/subgoal_pddl` 是中间答案或 evaluator 目标，默认不该喂。`delta_env_state` 更像领域谓词说明，不是目标答案，可以讨论是否加入原始输入。

## EAI BEHAVIOR 样例

当前模型侧允许字段：

```text
identifier, task_id, dataset, instruction, raw_initial_condition, raw_goal_condition, name_category, profile, allow_task_name_fallback
```

样例 case：

```json
{
  "case_id": "assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37",
  "instruction": "assembling gift baskets",
  "raw_initial_condition_sample": [
    ["onfloor", "basket.n.01_1", "floor.n.01_1"],
    ["onfloor", "basket.n.01_2", "floor.n.01_1"],
    ["onfloor", "basket.n.01_3", "floor.n.01_1"],
    ["onfloor", "basket.n.01_4", "floor.n.01_1"],
    ["ontop", "candle.n.01_1", "table.n.02_1"],
    ["ontop", "candle.n.01_2", "table.n.02_1"],
    ["ontop", "candle.n.01_3", "table.n.02_1"],
    ["ontop", "candle.n.01_4", "table.n.02_1"]
  ],
  "name_category_sample": {
    "basket.n.01_1": "basket.n.01",
    "basket.n.01_2": "basket.n.01",
    "basket.n.01_3": "basket.n.01",
    "basket.n.01_4": "basket.n.01",
    "floor.n.01_1": "floor.n.01",
    "candle.n.01_1": "candle.n.01",
    "candle.n.01_2": "candle.n.01",
    "candle.n.01_3": "candle.n.01"
  },
  "scene_entity_count_after_conversion": 25,
  "llm_prompt_present_in_framework_case": false
}
```

raw goal 现在作为原始任务目标输入 understanding：

```json
{
  "goal_condition_sample": [
    ["forpairs", "basket.n.01", "-", "basket.n.01", "candle.n.01", "-", "candle.n.01", "inside", "candle.n.01", "basket.n.01"],
    ["forpairs", "basket.n.01", "-", "basket.n.01", "cheese.n.01", "-", "cheese.n.01", "inside", "cheese.n.01", "basket.n.01"],
    ["forpairs", "basket.n.01", "-", "basket.n.01", "cookie.n.01", "-", "cookie.n.01", "inside", "cookie.n.01", "basket.n.01"],
    ["forpairs", "basket.n.01", "-", "basket.n.01", "bow.n.08", "-", "bow.n.08", "inside", "bow.n.08", "basket.n.01"]
  ]
}
```

判断：不使用 `llm_prompt` 是对的；`goal_condition` 是紧凑 raw dataset 目标，允许进入 understanding，用来生成 `structured_task.goal_state`。`goal_option` 虽然来自原始 BEHAVIOR json，但它是把量词目标展开后的巨大候选集合，只保留在 `reference`/官方评测侧，不进入 framework 输入。

## EAI VirtualHome 样例

当前模型侧允许字段：

```text
identifier, task_id, dataset, instruction, pddl_objects, pddl_init, pddl_goal, profile, allow_task_name_fallback
```

样例 case：

```json
{
  "case_id": "384_1",
  "instruction": "Browse internet",
  "pddl_objects_sample": [
    "character",
    "bathroom",
    "home_office",
    "desk",
    "walllamp",
    "mouse",
    "keyboard",
    "powersocket",
    "cpuscreen",
    "doorjamb",
    "computer",
    "chair"
  ],
  "pddl_init_sample": [
    ["obj_inside", "powersocket", "home_office"],
    ["obj_next_to", "cpuscreen", "mousepad"],
    ["obj_next_to", "wall", "powersocket"],
    ["surfaces", "chair"],
    ["obj_next_to", "cpuscreen", "floor"],
    ["movable", "mousepad"],
    ["obj_next_to", "keyboard", "computer"],
    ["obj_next_to", "doorjamb", "walllamp"]
  ],
  "scene_entity_count_after_conversion": 15,
  "llm_prompt_present_in_framework_case": false
}
```

raw PDDL goal 现在作为原始任务目标输入 understanding：

```json
{
  "pddl_goal_sample": [
    ["on", "computer"],
    ["inside", "character", "home_office"],
    ["facing", "character", "computer"],
    ["holds_rh", "character", "mouse"]
  ]
}
```

判断：`:objects` 和 `:init` 是环境；`:goal` 是任务目标，不是环境。现在 `:goal` 进入 understanding，帮助生成最终态；仍不要使用 action sequencing `llm_prompt`。

## ReActree WAH 样例

当前模型侧允许字段：

```text
task_id, identifier, dataset, task_name, instruction, task_goal, init_room, profile
```

样例 case：

```json
{
  "case_id": "0:0",
  "task_name": "prepare_snack",
  "instruction": "Put one cupcake and one apple on the coffee table",
  "init_room": "bedroom",
  "init_graph_node_count": 343,
  "init_graph_edge_count": 595,
  "scene_entity_count_after_conversion": 343
}
```

`init_graph` 样例节点：

```json
[
  {
    "id": 11,
    "category": "Rooms",
    "class_name": "kitchen",
    "properties": [],
    "states": []
  },
  {
    "id": 12,
    "category": "Floor",
    "class_name": "floor",
    "properties": ["SURFACES"],
    "states": []
  }
]
```

raw `task_goal` 当前作为原始任务目标输入 understanding，同时仍给 evaluator/reference 使用：

```json
{
  "task_goal_keys_sample": [
    "on_cupcake_coffeetable",
    "on_apple_coffeetable"
  ]
}
```

判断：`init_graph` 是原始初始环境，合规；`task_goal` 是 ReActree WAH 数据集给出的原始目标条件，当前会进入 understanding，帮助生成 `structured_task.goal_state`，不是论文中间 prompt。

## ReActree ALFRED 样例

当前模型侧允许字段：

```text
task_id, task, repeat_idx, instruction, task_desc, profile
```

样例 case：

```json
{
  "case_id": "pick_heat_then_place_in_recep-PotatoSliced-None-SinkBasin-13__trial_T20190909_115736_122556__ann_0",
  "task": "pick_heat_then_place_in_recep-PotatoSliced-None-SinkBasin-13/trial_T20190909_115736_122556",
  "repeat_idx": 0,
  "instruction": "Place a cooked potato slice in the sink",
  "environment_source": "ALFRED simulator initial observation and object metadata for this raw task"
}
```

判断：ALFRED 的环境不在 split JSON 里直接给完整 scene graph，需要用原始 task 初始化模拟器，然后读取初始 observation / object metadata。这个不是论文 prompt 派生。

## 已确认的 EAI 点

之前说 “EAI VirtualHome 的 `:goal` 只作为 reference/eval，不喂给模型”，这是一个偏严格的实现口径；当前已改成使用 raw dataset goal。

更准确地说：

- `:objects` / `:init` / `initial_condition` 是环境。
- `:goal` / `goal_condition` 是原始数据集目标，进入 understanding，用于生成 `structured_task.goal_state`。
- BEHAVIOR `goal_option` 是展开候选集合，过大且不是必要任务输入，只保留给 reference/eval。
- `llm_prompt` 是论文 action sequencing 阶段拼好的中间 prompt。

当前采用的原则是：允许 raw dataset goal，禁止 paper-generated `llm_prompt`；最终态由 understanding 结果和 benchmark-local raw-goal inference 对齐到 `structured_task.goal_state`。
