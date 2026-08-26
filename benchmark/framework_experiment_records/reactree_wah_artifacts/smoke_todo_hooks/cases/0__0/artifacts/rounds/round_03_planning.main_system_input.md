# Round 3 planning.main_system Input

## Message 1: system

任务：生成 WAH/ReAcTree 官方原生动作计划。
只输出 JSON；不要解释，不要输出 Markdown。

原始任务：


规划目标：
Put one cupcake and one apple on the coffee table

机器人状态：
- 位置：bedroom 1
- 手持：空
- 完整状态：{"robot_location":"bedroom 1","robot_holding":"空"}

当前环境 JSON：
{"cupcake 1":{"direct_parent":"kitchen table 1","direct_relation":"on","type":null,"states":{},"properties":["GRABBABLE","EATABLE","MOVABLE"],"is_container":false,"full_path":["kitchen 1","floor 2","kitchen table 1"]},"kitchen 1":{"direct_parent":"未知环境","direct_relation":null,"type":"room","states":{},"properties":[],"is_container":false,"full_path":[]},"floor 2":{"direct_parent":"kitchen 1","direct_relation":"inside","type":"receptacle","states":{},"properties":["SURFACES"],"is_container":true,"full_path":["kitchen 1"]},"kitchen table 1":{"direct_parent":"floor 2","direct_relation":"on","type":"receptacle","states":{},"properties":["SURFACES","MOVABLE"],"is_container":true,"full_path":["kitchen 1","floor 2"]},"cupcake 2":{"direct_parent":"kitchen table 1","direct_relation":"on","type":null,"states":{},"properties":["GRABBABLE","EATABLE","MOVABLE"],"is_container":false,"full_path":["kitchen 1","floor 2","kitchen table 1"]},"cupcake 3":{"direct_parent":"cabinet 1","direct_relation":"inside","type":null,"states":{},"properties":["GRABBABLE","EATABLE","MOVABLE"],"is_container":false,"full_path":["bedroom 1","floor 16","cabinet 1"]},"bedroom 1":{"direct_parent":"未知环境","direct_relation":null,"type":"room","states":{},"properties":[],"is_container":false,"full_path":[]},"floor 16":{"direct_parent":"bedroom 1","direct_relation":"inside","type":"receptacle","states":{},"properties":["SURFACES"],"is_container":true,"full_path":["bedroom 1"]},"cabinet 1":{"direct_parent":"floor 16","direct_relation":"on","type":"receptacle","states":{"isOpen":false},"properties":["SURFACES","CAN_OPEN","CONTAINERS"],"is_container":true,"full_path":["bedroom 1","floor 16"]},"apple 1":{"direct_parent":"fridge 1","direct_relation":"inside","type":null,"states":{},"properties":["GRABBABLE","MOVABLE"],"is_container":false,"full_path":["kitchen 1","floor 4","fridge 1"]},"floor 4":{"direct_parent":"kitchen 1","direct_relation":"inside","type":"receptacle","states":{},"properties":["SURFACES"],"is_container":true,"full_path":["kitchen 1"]},"fridge 1":{"direct_parent":"floor 4","direct_relation":"on","type":"receptacle","states":{"isOpen":false},"properties":["CAN_OPEN","HAS_SWITCH","CONTAINERS","HAS_PLUG"],"is_container":true,"full_path":["kitchen 1","floor 4"]},"apple 2":{"direct_parent":"kitchen table 1","direct_relation":"on","type":null,"states":{},"properties":["GRABBABLE","MOVABLE"],"is_container":false,"full_path":["kitchen 1","floor 2","kitchen table 1"]},"apple 3":{"direct_parent":"cabinet 1","direct_relation":"inside","type":null,"states":{},"properties":["GRABBABLE","MOVABLE"],"is_container":false,"full_path":["bedroom 1","floor 16","cabinet 1"]},"coffee table 1":{"direct_parent":"floor 25","direct_relation":"on","type":null,"states":{},"properties":["SURFACES","MOVABLE"],"is_container":false,"full_path":["living room 1","floor 25"]},"living room 1":{"direct_parent":"未知环境","direct_relation":null,"type":"room","states":{},"properties":[],"is_container":false,"full_path":[]},"floor 25":{"direct_parent":"living room 1","direct_relation":"inside","type":"receptacle","states":{},"properties":["SURFACES"],"is_container":true,"full_path":["living room 1"]}}

