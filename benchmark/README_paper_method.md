# Paper Method 实验

本文只说明 `paper_method`，不包含 bare baseline 和 OurAgent framework。所有命令默认从仓库根目录运行：

```bash
cd /data/zmy/OurAgent-he1
export OURAGENT_WORKSPACE_ROOT=/data/zmy
```

## 实验边界

`paper_method` 的原则是：尽量使用论文自己的方法流程，只把 LLM 后端切到本地 OpenAI-compatible Qwen 接口。适配代码在本仓库 `benchmark/` 下，不直接修改外部论文源码。

| 论文/数据集 | 本仓库入口 | 实际调用 |
| --- | --- | --- |
| DELTA | `benchmark/delta/paper_method/code/run.py` | `/data/zmy/DELTA/delta.py`，通过 shim 接入本地 Qwen |
| EAI BEHAVIOR | `benchmark/eai/behavior/paper_method/code/run.py` | EAI 官方 action sequencing prompt cache + 官方 evaluator |
| EAI VirtualHome | `benchmark/eai/virtualhome/paper_method/code/run.py` | EAI 官方 action sequencing prompt cache + 官方 evaluator |
| ReAcTree WAH | `benchmark/reactree/wah/paper_method/code/run.py` | `/data/zmy/ReAcTree/src/evaluate.py`；`--full-observable` 时走本仓库 wrapper/overlay |
| ReAcTree ALFRED | `benchmark/reactree/alfred/paper_method/code/run.py` | 本仓库 wrapper + `/data/zmy/ReAcTree/src/evaluate.py` |

当前端口：

| 用途 | 端口 | 模型 |
| --- | ---: | --- |
| DELTA paper | `18004` | `Qwen3.5-9B` |
| EAI / ReAcTree paper | `18003` | `Qwen3.6-27B` |
| ALFRED optional ft endpoint | `8005` | `Qwen3.5-9B-alfred` |

旧文档里的 `18001`、`18002` 不再是当前默认口径。

ALFRED 的 18004/8005 四组实验本轮只指 bare baseline 与 OurAgent framework：裸基线在 `/data/zmy/alfred`，framework 在 `benchmark/reactree/alfred/framework/code`。paper method 仍是单独第三条方法线，只有需要补充 ReAcTree 原论文方法对比时才运行。

本仓库 paper wrapper 的 LLM 生成长度也按统一配置走 `max_tokens=4096`；只保留论文方法自己的 `max_steps` / `max_decisions` 等执行轮次参数。

## 数据集与输入

| 数据集 | paper method 使用的数据 | 默认规模 |
| --- | --- | ---: |
| DELTA | `/data/zmy/DELTA` 原论文 task/scene 入口，由 wrapper 按 domain/scene 组合调用 | 12 个 domain-scene，每个默认 50 episodes |
| EAI BEHAVIOR | EAI 官方 `helm_prompts.json` action sequencing prompt cache | 100 |
| EAI VirtualHome | EAI 官方 `helm_prompts.json` action sequencing prompt cache；主表用 `--valid-only` 对齐 338 个有效 case | 342 或 338 |
| ReAcTree WAH | `benchmark/datasets/native/reactree/wah/wah_nl_test_rev.json`，wrapper 为每个 case 写临时 testset | 100 |
| ReAcTree ALFRED | `oct21.json`、`json_2.1.0` 和 ReAcTree ALFRED evaluator | valid_seen 820，valid_unseen 821 |

EAI paper method 的输入是官方 action sequencing prompt cache，里面已经包含 Goal Interpretation 和 Subgoal Decomposition 的上下文，用于对齐 EAI Action Sequencing 指标；这和 OurAgent framework 的输入口径不完全等价，比较时需要注明。

## Smoke 命令

真实 smoke 会调用模型和论文/evaluator 代码。

```bash
cd /data/zmy/OurAgent-he1

/data/zmy/envs/ouragent/bin/python benchmark/delta/paper_method/code/run.py \
  --run-name smoke_real_delta_paper_20260807 \
  --limit 1 \
  --episodes 1 \
  --workers 1 \
  --ports 18004 \
  --api-model Qwen3.5-9B \
  --api-key qwen-local-key \
  --reset

/data/zmy/envs/ouragent/bin/python benchmark/eai/behavior/paper_method/code/run.py \
  --run-name smoke_real_behavior_paper_20260807 \
  --limit 1 \
  --workers 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key \
  --reset

/data/zmy/envs/ouragent/bin/python benchmark/eai/virtualhome/paper_method/code/run.py \
  --run-name smoke_real_virtualhome_paper_3_1_20260807 \
  --case-id 3_1 \
  --workers 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key \
  --reset

/data/zmy/envs/ouragent/bin/python benchmark/reactree/wah/paper_method/code/run.py \
  --run-name smoke_real_wah_paper_fixed_20260807 \
  --limit 1 \
  --workers 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key \
  --config-name wah_headless_reactree_wm \
  --full-observable \
  --official-base-port 9950 \
  --official-port-ids 0 \
  --official-timeout-s 240 \
  --reset

/data/zmy/envs/ouragent/bin/python benchmark/reactree/alfred/paper_method/code/run.py \
  --run-name smoke_real_alfred_paper_seen_single_x0_minilm20_20260807 \
  --eval-set valid_seen \
  --workers 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key \
  --config-name alfred_reactree \
  --full-observable \
  --x-displays 0 \
  --eval-portion 100 \
  --paper-override alfred.splits=/data/zmy/OurAgent-he1/benchmark/reactree/alfred/paper_method/scratch/alfred_singleton_splits_20260807.json \
  --paper-override llm_agent.max_steps=20 \
  --paper-override llm_agent.max_decisions=20 \
  --reset
```

