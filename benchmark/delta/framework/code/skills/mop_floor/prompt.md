---
name: mop_floor
description: DELTA official executable mop_floor action.
---

## 参数
| 参数名 | 类型 | 含义 |
| --- | --- | --- |
| agent | string | DELTA PDDL agent，固定为 `robot`。 |
| item | string | 当前机器人持有的 clean mop 实体名。 |
| room | string | 需要拖地的 DELTA 房间名。 |

## 前提条件
- 必须使用 DELTA PDDL 签名 `mop_floor(robot, item, room)` 和下面的同签名 JSON 对象。
- 当前 DELTA 场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- `agent` 必须是 `robot`。
- `item` 必须是当前环境中的真实 mop 实体，且当前状态为 clean。
- 机器人必须已经在 `room`，并且已经持有 `item`。
- `room` 必须是当前 DELTA 场景中的真实房间。
- 如果 mop 不是 clean，`mop_floor` 必须被 sandbox 拒绝。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，`room` 的 floor 变为 clean，mop 变为 not clean；电量相关变化只以 handler.apply(...) 的实际更新为准。

## 输出格式
在 DELTA 原生动作 JSON 数组中使用这个动作对象：

```json
{"action":"mop_floor","agent":"robot","item":"<held_clean_mop_entity>","room":"<floor_room>"}
```

- 尖括号中的值只是占位符，真实输出必须替换为当前环境中的精确实体名。
- 不要输出框架包装字段、公共 todo_list 字段或非 DELTA 动作名。
