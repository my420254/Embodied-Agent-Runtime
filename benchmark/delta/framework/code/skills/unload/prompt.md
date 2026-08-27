---
name: unload
description: DELTA official executable unload action.
---

## 参数
| 参数名 | 类型 | 含义 |
| --- | --- | --- |
| agent | string | DELTA PDDL agent，固定为 `robot`。 |
| item_1 | string | 当前环境中的非空 loadable container 实体名。 |
| item_2 | string | 当前位于 `item_1` 内的物品实体名。 |
| room | string | `item_1` 所在的 DELTA 房间名。 |

## 前提条件
- 必须使用 DELTA PDDL 签名 `unload(robot, item_1, item_2, room)` 和下面的同签名 JSON 对象。
- 当前 DELTA 场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- `agent` 必须是 `robot`。
- `item_1` 必须是当前环境中的真实 loadable container，且不为空。
- `item_2` 必须是当前环境中的真实实体，并且当前位于 `item_1` 内。
- `room` 必须是当前 DELTA 场景中的真实房间，并且必须是 `item_1` 所在房间。
- 机器人必须已经在 `room`，且手中没有物品。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，`item_2` 位于 `room`，`item_1` 变为空；机器人手持状态只以 handler.apply(...) 的实际更新为准。

## 输出格式
在 DELTA 原生动作 JSON 数组中使用这个动作对象：

```json
{"action":"unload","agent":"robot","item_1":"<loadable_entity>","item_2":"<contained_item_entity>","room":"<loadable_room>"}
```

- 尖括号中的值只是占位符，真实输出必须替换为当前环境中的精确实体名。
- 不要输出框架包装字段、公共 todo_list 字段或非 DELTA 动作名。
