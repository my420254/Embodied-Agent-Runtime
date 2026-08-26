# EAI BEHAVIOR Framework Smoke Audit

更新时间：2026-08-06 18:24 UTC

## 结论

EAI BEHAVIOR 3.6 冒烟已通过。当前框架不再按 `planning_output_mode=native_actions` 分流；`todo_list` 内直接保存 BEHAVIOR 官方动作 JSON，每步形如 `{"action": "LEFT_GRASP", "object": "candle_0"}`，不是 framework 的 `execution/skill/parameters` 包装。

本次 smoke：

- case：`assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37`
- instruction：`assembling gift baskets`
- 模型接口：18003
- 模型名：`Qwen3.6-27B`
- 运行命令：

```bash
python benchmark/eai/behavior/framework/code/run.py \
  --run-name eai_behavior_smoke_20260806_todo_hooks \
  --limit 1 \
  --expected-count 1 \
  --workers 1 \
  --launch-shards 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key
```

结果：

- `total_cases=1`
- `failed_cases=0`
- `task_success_count=1`
- `task_success_rate=1.0`
- `official_available_count=1`
- `official_task_success_rate=1.0`
- `execution_success=true`
- `execution_status=completed`
- `is_feasible=true`
- `todo_parse_error=""`
- `todo_count=32`
- `validated_todo_actions_count=32`
- `state_diff_audit.passed=true`
- sandbox 拦截：0

完整 artifacts 已复制到：

```text
/data/zmy/OurAgent-he1/benchmark/framework_experiment_records/eai_behavior_artifacts/smoke_todo_hooks
```

## 数据字段

本条输入来自 BEHAVIOR 初始环境缓存：

```text
/data/zmy/OurAgent-he1/benchmark/datasets/extracted/eai/behavior/initial_envs/assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37.json
```

case 输入关键字段：

- `identifier`
- `instruction`
- `raw_goal_condition`
- `name_category`
- `scene_id`
- `task_id`
- `initial_environment_cache_path`
- `initial_environment_source=igibson_behavior_native_loader`

目标条件为 4 条 `forpairs ... inside ...` 约束：每个 basket 内需要一个 candle、cheese、cookie、bow。`name_category` 记录 24 个 BEHAVIOR 原生实体名到 synset/category 的映射。

## todo_list 格式

planning prompt 要求模型直接输出 BEHAVIOR 官方动作 JSON 数组。本次前 4 步：

```json
[
  {"step": 1, "action": "LEFT_GRASP", "object": "candle_0"},
  {"step": 2, "action": "LEFT_PLACE_INSIDE", "object": "basket_0"},
  {"step": 3, "action": "RIGHT_GRASP", "object": "cheese_0"},
  {"step": 4, "action": "RIGHT_PLACE_INSIDE", "object": "basket_0"}
]
```

没有 `execution` 字段，没有 framework skill 包装。沙盒内部用：

```text
todo_output_parser_path=benchmark.eai.behavior.framework.code.native_actions.parse_behavior_native_actions
todo_step_adapter_path=benchmark.eai.behavior.framework.code.native_actions.behavior_native_step_to_skill_call
```

这两个 hook 只负责解析当前数据集动作和把单步动作交给 sandbox handler 检查，不改变 `todo_list` 本体，也不作为 benchmark/native 模式开关。

## Understanding 输出

`understanding.system` 看到的实体表来自当前 case：

- 可用实体包括 4 个 `basket_*`、4 个 `candle_*`、4 个 `cheese_*`、4 个 `cookie_*`、4 个 `bow_*`、`breakfast_table_13`、`coffee_table_12`、`room_floor_living_room_0` 等。
- `directly_related` 输出了 basket/candle/cheese/cookie/bow。
- `possibly_related` 输出了 `breakfast_table_13`、`coffee_table_12`、`room_floor_living_room_0`。
- `skill_closure` 输出了 `LEFT_GRASP`、`RIGHT_GRASP`、`LEFT_PLACE_INSIDE`、`RIGHT_PLACE_INSIDE`、`LEFT_RELEASE`、`RIGHT_RELEASE`。
- `structured_task.intent` 为把 candle、cheese、cookie、bow 放入每个 basket。

