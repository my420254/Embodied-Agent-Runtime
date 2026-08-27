---
name: Put
description: 将当前持有的物品放置到指定的物理表面或容器内。
---

# Put

## 参数
| 参数 | 类型 | 说明 |
|------|------|------|
| target_item | string | 待放置的物品唯一ID，如：`土豆_1` |
| destination | string | 目标放置的直接交互节点唯一ID（具体设施或容器），如：`砧板_1`、`冰箱_1` |

## 前提条件
* **【位置前提】** 机器人的全局坐标必须已到达 `destination` 所在位置。
* **【前置动作】** 执行本动作前，若机器人当前位置不是 `destination`（即机器人位置 != destination），必须先执行 `NavigateTo(destination)` 到达该节点；严禁在未导航到位时直接执行本动作。
* **【持物状态前提】** 机械臂必须正持有 `target_item`。严禁空手执行或放置非当前持有的物品。
* **【容器兼容性拦截】** 若 `destination` 是闭合类容器（如冰箱、橱柜、抽屉），其当前状态必须为 `isOpen: True`（已打开），禁止穿模放入。

## 后果
* `robot_holding` 更新为 `"空"`。
* `target_item.direct_parent` 更新为 `destination`；可开闭容器使用 `direct_relation: "inside"`，其他表面使用 `direct_relation: "on"`。
* `target_item.full_path` 更新为 `destination.full_path + [destination]`。

## 示例
```json
{
  "state_awareness": {
    "current_location": "冰箱_1",
    "current_held_item": "土豆_1"
  },
  "pre_flight_checks": [
    "检查：当前位置正好是目标容器 冰箱_1，满足精确位置前提",
    "检查：当前手里正拿着 土豆_1，符合待放置物品，满足持物前提",
    "检查：冰箱_1 处于打开状态（isOpen: True），允许放入"
  ],
  "execution": {
    "skill": "Put",
    "parameters": {
      "target_item": "土豆_1",
      "destination": "冰箱_1"
    }
  }
}