任务相关环境事实：
[{"name":"apple 1","direct_parent":"fridge 1","full_path":["kitchen 1","floor 4","fridge 1"],"states":{},"type":null,"is_container":false},{"name":"apple 2","direct_parent":"kitchen table 1","full_path":["kitchen 1","floor 2","kitchen table 1"],"states":{},"type":null,"is_container":false},{"name":"apple 3","direct_parent":"cabinet 1","full_path":["bedroom 1","floor 16","cabinet 1"],"states":{},"type":null,"is_container":false},{"name":"bedroom 1","direct_parent":"未知环境","full_path":[],"states":{},"type":"room","is_container":false},{"name":"cabinet 1","direct_parent":"floor 16","full_path":["bedroom 1","floor 16"],"states":{"isOpen":false},"type":"receptacle","is_container":true},{"name":"coffee table 1","direct_parent":"floor 25","full_path":["living room 1","floor 25"],"states":{},"type":null,"is_container":false},{"name":"cupcake 1","direct_parent":"kitchen table 1","full_path":["kitchen 1","floor 2","kitchen table 1"],"states":{},"type":null,"is_container":false},{"name":"cupcake 2","direct_parent":"kitchen table 1","full_path":["kitchen 1","floor 2","kitchen table 1"],"states":{},"type":null,"is_container":false},{"name":"cupcake 3","direct_parent":"cabinet 1","full_path":["bedroom 1","floor 16","cabinet 1"],"states":{},"type":null,"is_container":false},{"name":"floor 16","direct_parent":"bedroom 1","full_path":["bedroom 1"],"states":{},"type":"receptacle","is_container":true},{"name":"floor 2","direct_parent":"kitchen 1","full_path":["kitchen 1"],"states":{},"type":"receptacle","is_container":true},{"name":"floor 25","direct_parent":"living room 1","full_path":["living room 1"],"states":{},"type":"receptacle","is_container":true},{"name":"floor 4","direct_parent":"kitchen 1","full_path":["kitchen 1"],"states":{},"type":"receptacle","is_container":true},{"name":"fridge 1","direct_parent":"floor 4","full_path":["kitchen 1","floor 4"],"states":{"isOpen":false},"type":"receptacle","is_container":true},{"name":"kitchen 1","direct_parent":"未知环境","full_path":[],"states":{},"type":"room","is_container":false},{"name":"kitchen table 1","direct_parent":"floor 2","full_path":["kitchen 1","floor 2"],"states":{},"type":"receptacle","is_container":true},{"name":"living room 1","direct_parent":"未知环境","full_path":[],"states":{},"type":"room","is_container":false}]

