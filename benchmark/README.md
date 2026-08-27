# Benchmark 统一运行说明

本目录统一管理 DELTA、EAI BEHAVIOR、EAI VirtualHome、ReAcTree ALFRED 和 ReAcTree WAH。正式 framework 实验只允许从各数据集的 `framework/code/run.py` 启动；推荐使用同目录的 `run.sh` 一键入口。

## 运行前提

从仓库根目录运行：

```bash
cd <PROJECT_ROOT>
export OURAGENT_WORKSPACE_ROOT=/data/zmy
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY all_proxy
```

`run.sh` 会再次清除代理变量，避免本地 OpenAI-compatible 接口被系统代理转发。

默认解释器：

| 用途 | 路径 |
| --- | --- |
| framework | `/data/zmy/envs/ouragent/bin/python` |
| ReAcTree 原论文子进程 | `/data/zmy/envs/reactree_py38/bin/python` |

## 唯一入口

| 数据集 | 一键入口 | 默认规模 |
| --- | --- | ---: |
| DELTA | `benchmark/delta/framework/code/run.sh` | 600 |
| EAI BEHAVIOR | `benchmark/eai/behavior/framework/code/run.sh` | 100 |
| EAI VirtualHome | `benchmark/eai/virtualhome/framework/code/run.sh` | 342 |
| ReAcTree ALFRED | `benchmark/reactree/alfred/framework/code/run.sh` | seen 820；unseen 821 |
| ReAcTree WAH | `benchmark/reactree/wah/framework/code/run.sh` | task-level 100 |

`run.sh` 只定位仓库、选择 Python、清除代理并调用同目录 `run.py`。禁止直接调用 `launcher.py` 或 `_case_worker.py` 做正式实验；launcher 会校验入口标记。

## 单一配置源

每个 framework 的运行参数只在以下文件维护：

```text
benchmark/<paper>/<dataset>/framework/code/config/launch_config.json
benchmark/<paper>/<dataset>/framework/code/config/settings.json
```

`launch_config.json` 管理 `ports`、`launch_shards`、`expected_count`、超时、仿真资源和结果名；`settings.json` 管理模型名/key、prompt、rules、skill root 和 feature flags。长期变更接口、模型、分片或仿真端口时直接修改配置文件，命令行只用于一次性覆盖。

`launch_shards` 是整个实验的总分片数。每个 unit 固定绑定一个 LLM endpoint 和一个仿真资源；同一 unit 内案例串行，不同 unit 并行。ReAcTree 默认 3 个接口、5 个总分片：

| unit | LLM | ALFRED display | WAH port id |
| ---: | ---: | ---: | ---: |
| 0 | 18002 | 1200 | 700 |
| 1 | 18003 | 1201 | 701 |
| 2 | 18004 | 1202 | 702 |
| 3 | 18002 | 1203 | 703 |
| 4 | 18003 | 1204 | 704 |

因此接口案例量为 `2:2:1`，是固定 shard 轮转，不是接口失效。当前三个端口均为 Qwen3.6-27B。ALFRED 使用 X display `1200-1204`；WAH 使用 `official_base_port=8906`、port id `700-704`（TCP `9606-9610`）。数据从 `benchmark/datasets/extracted/reactree` 加载。

## 预检、冒烟和全量

静态预检：

```bash
benchmark/reactree/alfred/framework/code/run.sh --preflight --all-cases --eval-set valid_seen
benchmark/reactree/wah/framework/code/run.sh --preflight
```

仿真预检：

```bash
benchmark/reactree/alfred/framework/code/run.sh --sim-preflight --limit 5 --expected-count 5
benchmark/reactree/wah/framework/code/run.sh --sim-preflight --limit 5 --expected-count 5
```

端到端冒烟：

```bash
benchmark/reactree/alfred/framework/code/run.sh --run-name smoke_alfred --limit 5 --expected-count 5
benchmark/reactree/wah/framework/code/run.sh --run-name smoke_wah --limit 5 --expected-count 5
```

冒烟后检查 `launch_manifest.json` 的 endpoint/unit/资源映射，以及每个 case 的 `worker_result.json`、`llm_io.json`、`official_eval.json`、`rounds/interceptions.md` 和实际 `LANGGRAPH_JSZN_*_API_BASE`。

配置确认后一键全量：

```bash
benchmark/reactree/alfred/framework/code/run.sh --run-name reactree_alfred_seen --all-cases --eval-set valid_seen
benchmark/reactree/alfred/framework/code/run.sh --run-name reactree_alfred_unseen --all-cases --eval-set valid_unseen --expected-count 821
benchmark/reactree/wah/framework/code/run.sh --run-name reactree_wah_full
benchmark/delta/framework/code/run.sh --run-name delta_framework_full
benchmark/eai/behavior/framework/code/run.sh --run-name eai_behavior_framework_full
benchmark/eai/virtualhome/framework/code/run.sh --run-name eai_virtualhome_framework_full
```

长任务可用 tmux，但 tmux 中仍调用 `run.sh`。中断后用同一 `run_name` 加 `--resume`；`done` 或 `evaluation_failed` 会跳过，失败/缺失结果会重跑。

## 输出与数据边界

结果目录为 `benchmark/<paper>/<dataset>/framework/results/<run-name>/`。主要文件是 `launch_manifest.json`、`merged_results.json`、`summary.json`、每案例 `worker_result.json`、`artifacts/llm_io.json`、`official_eval.json` 和 `rounds/interceptions.md`。

framework 输入必须来自 `benchmark/datasets/extracted`；不要把 paper method 中间答案、专家轨迹或 official evaluator 输出回填到 framework prompt。原生数据只能用于环境初始化和最终官方评测。
