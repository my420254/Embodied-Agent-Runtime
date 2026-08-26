# Sleep

## 参数

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| target_bed | string | 要躺下或睡眠的对象唯一 ID |

## 前提条件

- 机器人必须已经导航到 `target_bed` 所在位置。

## 后果

- 机器人进入睡眠/躺卧状态。

## 示例

```json
{
  "skill": "Sleep",
  "parameters": {
    "target_bed": "床_1"
  }
}
```
