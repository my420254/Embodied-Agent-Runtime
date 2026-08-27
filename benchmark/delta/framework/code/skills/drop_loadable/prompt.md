---
name: drop_loadable
description: DELTA official executable drop_loadable action.
---

## 参数
| 参数名 | 类型 | 含义 |
| --- | --- | --- |
| agent | string | DELTA PDDL agent，固定为 `robot`。 |
| item | string | 当前机器人持有的空 loadable container 实体名。 |
| room | string | 放下 `item` 的 DELTA 房间名。 |

## 前提条件
- 必须使用 DELTA PDDL 签名 `drop_loadable(robot, item, room)` 和下面的同签名 JSON 对象。
- 当前 DELTA 场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- `agent` 必须是 `robot`。
- `item` 必须是当前环境中的真实 loadable container，且机器人已经持有它。
- `item` 必须为空；非 loadable 或非空容器不能使用 `drop_loadable`。
- `room` 必须是当前 DELTA 场景中的真实房间，并且必须等于机器人当前所在房间。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，`item` 位于 `room`，机器人手变为空。

## 输出格式
在 DELTA 原生动作 JSON 数组中使用这个动作对象：

```json
{"action":"drop_loadable","agent":"robot","item":"<held_loadable_entity>","room":"<drop_room>"}
```

- 尖括号中的值只是占位符，真实输出必须替换为当前环境中的精确实体名。
- 不要输出框架包装字段、公共 todo_list 字段或非 DELTA 动作名。