任务上下文：
{
  "dataset": "reactree",
  "env_id": 3,
  "task_name": "prepare_snack",
  "instruction": "Put one cupcake and one apple on the coffee table",
  "init_room": "bedroom",
  "task_source": "reactree_wah_testset",
  "environment_source": "reactree_case_runtime_scene",
  "init_graph_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json",
  "task_goal": {
    "on_cupcake_coffeetable": 1,
    "on_apple_coffeetable": 1
  },
  "available_entities": [
    "apple 1",
    "apple 2",
    "apple 3",
    "bananas 1",
    "bar soap 1",
    "bathroom 1",
    "bathroom cabinet 1",
    "bathroom counter 1",
    "bed 1",
    "bedroom 1",
    "book 1",
    "book 2",
    "bookshelf 1",
    "bookshelf 2",
    "bookshelf 3",
    "bowl 1",
    "bowl 2",
    "bowl 3",
    "bowl 4",
    "bowl 5",
    "bowl 6",
    "bowl 7",
    "bowl 8",
    "bowl 9",
    "box 1",
    "box 2",
    "box 3",
    "box 4",
    "box 5",
    "bucket 1",
    "cabinet 1",
    "candle 1",
    "candy bar 1",
    "ceiling 1",
    "ceiling 10",
    "ceiling 11",
    "ceiling 12",
    "ceiling 13",
    "ceiling 14",
    "ceiling 15",
    "ceiling 16",
    "ceiling 17",
    "ceiling 18",
    "ceiling 19",
    "ceiling 2",
    "ceiling 20",
    "ceiling 21",
    "ceiling 22",
    "ceiling 23",
    "ceiling 24",
    "ceiling 25",
    "ceiling 26",
    "ceiling 3",
    "ceiling 4",
    "ceiling 5",
    "ceiling 6",
    "ceiling 7",
    "ceiling 8",
    "ceiling 9",
    "ceiling lamp 1",
    "ceiling lamp 2",
    "ceiling lamp 3",
    "ceiling lamp 4",
    "ceiling lamp 5",
    "cell phone 1",
    "cell phone 2",
    "cereal 1",
    "chair 1",
    "chair 2",
    "chair 3",
    "chair 4",
    "chair 5",
    "chair 6",
    "chips 1",
    "chips 2",
    "chocolate syrup 1",
    "closet 1",
    "closet drawer 1",
    "closet drawer 2",
    "closet drawer 3",
    "closet drawer 4",
    "closet drawer 5",
    "closet drawer 6",
    "closet drawer 7",
    "coffee maker 1",
    "coffee pot 1",
    "coffee table 1",
    "computer 1",
    "condiment bottle 1",
    "condiment bottle 2",
    "condiment bottle 3",
    "condiment bottle 4",
    "condiment shaker 1",
    "condiment shaker 2",
    "condiment shaker 3",
    "condiment shaker 4",
    "cooking pot 1",
    "cooking pot 2",
    "cpu screen 1",
    "crackers 1",
    "crackers 2",
    "creamy buns 1",
    "cupcake 1",
    "cupcake 2",
    "cupcake 3",
    "curtains 1",
    "curtains 2",
    "curtains 3",
    "curtains 4",
    "curtains 5",
    "curtains 6",
    "curtains 7",
    "cutlery fork 1",
    "cutlery fork 2",
    "cutlery fork 3",
    "cutlery fork 4",
    "cutlery knife 1",
    "cutlery knife 2",
    "cutlery knife 3",
    "cutlery knife 4",
    "cutlery knife 5",
    "cutlery knife 6",
    "cutlets 1",
    "deodorant 1",
    "deodorant 2",
    "deodorant 3",
    "desk 1",
    "desk 2",
    "dishwasher 1",
    "dishwashing liquid 1",
    "door 1",
    "door 2",
    "door 3",
    "door jamb 1",
    "door jamb 2",
    "door jamb 3",
    "door jamb 4",
    "face cream 1",
    "face cream 2",
    "face cream 3",
    "faucet 1",
    "faucet 2",
    "floor 1",
    "floor 10",
    "floor 11",
    "floor 12",
    "floor 13",
    "floor 14",
    "floor 15",
    "floor 16",
    "floor 17",
    "floor 18",
    "floor 19",
    "floor 2",
    "floor 20",
    "floor 21",
    "floor 22",
    "floor 23",
    "floor 24",
    "floor 25",
    "floor 26",
    "floor 3",
    "floor 4",
    "floor 5",
    "floor 6",
    "floor 7",
    "floor 8",
    "floor 9",
    "folder 1",
    "folder 2",
    "folder 3",
    "folder 4",
    "fridge 1",
    "frying pan 1",
    "hair product 1",
    "hair product 2",
    "hair product 3",
    "hair product 4",
    "hanger 1",
    "hanger 2",
    "hanger 3",
    "hanger 4",
    "hanger 5",
    "hanger 6",
    "hanger 7",
    "juice 1",
    "juice 2",
    "keyboard 1",
    "kitchen 1",
    "kitchen cabinet 1",
    "kitchen cabinet 2",
    "kitchen cabinet 3",
    "kitchen cabinet 4",
    "kitchen cabinet 5",
    "kitchen cabinet 6",
    "kitchen cabinet 7",
    "kitchen cabinet 8",
    "kitchen counter 1",
    "kitchen counter 2",
    "kitchen counter 3",
    "kitchen counter drawer 1",
    "kitchen counter drawer 2",
    "kitchen counter drawer 3",
    "kitchen counter drawer 4",
    "kitchen counter drawer 5",
    "kitchen counter drawer 6",
    "kitchen counter drawer 7",
    "kitchen counter drawer 8",
    "kitchen table 1",
    "knife block 1",
    "light switch 1",
    "light switch 2",
    "light switch 3",
    "light switch 4",
    "lime 1",
    "living room 1",
    "microwave oven 1",
    "milk 1",
    "mouse 1",
    "mouse mat 1",
    "mug 1",
    "mug 2",
    "mug 3",
    "nightstand 1",
    "nightstand 2",
    "nightstand 3",
    "nightstand 4",
    "notes 1",
    "orchid 1",
    "oven tray 1",
    "painkillers 1",
    "pancake 1",
    "peach 1",
    "peach 2",
    "peach 3",
    "pear 1",
    "perfume 1",
    "perfume 2",
    "photo frame 1",
    "photo frame 2",
    "photo frame 3",
    "pile of clothes 1",
    "pile of clothes 2",
    "pillow 1",
    "pillow 2",
    "pillow 3",
    "pillow 4",
    "pillow 5",
    "pillow 6",
    "plate 1",
    "plate 2",
    "plate 3",
    "plate 4",
    "plate 5",
    "plate 6",
    "plate 7",
    "plum 1",
    "plum 2",
    "power socket 1",
    "power socket 2",
    "power socket 3",
    "pudding 1",
    "pudding 2",
    "radio 1",
    "rug 1",
    "rug 2",
    "rug 3",
    "rug 4",
    "sink 1",
    "sink 2",
    "slice of bread 1",
    "slice of bread 2",
    "sofa 1",
    "sofa 2",
    "sofa 3",
    "stall 1",
    "stall 2",
    "stove 1",
    "stove fan 1",
    "table lamp 1",
    "toaster 1",
    "toilet 1",
    "toilet paper 1",
    "toothbrush 1",
    "toothpaste 1",
    "tv 1",
    "tv stand 1",
    "wall 1",
    "wall 10",
    "wall 11",
    "wall 12",
    "wall 13",
    "wall 14",
    "wall 15",
    "wall 16",
    "wall 17",
    "wall 18",
    "wall 19",
    "wall 2",
    "wall 20",
    "wall 21",
    "wall 22",
    "wall 23",
    "wall 24",
    "wall 25",
    "wall 26",
    "wall 3",
    "wall 4",
    "wall 5",
    "wall 6",
    "wall 7",
    "wall 8",
    "wall 9",
    "wall lamp 1",
    "wall lamp 2",
    "wall lamp 3",
    "wall lamp 4",
    "wall lamp 5",
    "wall lamp 6",
    "wall lamp 7",
    "wall lamp 8",
    "wall lamp 9",
    "wall phone 1",
    "wall picture frame 1",
    "wall picture frame 2",
    "wall picture frame 3",
    "wall picture frame 4",
    "wall picture frame 5",
    "wall picture frame 6",
    "wall picture frame 7",
    "wall picture frame 8",
    "wall shelf 1",
    "wall shelf 2",
    "washing machine 1",
    "washing sponge 1",
    "water glass 1",
    "water glass 2",
    "water glass 3",
    "water glass 4",
    "water glass 5",
    "window 1",
    "window 2",
    "wine 1"
  ]
}

