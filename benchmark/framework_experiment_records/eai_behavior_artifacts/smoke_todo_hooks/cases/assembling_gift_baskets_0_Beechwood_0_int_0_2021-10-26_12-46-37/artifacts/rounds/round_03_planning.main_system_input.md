# Round 3 planning.main_system Input

## Message 1: system

任务：生成 BEHAVIOR 官方原生动作计划。
只输出 JSON；不要解释，不要输出 Markdown。

原始任务：


规划目标：
Assemble gift baskets by placing one candle, one cheese, one cookie, and one bow inside each basket.

机器人状态：
- 位置：room_floor_living_room_0
- 手持：空
- 完整状态：{"robot_location":"room_floor_living_room_0","robot_holding":"空","robot_hands":{"left":"空","right":"空"},"manipulator_mode":"dual_arm"}

当前环境 JSON：
{"basket_0":{"direct_parent":"room_floor_living_room_0","direct_relation":"onfloor","type":"receptacle","states":{},"properties":[],"is_container":true,"full_path":["behavior_room","behavior_room_anchor","room_floor_living_room_0"]},"behavior_room":{"direct_parent":"未知环境","direct_relation":null,"type":"room","states":{},"properties":[],"is_container":false,"full_path":[]},"behavior_room_anchor":{"direct_parent":"behavior_room","direct_relation":"inside","type":"receptacle","states":{},"properties":[],"is_container":true,"full_path":["behavior_room"]},"room_floor_living_room_0":{"direct_parent":"behavior_room_anchor","direct_relation":"inside","type":"receptacle","states":{},"properties":[],"is_container":true,"full_path":["behavior_room","behavior_room_anchor"]},"basket_1":{"direct_parent":"room_floor_living_room_0","direct_relation":"onfloor","type":"receptacle","states":{},"properties":[],"is_container":true,"full_path":["behavior_room","behavior_room_anchor","room_floor_living_room_0"]},"basket_2":{"direct_parent":"room_floor_living_room_0","direct_relation":"onfloor","type":"receptacle","states":{},"properties":[],"is_container":true,"full_path":["behavior_room","behavior_room_anchor","room_floor_living_room_0"]},"basket_3":{"direct_parent":"room_floor_living_room_0","direct_relation":"onfloor","type":"receptacle","states":{},"properties":[],"is_container":true,"full_path":["behavior_room","behavior_room_anchor","room_floor_living_room_0"]},"candle_0":{"direct_parent":"breakfast_table_13","direct_relation":"ontop","type":null,"states":{},"properties":[],"is_container":false,"full_path":["behavior_room","behavior_room_anchor","breakfast_table_13"]},"breakfast_table_13":{"direct_parent":"behavior_room_anchor","direct_relation":"inside","type":"receptacle","states":{},"properties":[],"is_container":true,"full_path":["behavior_room","behavior_room_anchor"]},"candle_1":{"direct_parent":"breakfast_table_13","direct_relation":"ontop","type":null,"states":{},"properties":[],"is_container":false,"full_path":["behavior_room","behavior_room_anchor","breakfast_table_13"]},"candle_2":{"direct_parent":"breakfast_table_13","direct_relation":"ontop","type":null,"states":{},"properties":[],"is_container":false,"full_path":["behavior_room","behavior_room_anchor","breakfast_table_13"]},"candle_3":{"direct_parent":"breakfast_table_13","direct_relation":"ontop","type":null,"states":{},"properties":[],"is_container":false,"full_path":["behavior_room","behavior_room_anchor","breakfast_table_13"]},"cheese_0":{"direct_parent":"coffee_table_12","direct_relation":"ontop","type":null,"states":{},"properties":[],"is_container":false,"full_path":["behavior_room","behavior_room_anchor","coffee_table_12"]},"coffee_table_12":{"direct_parent":"behavior_room_anchor","direct_relation":"inside","type":"receptacle","states":{},"properties":[],"is_container":true,"full_path":["behavior_room","behavior_room_anchor"]},"cheese_1":{"direct_parent":"coffee_table_12","direct_relation":"ontop","type":null,"states":{},"properties":[],"is_container":false,"full_path":["behavior_room","behavior_room_anchor","coffee_table_12"]},"cheese_2":{"direct_parent":"coffee_table_12","direct_relation":"ontop","type":null,"states":{},"properties":[],"is_container":false,"full_path":["behavior_room","behavior_room_anchor","coffee_table_12"]},"cheese_3":{"direct_parent":"coffee_table_12","direct_relation":"ontop","type":null,"states":{},"properties":[],"is_container":false,"full_path":["behavior_room","behavior_room_anchor","coffee_table_12"]},"cookie_0":{"direct_parent":"breakfast_table_13","direct_relation":"ontop","type":null,"states":{},"properties":[],"is_container":false,"full_path":["behavior_room","behavior_room_anchor","breakfast_table_13"]},"cookie_1":{"direct_parent":"breakfast_table_13","direct_relation":"ontop","type":null,"states":{},"properties":[],"is_container":false,"full_path":["behavior_room","behavior_room_anchor","breakfast_table_13"]},"cookie_2":{"direct_parent":"breakfast_table_13","direct_relation":"ontop","type":null,"states":{},"properties":[],"is_container":false,"full_path":["behavior_room","behavior_room_anchor","breakfast_table_13"]},"cookie_3":{"direct_parent":"breakfast_table_13","direct_relation":"ontop","type":null,"states":{},"properties":[],"is_container":false,"full_path":["behavior_room","behavior_room_anchor","breakfast_table_13"]},"bow_0":{"direct_parent":"coffee_table_12","direct_relation":"ontop","type":null,"states":{},"properties":[],"is_container":false,"full_path":["behavior_room","behavior_room_anchor","coffee_table_12"]},"bow_1":{"direct_parent":"coffee_table_12","direct_relation":"ontop","type":null,"states":{},"properties":[],"is_container":false,"full_path":["behavior_room","behavior_room_anchor","coffee_table_12"]},"bow_2":{"direct_parent":"coffee_table_12","direct_relation":"ontop","type":null,"states":{},"properties":[],"is_container":false,"full_path":["behavior_room","behavior_room_anchor","coffee_table_12"]},"bow_3":{"direct_parent":"coffee_table_12","direct_relation":"ontop","type":null,"states":{},"properties":[],"is_container":false,"full_path":["behavior_room","behavior_room_anchor","coffee_table_12"]}}

