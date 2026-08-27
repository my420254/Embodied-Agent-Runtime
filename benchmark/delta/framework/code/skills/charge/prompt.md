---
name: charge
description: DELTA official executable charge action.
---

## 参数
| 参数名 | 类型 | 含义 |
| --- | --- | --- |
| agent | string | DELTA PDDL agent，固定为 `robot`。 |
| item | string | 当前环境中的充电设施实体名。 |
| room | string | `item` 所在的 DELTA 房间名。 |

## 前提条件
- 必须使用 DELTA PDDL 签名 `charge(robot, item, room)` 和下面的同签名 JSON 对象。
- 当前 DELTA 场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- `agent` 必须是 `robot`。
- `item` 必须是当前任务环境中的真实实体，并满足 DELTA robot-hub/charging station 谓词。
- `room` 必须是当前 DELTA 场景中的真实房间，并且必须是 `item` 所在房间。
- 机器人必须已经在 `room`，且手中没有物品。
- 如果机器人正在持有物品，`charge` 必须被 sandbox 拒绝。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，机器人电量进入充满状态；其他状态只以 handler.apply(...) 的实际更新为准。

## 输出格式
在 DELTA 原生动作 JSON 数组中使用这个动作对象：

```json
{"action":"charge","agent":"robot","item":"<charging_station_entity>","room":"<charging_station_room>"}
```

- 尖括号中的值只是占位符，真实输出必须替换为当前环境中的精确实体名。
- 不要输出框架包装字段、公共 todo_list 字段或非 DELTA 动作名。
