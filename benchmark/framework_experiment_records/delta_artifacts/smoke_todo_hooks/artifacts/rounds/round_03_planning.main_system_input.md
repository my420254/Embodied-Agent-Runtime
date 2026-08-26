# Round 3 planning.main_system Input

## Message 1: system

任务：生成 DELTA 官方原生动作计划。
只输出 JSON；不要解释，不要输出 Markdown。

原始任务：


规划目标：
Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.

机器人状态：
- 位置：living_room
- 手持：空
- 完整状态：{"robot_location":"living_room","robot_holding":"空","delta_room_neighbors":{"bathroom_1":["corridor_2"],"bathroom_2":["corridor_3"],"bedroom_1":["corridor_2"],"bedroom_2":["corridor_3"],"corridor_1":["lobby","corridor_3"],"corridor_2":["bathroom_1","bedroom_1","corridor_3"],"corridor_3":["corridor_1","corridor_2","bathroom_2","bedroom_2","kitchen","living_room"],"dining_room":["kitchen","living_room"],"kitchen":["corridor_3","dining_room"],"living_room":["corridor_3","dining_room"],"lobby":["corridor_1"]},"domain":"dining","delta_initial_predicates":["item_is_dining_table dining_table","item_pickable plate","item_accessible plate","item_pickable fork","item_accessible fork","item_pickable knife","item_accessible knife","item_pickable spoon","item_accessible spoon","item_pickable glass","item_accessible glass","item_pickable flower","item_accessible flower"]}

当前环境 JSON：
{"dining_table":{"direct_parent":"dining_room","direct_relation":"inside","type":"receptacle","states":{},"properties":["delta_accessible:true","delta_predicate:item_is_dining_table"],"is_container":true,"full_path":["dining_room"]},"dining_room":{"direct_parent":"未知环境","direct_relation":null,"type":"room","states":{},"properties":[],"is_container":false,"full_path":[]},"plate":{"direct_parent":"bedroom_2","direct_relation":"inside","type":null,"states":{},"properties":["delta_accessible:true","delta_affordance:drop","delta_affordance:pick","delta_affordance:place_on","delta_predicate:item_pickable","delta_predicate:item_accessible"],"is_container":false,"full_path":["bedroom_2"]},"bedroom_2":{"direct_parent":"未知环境","direct_relation":null,"type":"room","states":{},"properties":[],"is_container":false,"full_path":[]},"fork":{"direct_parent":"kitchen","direct_relation":"inside","type":null,"states":{},"properties":["delta_accessible:true","delta_affordance:drop","delta_affordance:pick","delta_affordance:place_on","delta_predicate:item_pickable","delta_predicate:item_accessible"],"is_container":false,"full_path":["kitchen"]},"kitchen":{"direct_parent":"未知环境","direct_relation":null,"type":"room","states":{},"properties":[],"is_container":false,"full_path":[]},"knife":{"direct_parent":"kitchen","direct_relation":"inside","type":null,"states":{},"properties":["delta_accessible:true","delta_affordance:drop","delta_affordance:pick","delta_affordance:place_on","delta_predicate:item_pickable","delta_predicate:item_accessible"],"is_container":false,"full_path":["kitchen"]},"spoon":{"direct_parent":"kitchen","direct_relation":"inside","type":null,"states":{},"properties":["delta_accessible:true","delta_affordance:drop","delta_affordance:pick","delta_affordance:place_on","delta_predicate:item_pickable","delta_predicate:item_accessible"],"is_container":false,"full_path":["kitchen"]},"glass":{"direct_parent":"bedroom_1","direct_relation":"inside","type":null,"states":{},"properties":["delta_accessible:true","delta_affordance:drop","delta_affordance:pick","delta_affordance:place_on","delta_predicate:item_pickable","delta_predicate:item_accessible"],"is_container":false,"full_path":["bedroom_1"]},"bedroom_1":{"direct_parent":"未知环境","direct_relation":null,"type":"room","states":{},"properties":[],"is_container":false,"full_path":[]},"flower":{"direct_parent":"lobby","direct_relation":"inside","type":null,"states":{},"properties":["delta_accessible:true","delta_affordance:drop","delta_affordance:pick","delta_affordance:place_on","delta_predicate:item_pickable","delta_predicate:item_accessible"],"is_container":false,"full_path":["lobby"]},"lobby":{"direct_parent":"未知环境","direct_relation":null,"type":"room","states":{},"properties":[],"is_container":false,"full_path":[]},"living_room":{"direct_parent":"未知环境","direct_relation":null,"type":"room","states":{},"properties":[],"is_container":false,"full_path":[]},"bathroom_1":{"direct_parent":"未知环境","direct_relation":null,"type":"room","states":{},"properties":[],"is_container":false,"full_path":[]},"bathroom_2":{"direct_parent":"未知环境","direct_relation":null,"type":"room","states":{},"properties":[],"is_container":false,"full_path":[]},"corridor_1":{"direct_parent":"未知环境","direct_relation":null,"type":"room","states":{},"properties":[],"is_container":false,"full_path":[]},"corridor_2":{"direct_parent":"未知环境","direct_relation":null,"type":"room","states":{},"properties":[],"is_container":false,"full_path":[]},"corridor_3":{"direct_parent":"未知环境","direct_relation":null,"type":"room","states":{},"properties":[],"is_container":false,"full_path":[]}}