任务相关环境事实：
[{"name":"basket_0","direct_parent":"room_floor_living_room_0","full_path":["behavior_room","behavior_room_anchor","room_floor_living_room_0"],"states":{},"type":"receptacle","is_container":true},{"name":"basket_1","direct_parent":"room_floor_living_room_0","full_path":["behavior_room","behavior_room_anchor","room_floor_living_room_0"],"states":{},"type":"receptacle","is_container":true},{"name":"basket_2","direct_parent":"room_floor_living_room_0","full_path":["behavior_room","behavior_room_anchor","room_floor_living_room_0"],"states":{},"type":"receptacle","is_container":true},{"name":"basket_3","direct_parent":"room_floor_living_room_0","full_path":["behavior_room","behavior_room_anchor","room_floor_living_room_0"],"states":{},"type":"receptacle","is_container":true},{"name":"behavior_room","direct_parent":"未知环境","full_path":[],"states":{},"type":"room","is_container":false},{"name":"behavior_room_anchor","direct_parent":"behavior_room","full_path":["behavior_room"],"states":{},"type":"receptacle","is_container":true},{"name":"bow_0","direct_parent":"coffee_table_12","full_path":["behavior_room","behavior_room_anchor","coffee_table_12"],"states":{},"type":null,"is_container":false},{"name":"bow_1","direct_parent":"coffee_table_12","full_path":["behavior_room","behavior_room_anchor","coffee_table_12"],"states":{},"type":null,"is_container":false},{"name":"bow_2","direct_parent":"coffee_table_12","full_path":["behavior_room","behavior_room_anchor","coffee_table_12"],"states":{},"type":null,"is_container":false},{"name":"bow_3","direct_parent":"coffee_table_12","full_path":["behavior_room","behavior_room_anchor","coffee_table_12"],"states":{},"type":null,"is_container":false},{"name":"breakfast_table_13","direct_parent":"behavior_room_anchor","full_path":["behavior_room","behavior_room_anchor"],"states":{},"type":"receptacle","is_container":true},{"name":"candle_0","direct_parent":"breakfast_table_13","full_path":["behavior_room","behavior_room_anchor","breakfast_table_13"],"states":{},"type":null,"is_container":false},{"name":"candle_1","direct_parent":"breakfast_table_13","full_path":["behavior_room","behavior_room_anchor","breakfast_table_13"],"states":{},"type":null,"is_container":false},{"name":"candle_2","direct_parent":"breakfast_table_13","full_path":["behavior_room","behavior_room_anchor","breakfast_table_13"],"states":{},"type":null,"is_container":false},{"name":"candle_3","direct_parent":"breakfast_table_13","full_path":["behavior_room","behavior_room_anchor","breakfast_table_13"],"states":{},"type":null,"is_container":false},{"name":"cheese_0","direct_parent":"coffee_table_12","full_path":["behavior_room","behavior_room_anchor","coffee_table_12"],"states":{},"type":null,"is_container":false},{"name":"cheese_1","direct_parent":"coffee_table_12","full_path":["behavior_room","behavior_room_anchor","coffee_table_12"],"states":{},"type":null,"is_container":false},{"name":"cheese_2","direct_parent":"coffee_table_12","full_path":["behavior_room","behavior_room_anchor","coffee_table_12"],"states":{},"type":null,"is_container":false},{"name":"cheese_3","direct_parent":"coffee_table_12","full_path":["behavior_room","behavior_room_anchor","coffee_table_12"],"states":{},"type":null,"is_container":false},{"name":"coffee_table_12","direct_parent":"behavior_room_anchor","full_path":["behavior_room","behavior_room_anchor"],"states":{},"type":"receptacle","is_container":true},{"name":"cookie_0","direct_parent":"breakfast_table_13","full_path":["behavior_room","behavior_room_anchor","breakfast_table_13"],"states":{},"type":null,"is_container":false},{"name":"cookie_1","direct_parent":"breakfast_table_13","full_path":["behavior_room","behavior_room_anchor","breakfast_table_13"],"states":{},"type":null,"is_container":false},{"name":"cookie_2","direct_parent":"breakfast_table_13","full_path":["behavior_room","behavior_room_anchor","breakfast_table_13"],"states":{},"type":null,"is_container":false},{"name":"cookie_3","direct_parent":"breakfast_table_13","full_path":["behavior_room","behavior_room_anchor","breakfast_table_13"],"states":{},"type":null,"is_container":false},{"name":"room_floor_living_room_0","direct_parent":"behavior_room_anchor","full_path":["behavior_room","behavior_room_anchor"],"states":{},"type":"receptacle","is_container":true}]

