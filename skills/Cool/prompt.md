---
name: Cool
description: 在指定的制冷设备中冷却物品。执行前需确保设备通电且门已关闭。
---

## 参数
| 参数 | 类型 | 说明 |
|------|------|------|
| target_item | string | 待冷却的物品唯一ID，如：`牛奶_1` |
| cooling_device | string | 正在使用的制冷设备唯一ID，如：`冰箱_1` |

## 前提条件
* **【位置前提】** 机器人的全局坐标必须已到达 `cooling_device` 所在位置。
* **【前置动作】** 执行本动作前，若机器人当前位置不是 `cooling_device`（即机器人位置 != cooling_device），必须先执行 `NavigateTo(cooling_device)` 到达该节点；严禁在未导航到位时直接执行本动作。
* **【状态前提】** `target_item` 必须为未冷却状态（`isCold: False`）。
* **【容器前提】** `target_item` 必须已经放入 `cooling_device` 内部，且设备舱门必须关闭（`isOpen: False`）。
* **【设备电源前提】** `cooling_device` 必须正常通电工作（`isToggled: True`）。
* **【单臂防呆约束】** 启动制冷设备面板必须保证机械臂空闲。

## 后果
* `target_item` 更新为 `isCold: True`。

## 示例
```json
{
  "state_awareness": {
    "current_location": "冰箱_1",
    "current_held_item": "空"
  },
  "pre_flight_checks": [
    "检查：当前位置是 冰箱_1，满足精确位置前提",
    "检查：牛奶_1 已位于 冰箱_1 内部，且冰箱_1 舱门关闭（isOpen: False）",
    "检查：冰箱_1 已正常工作（isToggled: True），满足电源前提",
    "检查：牛奶_1 需要冷却，手里没有拿东西，状态合法"
  ],
  "execution": {
    "skill": "Cool",
    "parameters": {
      "target_item": "牛奶_1",
      "cooling_device": "冰箱_1"
    }
  }
}
