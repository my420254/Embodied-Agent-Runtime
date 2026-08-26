---
name: Open
description: 打开指定的闭合容器，暴露其内部物品。
---

## 参数
| 参数 | 类型 | 说明 |
|------|------|------|
| target_container | string | 待打开的容器唯一ID，如：`冰箱_1`、`顶层橱柜_1` |

## 前提条件
* **【位置前提】** 机器人的全局坐标必须已到达 `target_container` 所在位置。
* **【状态前提】** `target_container` 当前属性必须为 `isOpen: False`。严禁重复打开已开的门。
* **【单臂死锁防范】** 打开容器需要发力，必须保证机械臂绝对空闲。手里有东西必须先 Put 放下。

## 后果
* `target_container` 更新为 `isOpen: True`。内部物品将进入可见/可达视野。

## 示例
```json
{
  "state_awareness": {
    "current_location": "冰箱_1",
    "current_held_item": "空"
  },
  "pre_flight_checks": [
    "检查：当前位置是 冰箱_1，满足位置前提",
    "检查：冰箱_1 当前是关着的（isOpen: False），可以执行打开",
    "检查：当前手里没有拿东西，可以发力开门"
  ],
  "execution": {
    "skill": "Open",
    "parameters": {
      "target_container": "冰箱_1"
    }
  }
}