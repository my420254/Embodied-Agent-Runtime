# OurAgent-he1 框架与控制台使用说明

本文只说明当前仓库里已经存在、并且默认会走的能力，以及如何从命令行启动。

## 先说结论

- 核心运行循环是 `agent_runtime/engine.py`；推荐 CLI 入口是 `scripts/run_agent.py`。
- `scripts/run_agent.py` 是唯一 CLI 入口（参数解析 + 调引擎），终端渲染在 `scripts/renderer.py`（原 `run_console.py` 已并入）。
- 正式 ROS/前端联调入口是 `main.py`：它启动后常驻监听文本命令，并把命令交给同一个任务 runtime。
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

正式 ROS/前端路径是先启动常驻服务：

```bash
/data/zmy/envs/ouragent/bin/python main.py
```

`main.py` 会监听 `/genesis_arm/send_text_command`，收到第一条文本任务就开始执行；执行中再收到第二条文本任务，就会中断当前任务、保留剩余 task_stack，先规划并执行新任务，新任务完成后恢复原任务。

CLI 调试时，也可以直接用同一条启动命令模拟这个行为。第一个进程启动主任务：

```bash
/data/zmy/envs/ouragent/bin/python scripts/run_agent.py --task '把土豆切成片' --execute
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

ROS 文本服务接收逻辑在 `adapters/ros_text_command_service.py`；它收到 `TextCommand.command` 后调用 `adapters.ros_bridge.publish_ros_interrupt_command(...)`，任务管理层只消费统一的 CommandBus，不依赖 ROS 版本。

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