理解层实体选择：
{
  "targets": {
    "primary": [
      "cupcake 1",
      "apple 1"
    ],
    "alternatives": []
  },
  "tools": {
    "primary": [],
    "alternatives": []
  },
  "receptacles": {
    "primary": [
      "coffee table 1"
    ],
    "alternatives": []
  }
}

可用动作与 skill 契约：
<available_skills>
---
name: go to
description: Official ReAcTree WAH navigation action.
---

## 参数
planning、handler 和官方导出均使用 WAH 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `go to`。 |
| target | string | 当前 WAH 场景中的精确目标实体名。 |
## 前提条件
- 必须使用官方 WAH 原生动作名 `go to` 和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的房间或对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 只有在目标位置或交互锚点当前不可直接到达时，才应导航。
- 如果机器人已经处于同一个可交互位置簇，不要重复导航。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，模拟机器人位置应更新到该 WAH 官方实体。

## 输出格式
- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "go to", "target": "<target>"}
```
- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。

---
name: pick up
description: Official ReAcTree WAH pickup action.
---

## 参数
planning、handler 和官方导出均使用 WAH 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `pick up`。 |
| target | string | 当前 WAH 场景中的精确目标实体名。 |
## 前提条件
- 必须使用官方 WAH 原生动作名 `pick up` 和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标必须具备 WAH `GRABBABLE` 属性；桌面、房间、灯、容器本身不能被当作普通可拿取物。
- 目标物体必须可达；当前机器人位置、目标父节点以及对应手或携带槽位必须满足 handler 校验。
- 如果目标位于关闭的 `CAN_OPEN` 容器内，`pick up` 会被 handler 拒绝。
- 如果 benchmark 使用多只手，必须依据各只手的占用状态判断，而不是假设只有一个抓手。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标物体会进入对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "pick up", "target": "<target>"}
```
- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。

