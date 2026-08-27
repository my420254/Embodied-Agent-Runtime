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
