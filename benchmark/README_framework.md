# Framework Benchmark 运行与审计

本文只描述 `benchmark/*/*/framework`。bare baseline 和 paper method 分别见 `benchmark/README_bare_baseline.md`、`benchmark/README_paper_method.md`。

默认工作目录：

```bash
cd <PROJECT_ROOT>
export OURAGENT_WORKSPACE_ROOT=/data/zmy
```

## 当前结论

截至 2026-08-07，本轮已经核对 `benchmark/framework_experiment_records`：

- EAI BEHAVIOR、EAI VirtualHome、ReAcTree WAH、ReAcTree ALFRED 的 smoke `launch_manifest.json` 均为 `dry_run=false`、`status=completed`，worker 模块是各自 `benchmark.<dataset>.framework.code._case_worker`。
- DELTA smoke artifact 目录没有复制 `launch_manifest.json`，但 `run.log` 明确调用 `/data/zmy/envs/ouragent/bin/python -m benchmark.delta.framework.code._case_worker`，case artifacts 也记录了 DELTA 自己的 `benchmark_settings_file`、parser、adapter、skill contract 和 VAL official evaluation。
- 所有 framework smoke 的 `planning_input_summary.json` 都记录了数据集自己的 parser、adapter、skill root 和 feature flags。`sandbox_evaluator=true`、`state_diff_audit=true` 已实际生效。
- 当前没有 `planning_output_mode=native_actions` 这类旧旁路；`todo_list` 是统一变量名，里面保存各数据集自己的原生动作。

## 入口规则

framework 正式入口只能是各数据集自己的 `framework/code/run.py`：

| 数据集 | 入口 | 启动器 | worker | case executor |
| --- | --- | --- | --- | --- |
| DELTA | `benchmark/delta/framework/code/run.py` | `launcher.py` | `_case_worker.py` | `case_executor.py` |
| EAI BEHAVIOR | `benchmark/eai/behavior/framework/code/run.py` | `launcher.py` | `_case_worker.py` | `case_executor.py` |
| EAI VirtualHome | `benchmark/eai/virtualhome/framework/code/run.py` | `launcher.py` | `_case_worker.py` | `case_executor.py` |
| ReAcTree WAH | `benchmark/reactree/wah/framework/code/run.py` | `launcher.py` | `_case_worker.py` | `case_executor.py` |
| ReAcTree ALFRED | `benchmark/reactree/alfred/framework/code/run.py` | `launcher.py` | `_case_worker.py` | `case_executor.py` |

`run.py` 会设置 `OURAGENT_FRAMEWORK_ENTRYPOINT=run.py`；`launcher.py` 会检查这个变量，直接调用 `launcher.py` 或 `_case_worker.py` 会被拒绝。`run.sh` 只是环境包装，不是另一套逻辑。

跨数据集脚本只能作为队列包装使用，必须仍然调用每个数据集自己的 `framework/code/run.py`。当前 `benchmark/framework_experiment_records/run_full_queue_20260806.sh` 就是这种 tmux 串行队列。

## 环境与端口

| 项 | 当前值 |
| --- | --- |
| 框架 Python | `/data/zmy/envs/ouragent/bin/python` |
| ReAcTree Python | `/data/zmy/envs/reactree_py38/bin/python` |
| DELTA 外部 repo | `/data/zmy/DELTA` |
| ReAcTree 外部 repo | `/data/zmy/ReAcTree` |
| EAI 资源 | `/data/zmy/embodied-agent-interface` |
| Qwen3.6 endpoint | `http://192.168.27.250:18003/v1`，`Qwen3.6-27B` |
| Qwen3.5 endpoint | `http://192.168.27.250:18004/v1`，`Qwen3.5-9B` |
| Qwen3.5 ALFRED endpoint | `http://192.168.27.250:8005/v1`，`Qwen3.5-9B-alfred` |

当前全局 `config/settings.json` 中 `18003`、`18004`、`8005` enabled；`18001`、`18002` disabled。各数据集自己的 `framework/code/config/settings.json` 必须也包含要用的 endpoint。本轮已经在 ALFRED framework settings 中加入 `8005/Qwen3.5-9B-alfred`，因此 ALFRED 可以切到 `18004/Qwen3.5-9B` 或 `8005/Qwen3.5-9B-alfred`。

当前 framework planning 模块统一使用 `max_tokens=4096`、`temperature=0`；ALFRED 18004/8005 命令不额外覆盖 `max_tokens`。

## 数据集与规模

