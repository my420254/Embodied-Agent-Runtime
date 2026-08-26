# EAI VirtualHome Framework Smoke Audit

更新时间：2026-08-06 18:28 UTC

## 结论

EAI VirtualHome 3.6 冒烟已通过。当前框架不再用 `planning_output_mode=native_actions` 分流；`todo_list` 内直接保存 VirtualHome 原生动作结构，每步形如 `{"action": "WALK", "args": ["couch"]}`，不是 framework 的 `execution/skill/parameters` 包装。

本次 smoke：

- case：`3_1`
- instruction：`Relax on sofa`
- 模型接口：18003
- 模型名：`Qwen3.6-27B`
- 运行命令：

```bash
python benchmark/eai/virtualhome/framework/code/run.py \
  --run-name eai_virtualhome_smoke_20260806_todo_hooks \
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
- `todo_count=2`
- `validated_todo_actions_count=2`
- `state_diff_audit.passed=true`
- sandbox 拦截：0

完整 artifacts 已复制到：

```text
/data/zmy/OurAgent-he1/benchmark/framework_experiment_records/eai_virtualhome_artifacts/smoke_todo_hooks
```

## 数据字段

case 输入关键字段：

- `identifier`
- `instruction`
- `pddl_goal`
- `pddl_objects`
- `scene_id`
- `task_id`
- `initial_environment_cache_path`
- `initial_environment_source`

本条 case 的 instruction 为 `Relax on sofa`。环境来自 VirtualHome 抽取后的当前 case 环境缓存，包含完整对象表和场景层级；不是框架统一环境。

## 环境闭包

本次 planning 使用的 VirtualHome 环境闭包：

- `entity_catalog`：293 个可用实体。
- 实体预览：`bathroom`、`bathroom_anchor`、`bathroom_cabinet`、`bedroom`、`bench_227` 等。
- `env_state.robot_location=bedroom_anchor`
- `env_state.robot_holding=空`
- `env_state.robot_hands.left=空`
- `env_state.robot_hands.right=空`
- `manipulator_mode=dual_arm`

VirtualHome 的环境闭包包含对象名、房间锚点、对象 id 对齐表和可执行动作所需的场景图。模型输出时不要求直接输出对象 id；导出到官方 evaluator 时，框架根据对象表把 `couch` 对齐为官方格式中的 `(352)`。

## todo_list 格式

本次模型输出的 `todo_list`：

```json
[
  {"step": 1, "action": "WALK", "args": ["couch"]},
  {"step": 2, "action": "SIT", "args": ["couch"]}
]
```

官方 evaluator 看到的导出动作：

```text
[WALK] <couch> (352)
[SIT] <couch> (352)
```

这一步导出是 VirtualHome 自己的官方格式适配，不改变 planning 内部的 `todo_list`。

使用的 todo hooks：

```text
todo_output_parser_path=benchmark.eai.virtualhome.framework.code.native_actions.parse_virtualhome_native_actions
todo_step_adapter_path=benchmark.eai.virtualhome.framework.code.native_actions.virtualhome_native_step_to_skill_call
```

## 检查链路

1. Understanding 根据 VirtualHome case 输入和实体表抽取结构化任务。
2. Planning prompt 注入 VirtualHome skill contract，模型输出 VirtualHome 原生动作 JSON 数组。
3. `todo_output_parser` 解析 JSON 数组。
4. `todo_contract` 根据 VirtualHome skills root 检查动作名、`args` 字段和额外字段。
5. sandbox 用 `todo_step_adapter` 执行 `WALK couch`、`SIT couch` 并更新环境。
6. `state_diff_audit` 检查最终状态满足 “relax on sofa”。
7. 官方 VirtualHome evaluator 用导出的官方动作串计算成功率。

contract artifact 显示：

- `status=passed`
- `enabled_contract_skill_count=47`
- `todo_list_count=2`
- `validated_todo_actions_count=2`
- `validated_steps_count=0`
- `execution_wrapper_count=0`
- 原生动作集合包括 `WALK`、`GRAB`、`PUTIN`、`PUTON`、`OPEN`、`CLOSE`、`SIT`、`LIE`、`SLEEP`、`EAT`、`WASH` 等。

skill contract 只描述 VirtualHome 动作 schema 和参数规则，不写具体 case 的答案序列或目标实体。

## 官方评估说明

官方 VirtualHome evaluator 原版在本条 case 的 action goal 数为 0 时触发了 summary 零分母报错：

```text
ZeroDivisionError: float division by zero
```

本次结果使用框架内安全汇总逻辑读取同一官方日志中的有效评估事实：官方日志显示 `Executable!`、`Correct plan: 1, rate = 100.00%`、`Goals all satisfied: all_pred_success=True`。记录中保留了这个 fallback：

```text
fallback_reason=official_evaluator_zero_denominator_in_summary
```

这不是更改模型输出，也不是绕过动作执行；只是避免官方 summary 在零分母 case 上崩溃。

## LLM 调用

本次 trace 记录 4 次模型调用：

- `understanding.system`
- `understanding.final_state`
- `planning.main_system`
- `planning.state_diff_audit`

prompt 大小记录：

- understanding system prompt：30386 chars
- final-state prompt：17596 chars
- planning prompt：51404 chars
- state-diff audit prompt：19893 chars

完整输入输出：

```text
.../smoke_todo_hooks/cases/3_1/artifacts/llm_io.json
.../smoke_todo_hooks/cases/3_1/trace_report.md
```

## 全量运行

VirtualHome full 已由 18003 队列完成：

```text
/data/zmy/OurAgent-he1/benchmark/eai/virtualhome/framework/results/eai_virtualhome_full_20260806_todo_hooks
```

队列命令：

```bash
python benchmark/eai/virtualhome/framework/code/run.py \
  --run-name eai_virtualhome_full_20260806_todo_hooks \
  --expected-count 342 \
  --workers 1 \
  --launch-shards 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key
```

当前 `summary.json` 统计：

- `total_cases=342`
- `done_cases=342`
- `failed_cases=0`
- `task_success_count=132`
- `task_success_rate=0.38596491228070173`
- `official_available_count=342`
- `official_task_success_rate=0.38596491228070173`

这个 run 是 342 个 id 的补充口径；主表 338 口径需要重新使用 `--valid-only --expected-count 338`。
