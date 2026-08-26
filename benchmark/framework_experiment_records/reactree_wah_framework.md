# ReAcTree WAH Framework Smoke Audit

更新时间：2026-08-06 18:42 UTC

## 结论

ReAcTree WAH 3.6 冒烟已通过。当前框架不再用 `planning_output_mode=native_actions` 分流；`todo_list` 内直接保存 WAH/ReAcTree 原生动作 JSON，每步形如 `{"action": "go to", "target": "kitchen table 1"}`，不是 framework 的 `execution/skill/parameters` 包装。

本次 smoke：

- case：`0:0`
- task：`prepare_snack`
- instruction：`Put one cupcake and one apple on the coffee table`
- eval mode：`graph_replay`
- 模型接口：18003
- 模型名：`Qwen3.6-27B`
- 运行命令：

```bash
python benchmark/reactree/wah/framework/code/run.py \
  --run-name reactree_wah_smoke_20260806_todo_hooks_fix2 \
  --limit 1 \
  --expected-count 1 \
  --workers 1 \
  --launch-shards 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key \
  --eval-mode graph_replay
```

结果：

- `count=1`
- `task_success_count=1`
- `task_success_rate=1.0`
- `goal_success_rate=1.0`
- `subgoal_success_rate=1.0`
- `evaluation_mode=reactree_graph_replay_debug`
- `official_available_count=0`
- `execution_status=completed`
- `is_feasible=true`
- `todo_parse_error=""`
- `todo_count=8`
- `validated_todo_actions_count=8`
- `state_diff_audit.passed=true`
- sandbox 拦截：0

完整 artifacts 已复制到：

```text
/data/zmy/OurAgent-he1/benchmark/framework_experiment_records/reactree_wah_artifacts/smoke_todo_hooks
```

## 本次修复

第一次 WAH graph replay smoke 出现了评估层 0 分，但 planning/sandbox/final-state audit 已经显示任务完成。原因是 debug replay 旧代码把 `cupcake 1`、`coffee table 1` 的末尾数字直接当成 graph node id；而 WAH 官方图里真实 sim id 需要通过 `wah_utils.make_name_id_dict` 从自然语言序号映射，例如 `('cupcake', 1) -> ('cupcake', 368)`、`('coffee table', 1) -> ('coffeetable', 268)`。

已修复文件：

```text
/data/zmy/OurAgent-he1/benchmark/reactree/wah/framework/code/official_evaluator.py
```

修复内容：

- `graph_replay` 同时支持空格实体名和下划线实体名。
- replay 使用 WAH 官方 `name_id_dict_nl2sim` 将 `object ordinal` 映射到真实 sim id。
- 这只影响 WAH debug evaluator 的名称解析，不改变模型 prompt、模型输出、`todo_list`、sandbox 执行逻辑。

修复后，用同一条 8 步动作直接本地 replay 得到：

```json
{"goal_success_rate": 1.0, "subgoal_success_rate": 1.0}
```

## 数据字段

case 输入关键字段：

- `task_id=0`
- `task_name=prepare_snack`
- `env_id=3`
- `init_room=bedroom`
- `instruction=Put one cupcake and one apple on the coffee table`
- `task_goal={"on_cupcake_coffeetable": 1, "on_apple_coffeetable": 1}`
- `init_graph_cache_path=/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json`
- `environment_source=reactree_case_runtime_scene`
- `task_source=reactree_wah_testset`

`task_goal` 只作为最终态审计目标投影，不作为动作序列答案写入 skill。

## 环境闭包

本次 WAH planning 使用的环境闭包：

- `entity_catalog`：343 个 WAH 可用实体。
- `scene` 字段包含 `environment`、`robot_holding_items`、`robot_inventory`、`robot_location`。
- 初始机器人：`robot_location=bedroom 1`，`robot_holding=空`。
- 关键初始关系：
  - `cupcake 1 on kitchen table 1`
  - `apple 2 on kitchen table 1`
  - `coffee table 1 on floor 25`

## todo_list 格式

本次模型输出的 `todo_list`：

```json
[
  {"step": 1, "action": "go to", "target": "kitchen table 1"},
  {"step": 2, "action": "pick up", "target": "cupcake 1"},
  {"step": 3, "action": "go to", "target": "coffee table 1"},
  {"step": 4, "action": "put down", "target": "cupcake 1"},
  {"step": 5, "action": "go to", "target": "kitchen table 1"},
  {"step": 6, "action": "pick up", "target": "apple 2"},
  {"step": 7, "action": "go to", "target": "coffee table 1"},
  {"step": 8, "action": "put down", "target": "apple 2"}
]
```