| 数据集 | 文件 | 默认规模 | 重要参数 |
| --- | --- | ---: | --- |
| DELTA | `benchmark/datasets/extracted/delta/cases.json` | 600 | `--domain`、`--scene`、`--episodes` |
| EAI BEHAVIOR | `benchmark/datasets/extracted/eai/behavior/cases.json` | 100 | `--task-name`、`--scene-id` |
| EAI VirtualHome | `benchmark/datasets/extracted/eai/virtualhome/cases.json` | 342 | `--valid-only` 可过滤到 338 个有 native `problem_pddl` 的 case |
| ReAcTree WAH | `benchmark/datasets/extracted/reactree/wah/cases.json` | 默认 100 | 不传 `--instruction-level` 时只跑每个任务第 0 条 instruction；传入后为 195 |
| ReAcTree ALFRED | `cases_valid_seen.json`、`cases_valid_unseen.json` | valid_seen 820，valid_unseen 821 | `--eval-set valid_seen|valid_unseen` |

VirtualHome 缺失 native `problem_pddl` 的 id 是 `84_1`、`93_1`、`339_1`、`627_1`。默认 framework full 是 342 个 id 的补充口径；主表口径需要显式 `--valid-only --expected-count 338`。

## 自有配置如何生效

每个 framework 数据集都有独立配置：

```text
benchmark/<paper>/<dataset>/framework/code/config/launch_config.json
benchmark/<paper>/<dataset>/framework/code/config/settings.json
benchmark/<paper>/<dataset>/framework/code/config/prompts.json
benchmark/<paper>/<dataset>/framework/code/config/rules.json
benchmark/<paper>/<dataset>/framework/code/prompt_inputs.py
benchmark/<paper>/<dataset>/framework/code/task_environment.py
benchmark/<paper>/<dataset>/framework/code/native_actions.py
benchmark/<paper>/<dataset>/framework/code/skills/
benchmark/<paper>/<dataset>/framework/code/official_evaluator.py
```

`launch_config.json` 决定结果根目录、默认 run name、默认端口、`expected_count`、worker timeout、`shards_per_interface` 等启动配置。当前默认值：

| 数据集 | results_root | 默认端口 | expected_count | shards_per_interface |
| --- | --- | ---: | ---: | ---: |
| DELTA | `benchmark/delta/framework/results` | 18004 | 600 | 5 |
| EAI BEHAVIOR | `benchmark/eai/behavior/framework/results` | 18003 | 100 | 5 |
| EAI VirtualHome | `benchmark/eai/virtualhome/framework/results` | 18003 | 342 | 5 |
| ReAcTree WAH | `benchmark/reactree/wah/framework/results` | 18003 | 100 | 5 |
| ReAcTree ALFRED | `benchmark/reactree/alfred/framework/results` | 18003 | 820 valid_seen | 5 |

`settings.json` 决定 prompt/rules 模块、`prompt_inputs_module`、`final_state_module`、skill root、enabled skills 和模型默认值。运行时会把 `case_input.benchmark_settings_file` 写成对应数据集自己的 settings 路径。

真实生效证据要看 case artifact：

```text
cases/<safe-case-id>/artifacts/
  worker_input.json
  case_input.json
  case_input_summary.json
  prepared_environment.json
  prepared_environment_summary.json
  environment_audit.json
  understanding_input.json
  understanding_output.json
  planning_input.json
  planning_input_summary.json
  planning_output.json
  planning_output_summary.json
  planning_feature_records.json
  official_eval.json
  llm_io.json
  process_summary.json
```

本次 smoke 审计中实际加载的关键函数：

| 数据集 | parser | adapter | skills |
| --- | --- | --- | ---: |
| DELTA | `benchmark.delta.framework.code.native_actions.parse_delta_native_actions` | `delta_native_step_to_skill_call` | 13 |
| EAI BEHAVIOR | `benchmark.eai.behavior.framework.code.native_actions.parse_behavior_native_actions` | `behavior_native_step_to_skill_call` | 29 |
| EAI VirtualHome | `benchmark.eai.virtualhome.framework.code.native_actions.parse_virtualhome_native_actions` | `virtualhome_native_step_to_skill_call` | 47 |
| ReAcTree WAH | `benchmark.reactree.wah.framework.code.native_actions.parse_wah_native_actions` | `wah_native_step_to_skill_call` | 8 |
| ReAcTree ALFRED | `benchmark.reactree.alfred.framework.code.native_actions.parse_alfred_native_actions` | `alfred_native_step_to_skill_call` | 8 |

ALFRED 还加载了 `benchmark.reactree.alfred.framework.code.native_plan_validator.validate_todo_list`。

## 框架流程

```text
framework/code/run.py
  -> launcher.py
  -> 读取 launch_config.json
  -> 选择 extracted cases
  -> 激活 framework/code/config/settings.json
  -> 写 launch_manifest.json 和 worker_input.json
  -> _case_worker.py
  -> case_executor.run_case
  -> task_environment.prepare_environment
  -> framework_task_bridge 激活 benchmark settings
  -> graph/understanding
  -> graph/planning
  -> 数据集 native_actions parser/adapter
  -> 数据集 skills sandbox handler
  -> final_state / state_diff_audit
  -> official_evaluator
  -> case artifacts / merged_results.json / summary.json
```

