# Codex 续接状态

- 原 session id: `01a01d05-abc7-73c2-ba8b-a6dfa65200ed`
- rollout: `/data/zmy/.codex_runtime/sessions/2026/08/20/rollout-2026-08-20T02-35-06-01a01d05-abc7-73c2-ba8b-a6dfa65200ed.jsonl`
- 当前工作区: `/data/zmy/OurAgent-he1`

## 任务目标

用户要的不是暴露 `command-file` 或强制使用 `scripts/send_command.py`，而是：

- 框架启动后常驻监听 ROS/前端文本命令。
- 第一条任务进入 agent 执行。
- 执行中第二条任务到来时，中断当前任务，保留原 `task_stack` 断点，优先执行新任务。
- 新任务完成后恢复原任务。
- CLI 调试时，第二次执行 `scripts/run_console.py --task ... --execute` 也应表现为向已有 runtime 投递新任务，而不是启动第二套独立 agent。

## 已完成

- 新增 `agent_runtime/process_registry.py`：用 `/tmp/ouragent_runtime.json` 登记活跃 runtime 的 pid 和 CommandBus 通道。
- 新增 `agent_runtime/service.py`：提供 `AgentRuntimeThread`，供 `main.py` 后台启动常驻图运行器。
- 修改 `scripts/run_console.py`：
  - 去掉对 `main.app` 的依赖，直接 `build_main_graph()`，避免 ROS 入口和控制台入口互相耦合。
  - 执行模式默认登记 runtime。
  - 已有 runtime 时，第二次 `--task ... --execute` 自动转发为 `new_task` 并退出。
  - 常驻 `listen` 模式下从 CommandBus 等待第一条和后续任务。
- 修改 `main.py`：
  - 已将 ROS TextCommand 接收细节抽到 `adapters/ros_text_command_service.py`。
  - `main.py` 现在只负责启动后台 `AgentRuntimeThread` 和 ROS service。
  - 支持 `--no-agent-runtime` 保留旧的只接收/回显模式。
- 新增 `adapters/ros_text_command_service.py`：负责 ROS service 名称、ROS_DOMAIN_ID、TextCommandReceiver 和文本命令投递。
- 清理 `adapters/ros_bridge.py` 中无人引用的 `receive_interrupt_command()`。
- 更新 `README.md`、`console_framework_guide.md`、`docs/console_framework_guide.md`，把推荐路径改为 `main.py` 常驻监听和 CLI 自动转发。

## 验证

- `python -m py_compile main.py scripts/run_console.py scripts/send_command.py adapters/command_bus.py adapters/ros_bridge.py agent_runtime/__init__.py agent_runtime/process_registry.py agent_runtime/service.py tests/agent_runtime/test_process_registry.py tests/adapters/test_command_bus.py tests/graph/test_task_management_interrupts.py`
- `/data/zmy/envs/ouragent/bin/python -m pytest tests/agent_runtime/test_process_registry.py tests/adapters/test_command_bus.py tests/graph/test_task_management_interrupts.py tests/graph/test_graph_nodes.py -q`
- 手工验证：伪造活跃 runtime 后运行 `/data/zmy/envs/ouragent/bin/python scripts/run_console.py --task '切番茄' --execute`，确认它写入 `{"kind": "new_task", "text": "切番茄", ...}` 并退出。
- 后续抽取验证：`python -m py_compile main.py adapters/ros_text_command_service.py adapters/ros_bridge.py adapters/command_bus.py adapters/sandbox.py adapters/tracing/jsonl.py scripts/run_console.py agent_runtime/service.py agent_runtime/process_registry.py`，以及同一组 26 个 pytest 通过。

## 后续建议

- 在已 source ROS 环境的 shell 里运行 `/data/zmy/envs/ouragent/bin/python main.py`，再从前端/ROS TextCommand 服务连续发两条任务做端到端验证。
- 如果要同时跑多个机器人实例，用 `OURAGENT_COMMAND_FILE` 和 `OURAGENT_RUNTIME_STATUS_FILE` 分别隔离每个实例。