ALFRED unseen smoke 把 `--eval-set valid_seen` 改成 `valid_unseen`，run name 改成 `smoke_real_alfred_paper_unseen_single_x0_minilm20_20260807`。

## Full 命令

DELTA：

```bash
tmux new -d -s delta_paper_full_qwen35 \
  '/data/zmy/envs/ouragent/bin/python benchmark/delta/paper_method/code/run.py --run-name delta_paper_full_qwen35 --episodes 50 --workers 1 --ports 18004 --api-model Qwen3.5-9B --api-key qwen-local-key --reset'
```

EAI BEHAVIOR：

```bash
tmux new -d -s eai_behavior_paper_full_qwen36 \
  '/data/zmy/envs/ouragent/bin/python benchmark/eai/behavior/paper_method/code/run.py --run-name eai_behavior_paper_full_qwen36 --workers 1 --ports 18003 --api-model Qwen3.6-27B --api-key qwen-local-key --reset'
```

EAI VirtualHome 主表 338 口径：

```bash
tmux new -d -s eai_virtualhome_paper_valid_full_qwen36 \
  '/data/zmy/envs/ouragent/bin/python benchmark/eai/virtualhome/paper_method/code/run.py --run-name eai_virtualhome_paper_valid_full_qwen36 --valid-only --workers 1 --ports 18003 --api-model Qwen3.6-27B --api-key qwen-local-key --reset'
```

ReAcTree WAH 主表公平口径：

```bash
tmux new -d -s wah_paper_reactree_wm_fullobs_qwen36 \
  '/data/zmy/envs/ouragent/bin/python benchmark/reactree/wah/paper_method/code/run.py --run-name wah_paper_reactree_wm_fullobs_qwen36 --workers 1 --ports 18003 --api-model Qwen3.6-27B --api-key qwen-local-key --config-name wah_headless_reactree_wm --full-observable --official-base-port 9950 --official-port-ids 0 --official-timeout-s 240 --reset'
```

ReAcTree ALFRED valid_seen 主表公平口径：

```bash
tmux new -d -s alfred_paper_reactree_wm_seen_qwen36 \
  '/data/zmy/envs/ouragent/bin/python benchmark/reactree/alfred/paper_method/code/run.py --run-name alfred_paper_reactree_wm_seen_qwen36 --eval-set valid_seen --workers 1 --ports 18003 --api-model Qwen3.6-27B --api-key qwen-local-key --config-name alfred_reactree --full-observable --x-displays 0 --eval-portion 100 --reset'
```

ALFRED valid_unseen 把 `--eval-set valid_seen` 改成 `valid_unseen`，并换一个可用 X display 或单独 tmux 串行运行。

常用 tmux 查看命令：

```bash
tmux ls
tmux attach -t <session-name>
tmux capture-pane -pt <session-name> -S -120
```

## ReAcTree 公平对比口径

如果 OurAgent framework 使用全景环境信息，ReAcTree paper method 主比较也应加 `--full-observable`，否则输入假设不对等。

主表建议使用：

| 数据集 | ReAcTree baseline |
| --- | --- |
| WAH-NL | `--config-name wah_headless_reactree_wm --full-observable` |
| ALFRED | `--config-name alfred_reactree --full-observable` |

可选消融：

| 变体 | WAH 命令差异 | ALFRED 命令差异 |
| --- | --- | --- |
| ReAct | `--config-name wah_headless_react` | `--config-name alfred_react --paper-override llm_agent.working_memory=False` |
| ReAct + WM | `--config-name wah_headless_react --paper-override llm_agent.working_memory=True` | `--config-name alfred_react` |
| ReActree | `--config-name wah_headless_reactree` | `--config-name alfred_reactree --paper-override llm_agent.working_memory=False` |
| ReActree + WM | `--config-name wah_headless_reactree_wm` | `--config-name alfred_reactree` |