任务上下文：
{
  "dataset": "behavior",
  "instruction": "assembling gift baskets",
  "identifier": "assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37",
  "raw_source": "behavior_initial_env_cache",
  "initial_environment_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/eai/behavior/initial_envs/assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37.json",
  "initial_environment_source": "igibson_behavior_native_loader",
  "environment_source": "igibson_behavior_native_loader",
  "raw_goal_condition": [
    [
      "forpairs",
      "basket.n.01",
      "-",
      "basket.n.01",
      "candle.n.01",
      "-",
      "candle.n.01",
      "inside",
      "candle.n.01",
      "basket.n.01"
    ],
    [
      "forpairs",
      "basket.n.01",
      "-",
      "basket.n.01",
      "cheese.n.01",
      "-",
      "cheese.n.01",
      "inside",
      "cheese.n.01",
      "basket.n.01"
    ],
    [
      "forpairs",
      "basket.n.01",
      "-",
      "basket.n.01",
      "cookie.n.01",
      "-",
      "cookie.n.01",
      "inside",
      "cookie.n.01",
      "basket.n.01"
    ],
    [
      "forpairs",
      "basket.n.01",
      "-",
      "basket.n.01",
      "bow.n.08",
      "-",
      "bow.n.08",
      "inside",
      "bow.n.08",
      "basket.n.01"
    ]
  ],
  "raw_goal_clauses": [
    "forpairs basket.n.01 - basket.n.01 candle.n.01 - candle.n.01 inside candle.n.01 basket.n.01",
    "forpairs basket.n.01 - basket.n.01 cheese.n.01 - cheese.n.01 inside cheese.n.01 basket.n.01",
    "forpairs basket.n.01 - basket.n.01 cookie.n.01 - cookie.n.01 inside cookie.n.01 basket.n.01",
    "forpairs basket.n.01 - basket.n.01 bow.n.08 - bow.n.08 inside bow.n.08 basket.n.01"
  ],
  "raw_goal_condition_count": 4,
  "name_category": {
    "basket_0": "basket.n.01",
    "basket_1": "basket.n.01",
    "basket_2": "basket.n.01",
    "basket_3": "basket.n.01",
    "room_floor_living_room_0": "floor.n.01",
    "candle_0": "candle.n.01",
    "candle_1": "candle.n.01",
    "candle_2": "candle.n.01",
    "candle_3": "candle.n.01",
    "cookie_0": "cookie.n.01",
    "cookie_1": "cookie.n.01",
    "cookie_2": "cookie.n.01",
    "cookie_3": "cookie.n.01",
    "cheese_0": "cheese.n.01",
    "cheese_1": "cheese.n.01",
    "cheese_2": "cheese.n.01",
    "cheese_3": "cheese.n.01",
    "bow_0": "bow.n.08",
    "bow_1": "bow.n.08",
    "bow_2": "bow.n.08",
    "bow_3": "bow.n.08",
    "breakfast_table_13": "table.n.02",
    "coffee_table_12": "table.n.02",
    "agent.n.01_1": "agent.n.01"
  },
  "available_entities": [
    "basket_0",
    "basket_1",
    "basket_2",
    "basket_3",
    "behavior_room",
    "behavior_room_anchor",
    "bow_0",
    "bow_1",
    "bow_2",
    "bow_3",
    "breakfast_table_13",
    "candle_0",
    "candle_1",
    "candle_2",
    "candle_3",
    "cheese_0",
    "cheese_1",
    "cheese_2",
    "cheese_3",
    "coffee_table_12",
    "cookie_0",
    "cookie_1",
    "cookie_2",
    "cookie_3",
    "room_floor_living_room_0"
  ]
}