目标物品当前位置（来自官方场景图；pick 的 room 必须与此表一致，只能从物体当前所在房间拾取）：
- dining_table: dining_room
- flower: lobby
- fork: kitchen
- glass: bedroom_1
- knife: kitchen
- plate: bedroom_2
- spoon: kitchen

任务相关环境事实：
[{"name":"bathroom_1","direct_parent":"未知环境","full_path":[],"states":{},"type":"room","is_container":false},{"name":"bathroom_2","direct_parent":"未知环境","full_path":[],"states":{},"type":"room","is_container":false},{"name":"bedroom_1","direct_parent":"未知环境","full_path":[],"states":{},"type":"room","is_container":false},{"name":"bedroom_2","direct_parent":"未知环境","full_path":[],"states":{},"type":"room","is_container":false},{"name":"corridor_1","direct_parent":"未知环境","full_path":[],"states":{},"type":"room","is_container":false},{"name":"corridor_2","direct_parent":"未知环境","full_path":[],"states":{},"type":"room","is_container":false},{"name":"corridor_3","direct_parent":"未知环境","full_path":[],"states":{},"type":"room","is_container":false},{"name":"dining_room","direct_parent":"未知环境","full_path":[],"states":{},"type":"room","is_container":false},{"name":"dining_table","direct_parent":"dining_room","full_path":["dining_room"],"states":{},"type":"receptacle","is_container":true},{"name":"flower","direct_parent":"lobby","full_path":["lobby"],"states":{},"type":null,"is_container":false},{"name":"fork","direct_parent":"kitchen","full_path":["kitchen"],"states":{},"type":null,"is_container":false},{"name":"glass","direct_parent":"bedroom_1","full_path":["bedroom_1"],"states":{},"type":null,"is_container":false},{"name":"kitchen","direct_parent":"未知环境","full_path":[],"states":{},"type":"room","is_container":false},{"name":"knife","direct_parent":"kitchen","full_path":["kitchen"],"states":{},"type":null,"is_container":false},{"name":"living_room","direct_parent":"未知环境","full_path":[],"states":{},"type":"room","is_container":false},{"name":"lobby","direct_parent":"未知环境","full_path":[],"states":{},"type":"room","is_container":false},{"name":"plate","direct_parent":"bedroom_2","full_path":["bedroom_2"],"states":{},"type":null,"is_container":false},{"name":"spoon","direct_parent":"kitchen","full_path":["kitchen"],"states":{},"type":null,"is_container":false}]

