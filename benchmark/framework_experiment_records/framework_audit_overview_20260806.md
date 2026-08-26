# Framework Audit Overview

更新时间：2026-08-07 UTC

## 总体结论

本轮已按当前 OurAgent framework 路径核对 5 个数据集。结论：

- smoke 不是 dry-run；EAI BEHAVIOR、EAI VirtualHome、ReAcTree WAH、ReAcTree ALFRED 的 `launch_manifest.json` 都记录 `dry_run=false`、`status=completed`、真实 `_case_worker`。
- DELTA smoke artifact 目录没有复制 `launch_manifest.json`，但 `run.log` 明确调用 `/data/zmy/envs/ouragent/bin/python -m benchmark.delta.framework.code._case_worker`，case artifacts 记录了真实 `benchmark_settings_file`、parser、adapter、skill contract 和 VAL official evaluation。
- 每个数据集都使用自己的 `framework/code/config/settings.json`、`prompts.json`、`rules.json`、`prompt_inputs.py`、`task_environment.py`、`native_actions.py`、`skills/` 和 official evaluator。
- `planning_input_summary.json` 证明 `sandbox_evaluator=true`、`state_diff_audit=true` 已生效；不是只把模型 prompt 改掉。
- 当前没有 `planning_output_mode=native_actions` 旧旁路；`todo_list` 是统一变量名，动作 schema 由各数据集自己的 parser/adapter/skill contract 决定。

## Smoke 汇总

| 数据集 | 模型 | 端口 | run_name | 结果 |
| --- | --- | ---: | --- | --- |
| DELTA | `Qwen3.5-9B` | 18004 | `delta_audit_smoke_20260806_todo_hooks` | `task_success_rate=1.0`，VAL 通过 |
| EAI BEHAVIOR | `Qwen3.6-27B` | 18003 | `eai_behavior_smoke_20260806_todo_hooks` | `task_success_rate=1.0` |
| EAI VirtualHome | `Qwen3.6-27B` | 18003 | `eai_virtualhome_smoke_20260806_todo_hooks` | `task_success_rate=1.0` |
| ReAcTree WAH graph replay | `Qwen3.6-27B` | 18003 | `reactree_wah_smoke_20260806_todo_hooks_fix2` | `task_success_rate=1.0` |
| ReAcTree WAH official | `Qwen3.6-27B` | 18003 | `reactree_wah_official_smoke_20260806_todo_hooks` | `official_task_success_rate=1.0` |
| ReAcTree ALFRED valid_seen | `Qwen3.6-27B` | 18003 | `reactree_alfred_seen_smoke_20260806_todo_hooks_fix2` | `official_task_success_rate=1.0` |

逐数据集 smoke 细节：

```text
benchmark/framework_experiment_records/delta_framework.md
benchmark/framework_experiment_records/eai_behavior_framework.md
benchmark/framework_experiment_records/eai_virtualhome_framework.md
benchmark/framework_experiment_records/reactree_wah_framework.md
benchmark/framework_experiment_records/reactree_alfred_framework.md
```

对应 artifacts：

```text
benchmark/framework_experiment_records/delta_artifacts/smoke_todo_hooks
benchmark/framework_experiment_records/eai_behavior_artifacts/smoke_todo_hooks
benchmark/framework_experiment_records/eai_virtualhome_artifacts/smoke_todo_hooks
benchmark/framework_experiment_records/reactree_wah_artifacts/smoke_todo_hooks
benchmark/framework_experiment_records/reactree_wah_artifacts/official_smoke_todo_hooks
benchmark/framework_experiment_records/reactree_alfred_artifacts/smoke_todo_hooks
```

## 真实配置证据

本次 smoke 的 `planning_input_summary.json` 中实际加载：

| 数据集 | settings | parser | adapter | skills |
| --- | --- | --- | --- | ---: |
| DELTA | `benchmark/delta/framework/code/config/settings.json` | `parse_delta_native_actions` | `delta_native_step_to_skill_call` | 13 |
| EAI BEHAVIOR | `benchmark/eai/behavior/framework/code/config/settings.json` | `parse_behavior_native_actions` | `behavior_native_step_to_skill_call` | 29 |
| EAI VirtualHome | `benchmark/eai/virtualhome/framework/code/config/settings.json` | `parse_virtualhome_native_actions` | `virtualhome_native_step_to_skill_call` | 47 |
| ReAcTree WAH | `benchmark/reactree/wah/framework/code/config/settings.json` | `parse_wah_native_actions` | `wah_native_step_to_skill_call` | 8 |
| ReAcTree ALFRED | `benchmark/reactree/alfred/framework/code/config/settings.json` | `parse_alfred_native_actions` | `alfred_native_step_to_skill_call` | 8 |

ALFRED 额外使用 `benchmark.reactree.alfred.framework.code.native_plan_validator.validate_todo_list`。

case 输入也记录了自己的环境来源：

| 数据集 | environment_source |
| --- | --- |
| DELTA | `delta_data_scene_graph_py` |
| EAI BEHAVIOR | `igibson_behavior_native_loader` |
| EAI VirtualHome | `virtualhome_original_init_graph` |
| ReAcTree WAH | `reactree_case_runtime_scene` |
| ReAcTree ALFRED | `alfred_official_scene_prepare_cache` |

