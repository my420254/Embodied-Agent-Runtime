# Bare Baseline 实验

本文只说明 `bare_baseline`，不包含 OurAgent framework 和 paper method。所有命令默认从仓库根目录运行：

```bash
cd /data/zmy/OurAgent-he1
export OURAGENT_WORKSPACE_ROOT=/data/zmy
```

## 实验边界

`bare_baseline` 的原则是：把原始 benchmark 输入直接给本地 Qwen 接口，让模型一次性输出目标数据集的原生动作，再交给对应 evaluator。它不调用 OurAgent 的 understanding、planning、skills、sandbox、最终态推断或修复循环。

ALFRED 是单独的本地仓库：`/data/zmy/alfred`。它的 bare baseline 入口是 `bare_baseline/run_bare_baseline.py`，会先跑文本生成和 Wang Jie 风格文本指标，再跑真实 AI2-THOR 仿真。

| 数据集 | raw 输入来源 | 实际评测 |
| --- | --- | --- |
| DELTA | domain、scene 和 DELTA 原始 scene graph/task | `/data/zmy/DELTA/baselines/llm_as_planner.py`，再读 DELTA 日志中的 success rate |
| EAI BEHAVIOR | `behavior_bddl_info`、`initial_envs`、`raw_goal_condition`、`name_category` | EAI BEHAVIOR action sequencing evaluator |
| EAI VirtualHome | `id2task.json`、`problem_pddl`、`initial_envs` 的 symbolic env | EAI VirtualHome action sequencing evaluator |
| ReAcTree WAH | WAH `init_graph`、`task_goal`、instruction、init room | ReAcTree WAH Unity official evaluator |
| ReAcTree ALFRED | ALFRED annotation、scene summary、可选 simulator observation | ALFRED AI2-THOR evaluator |

当前 LLM 端口口径：

| 用途 | 端口 | 模型 |
| --- | ---: | --- |
| DELTA bare | `18004` | `Qwen3.5-9B` |
| EAI / ReAcTree bare | `18003` | `Qwen3.6-27B` |
| ALFRED bare base | `18004` | `Qwen3.5-9B` |
| ALFRED bare ft | `8005` | `Qwen3.5-9B-alfred` |

`18001`、`18002` 是旧文档端口，当前 `config/settings.json` 中没有作为默认启用端口。

ALFRED bare runner 默认 `max_tokens=4096`、`temperature=0.0`、`enable_thinking=false`；旧 WJ 脚本里出现过的 `300` 和 `81920` 不再作为当前口径。

## 数据集

| 数据集 | 当前文件 | bare 默认规模 |
| --- | --- | ---: |
| DELTA | `/data/zmy/DELTA` 原生代码，场景/任务由 wrapper 按 domain/scene 组合选择 | 12 个 domain-scene，每个默认 50 episodes |
| EAI BEHAVIOR | `benchmark/datasets/extracted/eai/behavior/cases.json` | 100 |
| EAI VirtualHome | `benchmark/datasets/extracted/eai/virtualhome/cases.json` | 342；主表建议 `--valid-only` 过滤到 338 个有 `problem_pddl` 的 case |
| ReAcTree WAH | `benchmark/datasets/native/reactree/wah/wah_nl_test_rev.json`，wrapper 默认每个任务取第 0 条 instruction | 100 |
| ReAcTree ALFRED | `/data/zmy/alfred/splits/oct21.json` + `/data/zmy/alfred/json_2.1.0` | valid_seen 820，valid_unseen 821 |

VirtualHome 原始 342 个 id 中，`84_1`、`93_1`、`339_1`、`627_1` 缺少 native `problem_pddl`。如果要和 action sequencing 主表对齐，使用 `--valid-only`。

## Smoke 命令

这些命令用于真实链路小样本核对，会调用模型和 evaluator。