理解层实体选择：
{
  "targets": {
    "primary": [
      "candle_0",
      "candle_1",
      "candle_2",
      "candle_3",
      "cheese_0",
      "cheese_1",
      "cheese_2",
      "cheese_3",
      "cookie_0",
      "cookie_1",
      "cookie_2",
      "cookie_3",
      "bow_0",
      "bow_1",
      "bow_2",
      "bow_3"
    ],
    "alternatives": []
  },
  "tools": {
    "primary": [],
    "alternatives": []
  },
  "receptacles": {
    "primary": [
      "basket_0",
      "basket_1",
      "basket_2",
      "basket_3"
    ],
    "alternatives": []
  }
}

可用动作与 skill 契约：
<available_skills>
---
name: LEFT_GRASP
description: Official BEHAVIOR LEFT_GRASP action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `LEFT_GRASP`。 |
| object | string | 要用左手抓取的 BEHAVIOR 场景对象。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标物体必须可达，并且对应手或携带槽位必须可用。
- 如果 benchmark 使用多只手，必须依据各只手的占用状态判断，而不是假设只有一个抓手。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标物体会进入对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "LEFT_GRASP", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: RIGHT_GRASP
description: Official BEHAVIOR RIGHT_GRASP action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `RIGHT_GRASP`。 |
| object | string | 要用右手抓取的 BEHAVIOR 场景对象。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标物体必须可达，并且对应手或携带槽位必须可用。
- 如果 benchmark 使用多只手，必须依据各只手的占用状态判断，而不是假设只有一个抓手。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标物体会进入对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "RIGHT_GRASP", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: LEFT_PLACE_ONTOP
description: Official BEHAVIOR LEFT_PLACE_ONTOP action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `LEFT_PLACE_ONTOP`。 |
| object | string | 目标位置、目标容器或目标支撑面；待放置或待转移内容物的源对象由当前左/右手状态决定。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- 如果目标位置是容器类对象，则其开闭状态和容量约束必须满足 handler 的校验规则。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "LEFT_PLACE_ONTOP", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: RIGHT_PLACE_ONTOP
description: Official BEHAVIOR RIGHT_PLACE_ONTOP action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `RIGHT_PLACE_ONTOP`。 |
| object | string | 目标位置、目标容器或目标支撑面；待放置或待转移内容物的源对象由当前左/右手状态决定。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- 如果目标位置是容器类对象，则其开闭状态和容量约束必须满足 handler 的校验规则。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "RIGHT_PLACE_ONTOP", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: LEFT_PLACE_INSIDE
description: Official BEHAVIOR LEFT_PLACE_INSIDE action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `LEFT_PLACE_INSIDE`。 |
| object | string | 目标位置、目标容器或目标支撑面；待放置或待转移内容物的源对象由当前左/右手状态决定。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- 如果目标位置是容器类对象，则其开闭状态和容量约束必须满足 handler 的校验规则。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "LEFT_PLACE_INSIDE", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: RIGHT_PLACE_INSIDE
description: Official BEHAVIOR RIGHT_PLACE_INSIDE action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `RIGHT_PLACE_INSIDE`。 |
| object | string | 目标位置、目标容器或目标支撑面；待放置或待转移内容物的源对象由当前左/右手状态决定。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- 如果目标位置是容器类对象，则其开闭状态和容量约束必须满足 handler 的校验规则。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "RIGHT_PLACE_INSIDE", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: RIGHT_RELEASE
description: Official BEHAVIOR RIGHT_RELEASE action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `RIGHT_RELEASE`。 |
| object | string | 右手当前持有、准备释放的 BEHAVIOR 场景对象。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- 如果目标位置是容器类对象，则其开闭状态和容量约束必须满足 handler 的校验规则。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "RIGHT_RELEASE", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: LEFT_RELEASE
description: Official BEHAVIOR LEFT_RELEASE action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `LEFT_RELEASE`。 |
| object | string | 左手当前持有、准备释放的 BEHAVIOR 场景对象。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- 如果目标位置是容器类对象，则其开闭状态和容量约束必须满足 handler 的校验规则。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "LEFT_RELEASE", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: OPEN
description: Official BEHAVIOR OPEN action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `OPEN`。 |
| object | string | 要打开的 BEHAVIOR 容器或可开合对象。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须支持当前请求的状态切换。
- 如果 benchmark 区分 open/close 或 on/off 的先决条件，则以 `handler.validate(...)` 的检查为准。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "OPEN", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: CLOSE
description: Official BEHAVIOR CLOSE action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `CLOSE`。 |
| object | string | 要关闭的 BEHAVIOR 容器或可开合对象。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须支持当前请求的状态切换。
- 如果 benchmark 区分 open/close 或 on/off 的先决条件，则以 `handler.validate(...)` 的检查为准。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "CLOSE", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: COOK
description: Official BEHAVIOR COOK action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `COOK`。 |
| object | string | 要烹饪的 BEHAVIOR 场景对象。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象以及任何依赖的支持状态，必须已经满足 benchmark-local handler 的校验。
- 不要假设隐藏设备、隐藏工具或隐藏容器；只依赖当前场景状态和已验证动作。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，会更新相关状态标志，例如 cooked、frozen、heated、cooled、charged 或 assembled。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "COOK", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: CLEAN
description: Official BEHAVIOR CLEAN action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `CLEAN`。 |
| object | string | 要清洁的 BEHAVIOR 场景对象。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 所需工具、液体状态或清洁装置状态，必须已经满足 handler 的校验规则。
- 不要假设工具会自动变湿、变干净或自动可用；只有已验证步骤造成的状态变化才有效。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，会按 handler 约定更新清洁、浸湿或相关状态标志。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "CLEAN", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: FREEZE
description: Official BEHAVIOR FREEZE action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `FREEZE`。 |
| object | string | 要冷冻的 BEHAVIOR 场景对象。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象以及任何依赖的支持状态，必须已经满足 benchmark-local handler 的校验。
- 不要假设隐藏设备、隐藏工具或隐藏容器；只依赖当前场景状态和已验证动作。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，会更新相关状态标志，例如 cooked、frozen、heated、cooled、charged 或 assembled。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "FREEZE", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: UNFREEZE
description: Official BEHAVIOR UNFREEZE action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `UNFREEZE`。 |
| object | string | 要解冻的 BEHAVIOR 场景对象。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象以及任何依赖的支持状态，必须已经满足 benchmark-local handler 的校验。
- 不要假设隐藏设备、隐藏工具或隐藏容器；只依赖当前场景状态和已验证动作。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，会更新相关状态标志，例如 cooked、frozen、heated、cooled、charged 或 assembled。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "UNFREEZE", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: SLICE
description: Official BEHAVIOR SLICE action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `SLICE`。 |
| object | string | 要切分的 BEHAVIOR 场景对象。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 任何所需工具、支撑平面或放置前提，都必须已由更早的已验证步骤满足。
- 如果 benchmark 会生成切片后的 part 对象，则后续必须在 handler 要求时改用这些 part 对象。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，会更新切片状态，并可能生成新的 part 对象或改变后续可用的目标对象名。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "SLICE", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: SOAK
description: Official BEHAVIOR SOAK action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `SOAK`。 |
| object | string | 要浸湿的 BEHAVIOR 场景对象。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 所需工具、液体状态或清洁装置状态，必须已经满足 handler 的校验规则。
- 不要假设工具会自动变湿、变干净或自动可用；只有已验证步骤造成的状态变化才有效。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，会按 handler 约定更新清洁、浸湿或相关状态标志。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "SOAK", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: DRY
description: Official BEHAVIOR DRY action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `DRY`。 |
| object | string | 要弄干的 BEHAVIOR 场景对象。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 所需工具、液体状态或清洁装置状态，必须已经满足 handler 的校验规则。
- 不要假设工具会自动变湿、变干净或自动可用；只有已验证步骤造成的状态变化才有效。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，会按 handler 约定更新清洁、浸湿或相关状态标志。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "DRY", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: TOGGLE_ON
description: Official BEHAVIOR TOGGLE_ON action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `TOGGLE_ON`。 |
| object | string | 要打开电源或开关的 BEHAVIOR 设备对象。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须支持当前请求的状态切换。
- 如果 benchmark 区分 open/close 或 on/off 的先决条件，则以 `handler.validate(...)` 的检查为准。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "TOGGLE_ON", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: TOGGLE_OFF
description: Official BEHAVIOR TOGGLE_OFF action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `TOGGLE_OFF`。 |
| object | string | 要关闭电源或开关的 BEHAVIOR 设备对象。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须支持当前请求的状态切换。
- 如果 benchmark 区分 open/close 或 on/off 的先决条件，则以 `handler.validate(...)` 的检查为准。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "TOGGLE_OFF", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: LEFT_PLACE_NEXTTO
description: Official BEHAVIOR LEFT_PLACE_NEXTTO action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `LEFT_PLACE_NEXTTO`。 |
| object | string | 目标位置、目标容器或目标支撑面；待放置或待转移内容物的源对象由当前左/右手状态决定。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- 如果目标位置是容器类对象，则其开闭状态和容量约束必须满足 handler 的校验规则。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "LEFT_PLACE_NEXTTO", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: RIGHT_PLACE_NEXTTO
description: Official BEHAVIOR RIGHT_PLACE_NEXTTO action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `RIGHT_PLACE_NEXTTO`。 |
| object | string | 目标位置、目标容器或目标支撑面；待放置或待转移内容物的源对象由当前左/右手状态决定。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- 如果目标位置是容器类对象，则其开闭状态和容量约束必须满足 handler 的校验规则。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "RIGHT_PLACE_NEXTTO", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: LEFT_TRANSFER_CONTENTS_INSIDE
description: Official BEHAVIOR LEFT_TRANSFER_CONTENTS_INSIDE action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `LEFT_TRANSFER_CONTENTS_INSIDE`。 |
| object | string | 目标位置、目标容器或目标支撑面；待放置或待转移内容物的源对象由当前左/右手状态决定。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- 如果目标位置是容器类对象，则其开闭状态和容量约束必须满足 handler 的校验规则。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "LEFT_TRANSFER_CONTENTS_INSIDE", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: RIGHT_TRANSFER_CONTENTS_INSIDE
description: Official BEHAVIOR RIGHT_TRANSFER_CONTENTS_INSIDE action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `RIGHT_TRANSFER_CONTENTS_INSIDE`。 |
| object | string | 目标位置、目标容器或目标支撑面；待放置或待转移内容物的源对象由当前左/右手状态决定。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- 如果目标位置是容器类对象，则其开闭状态和容量约束必须满足 handler 的校验规则。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "RIGHT_TRANSFER_CONTENTS_INSIDE", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: LEFT_TRANSFER_CONTENTS_ONTOP
description: Official BEHAVIOR LEFT_TRANSFER_CONTENTS_ONTOP action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `LEFT_TRANSFER_CONTENTS_ONTOP`。 |
| object | string | 目标位置、目标容器或目标支撑面；待放置或待转移内容物的源对象由当前左/右手状态决定。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- 如果目标位置是容器类对象，则其开闭状态和容量约束必须满足 handler 的校验规则。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "LEFT_TRANSFER_CONTENTS_ONTOP", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: RIGHT_TRANSFER_CONTENTS_ONTOP
description: Official BEHAVIOR RIGHT_TRANSFER_CONTENTS_ONTOP action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `RIGHT_TRANSFER_CONTENTS_ONTOP`。 |
| object | string | 目标位置、目标容器或目标支撑面；待放置或待转移内容物的源对象由当前左/右手状态决定。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- 如果目标位置是容器类对象，则其开闭状态和容量约束必须满足 handler 的校验规则。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "RIGHT_TRANSFER_CONTENTS_ONTOP", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: LEFT_PLACE_NEXTTO_ONTOP
description: Official BEHAVIOR LEFT_PLACE_NEXTTO_ONTOP action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `LEFT_PLACE_NEXTTO_ONTOP`。 |
| object | string | 目标位置、目标容器或目标支撑面；待放置或待转移内容物的源对象由当前左/右手状态决定。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- 如果目标位置是容器类对象，则其开闭状态和容量约束必须满足 handler 的校验规则。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "LEFT_PLACE_NEXTTO_ONTOP", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: RIGHT_PLACE_NEXTTO_ONTOP
description: Official BEHAVIOR RIGHT_PLACE_NEXTTO_ONTOP action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `RIGHT_PLACE_NEXTTO_ONTOP`。 |
| object | string | 目标位置、目标容器或目标支撑面；待放置或待转移内容物的源对象由当前左/右手状态决定。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- 如果目标位置是容器类对象，则其开闭状态和容量约束必须满足 handler 的校验规则。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "RIGHT_PLACE_NEXTTO_ONTOP", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: LEFT_PLACE_UNDER
description: Official BEHAVIOR LEFT_PLACE_UNDER action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `LEFT_PLACE_UNDER`。 |
| object | string | 目标位置、目标容器或目标支撑面；待放置或待转移内容物的源对象由当前左/右手状态决定。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- 如果目标位置是容器类对象，则其开闭状态和容量约束必须满足 handler 的校验规则。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "LEFT_PLACE_UNDER", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。