任务上下文：
{
  "dataset": "delta",
  "task_name": "dining:allensville:episode-01",
  "domain": "dining",
  "instruction": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.",
  "task_source": "delta_data_example_py",
  "environment_source": "delta_data_scene_graph_py",
  "scene_graph_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/delta/initial_envs/allensville.json",
  "delta_add_obj_types": [],
  "delta_env_state_predicates": [
    "item_on(<item_1>, <item_2>): <item_1> is on <item_2>.",
    "item_is_dining_table(<item>): <item> is dining_table."
  ],
  "delta_initial_predicates": [
    "item_is_dining_table dining_table",
    "item_pickable plate",
    "item_accessible plate",
    "item_pickable fork",
    "item_accessible fork",
    "item_pickable knife",
    "item_accessible knife",
    "item_pickable spoon",
    "item_accessible spoon",
    "item_pickable glass",
    "item_accessible glass",
    "item_pickable flower",
    "item_accessible flower"
  ],
  "delta_room_neighbors": {
    "bathroom_1": [
      "corridor_2"
    ],
    "bathroom_2": [
      "corridor_3"
    ],
    "bedroom_1": [
      "corridor_2"
    ],
    "bedroom_2": [
      "corridor_3"
    ],
    "corridor_1": [
      "lobby",
      "corridor_3"
    ],
    "corridor_2": [
      "bathroom_1",
      "bedroom_1",
      "corridor_3"
    ],
    "corridor_3": [
      "corridor_1",
      "corridor_2",
      "bathroom_2",
      "bedroom_2",
      "kitchen",
      "living_room"
    ],
    "dining_room": [
      "kitchen",
      "living_room"
    ],
    "kitchen": [
      "corridor_3",
      "dining_room"
    ],
    "living_room": [
      "corridor_3",
      "dining_room"
    ],
    "lobby": [
      "corridor_1"
    ]
  },
  "delta_accessible_items": [
    "psu",
    "sink_1",
    "mop",
    "gpu",
    "sink_2",
    "mainboard",
    "glass",
    "shelf",
    "book",
    "cpu",
    "rotting_apple",
    "plate",
    "lamp",
    "fridge_1",
    "fridge_2",
    "ssd",
    "cola_can",
    "dining_table",
    "knife",
    "fork",
    "spoon",
    "microwave",
    "oven",
    "rubbish_bin",
    "fridge_3",
    "desk",
    "bowl_2",
    "bowl_3",
    "robot_hub",
    "ram",
    "banana_peel",
    "flower",
    "locker",
    "paper"
  ],
  "loadable_containers": [
    {
      "name": "shelf",
      "room": "bedroom_1",
      "is_loaded": true,
      "contents": [
        "book"
      ],
      "affordances": [
        "drop",
        "load",
        "pick",
        "unload"
      ]
    },
    {
      "name": "locker",
      "room": "lobby",
      "is_loaded": true,
      "contents": [
        "paper"
      ],
      "affordances": [
        "drop",
        "load",
        "pick",
        "unload"
      ]
    }
  ],
  "task_environment_mode": "understanding_pruned",
  "available_entities": [
    "banana_peel",
    "bathroom_1",
    "bathroom_2",
    "bed_1",
    "bed_2",
    "bedroom_1",
    "bedroom_2",
    "book",
    "bowl_2",
    "bowl_3",
    "chair_1",
    "chair_2",
    "chair_3",
    "chair_4",
    "chair_5",
    "clock",
    "cola_can",
    "corridor_1",
    "corridor_2",
    "corridor_3",
    "couch",
    "cpu",
    "desk",
    "dining_room",
    "dining_table",
    "flower",
    "fork",
    "fridge_1",
    "fridge_2",
    "fridge_3",
    "glass",
    "gpu",
    "kitchen",
    "knife",
    "lamp",
    "living_room",
    "lobby",
    "locker",
    "mainboard",
    "microwave",
    "mop",
    "oven",
    "paper",
    "plant_1",
    "plant_2",
    "plate",
    "psu",
    "ram",
    "robot_hub",
    "rotting_apple",
    "rubbish_bin",
    "shelf",
    "sink_1",
    "sink_2",
    "spoon",
    "ssd",
    "toilet_1",
    "toilet_2"
  ]
}

新增对象类型（若有）：
（无）


房间邻接表（goto 的 from/to 之间必须在此表中存在可达路径；框架会自动展开为走廊逐跳）：
- bathroom_1: corridor_2
- bathroom_2: corridor_3
- bedroom_1: corridor_2
- bedroom_2: corridor_3
- corridor_1: corridor_3, lobby
- corridor_2: bathroom_1, bedroom_1, corridor_3
- corridor_3: bathroom_2, bedroom_2, corridor_1, corridor_2, kitchen, living_room
- dining_room: kitchen, living_room
- kitchen: corridor_3, dining_room
- living_room: corridor_3, dining_room
- lobby: corridor_1


理解层实体选择：
{
  "targets": {
    "primary": [
      "dining_table"
    ],
    "alternatives": []
  },
  "tools": {
    "primary": [
      "plate",
      "fork",
      "knife",
      "spoon",
      "glass"
    ],
    "alternatives": []
  },
  "receptacles": {
    "primary": [
      "flower"
    ],
    "alternatives": []
  }
}

可用动作与 skill 契约：
<available_skills>
---
name: goto
description: DELTA official executable goto action.
---

## 参数
| 参数名 | 类型 | 含义 |
| --- | --- | --- |
| agent | string | DELTA PDDL agent，固定为 `robot`。 |
| room_1 | string | 机器人当前所在的 DELTA 房间名。 |
| room_2 | string | 机器人要移动到的 DELTA 房间名。 |

## 前提条件
- 必须使用 DELTA PDDL 签名 `goto(robot, room_1, room_2)` 和下面的同签名 JSON 对象。
- 当前 DELTA 场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- `agent` 必须是 `robot`。
- `room_1` 和 `room_2` 都必须是当前 DELTA 场景中的真实房间。
- `room_1` 必须等于机器人当前所在房间。
- `room_1` 与 `room_2` 之间必须在 `delta_room_neighbors`（任务上下文中的房间邻接表）里存在可达路径。
- 框架会按公开场景图邻接关系自动把房间级 `goto` 展开为具体走廊逐跳，模型不需要输出中间走廊步。
- 如果机器人已经在目标房间，不要输出同房间 `goto`。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，机器人位置从 `room_1` 更新为 `room_2`。

