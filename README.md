# Embodied Agent Runtime

面向具身任务、ROS 文本接入和多 benchmark 评测的 LangGraph 智能体运行时。

本项目围绕“自然语言任务如何稳定进入机器人或仿真执行闭环”构建，覆盖文本入口、任务理解、结构化规划、执行前审计、任务栈调度、外部中断、失败反思和评测对齐。它不是单轮 prompt demo，而是一套可常驻运行、可接入外部系统、可追踪状态变化的 Agent runtime。

## 核心能力

- **统一文本入口**：ROS 服务、前端适配层和 CLI 调试命令最终都进入同一个 CommandBus，避免多入口维护多套任务逻辑。
- **LangGraph 分层编排**：将任务处理拆成 Understanding、Planning、Task Management、Execution、Reflection 等阶段，状态字段清晰，便于定位失败层。
- **任务栈式中断恢复**：执行过程中收到新任务时，可以保存当前任务状态，优先处理新任务，完成后恢复原任务。
- **取消与暂停控制**：外部可以发送 `cancel_current`、`cancel_all`、`pause`、`resume` 等控制命令，运行时在调度边界进行处理。
- **执行前可行性审计**：规划结果进入执行层前，会经过 sandbox evaluator、state-diff audit、skill contract 等检查，降低 LLM 直接控制执行层的风险。
- **失败反思与局部重试**：执行失败会保留 `failure_layer`、错误信息、状态差异和 trace，Reflection 层可根据失败类型回到理解、规划或执行阶段继续修复。
- **benchmark 数据口径对齐**：framework、paper method 和 bare baseline 使用同一份抽取/清洗后的数据输入，避免不同方法使用不同预处理结果导致比较失真。
- **vLLM 并行评测支持**：支持本地 Qwen/vLLM OpenAI-compatible 端点、多端口、多 worker 评测和端点拥塞排查。

## 架构流程

```text
ROS / Frontend / CLI Text
  -> CommandBus
  -> LangGraph Runtime
  -> Understanding
  -> Planning
  -> Sandbox / State Diff Audit
  -> Task Stack Management
  -> Simulation or ROS Execution Backend
  -> Reflection / Replan / Report
```

## 目录说明

| 路径 | 作用 |
| --- | --- |
| `main.py` | 正式 ROS / 前端联调入口，启动常驻 runtime 和文本命令接收服务 |
| `scripts/run_agent.py` | CLI 调试入口，支持 `--task` 注入任务、`--execute` 执行和向已有 runtime 投递新任务 |
| `scripts/send_command.py` | 向 CommandBus 写入控制命令，用于取消、暂停、恢复或插入新任务 |
| `adapters/command_bus.py` | 统一命令通道，将文本和控制信号规范化为事件 |
| `adapters/ros_text_command_service.py` | ROS2 文本服务适配层，接收 `genesis_msgs/srv/TextCommand` |
| `agent_runtime/engine.py` | 常驻运行循环，消费 CommandBus 并驱动 LangGraph 执行 |
| `agent_runtime/service.py` | 后台 runtime thread 封装，供 `main.py` 调用 |
| `graph/understanding/` | 指令理解、实体归一化、目标状态抽取和澄清逻辑 |
| `graph/planning/` | 任务分解、技能约束、sandbox 审计、repair strategy |
| `graph/task_management/` | 任务栈、中断、恢复、取消和暂停控制 |
| `graph/reflection/` | 失败层判断、反思修复和重试调度 |
| `execution/` | simulation / ROS 后端执行封装 |
| `skills/` | PrimitiveTool 技能契约、prompt、handler 和状态推进逻辑 |
| `benchmark/` | DELTA、EAI、ReAcTree、ALFRED、WAH 等 benchmark 接入与评测 |
| `docs/ARCHITECTURE.md` | 模块边界、数据流和长期架构约束 |

## 文本命令如何进入系统

正式运行时由 `main.py` 启动。外部系统发送文本后，链路如下：

```text
TextCommand.command
  -> TextCommandReceiver._on_command
  -> publish_text_command(cmd)
  -> publish_ros_interrupt_command(cmd)
  -> publish_interrupt_command(...)
  -> CommandBus
  -> agent_runtime/engine.py
```

其中 `TextCommand.command` 是原始文本；CommandBus 保存的是规范化后的命令事件；任务管理层消费的是结构化任务状态和任务栈。

## 启动方式

### CLI 只运行理解与规划

```bash
python scripts/run_agent.py --task '把土豆切成片' --once
```

默认是 plan-only 模式，会输出理解结果和规划结果，不进入执行层。

### CLI 运行到执行层

```bash
python scripts/run_agent.py --task '把土豆切成片' --execute
```

加入 `--execute` 后，规划通过可行性审计会继续进入执行层。默认执行后端由 `config/settings.json` 控制。

### 常驻监听模式

```bash
python scripts/run_agent.py --listen --execute
```

该模式会持续监听 CommandBus，适合和其他进程或外部脚本联调。

