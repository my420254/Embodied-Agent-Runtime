# DELTA Framework Smoke Audit

更新时间：2026-08-06 18:10 UTC

## 结论

DELTA 3.5 冒烟已通过。当前框架不再使用 `planning_output_mode=native_actions` 选择 parser/evaluator；`todo_list` 内直接保存 DELTA 论文动作 JSON，不再包成 `execution/skill/parameters`。

本次 smoke：

- case：`dining:allensville:episode-01`
- 模型接口：18004
- 模型名：`Qwen3.5-9B`
- 运行命令：

```bash
python benchmark/delta/framework/code/run.py \
  --run-name delta_audit_smoke_20260806_todo_hooks \
  --case-id dining:allensville:episode-01 \
  --workers 1 \
  --ports 18004 \
  --api-model Qwen3.5-9B \
  --api-key qwen-local-key
```

结果：

- `task_success=true`
- `task_success_rate=1.0`
- `evaluation_route=val`
- `val_success=true`
- `symbolic_success=true`
- `execution_status=completed`
- `is_feasible=true`
- `todo_parse_error=""`
- `official_actions_len=25`
- `todo_contract_status=passed`
- `validated_todo_actions_count=25`
- `state_diff_audit.passed=true`
- sandbox 拦截：0

完整 artifacts 已复制到：

```text
/data/zmy/OurAgent-he1/benchmark/framework_experiment_records/delta_artifacts/smoke_todo_hooks
```

## 本次代码对齐

本次已清理掉旧的内部模式债：

- 删除 benchmark runtime 的 `planning_output_mode`。
- 删除 `graph/planning/node.py` 中按 `native_actions` 分 evaluator 的逻辑。
- 五个 benchmark settings 统一改成：
  - `todo_output_parser`
  - `todo_step_adapter`
  - `todo_list_validator`
- planning state 统一改成：
  - `todo_output_parser_path`
  - `todo_step_adapter_path`
  - `todo_list_validator_path`
  - `todo_llm_output`
  - `todo_parse_error`
  - `validated_todo_actions`
  - `todo_checkpoint_env`
  - `todo_checkpoint_robot`
- sandbox 只看当前 `todo_list` 和当前数据集的 `todo_step_adapter_path` 做审计；没有 benchmark/native action 旁路。

保留的 `benchmark.delta.framework.code.native_actions.*` 是 DELTA 数据集官方动作解析/导出工具文件名，不是框架内分流模式。它现在作为 `todo_output_parser` / `todo_step_adapter` 使用。

## DELTA 的 todo_list 格式

当前 DELTA planning prompt 要求模型直接输出 JSON 数组，每一项就是 DELTA 动作。例如本次前 5 步：

```json
[
  {"step": 1, "action": "goto", "agent": "robot", "room_1": "living_room", "room_2": "dining_room"},
  {"step": 2, "action": "goto", "agent": "robot", "room_1": "dining_room", "room_2": "kitchen"},
  {"step": 3, "action": "pick", "agent": "robot", "item": "fork", "room": "kitchen"},
  {"step": 4, "action": "goto", "agent": "robot", "room_1": "kitchen", "room_2": "dining_room"},
  {"step": 5, "action": "place_on", "agent": "robot", "item_1": "fork", "item_2": "dining_table", "room": "dining_room"}
]
```

没有 `execution` 字段，没有 framework skill 包装。沙盒内部临时用 `todo_step_adapter_path=benchmark.delta.framework.code.native_actions.delta_native_step_to_skill_call` 把单步动作映射到 handler 参数，只用于检查环境变更，不改变 `todo_list` 本体。

## 输入与环境闭包

本次 task：

```text
Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.
```

planning 输入记录：

```text
.../smoke_todo_hooks/artifacts/planning_input.json
.../smoke_todo_hooks/artifacts/planning_input_summary.json
```

环境闭包摘要：

- 环境实体数：18
- 房间/通路包含：`living_room`, `dining_room`, `kitchen`, `bedroom_1`, `bedroom_2`, `lobby`, `corridor_1`, `corridor_2`, `corridor_3`, `bathroom_1`, `bathroom_2`
- 关键物体：`dining_table`, `plate`, `fork`, `knife`, `spoon`, `glass`, `flower`
- 初始机器人：`robot_location=living_room`, `robot_holding=空`
- 终态机器人：`robot_location=dining_room`, `robot_holding=空`

环境闭包来自 benchmark 的 `build_sandbox_environment`，不是框架硬编码的统一环境。planning/sandbox/state-diff 都读同一份 DELTA 环境。

## 检查链路

1. Understanding 输出结构化任务和最终态。
2. Planning prompt 注入 DELTA 当前技能契约，模型输出 DELTA JSON 数组。
3. `todo_output_parser` 解析 JSON 数组，并按 DELTA schema 检查动作字段。
4. `todo_contract` 使用 DELTA skill.yaml 的 planner schema 检查动作名、必填字段、固定字段、实体字段、房间字段、额外字段。
5. sandbox 用 `todo_step_adapter` 将每个 DELTA step 映射到 handler 参数后执行。
6. state-diff audit 检查 sandbox 前后状态是否满足 understanding 的最终态。
7. 官方 DELTA PDDL/VAL evaluator 在 planning 结束后执行，不进入 prompt。

本次 contract 结果：

- configured raw actions：13
- observed actions：25
- unknown observed actions：[]
- `todo_list_count=25`
- `validated_todo_actions_count=25`
- `validated_steps_count=0`

## LLM 调用

本次 trace 记录 4 次模型调用：

- `understanding.system`
- `understanding.final_state`
- `planning.main_system`
- `planning.state_diff_audit`

完整输入输出：

```text
.../smoke_todo_hooks/artifacts/llm_io.json
.../smoke_todo_hooks/trace_report.md
```

## 全量运行

DELTA 3.5 全量已完成：

```bash
tmux attach -t delta_full_todo_20260806
```

启动命令：

```bash
python benchmark/delta/framework/code/run.py \
  --run-name delta_framework_full_20260806_todo_hooks \
  --workers 2 \
  --ports 18004 \
  --api-model Qwen3.5-9B \
  --api-key qwen-local-key
```

实际 `launch_manifest.json` 显示本次 full 是 5 切片调度：

- `selected_case_count=600`
- `scheduled_command_count=600`
- `unit_count=5`
- `endpoint_slots=2`，两个 slot 都指向 `18004/Qwen3.5-9B`
- command 的 `unit_index` 覆盖 `0..4`

也就是说，`--workers 2` 只生成两个同端口 endpoint slot；因为 DELTA launch config 默认 `shards_per_interface=5`，没有显式覆盖 `--launch-shards` 时，实际仍按 5 个 launch unit/shard 切片调度。

日志：

```text
/data/zmy/OurAgent-he1/benchmark/delta/framework/results/delta_framework_full_20260806_todo_hooks.tmux.log
```

当前 `summary.json` 统计：

- `count=600`
- `task_success_count=303`
- `task_success_rate=0.505`
- `official_available_count=327`
- `official_task_success_count=303`
- `official_task_success_rate=0.926605504587156`
- `symbolic_success_count=156`
- `symbolic_success_rate=0.26`
- domain breakdown：clean 0/150，dining 150/150，office 3/150，pc 150/150
