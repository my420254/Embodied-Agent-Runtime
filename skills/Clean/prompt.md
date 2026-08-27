---
name: Clean
description: 在指定的水源设施处清洗物品，去除污垢。
---

## 参数
| 参数 | 类型 | 说明 |
|------|------|------|
| target_item | string | 待清洗的物品唯一ID，如：`脏盘子_1` |
| water_source | string | 正在使用的水源设施唯一ID，如：`水槽_1` |

## 前提条件
* **【位置前提】** 机器人的全局坐标必须已到达 `water_source` 所在位置。
* **【前置动作】** 执行本动作前，若机器人当前位置不是 `water_source`（即机器人位置 != water_source），必须先执行 `NavigateTo(water_source)` 到达该节点；严禁在未导航到位时直接执行本动作。
* **【状态前提】** `target_item` 当前必须是脏的（`isClean: False`）。
* **【持物前提】** `target_item` 必须正拿在手里，或者已被放置在水源设施内部。

## 后果
* `target_item` 更新为 `isClean: True` 和 `isDirty: False`。
* **【位置延续】** 清洗不改变物品所在位置：若清洗时物品在机器人手中，清洗后**仍在手中**（`robot_holding` 不变）；若物品在水源设施内，清洗后仍在设施内。后续若要放置/使用该物品，必须继续执行 `NavigateTo(目标节点)` → `Put(...)` 等动作。

## 示例
```json
{
  "state_awareness": {
    "current_location": "水槽_1",
    "current_held_item": "脏盘子_1"
  },
  "pre_flight_checks": [
    "检查：当前位置是 水槽_1，满足水源位置前提",
    "检查：脏盘子_1 当前是脏的，需要清洗，满足状态前提",
    "检查：手里正拿着 脏盘子_1，满足持物清洗前提"
  ],
  "execution": {
    "skill": "Clean",
    "parameters": {
      "target_item": "脏盘子_1",
      "water_source": "水槽_1"
    }
  }
}