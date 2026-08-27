# OurAgent-he1

面向具身任务、ROS 前端联调和命令行实验的 LangGraph Agent Runtime。这个仓库沉淀的是我实习阶段后期围绕“自然语言任务如何稳定进入机器人/仿真执行闭环”构建的一套工程化框架：统一文本入口、结构化理解、任务规划、任务栈管理、插单中断、失败反思、benchmark 对齐和 vLLM 并行实验。

它不是一个只把 prompt 串起来的 demo，而是一个更接近真实落地链路的 Agent 框架：

```text
ROS / Frontend / CLI Text
  -> CommandBus
  -> LangGraph Runtime
  -> Understanding
  -> Planning + Sandbox Audit
  -> Task Stack / Interrupt / Resume
  -> Execution Backend
  -> Reflection / Replan / Benchmark Report
```

## 项目亮点

- **多入口统一接入**：`main.py` 面向 ROS/前端正式联调，`scripts/run_agent.py` 面向 CLI 调试，两者最终都进入同一个 `CommandBus` 和同一个 runtime，不维护两套任务逻辑。
- **可中断任务调度**：新任务、取消、暂停、恢复都被归一化为命令事件；执行中收到新任务时，任务管理层会压栈当前任务，先执行插单任务，再恢复原任务。
- **LangGraph 分层编排**：用图节点拆分理解、规划、任务管理、执行、反思，避免把所有状态压进单个循环，方便定位失败层和做局部重试。
- **执行前审计**：规划结果会经过 sandbox evaluator、state-diff audit、playbook retrieval/write 等检查，降低直接把 LLM 输出交给执行层的风险。
- **失败反思闭环**：执行失败会保留 `failure_layer`、错误信息和中间状态，反思层可以按理解、规划、执行三类失败决定从哪一层重试。
- **benchmark 公平对齐**：框架侧和裸基线使用同一份抽取/清洗后的数据集，避免旧实验里用 paper method 中间结果跑 bare baseline 造成口径不一致。
- **vLLM 工程联调**：支持本地 Qwen vLLM 端点、并行 worker、端口切换和拥塞排查，能解释真实部署里“偶发指令补全/超时”的原因。

## 代码导航

| 模块 | 路径 | 作用 |
| --- | --- | --- |
| 正式入口 | `main.py` | ROS/前端联调入口，启动常驻监听和 AgentRuntimeThread |
| CLI 入口 | `scripts/run_agent.py` | 命令行任务注入、执行调试、向已有 runtime 投递插单 |
| 命令总线 | `adapters/command_bus.py` | 统一 new_task/cancel/pause/resume 等外部命令 |
| ROS 文本适配 | `adapters/ros_text_command_service.py` | 接收 `genesis_msgs/srv/TextCommand` 并转发到 CommandBus |
| Runtime | `agent_runtime/engine.py` | 常驻消费命令，驱动 LangGraph 图执行 |
| 图编排 | `graph/` | Understanding、Planning、Task Management、Reflection 主流程 |
| 动作技能 | `skills/` | PrimitiveTool 契约、参数校验、状态推进 |
| 认知规划 | `cognitive/` | KG、SceneGraph、TaskGraph、BehaviorTree 等高级规划实验 |
| benchmark | `benchmark/` | 数据集适配、实验入口、baseline/framework 对齐说明 |
| 架构文档 | `docs/ARCHITECTURE.md` | 模块边界、数据流、后续重构约束 |

## 面试官可以重点看

1. `main.py`、`adapters/command_bus.py`、`agent_runtime/engine.py`：看 ROS/前端文本如何进入同一套 Agent runtime。
2. `graph/task_management/`：看任务栈、中断、取消、恢复的工程化处理。
3. `graph/planning/`、`skills/`：看 LLM 规划如何被技能契约和 sandbox 审计约束。
4. `benchmark/README_index.md`、`benchmark/README_bare_baseline.md`：看 framework 和裸基线如何保持同一数据口径。
5. `docs/ARCHITECTURE.md`：看整体架构边界，不把 benchmark、动作语义和主图编排混在一起。

## 先说结论

