# Drink

## 参数

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| target_item | string | 要饮用的对象唯一 ID |

## 前提条件

- 机器人必须已经持有 `target_item`，或目标已位于当前位置。

## 后果

- 完成一次饮用动作。
- 目标对象可能进入“已消费”状态。

## 示例

```json
{
  "skill": "Drink",
  "parameters": {
    "target_item": "咖啡杯_1"
  }
}
```