完整输入输出：

```text
.../smoke_todo_hooks/cases/assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37/artifacts/understanding_input.json
.../smoke_todo_hooks/cases/assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37/artifacts/understanding_output.json
.../smoke_todo_hooks/cases/assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37/artifacts/llm_io.json
```

## 环境闭包与 sandbox

BEHAVIOR 的环境闭包不是 DELTA 的房间图，而是当前 case 的 BEHAVIOR 实体集合和机器人状态：

- `entity_catalog`：数组，包含 25 个可用实体。
- `env_state.robot_location=room_floor_living_room_0`
- `env_state.robot_holding=空`
- `env_state.robot_hands.left=空`
- `env_state.robot_hands.right=空`
- `manipulator_mode=dual_arm`

sandbox 执行 32 步后，`state_diff_audit` 接受了 16 个关键状态变化：

- `candle_0..3 inside basket_0..3`
- `cheese_0..3 inside basket_0..3`
- `cookie_0..3 inside basket_0..3`
- `bow_0..3 inside basket_0..3`

机器人前后均为空手，位置保持 `room_floor_living_room_0`。这说明动作合法性和最终态检查使用的是 BEHAVIOR 自己的环境与状态表达，不是统一动作格式的旁路。

## 检查链路

1. Understanding 根据 BEHAVIOR case 输入抽取结构化任务和实体/技能闭包。
2. Planning prompt 注入 BEHAVIOR skill contract，模型输出 BEHAVIOR 官方动作 JSON 数组。
3. `todo_output_parser` 解析 JSON 数组。
4. `todo_contract` 根据 BEHAVIOR skills root 的 planner contract 检查动作名、必填字段、固定字段、实体字段和额外字段。
5. sandbox 用 `todo_step_adapter` 对每一步做 BEHAVIOR 动作执行检查，并更新 BEHAVIOR 环境状态。
6. `state_diff_audit` 对比 sandbox 前后状态，确认最终态满足 understanding/目标条件。
7. BEHAVIOR 官方 evaluator 用最终导出的动作序列统计官方成功率。

contract artifact 显示：

- `status=passed`
- `enabled_contract_skill_count=29`
- `raw_contract_count=29`
- BEHAVIOR 原生动作包括 `LEFT_GRASP`、`RIGHT_GRASP`、`LEFT_PLACE_INSIDE`、`RIGHT_PLACE_INSIDE`、`OPEN`、`CLOSE`、`COOK`、`CLEAN`、`SLICE` 等。

这些 skill contract 只描述动作 schema 和参数字段，不写入某个具体任务的目标实体或答案序列，因此不是把本条任务答案塞进 skill。

## LLM 调用

本次 trace 记录 4 次模型调用：

- `understanding.system`
- `understanding.final_state`
- `planning.main_system`
- `planning.state_diff_audit`

完整 prompt 和输出位于：

```text
.../smoke_todo_hooks/cases/assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37/artifacts/llm_io.json
.../smoke_todo_hooks/cases/assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37/trace_report.md
```

## 全量运行

BEHAVIOR full 已由 18003 队列完成：

```text
/data/zmy/OurAgent-he1/benchmark/eai/behavior/framework/results/eai_behavior_full_20260806_todo_hooks
```

队列命令：

```bash
python benchmark/eai/behavior/framework/code/run.py \
  --run-name eai_behavior_full_20260806_todo_hooks \
  --expected-count 100 \
  --workers 1 \
  --launch-shards 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key
```

当前 `summary.json` 统计：

- `total_cases=100`
- `done_cases=100`
- `failed_cases=0`
- `task_success_count=58`
- `task_success_rate=0.58`
- `official_available_count=100`
- `official_task_success_rate=0.58`

四个 3.6 数据集共用 18003。当前策略是用 `benchmark/framework_experiment_records/run_full_queue_20260806.sh` 串行跑 full，避免吞吐、超时和仿真资源冲突。
