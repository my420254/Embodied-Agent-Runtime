# 控制台与 ROS 文本接入说明

本文说明 Embodied Agent Runtime 的两类入口：命令行调试入口和 ROS/前端正式接入入口。

## 入口分工

| 入口 | 文件 | 用途 |
| --- | --- | --- |
| 正式服务入口 | `main.py` | 启动 ROS 文本服务和后台 Agent runtime |
| CLI 调试入口 | `scripts/run_agent.py` | 从命令行注入任务、验证理解/规划/执行链路 |
| 控制命令入口 | `scripts/send_command.py` | 向 CommandBus 写入取消、暂停、恢复或插单命令 |
| 终端渲染 | `scripts/renderer.py` | 将 LangGraph 流式状态渲染为可读日志 |

`run_console.py` 不再作为主入口，历史控制台渲染逻辑已经收敛到 `scripts/renderer.py`。

## CLI 调试

只运行理解与规划：

```bash
python scripts/run_agent.py --task '把土豆切成片' --once
```

运行到执行层：

```bash
python scripts/run_agent.py --task '把土豆切成片' --execute
```

常驻监听 CommandBus：

```bash
python scripts/run_agent.py --listen --execute
```

## ROS 文本服务

正式联调使用：

```bash
python main.py
```

默认服务名：

```text
/genesis_arm/send_text_command
```

指定实例号或端口后，服务名会带后缀：

```bash
python main.py 5001
```

```text
/genesis_arm_5001/send_text_command
```

发送文本命令：

```bash
ros2 service call /genesis_arm/send_text_command genesis_msgs/srv/TextCommand "{command: '把土豆切成片'}"
```

## 命令流

```text
ROS TextCommand / CLI --task
  -> adapters.ros_text_command_service 或 scripts.run_agent
  -> adapters.command_bus
  -> agent_runtime.engine
  -> graph/understanding
  -> graph/planning
  -> graph/task_management
  -> execution backend
  -> graph/reflection
```

CommandBus 默认文件是：

```text
/tmp/ouragent_commands.jsonl
```

可以通过环境变量覆盖：

```bash
export OURAGENT_COMMAND_FILE=/tmp/embodied_agent_commands.jsonl
```

## 插单、中断与取消

如果 runtime 正在执行任务，新的 `new_task` 会进入同一个 CommandBus。任务管理层会保存当前任务栈，优先处理新任务，完成后再恢复旧任务。

控制命令示例：

```bash
python scripts/send_command.py --kind cancel_current '取消当前任务'
python scripts/send_command.py --kind cancel_all '停止所有任务'
python scripts/send_command.py --kind pause '暂停'
python scripts/send_command.py --kind resume '继续'
```

当前中断是调度层中断，不是操作系统级强杀。底层动作如果阻塞，runtime 会在动作返回或超时后消费下一条控制命令。

## 指令澄清

理解层判断信息不足时，会输出澄清问题。正式 ROS/前端模式不会阻塞读取终端输入，而是等待下一条外部命令作为补充说明。连续多次澄清失败后，runtime 会放弃当前任务并回到空闲监听状态。

## LLM 端点检查

理解层和规划层依赖 OpenAI-compatible LLM 服务。部署前需要确认端点可访问：

```bash
curl --noproxy '*' http://<LLM_HOST>:<PORT>/v1/models \
  -H 'Authorization: Bearer qwen-local-key'
```

如果任务偶发进入澄清，优先检查 vLLM 是否拥塞：

```bash
curl --noproxy '*' -s http://<LLM_HOST>:<PORT>/metrics | grep -E "num_requests_(running|waiting)"
```