- 核心运行循环是 `agent_runtime/engine.py`；推荐 CLI 入口是 `scripts/run_agent.py`（参数解析）+ `scripts/renderer.py`（终端渲染）。
- 正式 ROS/前端联调入口是 `main.py`：它启动后常驻监听文本命令，并把命令交给同一个任务 runtime。
- 这里不再使用独立的 `run_console.py` 作为主入口，历史上的控制台渲染逻辑已经收敛到 `scripts/renderer.py`。
- 控制台默认是 `plan_only`，也就是只做理解 + 规划，默认不会进入执行层。
- 你说的“把字符串直接注入 console”已经实现了，入口是 `--task`。
- 如果已有执行中的 runtime，再运行一次 `scripts/run_agent.py --task ... --execute`，这次调用会自动变成“投递新任务”，不会再启动第二套 agent。

## 当前有哪些功能

### 理解层

当前 `config/settings.json` 里启用的理解层特征是：

- `cancel`
- `llm_extract`
- `normalize`
- `entity_repair`
- `goal_state_extract`
- `skill_closure`
- `relevant_items`
- `clarification`

其中：

- `entity_repair` 默认开启。
- `goal_state_extract` 代码里有实现，但默认关闭。
- 其余理解特征默认都会进入主流程。

### 规划层

当前规划层默认会用到：

- `sandbox_evaluator`
- `state_diff_audit`
- `playbook_retrieval`
- `playbook_write`
- `reflection`

当前默认关闭：

- `cognitive_planning`
- `cognitive_lightweight_path`
- `cognitive_bt_compile`
- `cognitive_bt_execute`
- `cognitive_bt_recovery_direct_replan`
- `cognitive_bt_execution_reflection_retry`
- `candidate_rules`
- `cognitive_trace_write`

规划层当前的修复策略是 `retrac`。

### 执行层

当前执行层默认配置是：

- `backend = simulation`
- `sync_runtime_scene = true`
- `ros.timeout_sec = 30`

也就是说，默认是仿真执行，不是空跑。

## 框架默认会不会用到

如果你只是跑 `scripts/run_agent.py` 的默认模式：

- 会用理解层
- 会用规划层
- 不会自动进入执行层

如果你加 `--execute`：

- 会继续进入执行层
- 会走任务管理、执行、反馈闭环

如果你跑正式 benchmark：

- 会走理解层
- 会走规划层
- 会走数据集自己的 parser / adapter / skill contract
- 会走 sandbox 和 state-diff 审计
- 需要时会走 reflection / retrac

## 正式 ROS/前端文本输入链路

正式入口是 `main.py`。它的职责很窄，只做三件事：

1. 解析实例号或端口，设置 `GENESIS_WEB_PORT` 和 `ROS_DOMAIN_ID`。
2. 启动 `agent_runtime.service.AgentRuntimeThread`，让 LangGraph runtime 在后台常驻。
3. 创建 ROS 服务 `TextCommandReceiver`，对外接收 `genesis_msgs/srv/TextCommand`。

如果传 `--no-agent-runtime`，`main.py` 只保留 ROS 接收层，不会启动任务 runtime。

文本不是直接写进图里，而是先进入统一命令通道：

`TextCommand.command` -> `TextCommandReceiver._on_command` -> `publish_text_command(cmd)` -> `publish_ros_interrupt_command(cmd)` -> `publish_interrupt_command(...)` -> CommandBus -> `agent_runtime/engine.py`

你最开始贴出来的那段代码，思路本身就是“收到一条文本，再留一个后续处理入口”。其中：

- `RECEIVED_TEXT_COMMANDS` 只是调试用的历史记录。
- 旧的 `handle_text_command(cmd)` 只是一个空 hook，默认并不真正驱动任务。
- 现在真正的驱动点已经转移到 `adapters/command_bus.py` 和 `agent_runtime/engine.py`，文本会先被规范化成命令，再由任务管理层消费。

### 外部怎么提供文本

ROS 侧的标准调用形式是：

```bash
ros2 service call /genesis_arm/send_text_command genesis_msgs/srv/TextCommand "{command: '把土豆切成片'}"
```

如果你启动的是实例端口 `5001`，服务名会变成：

```bash
/genesis_arm_5001/send_text_command
```

请求只需要填 `command` 字段。服务回包会带 `received` 和 `message`，用于确认收到的原始文本。

