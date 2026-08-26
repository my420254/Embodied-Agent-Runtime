# Type

## 参数

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| target_device | string | 要输入的设备或交互面唯一 ID |

## 前提条件

- 机器人必须已经导航到 `target_device` 所在位置。
- 推荐空手操作。

## 后果

- 完成一次输入或键入动作。
- 不直接改变环境主状态。

## 示例

```json
{
  "skill": "Type",
  "parameters": {
    "target_device": "笔记本电脑_1"
  }
}
```
