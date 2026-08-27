---
name: clean_mop
description: DELTA official executable clean_mop action.
---

## 参数
| 参数名 | 类型 | 含义 |
| --- | --- | --- |
| agent | string | DELTA PDDL agent，固定为 `robot`。 |
| item_1 | string | 当前环境中的 mop 实体名，且机器人当前持有该实体。 |
| item_2 | string | 当前环境中的 sink/water-source 实体名。 |
| room | string | `item_2` 所在的 DELTA 房间名。 |

## 前提条件

- 【签名与角色】必须使用 DELTA 原生动作 `clean_mop`；`agent` 固定为 `robot`。外部动作字段为 `item_1/item_2/room`，框架分别映射为 handler 的 `tool/water_source/room`。
- 【工具前提】`item_1` 必须是当前环境中的真实实体，并同时满足 `item_is_mop`、`item_pickable`、`item_accessible` 谓词。
- 【水源前提】`item_2` 必须是当前环境中的真实实体，并满足 `item_is_sink` 谓词。
- 【房间前提】`room` 必须是 `item_2` 通过当前场景关系解析出的真实所在房间；机器人当前位置必须是该房间，或处于 handler 允许的未知位置状态。
- 【持物前提】`sim_robot.robot_holding` 必须等于 `item_1`；否则 sandbox 必须拒绝该步并返回 handler 的 `issue/fix`。
- 【状态前提】mop 不能已经满足 `isClean: True` 且 `isDirty` 不是 `True`；清洁动作只在需要清洁时有效。

## 执行效果

- 【物体状态】`sim_env[item_1].states.isClean` 写为 `True`，`states.isDirty` 写为 `False`。
- 【物体位置】`sim_env[item_1].direct_parent` 写为 `room`，并按 handler 更新 `full_path`。
- 【机器人状态】如果机器人仍持有该 mop，`sim_robot.robot_holding` 写为 `"空"`；`robot_hands` 中持有该 mop 的手也写为 `"空"`。
- 【电量状态】`sim_robot.battery_full` 写为 `False`；其他状态只以 handler.apply(...) 的实际更新为准。
- 【失败处理】如果任一前提校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 `issue/fix`；不得执行部分状态更新。

## 输出格式
在 DELTA 原生动作 JSON 数组中使用这个动作对象：

```json
{"action":"clean_mop","agent":"robot","item_1":"<held_mop_entity>","item_2":"<sink_entity>","room":"<water_source_room>"}
```

- 尖括号中的值只是占位符，真实输出必须替换为当前环境中的精确实体名。
- 不要输出框架包装字段、公共 todo_list 字段或非 DELTA 动作名。
