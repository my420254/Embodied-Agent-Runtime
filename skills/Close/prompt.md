---
name: Close
description: 关闭指定的容器。
---


## 参数
| 参数 | 类型 | 说明 |
|------|------|------|
| target_container | string | 待关闭的容器唯一ID，如：`冰箱_1` |

## 前提条件
* **【位置前提】** 机器人的全局坐标必须已到达 `target_container` 所在位置。
* **【状态前提】** `target_container` 当前属性必须为 `isOpen: True`。严禁关闭已关闭的容器。
* **【单臂死锁防范】** 关门需要机械臂发力，必须保证机械臂空闲。手里有东西必须先 Put 放下。

## 后果
* `target_container` 更新为 `isOpen: False`。
## 示例
```json
{
  "state_awareness": {
    "current_location": "冰箱_1",
    "current_held_item": "空"
  },
  "pre_flight_checks": [
    "检查：当前位置是 冰箱_1，满足位置前提",
    "检查：冰箱_1 当前是开着的（isOpen: True），允许关闭",
    "检查：当前手里没有拿东西，可以发力关门"
  ],
  "execution": {
    "skill": "Close",
    "parameters": {
      "target_container": "冰箱_1"
    }
  }
}