如果前端不是 ROS-native，就要先通过 ROS2 client、rosbridge 或你自己的适配层，把文本转成同一个 `TextCommand` 请求，再走上面的链路。

### 部署机器必须能访问 LLM 端点

理解层/规划层都会调用本地 LLM。默认配置在 `config/settings.json` 的 `model` 段：

```json
{
  "api_base": "http://192.168.27.250:18003/v1",
  "model_name": "Qwen3.6-27B",
  "base_host": "192.168.27.250"
}
```

**注意：`192.168.27.250` 是内网地址。** 如果 ROS/前端跑在另一台机器上，那台机器必须能连通这个 IP:端口，否则每次理解都会失败，表现为“命令进去后一直要求指令补全”（澄清），因为 LLM 调用抛 `Connection error`，理解层兜底为 `needs_clarification=True`。

**另一个更隐蔽的原因：LLM 端点拥塞/超时。** 理解层默认 `timeout=120s`。如果同一时间有别的实验（例如 alfred/virtualhome benchmark 并行 worker）在打同一个 vLLM 端口，单次 LLM 调用可能要 20~60s 甚至更久；一旦超过 120s 或排队过长，`llm_extract` / `entity_repair` 就会抛 `APITimeoutError`，理解层兜底为 `needs_clarification=True`，话术是“抱歉，指令理解模块执行异常，请重新说明任务。”——这**不是代码 bug，也不是实体对齐问题**，纯粹是 LLM 太忙。判断方法：

```bash
# 看端口当前负载（running/waiting 高就说明在排队）
curl --noproxy '*' -s http://192.168.27.250:18003/metrics | grep -E "num_requests_(running|waiting)"
# 实测单次调用耗时（明显大于 20s 就是拥塞）
time curl --noproxy '*' -s http://192.168.27.250:18003/v1/chat/completions \
  -H "Authorization: Bearer qwen-local-key" -H "Content-Type: application/json" \
  -d '{"model":"Qwen3.6-27B","messages":[{"role":"user","content":"hi"}]}'
```

排查时注意：“拿土豆要补全、拿鸡蛋可以”这类**随机/间歇性**现象，几乎总是 LLM 拥塞导致偶发超时，而不是指令本身有问题。

部署到别的机器时，按下面任一方式改：

1. 改 `config/settings.json` 里 `model.base_host` / `model.api_base`，指向测试机能访问的地址（例如 vLLM 所在机器对外的 IP）。
2. 或启动前设置环境变量覆盖（优先级高于 settings.json）：
   - `OURAGENT_LLM_BASE_HOST=<可达IP>`：覆盖 base_host。
   - `OURAGENT_LLM_STICKY_HOST=<可达IP>`：强制所有本地端点的请求都打到这个 host。
   - `OURAGENT_COMMAND_FILE=<路径>`：覆盖命令通道文件（多实例时才需要）。

验证连通性（不带代理直接测）：

```bash
curl --noproxy '*' http://<可达IP>:18003/v1/models -H "Authorization: Bearer qwen-local-key"
```

### 指令补全（澄清）在正式链路里怎么工作

当理解层认为指令信息不足（或 LLM 调用失败）时，会设置 `needs_clarification=True` 和 `clarification_question`。

- 纯交互控制台（`scripts/run_agent.py` 不带 `--listen`）：runtime 会打印 `[指令补全] >>> ` 并在终端等你补输入。
- 正式 ROS/前端链路（`main.py`，即外部驱动模式）：runtime **不会**阻塞在终端 stdin 上等输入。它会：
  1. 把澄清问题打印到日志；
  2. 等待下一条外部 CommandBus 命令作为补充说明（你可以再用 `ros2 service call` 或 `send_command.py` 补发一条更完整的命令）；
  3. 如果连续 `MAX_CLARIFICATION_ATTEMPTS`（当前为 3）次都无法完成澄清，放弃当前任务，回到空闲等待下一条命令，而不是无限循环或挂死。

所以，正式联调里如果机器人“要求补全”，按顺序排查：