---
name: RIGHT_PLACE_UNDER
description: Official BEHAVIOR RIGHT_PLACE_UNDER action.
---

## 参数
planning、handler 和官方导出均使用 BEHAVIOR 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `RIGHT_PLACE_UNDER`。 |
| object | string | 目标位置、目标容器或目标支撑面；待放置或待转移内容物的源对象由当前左/右手状态决定。 |
## 前提条件
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- 如果目标位置是容器类对象，则其开闭状态和容量约束必须满足 handler 的校验规则。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 BEHAVIOR 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "RIGHT_PLACE_UNDER", "object": "<object>"}
```
- 除 `action`、`object` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `object` 字段，并结合 BEHAVIOR 当前手部状态执行前提校验和环境更新。

</available_skills>

历史失败反馈：
暂无相关拦截记录

规划边界：
1. 只使用 <available_skills> 中列出的动作。
2. 动作参数、前置条件、状态依赖和效果只以对应 skill 契约为准。
3. 只引用当前环境、任务上下文、任务相关环境事实或理解层结果中出现的实体/房间/对象名。
4. 如果已有修复反馈或修复状态，只生成尚未验证的后续动作。

输出格式：
直接输出 BEHAVIOR 原生动作 JSON 数组。
每个元素只能包含 action 和 object；object 是该原生动作的目标对象或目标位置字段。
如果任务已经完成，返回 []。

## Message 2: human

开始规划。
