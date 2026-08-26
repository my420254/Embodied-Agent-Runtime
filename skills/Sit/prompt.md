# Sit

## 参数

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| target_seat | string | 要坐下的对象唯一 ID |

## 前提条件

- 机器人必须已经导航到 `target_seat` 所在位置。

## 后果

- 机器人进入坐姿。

## 示例

```json
{
  "skill": "Sit",
  "parameters": {
    "target_seat": "沙发_1"
  }
}
```