使用的 todo hooks：

```text
todo_output_parser_path=benchmark.reactree.wah.framework.code.native_actions.parse_wah_native_actions
todo_step_adapter_path=benchmark.reactree.wah.framework.code.native_actions.wah_native_step_to_skill_call
```

## 检查链路

1. Understanding 根据 WAH case 输入、任务目标和实体表抽取结构化任务。
2. Planning prompt 注入 WAH skill contract，模型输出 WAH 原生动作 JSON 数组。
3. `todo_output_parser` 解析 JSON 数组。
4. `todo_contract` 根据 WAH skills root 检查动作名、`target` 字段和额外字段。
5. sandbox 用 `todo_step_adapter` 执行 WAH 原生动作并更新 WAH 环境状态。
6. `state_diff_audit` 检查最终状态：`cupcake 1` 和 `apple 2` 都移动到 `coffee table 1`。
7. `graph_replay` 用 WAH 官方目标检查函数对 replay 后 graph 计分。

contract artifact 显示：

- `status=passed`
- `enabled_contract_skill_count=8`
- `todo_list_count=8`
- `validated_todo_actions_count=8`
- `validated_steps_count=0`
- `execution_wrapper_count=0`
- 原生动作集合包括 `go to`、`pick up`、`put down`、`open`、`close`、`turn on`、`turn off`、`clean`。

## 状态变化

`state_diff_audit` 接受的变化：

- `cupcake 1 moved to coffee table 1`
- `apple 2 moved to coffee table 1`

最终机器人：

- `robot_location=coffee table 1`
- `robot_holding=空`

## LLM 调用

本次 trace 记录 4 次模型调用：

- `understanding.system`
- `understanding.final_state`
- `planning.main_system`
- `planning.state_diff_audit`

prompt 大小记录：

- understanding system prompt：16682 chars
- final-state prompt：20438 chars
- planning prompt：19492 chars
- state-diff audit prompt：26989 chars

完整输入输出：

```text
.../smoke_todo_hooks/cases/0__0/artifacts/llm_io.json
.../smoke_todo_hooks/cases/0__0/trace_report.md
```

## 官方仿真说明

主记录的第一次通过 smoke 使用的是 `graph_replay`，不是 Unity 官方仿真，所以：

```text
official_available_count=0
```

随后已补跑 WAH official Unity smoke：

```bash
python benchmark/reactree/wah/framework/code/run.py \
  --run-name reactree_wah_official_smoke_20260806_todo_hooks \
  --limit 1 \
  --expected-count 1 \
  --workers 1 \
  --launch-shards 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key \
  --eval-mode official \
  --official-port-ids 26
```

official smoke 结果：

- `task_success_rate=1.0`
- `goal_success_rate=1.0`
- `subgoal_success_rate=1.0`
- `official_available_count=1`
- `official_task_success_rate=1.0`
- `execution_success_count=1`
- `evaluation_mode=reactree_official_wah_unity`
- Unity TCP port：`8906 + 26 = 8932`

official smoke artifacts 已复制到：

```text
/data/zmy/OurAgent-he1/benchmark/framework_experiment_records/reactree_wah_artifacts/official_smoke_todo_hooks
```

因此 WAH full 按 official Unity evaluator 跑；需要固定 Unity 端口，不能让多个 WAH Unity 进程抢同一端口。

## 全量运行

当前 WAH full 正在 18003 队列中运行：

```text
/data/zmy/OurAgent-he1/benchmark/reactree/wah/framework/results/reactree_wah_full_20260806_todo_hooks
```

队列命令：

```bash
python benchmark/reactree/wah/framework/code/run.py \
  --run-name reactree_wah_full_20260806_todo_hooks \
  --expected-count 100 \
  --workers 1 \
  --launch-shards 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key \
  --eval-mode official \
  --official-port-ids 26
```

截至 2026-08-07 核对时，`launch_manifest.json` 仍为 `status=running`，当前 tmux session 是 `framework_full_3p6_queue_20260806`。WAH 完成后队列才会启动 ALFRED valid_seen full。
