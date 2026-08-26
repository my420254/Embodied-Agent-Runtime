---
name: ToggleOn
description: 触发指定的电器设备开关，使其通电开始工作。
---


## 参数
| 参数 | 类型 | 说明 |
|------|------|------|
| target_device | string | 待开启的设备唯一ID，如：`微波炉_1` |

## 前提条件
* **【位置前提】** 机器人的全局坐标必须已到达 `target_device` 所在位置。
* **【状态前提】** `target_device` 当前属性必须为 `isToggled: False`（已关闭）。严禁重复开启。
* **【单臂防呆约束】** 拨动开关需机械臂操作。强制要求手里不能拿东西。

## 后果
* `target_device` 更新为 `isToggled: True`。通电后方可执行加热/制冷等衍生操作。

## 示例
```json
{
  "state_awareness": {
    "current_location": "微波炉_1",
    "current_held_item": "空"
  },
  "pre_flight_checks": [
    "检查：当前位置就在 微波炉_1 处，满足精确位置前提",
    "检查：微波炉_1 当前未开启，满足状态前提",
    "检查：当前手里没有拿东西，可以单臂操作开关"
  ],
  "execution": {
    "skill": "ToggleOn",
    "parameters": {
      "target_device": "微波炉_1"
    }
  }
}