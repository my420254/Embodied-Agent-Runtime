---
name: Heat
description: 在指定的加热设备中加热物品。执行前需确保设备已通电开启，且门已关闭。
---


## 参数
| 参数 | 类型 | 说明 |
|------|------|------|
| target_item | string | 待加热的物品唯一ID，如：`土豆_1` |
| heating_device | string | 正在使用的加热设备唯一ID，如：`微波炉_1` |

## 前提条件
* **【位置前提】** 机器人的全局坐标必须已到达 `heating_device` 所在位置。
* **【前置动作】** 执行本动作前，若机器人当前位置不是 `heating_device`（即机器人位置 != heating_device），必须先执行 `NavigateTo(heating_device)` 到达该节点；严禁在未导航到位时直接执行本动作。
* **【状态前提】** `target_item` 必须为未加热状态（`isCooked: False`）。
* **【容器前提】** `target_item` 必须已经放入 `heating_device` 内部，且设备舱门必须关闭（`isOpen: False`）。
* **【设备电源前提】** `heating_device` 必须已通电工作（`isToggled: True`）。
* **【单臂防呆约束】** 启动加热面板必须保证机械臂空闲。

## 后果
* `target_item` 更新为 `isCooked: True` 且 `isCold: False`。

## 示例
```json
{
  "state_awareness": {
    "current_location": "微波炉_1",
    "current_held_item": "空"
  },
  "pre_flight_checks": [
    "检查：当前位置是 微波炉_1，满足位置前提",
    "检查：土豆_1 已位于 微波炉_1 内部，且微波炉_1 舱门关闭（isOpen: False）",
    "检查：微波炉_1 已开启（isToggled: True），满足电源前提",
    "检查：土豆_1 未加热，手里没有拿东西，状态全部合法"
  ],
  "execution": {
    "skill": "Heat",
    "parameters": {
      "target_item": "土豆_1",
      "heating_device": "微波炉_1"
    }
  }
}