```bash
cd /data/zmy/OurAgent-he1

/data/zmy/envs/ouragent/bin/python benchmark/delta/bare_baseline/code/run.py \
  --run-name smoke_real_delta_bare_20260807 \
  --limit 1 \
  --episodes 1 \
  --workers 1 \
  --ports 18004 \
  --api-model Qwen3.5-9B \
  --api-key qwen-local-key \
  --reset

/data/zmy/envs/ouragent/bin/python benchmark/eai/behavior/bare_baseline/code/run.py \
  --run-name smoke_real_behavior_bare_20260807 \
  --limit 1 \
  --workers 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key \
  --reset

/data/zmy/envs/ouragent/bin/python benchmark/eai/virtualhome/bare_baseline/code/run.py \
  --run-name smoke_real_virtualhome_bare_20260807 \
  --case-id 3_1 \
  --workers 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key \
  --reset

/data/zmy/envs/ouragent/bin/python benchmark/reactree/wah/bare_baseline/code/run.py \
  --run-name smoke_real_wah_bare_20260807 \
  --limit 1 \
  --workers 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key \
  --official-base-port 9900 \
  --official-port-ids 0 \
  --official-timeout-s 180 \
  --full-observable \
  --reset

cd /data/zmy/alfred

./bare_baseline/run_bare_18004.sh \
  --split valid_seen \
  --limit 1 \
  --run-name smoke_real_alfred_bare_18004_20260807 \
  --reset

./bare_baseline/run_bare_8005.sh \
  --split valid_seen \
  --limit 1 \
  --run-name smoke_real_alfred_bare_8005_20260807 \
  --reset
```

ALFRED unseen smoke 把 `--split valid_seen` 改成 `valid_unseen`，run name 改成 `smoke_real_alfred_bare_unseen_20260807`。

## Full 命令

建议每个 full 单独放入 tmux，会话名要包含方法、数据集、模型和日期。

```bash
cd /data/zmy/OurAgent-he1

tmux new -d -s delta_bare_full_qwen35 \
  '/data/zmy/envs/ouragent/bin/python benchmark/delta/bare_baseline/code/run.py --run-name delta_bare_full_qwen35 --episodes 50 --workers 1 --ports 18004 --api-model Qwen3.5-9B --api-key qwen-local-key --reset'

tmux new -d -s eai_behavior_bare_full_qwen36 \
  '/data/zmy/envs/ouragent/bin/python benchmark/eai/behavior/bare_baseline/code/run.py --run-name eai_behavior_bare_full_qwen36 --workers 1 --ports 18003 --api-model Qwen3.6-27B --api-key qwen-local-key --reset'

tmux new -d -s eai_virtualhome_bare_full_qwen36 \
  '/data/zmy/envs/ouragent/bin/python benchmark/eai/virtualhome/bare_baseline/code/run.py --run-name eai_virtualhome_bare_full_qwen36_valid --valid-only --workers 1 --ports 18003 --api-model Qwen3.6-27B --api-key qwen-local-key --reset'

tmux new -d -s wah_bare_full_qwen36 \
  '/data/zmy/envs/ouragent/bin/python benchmark/reactree/wah/bare_baseline/code/run.py --run-name wah_bare_full_qwen36_fullobs --workers 1 --ports 18003 --api-model Qwen3.6-27B --api-key qwen-local-key --official-base-port 9900 --official-port-ids 0 --official-timeout-s 180 --full-observable --reset'

tmux new -d -s alfred_bare_18004_full_20260807 \
  'cd /data/zmy/alfred && ./bare_baseline/run_bare_18004.sh --split valid_seen --all-cases --run-name alfred_bare_18004_full_20260807 --reset'

tmux new -d -s alfred_bare_8005_full_20260807 \
  'cd /data/zmy/alfred && ./bare_baseline/run_bare_8005.sh --split valid_seen --all-cases --run-name alfred_bare_8005_full_20260807 --reset'
```

常用 tmux 查看命令：

```bash
tmux ls
tmux attach -t <session-name>
tmux capture-pane -pt <session-name> -S -120
```