1. 命令是否真的进了 CommandBus（看 `/tmp/ouragent_commands.jsonl`）。
2. 部署机能不能访问 LLM 端点（`curl --noproxy '*'`）。
3. **LLM 是不是正被其他实验占满**（看 metrics 的 running/waiting，实测单次调用耗时）——这是“某些指令偶尔要补全、另一些指令正常”的头号原因。

### 命令会不会存储

会，但分三层，含义不一样：

- ROS 接收层会把本进程收到的原始文本追加到 `RECEIVED_TEXT_COMMANDS`，这是内存列表，只用于调试；进程退出后就没了。
- CommandBus 会把规范化后的命令写到默认 jsonl 文件 `/tmp/ouragent_commands.jsonl`，也可以用 `OURAGENT_COMMAND_FILE` 改路径。
- 执行阶段不会直接执行原始字符串，而是先经过理解和规划，生成 `todo_list`，再由任务管理层保存到 `task_stack`。

因此，`TextCommand.command` 是原始输入；CommandBus 保存的是统一命令；`task_stack` 保存的是正在执行或被插单挂起的任务状态。

这个 jsonl 文件不是完整任务数据库。runtime 启动时默认从文件末尾开始监听，所以旧命令不会因为重启而自动重放。

### 现在谁负责什么

- `main.py`：只负责启动常驻监听和 runtime，不负责业务推理。
- `adapters/ros_text_command_service.py`：ROS 文本服务适配层，负责接收和转发。
- `adapters/ros_bridge.py`：把 ROS payload 归一化成普通命令对象。
- `adapters/command_bus.py`：统一 `new_task`、`cancel_all`、`cancel_current`、`pause`、`resume` 等命令。
- `agent_runtime/engine.py`：常驻消费 CommandBus，驱动 LangGraph 执行。
- `graph/task_management/node.py`：处理插单、压栈、恢复、取消和暂停。

### 插单和取消怎么工作

执行中收到第二条任务时，会进入同一个 CommandBus。任务管理层会把它当作新的 `new_task` 放进 `task_stack`，先处理新任务，再恢复旧任务。

取消类文本会走同一条通道：

- `cancel_all`：清空任务栈，停止当前链路。
- `cancel_current`：取消栈顶任务，恢复下层任务。
- `pause` / `resume`：暂停或恢复任务栈。

这不是硬件级强杀。当前动作如果本身是阻塞的，系统只能在该动作返回后进入下一次调度，再消费新的中断命令。

### 反思和失败

第三阶段或执行阶段出错时，任务会先标成 `failed`，并带上 `failure_layer`。

如果开启了 reflection：

- `failure_layer=understanding` 会回到理解重试。
- `failure_layer=planning` 会回到规划重试。
- `failure_layer=execution` 可以回到执行重试，必要时也会退回规划。

如果同一层反复失败，反思层会逐级升级，直到超过 `max_retries` 并停止自动修复。

当前没有一个单独的全局 `impossible` 标志。也就是说，框架会根据失败层和重试次数尽量修复；如果你想显式标记“本身不可完成”，需要再加一层独立状态或策略。

### 标准启动方式

正式 ROS / 前端联调用这个：

```bash
/data/zmy/envs/ouragent/bin/python main.py
```

带实例号时：

```bash
/data/zmy/envs/ouragent/bin/python main.py 5001
```

CLI 调试仍然用这个：

```bash
/data/zmy/envs/ouragent/bin/python scripts/run_agent.py --task '你的任务' --execute
```

`scripts/run_agent.py` 是唯一 CLI 入口（参数解析 + 调引擎），终端渲染在 `scripts/renderer.py`（原 `run_console.py` 已并入）。

## 怎么用控制台

先切到仓库根目录：

```bash
cd /data/zmy/OurAgent-he1
export OURAGENT_WORKSPACE_ROOT=/data/zmy
```

### 只跑理解 + 规划

```bash
/data/zmy/envs/ouragent/bin/python scripts/run_agent.py --task '把土豆切成片' --once
```

说明：

- `--task` 把第一条任务字符串直接注入控制台
- `--once` 处理完第一轮就退出，适合脚本调用
- 这是默认的 `plan_only` 模式，不会继续执行动作

### 跑到执行层

```bash
/data/zmy/envs/ouragent/bin/python scripts/run_agent.py --task '把土豆切成片' --execute
```

说明：