`llm_io.json` 是判断 prompt 是否真的来自数据集覆盖的证据。不能只看 `prompts.json` 文件存在。

## Full 队列

当前 18003 队列脚本：

```text
benchmark/framework_experiment_records/run_full_queue_20260806.sh
benchmark/framework_experiment_records/full_queue_20260806/queue.log
```

启动和查看：

```bash
cd <PROJECT_ROOT>

tmux new -d -s framework_full_3p6_queue_20260806 \
  'bash benchmark/framework_experiment_records/run_full_queue_20260806.sh'

tmux ls
tmux attach -t framework_full_3p6_queue_20260806
tail -f benchmark/framework_experiment_records/full_queue_20260806/queue.log
```

队列顺序：

1. EAI BEHAVIOR full：100 cases。
2. EAI VirtualHome full：342 cases。
3. ReAcTree WAH full：100 cases，`--eval-mode official`，Unity port id `26`。
4. ReAcTree ALFRED valid_seen full：820 cases，X display `:71`。

截至本次核对：

| 数据集 | run_name | 状态 | 结果 |
| --- | --- | --- | --- |
| DELTA | `delta_framework_full_20260806_todo_hooks` | completed | 600 done；task success 303/600；official available 327，official success 303 |
| EAI BEHAVIOR | `eai_behavior_full_20260806_todo_hooks` | completed | 100 done；task success 58/100 |
| EAI VirtualHome | `eai_virtualhome_full_20260806_todo_hooks` | completed | 342 done；task success 132/342 |
| ReAcTree WAH | `reactree_wah_full_20260806_todo_hooks` | running | 当前 manifest 为 `status=running`，队列正在 WAH official full |
| ReAcTree ALFRED | `reactree_alfred_seen_full_20260806_todo_hooks` | pending | WAH 完成后启动 |

DELTA full 单独使用 `18004/Qwen3.5-9B`，可与 18003 队列并行。18003 上的 EAI/ReAcTree 不建议四个 full 同时跑，否则吞吐、超时和仿真失败来源难以解释。

## 逐数据集命令

DELTA full：

```bash
/data/zmy/envs/ouragent/bin/python benchmark/delta/framework/code/run.py \
  --run-name delta_framework_full_20260806_todo_hooks \
  --expected-count 600 \
  --workers 2 \
  --ports 18004 \
  --api-model Qwen3.5-9B \
  --api-key qwen-local-key
```

EAI BEHAVIOR full：

```bash
/data/zmy/envs/ouragent/bin/python benchmark/eai/behavior/framework/code/run.py \
  --run-name eai_behavior_full_20260806_todo_hooks \
  --expected-count 100 \
  --workers 1 \
  --launch-shards 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key
```

EAI VirtualHome full，342 补充口径：

```bash
/data/zmy/envs/ouragent/bin/python benchmark/eai/virtualhome/framework/code/run.py \
  --run-name eai_virtualhome_full_20260806_todo_hooks \
  --expected-count 342 \
  --workers 1 \
  --launch-shards 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key
```

EAI VirtualHome 主表 338 口径：

```bash
/data/zmy/envs/ouragent/bin/python benchmark/eai/virtualhome/framework/code/run.py \
  --run-name eai_virtualhome_valid_full_qwen36 \
  --valid-only \
  --expected-count 338 \
  --workers 1 \
  --launch-shards 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key
```

ReAcTree WAH official full：

```bash
/data/zmy/envs/ouragent/bin/python benchmark/reactree/wah/framework/code/run.py \
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

ReAcTree WAH graph replay 调试口径：

```bash
/data/zmy/envs/ouragent/bin/python benchmark/reactree/wah/framework/code/run.py \
  --run-name reactree_wah_graph_replay_debug \
  --limit 1 \
  --workers 1 \
  --launch-shards 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key \
  --eval-mode graph_replay
```

ReAcTree ALFRED valid_seen full：

```bash
/data/zmy/envs/ouragent/bin/python benchmark/reactree/alfred/framework/code/run.py \
  --run-name reactree_alfred_seen_full_20260806_todo_hooks \
  --eval-set valid_seen \
  --expected-count 820 \
  --workers 1 \
  --launch-shards 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key \
  --x-display 71
```

ReAcTree ALFRED 18004 base：

```bash
/data/zmy/envs/ouragent/bin/python benchmark/reactree/alfred/framework/code/run.py \
  --run-name reactree_alfred_seen_full_20260807_18004 \
  --eval-set valid_seen \
  --expected-count 820 \
  --workers 1 \
  --launch-shards 1 \
  --ports 18004 \
  --api-model Qwen3.5-9B \
  --api-key qwen-local-key \
  --x-display 71