## Full 状态

DELTA full 已完成：

```text
benchmark/delta/framework/results/delta_framework_full_20260806_todo_hooks
```

关键统计：

- `selected_case_count=600`
- `scheduled_command_count=600`
- `unit_count=5`
- `worker_module=benchmark.delta.framework.code._case_worker`
- `endpoint_slots=18004/Qwen3.5-9B`
- `done=600`
- `task_success_count=303`
- `task_success_rate=0.505`
- `official_available_count=327`
- `official_task_success_count=303`
- `official_task_success_rate=0.926605504587156`
- `symbolic_success_count=156`
- `symbolic_success_rate=0.26`

18003 full queue：

```text
tmux session: framework_full_3p6_queue_20260806
script: benchmark/framework_experiment_records/run_full_queue_20260806.sh
log: benchmark/framework_experiment_records/full_queue_20260806/queue.log
```

队列命令全部调用各数据集自己的 `framework/code/run.py`，并使用 `--launch-shards 1` 降低共享 18003 的吞吐和仿真干扰。

| 队列项 | run_name | 当前状态 | 结果 |
| --- | --- | --- | --- |
| EAI BEHAVIOR | `eai_behavior_full_20260806_todo_hooks` | completed | 100 done，58 success，`task_success_rate=0.58` |
| EAI VirtualHome | `eai_virtualhome_full_20260806_todo_hooks` | completed | 342 done，132 success，`task_success_rate=0.38596491228070173` |
| ReAcTree WAH | `reactree_wah_full_20260806_todo_hooks` | running | `launch_manifest.json` 为 `status=running`，当前仍在 official Unity full |
| ReAcTree ALFRED | `reactree_alfred_seen_full_20260806_todo_hooks` | pending | WAH 完成后启动 |

查看当前队列：

```bash
tmux ls
tmux attach -t framework_full_3p6_queue_20260806
tail -f benchmark/framework_experiment_records/full_queue_20260806/queue.log
```

## 队列脚本内容

```text
benchmark/framework_experiment_records/run_full_queue_20260806.sh
```

顺序：

1. `benchmark/eai/behavior/framework/code/run.py --expected-count 100 --launch-shards 1 --ports 18003`
2. `benchmark/eai/virtualhome/framework/code/run.py --expected-count 342 --launch-shards 1 --ports 18003`
3. `benchmark/reactree/wah/framework/code/run.py --expected-count 100 --launch-shards 1 --ports 18003 --eval-mode official --official-port-ids 26`
4. `benchmark/reactree/alfred/framework/code/run.py --eval-set valid_seen --expected-count 820 --launch-shards 1 --ports 18003 --x-display 71`

## 并发策略

- DELTA 使用 `18004/Qwen3.5-9B`，可以和 18003 队列并行。
- EAI BEHAVIOR、EAI VirtualHome、WAH、ALFRED 共享 `18003/Qwen3.6-27B`，当前用队列串行跑 full。
- WAH official 还占用 Unity TCP 端口；ALFRED 还占用 X display。仿真资源必须固定且隔离。
- 不建议四个 18003 full 同时跑，否则吞吐、超时和失败来源不可解释。

## 输出与排查

每个 framework run 应有：

```text
benchmark/<paper>/<dataset>/framework/results/<run-name>/
  launch_manifest.json
  merged_results.json
  summary.json
  cases/<safe-case-id>/
    worker_result.json
    case.json
    raw_output.json
    run.log
    trace_report.md
    artifacts/
```

判断是否用了真实功能时，优先看：

1. `launch_manifest.json`：`dry_run`、`status`、`worker_module`、`endpoint_slots`、`selected_case_count`。
2. `artifacts/case_input_summary.json`：`benchmark_settings_file` 和 environment source。
3. `artifacts/planning_input_summary.json`：parser、adapter、skill root、feature flags。
4. `artifacts/llm_io.json`：实际 prompt 和 LLM 调用。
5. `artifacts/official_eval.json`：官方 evaluator 是否 available 以及官方指标。

`summary.json` 只能说明聚合结果，不能单独证明配置或功能生效。

## 清理说明

本轮保留当前使用或审计相关目录：

- DELTA：`delta_audit_smoke_20260806_todo_hooks`、`delta_framework_full_20260806_todo_hooks`
- EAI BEHAVIOR：`eai_behavior_smoke_20260806_todo_hooks`、`eai_behavior_full_20260806_todo_hooks`
- EAI VirtualHome：`eai_virtualhome_smoke_20260806_todo_hooks`、`eai_virtualhome_full_20260806_todo_hooks`
- ReAcTree WAH：`reactree_wah_smoke_20260806_todo_hooks_fix2`、`reactree_wah_official_smoke_20260806_todo_hooks`、`reactree_wah_full_20260806_todo_hooks`
- ReAcTree ALFRED：`reactree_alfred_seen_smoke_20260806_todo_hooks_fix2`

旧 smoke、full、todo-contract 和 audit 目录不作为当前结论来源。
