# Embodied Agent Runtime 面试展示版增强说明

本文说明 `/data/zmy/OurAgent-he1-interview` 相比原始运行仓库增加了哪些工程化能力。原始 `/data/zmy/OurAgent-he1` 未被改动，仍可继续跑当前任务。

## 目录裁剪

为了让展示仓库更聚焦，副本中移出了不参与当前主线讲解的历史模块：

- `cognitive/`
- `interfaces/`
- `references/`
- `SDA/`
- `graphify-out/`
- `logs/`

这些目录没有从原项目删除，只是从面试副本中移走。被移走内容暂存在 `/data/zmy/OurAgent-he1-interview_removed_20260827`，后续如果发现某条旧测试依赖它，可以再恢复或改成可选依赖。

## 新增 Trace Harness

新增文件：

- `adapters/tracing/harness.py`
- `tests/adapters/test_trace_harness.py`

它解决的是 Agent 运行时最常被追问的问题：一次任务失败后，怎么定位是理解、规划、工具调用、执行还是反思失败。

核心能力：

- 每个任务生成 `trace_id` / `task_id`。
- 记录节点事件、工具事件、失败事件。
- 只记录可观测摘要，不记录模型内部推理链。
- 支持按 `trace_id` 回放。
- 支持生成 summary：步数、失败层、节点分布、累计耗时。
- 支持两次运行结果对比，便于讲 A/B、回归测试和优化收益。

示例：

```python
from adapters.tracing import TraceHarness

harness = TraceHarness()
harness.record_node("understanding", input_summary="把土豆切片", output_summary="intent=Slice")
harness.record_tool("Pickup", arguments={"target_item": "土豆_1"}, observation="ok", latency_ms=12.5)
harness.record_failure("execution", "刀具不可达", node="Slice")

events = harness.replay()
summary = TraceHarness.summarize(events)
```

## 新增 Redis CommandBus

新增能力位于：

- `adapters/command_bus.py`
- `tests/adapters/test_redis_command_bus.py`

它解决的是多入口任务投递问题：ROS、Web 前端、CLI、测试脚本都可以把文本命令统一写入 CommandBus，runtime 只消费标准化后的命令。

默认仍然是内存或 JSONL，不依赖 Redis。只有显式设置时才启用：

```bash
export OURAGENT_COMMAND_BUS=redis
export OURAGENT_REDIS_URL=redis://localhost:6379/0
export OURAGENT_REDIS_STREAM=ouragent:commands
export OURAGENT_REDIS_GROUP=ouragent-runtimes
python main.py
```

Redis 版适合面试讲生产部署：

- 多进程不会各自维护孤立队列。
- 可以按 stream id 做 ack，避免命令丢失。
- 可以扩展 priority、session_id、robot_id，实现多机器人或多会话调度。

## 新增 MCP 技能适配层

新增文件：

- `adapters/mcp_skill_adapter.py`
- `scripts/export_skill_mcp_manifest.py`
- `tests/adapters/test_mcp_skill_adapter.py`

它把现有 `skills/*/skill.yaml` 和 `prompt.md` 抽成 MCP 风格工具描述。这样面试时可以讲清楚：

- `Skill` 是机器人可执行能力。
- `Function Calling` 是模型选择工具的调用格式。
- `MCP` 是把工具能力标准化暴露给 Agent 的协议层。
- OurAgent 的技能库可以导出为工具清单，后续接 MCP server 或前端工具市场。

导出命令：

```bash
python scripts/export_skill_mcp_manifest.py --include-all
```

默认会生成：

```text
docs/mcp_skill_manifest.json
```

## 千问 3.5 / 3.6 是否还能用

可以。新增模块不绑定模型，只依赖你原来的 OpenAI-compatible 接口配置。

只要 `config/settings.json` 或环境变量指向可访问的 vLLM / API endpoint，就可以继续使用 Qwen 3.5 或 Qwen 3.6：

```bash
export LANGGRAPH_JSZN_API_BASE=http://<vllm-ip>:<port>/v1
export LANGGRAPH_JSZN_API_MODEL=Qwen3.6-27B
export LANGGRAPH_JSZN_API_KEY=qwen-local-key
```

模型版本影响理解/规划质量，不影响 CommandBus、Trace Harness、MCP 技能导出这些工程层。

## 推荐验证命令

```bash
python -m py_compile \
  adapters/command_bus.py \
  adapters/mcp_skill_adapter.py \
  adapters/logging_handler.py \
  adapters/tracing/jsonl.py \
  adapters/tracing/harness.py \
  graph/planning/evaluation/validation/native_action_validator.py \
  graph/planning/evaluation/validation/todo_validator.py \
  scripts/export_skill_mcp_manifest.py

python scripts/verify_architecture.py

python -m pytest \
  -q
```

当前展示仓库的验证结果：

- `scripts/verify_architecture.py` 通过。
- `/data/zmy/portfolio_workspace/github/Embodied-Agent-Runtime` 中 `pytest -q` 结果为 `225 passed, 1 skipped`。
- `/data/zmy/OurAgent-he1-interview` 独立副本中 `pytest -q` 结果为 `222 passed, 1 skipped`，少的 3 个用例来自公开仓库中保留的 benchmark 辅助测试。
- 唯一 skipped 用例依赖外部 ReActree ALFRED 技能包，该外部包不随公开 runtime 导出。
- 顶层 legacy `SDA/` 已移除；默认修复策略使用 `ReTrac`，内部 `graph/planning/evaluation/repair_strategies/sda/` 仍保留为策略研究对照。