这些消融如果用于对比全景 framework，也都应加 `--full-observable`。

## 当前重要修正

- DELTA paper method 通过 shim 设置 `DELTA_VLLM_BASE_URL`、`DELTA_VLLM_API_KEY`、`DELTA_VLLM_MODEL` 等环境变量，不修改 `/data/zmy/DELTA`。
- ReAcTree WAH paper method 默认追加 `+environment.executable_args.no_graphics=True`，除非用户通过 `--paper-override environment.executable_args.no_graphics=...` 显式覆盖。
- ReAcTree WAH `--full-observable` 使用本仓库 wrapper 和 overlay，把初始全量对象/位置写入 observation 和工作记忆，并让合法动作集合基于全量对象。
- ReAcTree ALFRED paper method 使用本地 all-MiniLM embedding：`/home/zmy/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/1110a243fdf4706b3f48f1d95db1a4f5529b4d41`。这是为了和当前 ReAcTree RAG 向量维度对齐，避免 all-roberta 1024 维与已有 384 维索引不匹配。
- ALFRED smoke 使用 `benchmark/reactree/alfred/paper_method/scratch/alfred_singleton_splits_20260807.json` 和 `llm_agent.max_steps=20` / `max_decisions=20`，只用于快速链路验证；full 不要带 singleton split 和 20-step override。
- ReAcTree paper wrapper 已处理当前 `jinja2` 的 `Markup/escape` 兼容问题。

## 输出目录

常规 wrapper 输出：

```text
benchmark/<paper>/<dataset>/paper_method/results/<run-name>/
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

DELTA 结果额外依赖外部日志：

```text
cases/<domain>__<scene>/run.log
cases/<domain>__<scene>/artifacts/
```

EAI 结果额外包含：

```text
artifacts/generated/<dataset>/action_sequencing/<run-name>_outputs.json
artifacts/evaluated/<dataset>/evaluate_results/action_sequencing/<run-name>/summary.json
```

ALFRED paper method 是论文原生批量评估，主要结果在：

```text
benchmark/reactree/alfred/paper_method/results/<run-name>/
  summary.json
  raw_output.json
  run.log
  paper_run/results.jsonl
```

`summary.json` 里会记录实际传给 ReAcTree 的 command、`api_base`、`api_model`、`paper_overrides`、`observability`、`returncode` 和 `result_path`。

## 常用参数

| 参数 | 作用 |
| --- | --- |
| `--ports` | LLM 服务端口，当前默认使用 18003/18004；ALFRED 需要补充 fine-tuned 对比时也可显式传 8005。 |
| `--api-model` / `--api-key` | 覆盖端口对应模型名和 key。 |
| `--workers` | wrapper 并发数；ALFRED paper batch 实际由论文 evaluator 自己批量跑。 |
| `--run-name` | 结果目录名。 |
| `--limit` | 只跑前 N 条；ALFRED paper batch 不用这个控制 full，使用 `--eval-portion` 或 split override。 |
| `--case-id` / `--case-ids-file` | 指定 case；WAH paper 可用，ALFRED paper batch 通常用 split 文件。 |
| `--valid-only` | 仅 EAI VirtualHome 使用，过滤缺失 `problem_pddl` 的 case。 |
| `--reset` | 删除同名旧结果后重新跑。 |
| `--resume` | 跳过已有完成 case。 |
| `--dry-run` | 只写命令和目录，不调用模型。 |
| `--summary` | 读取已有 `summary.json`。 |
| `--full-observable` | ReAcTree paper method 全景公平化开关。 |
| `--paper-override` | 追加 Hydra 覆盖项，例如 `--paper-override llm_agent.working_memory=True`。 |
| `--official-base-port` / `--official-port-ids` | WAH Unity evaluator 端口。 |
| `--x-displays` | ALFRED AI2-THOR 使用的 X display。 |

## 本次已核对结果

| 数据集 | run_name | 状态 |
| --- | --- | --- |
| DELTA | `smoke_real_delta_paper_20260807` | `done_cases=1, failed_cases=0` |
| EAI BEHAVIOR | `smoke_real_behavior_paper_20260807` | `done_cases=1, failed_cases=0` |
| EAI VirtualHome | `smoke_real_virtualhome_paper_3_1_20260807` | `done_cases=1, failed_cases=0` |
| ReAcTree WAH | `smoke_real_wah_paper_fixed_20260807` | `done_cases=1, failed_cases=0, goal_success_rate=1` |
| ReAcTree ALFRED valid_seen | `smoke_real_alfred_paper_seen_single_x0_minilm20_20260807` | `status=done, returncode=0, total_cases=1` |
| ReAcTree ALFRED valid_unseen | `smoke_real_alfred_paper_unseen_single_x0_minilm20_20260807` | `status=done, returncode=0, total_cases=1` |
