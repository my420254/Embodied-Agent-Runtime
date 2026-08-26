---
name: Slice
description: 使用手中持有的锋利切割工具，对台面/砧板上的指定食材进行切割。
---


## 参数
| 参数 | 类型 | 说明 |
|------|------|------|
| target_item | string | 待切割的食材唯一ID，如：`土豆_1` |
| surface | string | 食材当前直接所在的物理表面或节点唯一ID，如：`砧板_1`、`厨房操作台_1` |

## 前提条件
* **【位置前提】** 机器人的全局坐标必须已到达 `surface` 所在位置。
* **【工具持握前提】** 机械臂必须正持有切割工具（如 `厨师刀_1`）。严禁空手切割。
* **【工具状态红线】** 持有的切割工具必须处于完好且锋利状态（`isBroken: False` 且 `isSharp: True`）。
* **【食材状态前提】** `target_item` 必须未被切碎（`isSliced: False`），且必须已放置在 `surface` 上（严禁拿在手里切）。
* **【卫生前置约束】** `target_item` 在切割前必须已经清洗干净（`isClean: True`）；若仍为脏污状态，必须先执行 `Clean`。

## 后果
* `target_item` 更新为 `isSliced: True`。切割工具可能变脏。

## 示例
```json
{
  "state_awareness": {
    "current_location": "厨房操作台_1",
    "current_held_item": "厨师刀_1"
  },
  "pre_flight_checks": [
    "检查：当前位置是 厨房操作台_1，土豆_1 正放在其上，满足空间精确位置前提",
    "检查：手里正拿着 厨师刀_1，属于切割工具，满足工具前提",
    "检查：厨师刀_1 状态完好（isBroken: False）且锋利（isSharp: True），工具状态合法",
    "检查：土豆_1 当前未切碎且 isClean: True，满足食材和卫生前提"
  ],
  "execution": {
    "skill": "Slice",
    "parameters": {
      "target_item": "土豆_1",
      "surface": "厨房操作台_1"
    }
  }
}