## 输出目录

统一结果根目录：

```text
benchmark/<paper>/<dataset>/bare_baseline/results/<run-name>/
  manifest.json
  merged_results.json
  summary.json
  cases/<safe-case-id>/
    input.json
    prompt.md
    raw_output.json
    case.json
    run.log
    artifacts/
```

数据集差异：

| 数据集 | 额外输出 |
| --- | --- |
| DELTA | `cases/<case>/run.log` 记录外部 DELTA 命令，`artifacts/` 由 `DELTA_RESULT_ROOT` 指向外部代码写出 |
| EAI | `artifacts/generated/.../<run>_outputs.json` 和 `artifacts/evaluated/.../summary.json` |
| WAH | `raw_output.json` 记录官方 Unity evaluator 结果，summary 汇总 GSR/SSR/task success |
| ALFRED | `commands.json`、`text/`、`simulation/`、`logs/`，以及 case 级 `result.json`、`simulation.json`、`parse.json` |

`summary.json` 是 run 级聚合；排查错误时优先看 case 目录下的 `prompt.md`、`raw_output.json`、`case.json` 和 `run.log`。

## 常用参数

| 参数 | 作用 |
| --- | --- |
| `--ports` | 本仓库 bare wrapper 的 LLM 服务端口，当前默认使用 18003/18004。 |
| `--endpoint` | 仅 ALFRED `/data/zmy/alfred/bare_baseline/run_bare_baseline.py` 使用，当前支持 `18004`/`base_18004` 和 `8005`/`ft_8005`。 |
| `--api-model` / `--api-key` | 覆盖端口对应模型名和 key。 |
| `--workers` | wrapper 内部并发 worker 数；仿真类任务建议先用 1。 |
| `--run-name` | 结果目录名。 |
| `--limit` | 只跑前 N 条。 |
| `--case-id` / `--case-ids-file` | 指定 case。 |
| `--valid-only` | 仅 EAI VirtualHome 使用，过滤缺失 `problem_pddl` 的 case。 |
| `--reset` | 删除同名旧结果后重新跑。 |
| `--resume` | 跳过已有 `status=done` 的 case。 |
| `--dry-run` | 只写命令、prompt 和目录，不调用模型或 evaluator。 |
| `--summary` | 读取已有 `summary.json`。 |
| `--official-base-port` / `--official-port-ids` | WAH Unity official evaluator 端口。 |
| `--x-display` | ALFRED bare AI2-THOR 使用的单个 X display；默认不可用时会自动启动 Xvfb，除非传 `--no-auto-xvfb`。 |
| `--full-observable` | ReAcTree bare 对齐全景输入假设时使用。 |

## 本次已核对结果

已完成的真实 smoke 结果：

| 数据集 | run_name | 状态 |
| --- | --- | --- |
| DELTA | `smoke_real_delta_bare_20260807` | `done_cases=1, failed_cases=0` |
| EAI BEHAVIOR | `smoke_real_behavior_bare_20260807` | `done_cases=1, failed_cases=0` |
| EAI VirtualHome | `smoke_real_virtualhome_bare_20260807` | `done_cases=1, failed_cases=0` |
| ReAcTree WAH | `smoke_real_wah_bare_20260807` | `done_cases=1, failed_cases=0` |
| ReAcTree ALFRED 18004 text | `codex_live_text_18004_20260807` | `status=done, completed=1, ROUGE-1=0.1667` |
| ReAcTree ALFRED 8005 text | `codex_live_text_8005_20260807` | `status=done, completed=1, ROUGE-1=0.4788` |
| ReAcTree ALFRED 18004 simulation | `codex_live_sim_18004_20260807` | `status=done, official_available=1, execution_success=1, task_success=0` |
| ReAcTree ALFRED 8005 simulation | `codex_live_sim_8005_20260807` | `status=done, official_available=1, execution_success=0, task_success=0` |
