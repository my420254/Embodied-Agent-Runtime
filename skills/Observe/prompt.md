# Observe

## 参数

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| target_object | string | 要观察或注视的对象唯一 ID |

## 前提条件

- 机器人必须已经导航到 `target_object` 所在的具体交互节点。

## 后果

- 机器人完成一次观察动作。
- 不直接改变环境物理状态。

## 示例

```json
{
  "skill": "Observe",
  "parameters": {
    "target_object": "电视_1"
  }
}
```
