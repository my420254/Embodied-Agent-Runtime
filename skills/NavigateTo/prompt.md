---
name: NavigateTo
description: 移动机器人到指定的具体的物理设施或容器前方。
---


## 参数
| 参数 | 类型 | 说明 |
|------|------|------|
| target_location | string | 必须是环境拓扑图中存在的具体设施或容器节点，如：`水槽_1`、`冰箱_1`。严禁导航到无法直接交互的泛指大区域（如仅输入“厨房”）。 |

## 前提条件
* **【状态前提】** 机器人当前所在位置不能已经是 `target_location`，避免原地空转报错。
* **【移动兼容性】** 无论机械臂是空闲还是持有物品，均允许执行底盘移动（无需因为手里有东西而特意放下）。

## 后果
* 机器人的全局坐标更新至 `target_location`，并解锁对该位置/容器内部物品的交互视野。

## 示例
```json
{
  "state_awareness": {
    "current_location": "厨房",
    "current_held_item": "空"
  },
  "pre_flight_checks": [
    "检查：目标 冰箱_1 是具体的交互节点，满足合法性",
    "检查：当前位置是 厨房，不在 冰箱_1，需要移动",
    "检查：移动动作无视手部持物状态，当前状态合法"
  ],
  "execution": {
    "skill": "NavigateTo",
    "parameters": {
      "target_location": "冰箱_1"
    }
  }
}