# Touch

## 参数

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| target_object | string | 要接触的对象唯一 ID |

## 前提条件

- 机器人必须已经导航到 `target_object` 所在位置。

## 后果

- 机器人完成一次接触动作。
- 不直接改变环境主状态。

## 示例

```json
{
  "skill": "Touch",
  "parameters": {
    "target_object": "猫_1"
  }
}
```