---
name: put down
description: Official ReAcTree WAH put-down action.
---

## 参数
planning、handler 和官方导出均使用 WAH 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `put down`。 |
| target | string | 当前 WAH 场景中的精确目标实体名。 |
## 前提条件
- 必须使用官方 WAH 原生动作名 `put down` 和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- `put down` 的目标位置由当前机器人位置决定；当前位置不满足放置条件时 handler 必须拒绝。
- 如果当前位置是关闭的 `CAN_OPEN` 容器，handler 必须拒绝该步。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "put down", "target": "<target>"}
```
- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。

---
name: open
description: Official ReAcTree WAH open action.
---

## 参数
planning、handler 和官方导出均使用 WAH 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `open`。 |
| target | string | 当前 WAH 场景中的精确目标实体名。 |
## 前提条件
- 必须使用官方 WAH 原生动作名 `open` 和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须具备 WAH `CAN_OPEN` 属性，且当前不是已打开状态。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。

## 输出格式
- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "open", "target": "<target>"}
```
- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。

---
name: close
description: Official ReAcTree WAH close action.
---

## 参数
planning、handler 和官方导出均使用 WAH 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `close`。 |
| target | string | 当前 WAH 场景中的精确目标实体名。 |
## 前提条件
- 必须使用官方 WAH 原生动作名 `close` 和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须具备 WAH `CAN_OPEN` 属性，且当前不是已关闭状态。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。

## 输出格式
- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "close", "target": "<target>"}
```
- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。

---
name: turn on
description: Official ReAcTree WAH turn-on action.
---

## 参数
planning、handler 和官方导出均使用 WAH 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `turn on`。 |
| target | string | 当前 WAH 场景中的精确目标实体名。 |
## 前提条件
- 必须使用官方 WAH 原生动作名 `turn on` 和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须具备 WAH `HAS_SWITCH` 属性，当前不是已开启状态，并且机器人必须空手。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。

## 输出格式
- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "turn on", "target": "<target>"}
```
- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。

---
name: turn off
description: Official ReAcTree WAH turn-off action.
---

## 参数
planning、handler 和官方导出均使用 WAH 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `turn off`。 |
| target | string | 当前 WAH 场景中的精确目标实体名。 |
## 前提条件
- 必须使用官方 WAH 原生动作名 `turn off` 和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须具备 WAH `HAS_SWITCH` 属性，当前不是已关闭状态，并且机器人必须空手。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。

## 输出格式
- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "turn off", "target": "<target>"}
```
- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。

---
name: clean
description: Official ReAcTree WAH clean action.
---

## 参数
planning、handler 和官方导出均使用 WAH 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `clean`。 |
| target | string | 当前 WAH 场景中的精确目标实体名。 |
## 前提条件
- 必须使用官方 WAH 原生动作名 `clean` 和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 所需工具、液体状态或清洁装置状态，必须已经满足 handler 的校验规则。
- 不要假设工具会自动变湿、变干净或自动可用；只有已验证步骤造成的状态变化才有效。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，会按 handler 约定更新清洁、浸湿或相关状态标志。

## 输出格式
- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "clean", "target": "<target>"}
```
- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。
</available_skills>

历史失败反馈：
暂无相关拦截记录

规划边界：
1. 只使用 <available_skills> 中列出的动作。
2. 动作参数、前置条件、状态依赖和效果只以对应 skill 契约为准。
3. 只引用当前环境、任务上下文、任务相关环境事实或理解层结果中出现的实体/房间/对象名。
4. 如果已有修复反馈或修复状态，只生成尚未验证的后续动作。

输出格式：
直接输出 WAH/ReAcTree 原生动作 JSON 数组。
每个元素只能包含 action 和 target。
如果任务已经完成，返回 []。

## Message 2: human

开始规划。