- `--execute` 会关闭 `plan_only`
- 规划通过后会继续进入执行层
- 如果你只想看理解和 todo_list，不要加 `--execute`

### 外部中断 / 插单

CLI 调试时，也可以直接用同一条启动命令模拟这个行为。第一个进程启动主任务：

```bash
/data/zmy/envs/ouragent/bin/python scripts/run_agent.py --task '去拿土豆' --execute
```

它还在执行或休眠监听时，第二个终端继续运行：

```bash
/data/zmy/envs/ouragent/bin/python scripts/run_agent.py --task '切番茄' --execute
```

第二个进程会检测到已登记的 runtime，把 `切番茄` 投递为 `new_task` 后退出；第一个进程里的任务管理层负责中断、压栈、恢复。

手工发控制命令仍然可以用：

```bash
/data/zmy/envs/ouragent/bin/python scripts/send_command.py --kind cancel_all '不要做了'
```

常见 `kind`：

- `new_task`：插入新任务；执行完后恢复原任务栈。
- `cancel_all`：清空任务栈并停止。
- `cancel_current`：取消栈顶任务，恢复下面的任务。
- `pause` / `resume`：暂停或恢复已保留的任务栈。

本机多进程默认通道是 `/tmp/ouragent_commands.jsonl`，也可以用 `OURAGENT_COMMAND_FILE` 环境变量覆盖。正常使用不需要传 `--command-file`；只有同时跑多个 agent 实例时才需要显式区分通道。

ROS 文本服务接收逻辑见上面的正式链路说明；它收到 `TextCommand.command` 后会进入同一个 CommandBus，任务管理层只消费统一的命令，不依赖 ROS 版本。

### 纯交互

```bash
/data/zmy/envs/ouragent/bin/python scripts/run_agent.py
```

说明：

- 先读 stdin 里的第一条输入
- 之后按控制台提示继续输入

## 环境复原

当前控制台不是“每个任务自动回到初始场景”的模式。

- `agent_runtime/engine.py` 只在启动时调用一次 `reset_runtime_from_initial()`。
- 同一个控制台会话里，后续新任务会继承上一次已经被执行修改过的 runtime scene。
- `config/scene_state.py` 里有 `snapshot_scene()` / `restore_scene()` / `reset_runtime_from_initial()` 这组接口，但默认没有接到任务结束自动回滚。
- `Slice` 这类技能会真实改变环境状态，比如把刀弄脏，所以如果你想复原，就必须显式追加 cleanup 步骤。

现在可用的解决法有三种：

1. 每次 demo 重新启动控制台。
2. 在任务结束后显式调用 `reset_runtime_from_initial()` 或 `restore_scene(snapshot)`。
3. 如果你要让模型自己收尾，就把“归位、清洁、关门、恢复现场”写进任务目标或规则里。

benchmark 侧已经有更强的恢复链路，比如 `state_diff_audit` 的修复分支和 `state_recovery`，但那不是 agent runtime 的默认路径。

## 正式 benchmark 怎么跑

正式入口是各数据集自己的 `framework/code/run.py`，不要直接跑 `launcher.py` 或 `_case_worker.py`。

通用形式：

```bash
/data/zmy/envs/ouragent/bin/python benchmark/<paper>/<dataset>/framework/code/run.py \
  --run-name <run_name> \
  --expected-count <count> \
  --workers <n> \
  --launch-shards 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key
```

常见端口：

- `18003` -> `Qwen3.6-27B`
- `18004` -> `Qwen3.5-9B`
- `8005` -> `Qwen3.5-9B-alfred`

一个 EAI VirtualHome 示例：

```bash
/data/zmy/envs/ouragent/bin/python benchmark/eai/virtualhome/framework/code/run.py \
  --run-name eai_virtualhome_full_example \
  --expected-count 342 \
  --workers 1 \
  --launch-shards 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key
```

## 你问的字符串注入

已实现。

实现方式不是改死文件常量，而是直接用命令行参数：

```bash
--task '你的第一条任务字符串'
```

内部会把它传给 `run_engine(initial_instruction=args.task, ...)`，作为第一条输入使用。

如果你要的是“从环境变量自动读字符串”，那不是当前实现；现在支持的是 CLI 注入。
