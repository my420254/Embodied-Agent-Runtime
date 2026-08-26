# LLM Config And Baseline IO Audit 20260807

## 结论

本次已把实验入口的 LLM 配置收敛为同一个来源：

- 非 framework 实验统一经 `benchmark/experiment_utils.py -> config/llms.py` 解析模型、端口、key、`max_tokens`、`temperature`。
- framework 实验仍使用各自 `benchmark/*/framework/code/config/settings.json`，但这些配置通过 `activate_config(...)` 后也由 `config/llms.py` 读取。
- 当前自动候选端口已限制为：DELTA/Qwen3.5 使用 `18004`，其他四个数据集/Qwen3.6 使用 `18003`。
- 实验 LLM 温度统一为 `0`，planning `max_tokens=4096`。之前 dry-run 默认落到 `0.2` 的问题已消除。

## 当前端口与模型

| 范围 | 端口 | 模型 | temperature | max_tokens |
| --- | --- | --- | --- | --- |
| DELTA | `18004` | `Qwen3.5-9B` | `0.0` | `4096` |
| EAI BEHAVIOR | `18003` | `Qwen3.6-27B` | `0.0` | `4096` |
| EAI VirtualHome | `18003` | `Qwen3.6-27B` | `0.0` | `4096` |
| ReAcTree WAH | `18003` | `Qwen3.6-27B` | `0.0` | `4096` |
| ReAcTree ALFRED | `18003` | `Qwen3.6-27B` | `0.0` | `4096` |

全局根配置 `/data/zmy/OurAgent-he1/config/settings.json` 中：

- `18001.enabled=false`
- `18002.enabled=false`
- `18003.enabled=true, model_name=Qwen3.6-27B`
- `18004.enabled=true, model_name=Qwen3.5-9B`

五套 framework config 也已同步禁用 `18001/18002`，避免漏传 `--ports` 时自动选到旧端口。

## 改动文件

| 文件 | 改动 |
| --- | --- |
| `config/llms.py` | 新增中心化 endpoint/model/generation 解析和 `chat_completion_text(...)`。 |
| `benchmark/experiment_utils.py` | 非 framework runner 的 `endpoint_slots(...)`、`chat_completion(...)` 改为代理到 `config/llms.py`。 |
| `config/settings.json` | 根配置默认 3.6 指向 `18003`；understanding/planning/execution/reflection 温度均为 `0`；禁用 `18001/18002`。 |
| `benchmark/*/framework/code/config/settings.json` | 五套 framework 配置禁用 `18001/18002`，保留 `18003/18004`。 |
| `benchmark/delta/external_delta_runner.py` | DELTA bare/paper 命令传入中心解析出的 `-t 0.0`，manifest/case 记录 `temperature/max_tokens`。 |
| `benchmark/eai/external_eai_runner.py` | EAI bare/paper 使用中心 slot；bare baseline 从 `benchmark/datasets/extracted/eai/*/cases.json` 取抽取环境。 |
| `benchmark/reactree/external_reactree_runner.py` | WAH/ALFRED bare baseline 使用抽取环境；ALFRED 支持 `--eval-set`；case 记录 `temperature/max_tokens`。 |

## ALFRED 裸基线输入修正

之前 ALFRED bare baseline 的 prompt 使用 raw annotation 中的 scene summary，dry-run 时没有真实 initial observation，会出现“not available from simulator”的占位。这不适合和 framework 的抽取环境作公平对比。

现在 ALFRED bare baseline：

- case 来源：`benchmark/datasets/extracted/reactree/alfred/cases_valid_seen.json` 或 `cases_valid_unseen.json`。
- 环境来源：每条 case 的 `initial_scene_cache_path`。
- prompt 环境字段：
  - `Initial observation text`
  - `Visible object groups`
  - `Object catalog from extracted initial scene cache`
- 对象目录包含 `name/direct_parent/is_receptacle/states/properties/object_type`，不包含坐标，不包含 gold plan，不包含 evaluator success。
- 官方仿真评估仍走 ALFRED annotation + AI2-THOR evaluator，未改成 framework skill 或 planner 输出。

dry-run 证据：

| split | run | case_count | prompt 检查 |
| --- | --- | ---: | --- |
| valid_seen | `benchmark/reactree/alfred/bare_baseline/results/audit_alfred_bare_seen_dry_config_20260807` | 1 | 有 extracted object catalog；无 raw scene summary 占位。 |
| valid_unseen | `benchmark/reactree/alfred/bare_baseline/results/audit_alfred_bare_unseen_dry_config_20260807` | 1 | 有 extracted object catalog；无 simulator unavailable 占位。 |
| paper valid_unseen | `benchmark/reactree/alfred/paper_method/results/audit_alfred_paper_unseen_dry_config_20260807` | 1% dry-run | 命令含 `dataset.eval_set=valid_unseen`、`llm_agent.model_name=Qwen3.6-27B`、`api_base=18003`。 |

## 源码扫描结果

源码级扫描中没有发现新的 `temperature=0.2` 实验入口。剩余 `0.2` 命中来自：

- `time.sleep(0.25)` 这类等待。
- ALFRED 文本指标阈值 `step_match_rate_f1_gt_0_2`。
- 历史日志/结果文件。

仍存在直接 OpenAI 调用的源码集中在论文原方法或 DELTA shim：

- DELTA shim：通过外层 runner 传入 slot/环境变量，温度已固定为 `0.0`。
- ReAcTree ALFRED paper overlay：原方法适配层直接调用 OpenAI-compatible client，代码级固定 `temperature=0.0`。
- ReAcTree WAH delta_method 是单独旧实验路径，不是当前五数据集主公平线。

## 验证命令

已执行并通过：

```bash
python -m compileall config/llms.py benchmark/experiment_utils.py benchmark/reactree/external_reactree_runner.py benchmark/eai/external_eai_runner.py benchmark/delta/external_delta_runner.py -q
```

端口解析验证：

```text
framework delta auto -> 18004 / Qwen3.5-9B / temperature 0.0 / max_tokens 4096
framework eai_behavior auto -> 18003 / Qwen3.6-27B / temperature 0.0 / max_tokens 4096
framework eai_virtualhome auto -> 18003 / Qwen3.6-27B / temperature 0.0 / max_tokens 4096
framework reactree_alfred auto -> 18003 / Qwen3.6-27B / temperature 0.0 / max_tokens 4096
framework reactree_wah auto -> 18003 / Qwen3.6-27B / temperature 0.0 / max_tokens 4096
non-framework --ports 18003 -> Qwen3.6-27B / temperature 0.0 / max_tokens 4096
non-framework --ports 18004 -> Qwen3.5-9B / temperature 0.0 / max_tokens 4096
```

## 对精度的影响

这次改动主要消除配置漂移，不应改变已经启动的 full framework 进程的模型调用，因为那些进程启动时已经显式带端口并读取过配置。后续新启动实验会更稳定：

- 不再因为 dry-run 默认温度 `0.2` 和正式命令温度 `0` 不一致而产生记录偏差。
- 不再因为忘记 `--ports` 自动选到 18002/18001。
- ALFRED bare baseline 的输入更接近 framework 的抽取环境，旧的 ALFRED bare dry-run 报告如果基于 raw scene summary，应视为过期。
