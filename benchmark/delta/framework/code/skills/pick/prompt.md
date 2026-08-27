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
- 【单臂约束】机器人一次只能携带一个物品；如果当前已经持有其他物品，必须先用 `drop`、`place_on` 或任务要求的其他放置技能释放手持物，再执行 `pick`。
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