### ROS / 前端正式入口

```bash
python main.py
```

如果需要按实例号区分 ROS 服务命名空间，可以传端口或设置环境变量：

```bash
python main.py 5001
```

服务名规则：

```text
/genesis_arm/send_text_command
/genesis_arm_5001/send_text_command
```

ROS2 调用示例：

```bash
ros2 service call /genesis_arm/send_text_command genesis_msgs/srv/TextCommand "{command: '把土豆切成片'}"
```

## 外部中断与任务控制

执行中可以继续发送新任务：

```bash
python scripts/run_agent.py --task '去拿土豆' --execute
python scripts/run_agent.py --task '切番茄' --execute
```

如果已有常驻 runtime，第二条命令会写入同一个 CommandBus，而不是启动第二套 agent。任务管理层会把新任务作为 `new_task` 放入任务栈，优先执行新任务，再恢复旧任务。

也可以显式发送控制命令：

```bash
python scripts/send_command.py --kind cancel_current '取消当前任务'
python scripts/send_command.py --kind cancel_all '停止所有任务'
python scripts/send_command.py --kind pause '暂停'
python scripts/send_command.py --kind resume '继续'
```

常见命令类型：

| kind | 含义 |
| --- | --- |
| `new_task` | 插入新任务 |
| `cancel_current` | 取消栈顶任务，恢复下层任务 |
| `cancel_all` | 清空任务栈并停止当前链路 |
| `pause` | 暂停任务栈 |
| `resume` | 恢复已暂停任务 |

说明：当前实现是运行时调度层中断，不是操作系统级强杀。如果某个底层动作或外部工具调用本身阻塞，runtime 会在该调用返回或超时后处理下一条控制命令。

## 指令澄清机制

理解层判断信息不足时，会生成 `clarification_question`。在正式 ROS/前端链路中，runtime 不会阻塞等待终端输入，而是等待下一条外部 CommandBus 命令作为补充说明。连续多次无法完成澄清时，会放弃当前任务并回到空闲状态。

如果简单任务频繁进入澄清，通常需要先排查本地 LLM 端点：

```bash
curl --noproxy '*' http://<LLM_HOST>:<PORT>/v1/models \
  -H 'Authorization: Bearer qwen-local-key'
```

并检查 vLLM 端点是否拥塞：

```bash
curl --noproxy '*' -s http://<LLM_HOST>:<PORT>/metrics | grep -E "num_requests_(running|waiting)"
```

## 命令和任务状态存储

项目中有三类不同的状态记录：

- ROS 接收层的内存列表：只记录当前进程收到的原始文本，进程退出后消失。
- CommandBus jsonl：默认写入 `/tmp/ouragent_commands.jsonl`，记录规范化后的外部命令事件。
- 任务栈 `task_stack`：保存正在执行、被中断、待恢复的结构化任务状态。

CommandBus 不是完整任务数据库。runtime 启动时默认从命令文件末尾开始监听，旧命令不会在重启后自动重放。

## 失败反思与重试

执行链路失败后，状态中会记录 `failure_layer`：

| failure_layer | 处理方向 |
| --- | --- |
| `understanding` | 回到理解阶段，重新抽取任务目标、实体和约束 |
| `planning` | 回到规划阶段，重新生成或局部修复 todo_list |
| `execution` | 优先尝试执行层重试，必要时退回规划层重新分解 |

反思层会结合错误信息、状态差异和 trace 决定重试位置。达到最大重试次数后，任务会停止自动修复并返回失败状态。

## benchmark 与公平评测

benchmark 目录用于对齐不同论文方法、数据集和裸大模型基线。核心原则是：

- framework 和 bare baseline 使用同一份抽取/清洗后的 benchmark case；
- paper method 的中间状态不能作为 bare baseline 的输入；
- evaluator、adapter、action mapping 与主 runtime 语义保持隔离；
- 每次运行保留 trace、规划输出、状态差异和汇总报告，便于复盘。

通用运行形式：

```bash
python benchmark/<paper>/<dataset>/framework/code/run.py \
  --run-name <run_name> \
  --expected-count <count> \
  --workers <n> \
  --launch-shards 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key
```

## 环境说明

主要依赖包括：

- Python
- LangGraph / LangChain
- ROS2 `rclpy`
- `genesis_msgs.srv.TextCommand`
- OpenAI-compatible 本地 vLLM 服务
- pytest（用于单元测试）

如果本地没有 ROS 环境，可以先使用 CLI 模式验证理解、规划、任务管理和 CommandBus；ROS 服务需要在已 source ROS 工作区的 shell 中运行。

## 项目状态

本仓库是实习阶段构建的具身智能体 runtime 对外版本，重点展示系统结构、运行入口、任务中断恢复、失败反思和 benchmark 对齐能力。运行产物、锁文件、trace 和大规模实验中间输出已从公开版本中清理，核心代码、配置、技能、文档和 benchmark adapter 保留。