## 输出格式
在 DELTA 原生动作 JSON 数组中使用这个动作对象：

```json
{"action":"goto","agent":"robot","room_1":"<current_room>","room_2":"<destination_room>"}
```

- 尖括号中的值只是占位符，真实输出必须替换为当前环境中的精确房间名。
- 不要输出框架包装字段、公共 todo_list 字段或非 DELTA 动作名。


---
name: pick
description: DELTA official executable pick action.
---

## 参数
| 参数名 | 类型 | 含义 |
| --- | --- | --- |
| agent | string | DELTA PDDL agent，固定为 `robot`。 |
| item | string | 当前环境中的普通可拾取物品实体名。 |
| room | string | `item` 所在的 DELTA 房间名。 |

## 前提条件
- 必须使用 DELTA PDDL 签名 `pick(robot, item, room)` 和下面的同签名 JSON 对象。
- 当前 DELTA 场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- `agent` 必须是 `robot`。
- `item` 必须是当前环境中的真实实体，并满足可访问、可拾取条件。
- `room` 必须是当前 DELTA 场景中的真实房间，并且必须是 `item` 所在房间。
- 机器人必须已经在 `room`，且手中没有物品。
- 普通物品使用 `pick`；如果任务需要拾取 empty loadable container，应使用 `pick_loadable`。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，机器人持有 `item`，`item` 不再直接位于 `room`。

## 输出格式
在 DELTA 原生动作 JSON 数组中使用这个动作对象：

```json
{"action":"pick","agent":"robot","item":"<item_entity>","room":"<item_room>"}
```

- 尖括号中的值只是占位符，真实输出必须替换为当前环境中的精确实体名。
- 不要输出框架包装字段、公共 todo_list 字段或非 DELTA 动作名。


---
name: place_on
description: DELTA official executable place_on action.
---

## 参数
| 参数名 | 类型 | 含义 |
| --- | --- | --- |
| agent | string | DELTA PDDL agent，固定为 `robot`。 |
| item_1 | string | 当前机器人持有的 DELTA 物品实体名。 |
| item_2 | string | 当前环境中的 dining_table/surface 实体名。 |
| room | string | `item_2` 所在的 DELTA 房间名。 |

## 前提条件
- 必须使用 DELTA PDDL 签名 `place_on(robot, item_1, item_2, room)` 和下面的同签名 JSON 对象。
- 当前 DELTA 场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- `agent` 必须是 `robot`。
- `item_1` 必须是当前环境中的真实实体，且机器人已经持有它。
- `item_2` 必须是当前环境中的真实实体，且满足 DELTA dining-table/surface 谓词；不要把房间名当作 `item_2`。
- `room` 必须是当前 DELTA 场景中的真实房间，并且必须是 `item_2` 所在房间。
- 机器人必须已经在 `room`；如果 `item_1` 不在机器人手中，`place_on` 必须被 sandbox 拒绝。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，`item_1` 位于 `item_2` 上，机器人手变为空；其他位置变化只以 handler.apply(...) 的实际更新为准。

## 输出格式
在 DELTA 原生动作 JSON 数组中使用这个动作对象：

```json
{"action":"place_on","agent":"robot","item_1":"<held_item_entity>","item_2":"<dining_table_entity>","room":"<surface_room>"}
```

- 尖括号中的值只是占位符，真实输出必须替换为当前环境中的精确实体名。
- 不要输出框架包装字段、公共 todo_list 字段或非 DELTA 动作名。

</available_skills>

历史失败反馈：
暂无相关拦截记录

规划边界：
1. 只使用 <available_skills> 中列出的动作。
2. 动作参数、前置条件、状态依赖和效果只以对应 skill 契约为准。
3. 只引用当前环境、任务上下文、任务相关环境事实或理解层结果中出现的实体/房间/对象名。
4. 如果已有修复反馈或修复状态，只生成尚未验证的后续动作。
5. 机器人一次只能携带一个物品；拿取下一个物品前，必须先把当前手持物品 drop 到目标位置。
6. 执行需要多个物品位于同一房间的复合动作（如 assemble）之前，必须先通过 drop 把全部相关物品放到该动作要求的房间；复合动作只会因为物品未就位被拒绝。

输出格式：
直接输出 DELTA 官方动作 JSON 数组。
每个元素包含 action 和该动作 skill 契约要求的参数字段；不要输出任何框架包装字段。
如果任务已经完成，返回 []。

## Message 2: human

开始规划。
