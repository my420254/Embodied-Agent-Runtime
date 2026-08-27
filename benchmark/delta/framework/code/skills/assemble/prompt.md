---
name: assemble
description: DELTA official executable assemble action.
---

## 参数
| 参数名 | 类型 | 含义 |
| --- | --- | --- |
| agent | string | DELTA PDDL agent，固定为 `robot`。 |
| room | string | DELTA 房间名，表示执行组装的工作房间。 |
| item_1 | string | 当前环境中的主板实体名。 |
| item_2 | string | 当前环境中的 CPU 实体名。 |
| item_3 | string | 当前环境中的内存实体名。 |
| item_4 | string | 当前环境中的硬盘实体名。 |
| item_5 | string | 当前环境中的显卡实体名。 |
| item_6 | string | 当前环境中的电源实体名。 |
| pc | string | DELTA 任务上下文或环境中的目标 PC 实体名。 |

## 前提条件
- 必须使用 DELTA PDDL 签名 `assemble(robot, room, item_1, item_2, item_3, item_4, item_5, item_6, pc)` 和下面的同签名 JSON 对象。
- 当前 DELTA 场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- `agent` 必须是 `robot`。
- `room` 必须是当前 DELTA 场景中的真实房间；所有组件实体和 `pc` 必须来自当前任务上下文或当前环境。
- 机器人必须已经在 `room`，且手中没有物品。
- `item_1`、`item_2`、`item_3`、`item_4`、`item_5`、`item_6` 必须已经位于同一个 `room`，并满足 DELTA PC 组装动作要求的组件类型约束：主板、CPU、内存、硬盘、显卡、电源。
- 如果任一组件还没有位于 `room`，`assemble` 必须被 sandbox 拒绝。
- 【组件就位约束】在执行 `assemble` 前，必须先通过 `drop` 或其他适用的放置技能，把所有相关组件放到该 `room`；不能在仍由机器人持有或位于其他房间时直接组装。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标 PC 进入已组装状态；其他物体位置和机器人手持状态只以 handler.apply(...) 的实际更新为准。

## 输出格式
在 DELTA 原生动作 JSON 数组中使用这个动作对象：

```json
{"action":"assemble","agent":"robot","room":"<workspace_room>","item_1":"<mainboard_entity>","item_2":"<cpu_entity>","item_3":"<ram_entity>","item_4":"<ssd_entity>","item_5":"<gpu_entity>","item_6":"<psu_entity>","pc":"<target_pc_entity>"}
```

- 尖括号中的值只是占位符，真实输出必须替换为当前环境中的精确实体名。
- 不要输出框架包装字段、公共 todo_list 字段或非 DELTA 动作名。