```

ReAcTree ALFRED 8005 fine-tuned：

```bash
/data/zmy/envs/ouragent/bin/python benchmark/reactree/alfred/framework/code/run.py \
  --run-name reactree_alfred_seen_full_20260807_8005 \
  --eval-set valid_seen \
  --expected-count 820 \
  --workers 1 \
  --launch-shards 1 \
  --ports 8005 \
  --api-model Qwen3.5-9B-alfred \
  --api-key qwen-local-key \
  --x-display 72
```

也可以直接使用脚本入口：

```bash
cd <PROJECT_ROOT>

benchmark/reactree/alfred/framework/code/run_18004.sh \
  --run-name reactree_alfred_seen_full_20260807_18004 \
  --eval-set valid_seen \
  --expected-count 820 \
  --workers 1 \
  --launch-shards 1 \
  --x-display 71

benchmark/reactree/alfred/framework/code/run_8005.sh \
  --run-name reactree_alfred_seen_full_20260807_8005 \
  --eval-set valid_seen \
  --expected-count 820 \
  --workers 1 \
  --launch-shards 1 \
  --x-display 72
```

ALFRED valid_unseen：

```bash
/data/zmy/envs/ouragent/bin/python benchmark/reactree/alfred/framework/code/run.py \
  --run-name reactree_alfred_unseen_full_qwen36 \
  --eval-set valid_unseen \
  --expected-count 821 \
  --workers 1 \
  --launch-shards 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key \
  --x-display 72
```

## Preflight

普通 `--preflight` 只检查 case 选择、endpoint slots 和资源分配，不调用 LLM。

```bash
/data/zmy/envs/ouragent/bin/python benchmark/eai/behavior/framework/code/run.py \
  --preflight --expected-count 100 --ports 18003
```

WAH 和 ALFRED 还有 `--sim-preflight`，会检查真实仿真资源：

```bash
/data/zmy/envs/ouragent/bin/python benchmark/reactree/wah/framework/code/run.py \
  --sim-preflight --ports 18003 --official-port-ids 26

/data/zmy/envs/ouragent/bin/python benchmark/reactree/alfred/framework/code/run.py \
  --sim-preflight --ports 18003 --x-display 71
```

WAH 的 TCP 端口是 `official_base_port + official_port_id`，默认 `official_base_port=8906`。ALFRED 会锁定 X display；如果 display 不存在且未传 `--no-auto-xvfb`，launcher 会自动启动 Xvfb。

## 输出目录

统一结构：

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

run 级文件：

| 文件 | 用途 |
| --- | --- |
| `launch_manifest.json` | run name、端口、模型、selected/scheduled case count、worker module、dry-run/status、worker timeout |
| `merged_results.json` | compact 后的 case 结果列表 |
| `summary.json` | run 级统计，包含 done/failed 和官方指标 |

case 级排查顺序：

1. `artifacts/case_input_summary.json`：确认 `benchmark_settings_file`、dataset、instruction、environment source。
2. `artifacts/prepared_environment_summary.json`：确认实体表、初始状态、仿真/display 信息。
3. `artifacts/planning_input_summary.json`：确认 parser、adapter、skill root、feature flags。
4. `artifacts/llm_io.json`：确认使用了数据集自己的 understanding/planning prompt。
5. `artifacts/official_eval.json`：确认官方 evaluator 是否 available，以及 task/GSR/SSR/VAL 结果。
6. `trace_report.md` 和 `run.log`：定位 worker 异常。

ALFRED framework 的 `summary.json` 同时包含两类评测结果：`official_*` / `task_success_*` 是真实 AI2-THOR official evaluator 指标，`reference_text_metrics` 是和 ALFRED annotation high-level text 的 ROUGE/步数对比。文本指标只衡量表述相似度，不等价于仿真成功率；例如 `reactree_alfred_seen_smoke_20260806_todo_hooks_fix2` 的 official success 是 1.0，但 `reference_text_metrics.overall_rouge1_f1=0.2253521127`。

## 审计记录

本轮 framework 审计文档与产物在：

```text
benchmark/framework_experiment_records/framework_audit_overview_20260806.md
benchmark/framework_experiment_records/delta_framework.md
benchmark/framework_experiment_records/eai_behavior_framework.md
benchmark/framework_experiment_records/eai_virtualhome_framework.md
benchmark/framework_experiment_records/reactree_wah_framework.md
benchmark/framework_experiment_records/reactree_alfred_framework.md
benchmark/framework_experiment_records/*_artifacts/
benchmark/framework_experiment_records/full_queue_20260806/
```

这些记录只用于核对当前代码路径、真实配置、真实功能和输出结果。旧实验目录不能作为当前结论来源。
