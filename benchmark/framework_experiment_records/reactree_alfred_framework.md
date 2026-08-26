# ReAcTree ALFRED Framework Smoke Audit

更新时间：2026-08-06 18:50 UTC

## 结论

ReAcTree ALFRED valid_seen 3.6 冒烟已通过，并且使用真实 AI2-THOR official evaluator。当前框架不再用 `planning_output_mode=native_actions` 分流；`todo_list` 内直接保存 ALFRED/ReAcTree 原生动作 JSON，每步形如 `{"action": "go to", "target": "Fridge (1)"}`，不是 framework 的 `execution/skill/parameters` 包装。

本次 smoke：

- case：`pick_heat_then_place_in_recep-PotatoSliced-None-SinkBasin-13__trial_T20190909_115736_122556__ann_0`
- eval set：`valid_seen`
- instruction：`Place a cooked potato slice in the sink`
- 模型接口：18003
- 模型名：`Qwen3.6-27B`
- X display：`:71`
- 运行命令：

```bash
python benchmark/reactree/alfred/framework/code/run.py \
  --run-name reactree_alfred_seen_smoke_20260806_todo_hooks_fix2 \
  --eval-set valid_seen \
  --limit 1 \
  --expected-count 1 \
  --workers 1 \
  --launch-shards 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key \
  --x-display 71
```

结果：

- `count=1`
- `task_success_count=1`
- `task_success_rate=1.0`
- `goal_success_rate=1.0`
- `subgoal_success_rate=1.0`
- `official_available_count=1`
- `official_task_success_rate=1.0`
- `execution_success_count=1`
- `evaluation_mode=alfred_framework_official_ai2thor`
- `execution_status=completed`
- `is_feasible=true`
- `todo_parse_error=""`
- `todo_count=18`
- `validated_todo_actions_count=18`
- `state_diff_audit.passed=true`
- official action trace：18 步全部 `possible=true`

完整 artifacts 已复制到：

```text
/data/zmy/OurAgent-he1/benchmark/framework_experiment_records/reactree_alfred_artifacts/smoke_todo_hooks
```

## 本次修复

第一次 ALFRED official smoke 失败在 official evaluator import：

```text
ModuleNotFoundError: No module named 'alfred.env'
```

原因是 ReAcTree 里有两套 ALFRED 路径：

- `/data/zmy/ReAcTree/alfred/env/thor_env.py`：官方 ALFRED/AI2-THOR 环境。
- `/data/zmy/ReAcTree/src/alfred/*.py`：ReAcTree 自己的 ALFRED wrapper。

`/data/zmy/ReAcTree/alfred` 没有顶层 `__init__.py`，而 `/data/zmy/ReAcTree/src/alfred` 是普通 package，导致 `import alfred.env.thor_env` 被错误解析到 `src/alfred` 包下面。

已修复文件：

```text
/data/zmy/OurAgent-he1/benchmark/reactree/alfred/framework/code/official_evaluator.py
```

修复内容：

- official evaluator 启动时显式建立顶层 `alfred` namespace。
- `alfred.__path__` 同时包含 `/data/zmy/ReAcTree/alfred` 和 `/data/zmy/ReAcTree/src/alfred`。
- 这样 `alfred.env.thor_env` 指向官方环境，`alfred.utils` 指向 ReAcTree wrapper。

这只影响 official worker 的 Python import 路径，不改变 prompt、模型输出、`todo_list` 或评估标准。

## 数据字段

case 输入关键字段：

- `task=pick_heat_then_place_in_recep-PotatoSliced-None-SinkBasin-13/trial_T20190909_115736_122556`
- `repeat_idx=0`
- `instruction=Place a cooked potato slice in the sink`
- `task_source=alfred_pp_annotation_json`
- `environment_source=alfred_official_scene_prepare_cache`
- `initial_scene_cache_path=/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/alfred/initial_envs/pick_heat_then_place_in_recep-PotatoSliced-None-SinkBasin-13__trial_T20190909_115736_122556__ann_0.json`

输入来自 ALFRED annotation 和抽取后的 official scene prepare cache；不读取 expert trajectory 作为动作答案。reference text 指标仅用于文本相似度统计。

## 环境闭包

本次 planning 使用的 ALFRED 环境闭包：

- `entity_catalog`：105 个 ALFRED 实体。
- `scene` 字段包含 `kitchen`、`robot_holding_items`、`robot_inventory`、`robot_location`。
- 初始机器人：`robot_location=kitchen_anchor`，`robot_holding=空`，`x_display=71`。
- 关键实体：`Fridge (1)`、`Potato (1)`、`CounterTop (1)`、`Microwave (1)`、`SinkBasin (1)`。

## todo_list 格式

本次最终通过的 `todo_list`：

```json
[
  {"step": 1, "action": "go to", "target": "Fridge (1)"},
  {"step": 2, "action": "open", "target": "Fridge (1)"},
  {"step": 3, "action": "pick up", "target": "Potato (1)"},
  {"step": 4, "action": "go to", "target": "CounterTop (1)"},
  {"step": 5, "action": "put down", "target": "Potato (1)"},
  {"step": 6, "action": "slice", "target": "Potato (1)"},
  {"step": 7, "action": "pick up", "target": "Potato (2)"},
  {"step": 8, "action": "go to", "target": "Microwave (1)"},
  {"step": 9, "action": "open", "target": "Microwave (1)"},
  {"step": 10, "action": "put down", "target": "Potato (2)"},
  {"step": 11, "action": "close", "target": "Microwave (1)"},
  {"step": 12, "action": "turn on", "target": "Microwave (1)"},
  {"step": 13, "action": "turn off", "target": "Microwave (1)"},
  {"step": 14, "action": "open", "target": "Microwave (1)"},
  {"step": 15, "action": "pick up", "target": "Potato (2)"},
  {"step": 16, "action": "close", "target": "Microwave (1)"},
  {"step": 17, "action": "go to", "target": "SinkBasin (1)"},
  {"step": 18, "action": "put down", "target": "Potato (2)"}
]
```

官方 evaluator 接收到的动作在末尾追加 `done`，总计 19 条 official actions。

使用的 todo hooks：

```text
todo_output_parser_path=benchmark.reactree.alfred.framework.code.native_actions.parse_alfred_native_actions
todo_step_adapter_path=benchmark.reactree.alfred.framework.code.native_actions.alfred_native_step_to_skill_call
todo_list_validator_path=benchmark.reactree.alfred.framework.code.native_plan_validator.validate_todo_list
```

## 检查链路

1. Understanding 根据 ALFRED case 输入和实体表抽取结构化任务。
2. Planning prompt 注入 ALFRED skill contract，模型输出 ALFRED 原生动作 JSON 数组。
3. `todo_output_parser` 解析 JSON 数组。
4. `todo_contract` 检查动作名、`target` 字段和额外字段。
5. `todo_list_validator` 执行 ALFRED 计划级检查。
6. sandbox 用 `todo_step_adapter` 执行动作并更新 ALFRED 环境。
7. 第一次 planning 在第 7 步被拦截：`unknown ALFRED instance 'Potato (1)'`。原因是 slice 后原始 `Potato (1)` 被替换为 sliced instances。
8. repair 后模型改用 `Potato (2)`，18 步计划通过 sandbox。
9. `state_diff_audit` 检查最终态：sliced/cooked potato 放入 `SinkBasin (1)`。
10. AI2-THOR official evaluator 执行 18 步动作并 `done`，返回成功。

contract artifact 显示：

- `status=passed`
- `enabled_contract_skill_count=8`
- `todo_list_count=18`
- `validated_todo_actions_count=18`
- `validated_steps_count=0`
- `execution_wrapper_count=0`
- 原生动作集合包括 `go to`、`pick up`、`put down`、`open`、`close`、`turn on`、`turn off`、`slice`。

## 状态变化

`state_diff_audit` 接受的变化：

- `Potato (1) removed (sliced)`
- `Potato (2) added (sliced, cooked, placed in SinkBasin)`
- `Potato (3-10) added (sliced, on CounterTop)`
- `Fridge (1) opened`
- `Microwave (1) used for cooking`
- `Robot moved to SinkBasin (1)`

official action trace 前 6 步均 `possible=true`，完整 trace 在：

```text
.../smoke_todo_hooks/cases/pick_heat_then_place_in_recep-PotatoSliced-None-SinkBasin-13__trial_T20190909_115736_122556__ann_0/artifacts/official_eval.json
```

## LLM 调用

本次 trace 记录 5 次模型调用：

- `understanding.system`
- `understanding.final_state`
- `planning.main_system`，初次 planning
- `planning.main_system`，repair planning
- `planning.state_diff_audit`

prompt 大小记录：

- understanding system prompt：9565 chars
- final-state prompt：7734 chars
- 初次 planning prompt：76096 chars
- repair planning prompt：81321 chars
- state-diff audit prompt：50590 chars

完整输入输出：

```text
.../smoke_todo_hooks/cases/pick_heat_then_place_in_recep-PotatoSliced-None-SinkBasin-13__trial_T20190909_115736_122556__ann_0/artifacts/llm_io.json
.../smoke_todo_hooks/cases/pick_heat_then_place_in_recep-PotatoSliced-None-SinkBasin-13__trial_T20190909_115736_122556__ann_0/trace_report.md
```

## Reference Text 指标

本次还统计了 ALFRED reference text 对比：

- reference steps：12
- generated steps：18
- step count MAE：6
- overall ROUGE-1 F1：0.2253521127
- overall ROUGE-2 F1：0.0283687943
- overall ROUGE-L F1：0.1760563380

这个文本指标只反映和标注文本的相似度，不等价于仿真成功率；本条 official AI2-THOR 仿真成功。

## 全量运行

ALFRED valid_seen full 已排在 18003 队列的 WAH full 之后，当前尚未启动：

```text
/data/zmy/OurAgent-he1/benchmark/reactree/alfred/framework/results/reactree_alfred_seen_full_20260806_todo_hooks
```

队列命令：

```bash
python benchmark/reactree/alfred/framework/code/run.py \
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

valid_unseen full 需要单独启动，使用 `--eval-set valid_unseen --expected-count 821`，并分配不冲突的 X display。

## 2026-08-07 裸基线对照

本轮补做了 `/data/zmy/alfred` bare baseline 1-case 对照：

- `codex_live_sim_18004_20260807`
  - 模型输出拒绝执行的说明文字
  - 文本 `ROUGE-1=0.1667`，解析器识别为非计划输出，只生成 `done`
  - AI2-THOR official 可用，`execution_success=1`，但 `task_success=0`
- `codex_live_sim_8005_20260807`
  - 模型输出了 12 步计划
  - 但把 `Knife`、`Potato` 的位置和状态理解错了
  - 文本 `ROUGE-1=0.4788`，步数和 reference 一致
  - AI2-THOR official 可用，但 `execution_success=0`、`task_success=0`

诊断结论：

- 18004 的低分主要来自模型没有进入 ALFRED planning 格式，而不是 evaluator 或 skill bug。
- 8005 已能输出合理的编号步骤，但自然语言计划缺少真实对象实例和可见位置 grounding；本例把 knife 放在 sink、potato 放在 table，和 official 初始化场景不一致，所以真实仿真失败。
- Framework smoke 同一 case 成功，说明 ALFRED framework 的实体表、`todo_list` parser、repair、sandbox hooks 和 official evaluator 是连通的。
- 已核对 ALFRED skills：`turn_on`/`close`/`turn_on Faucet` 覆盖 heat/cook、cool、clean 语义，`slice` 会生成 sliced instances，`native_plan_validator` 覆盖 `look_at_obj_in_light` 特殊规则。当前 20 左右的文本 ROUGE 不能直接解释为仿真精度低；它只说明框架生成的官方动作 JSON 和人工 high-level 文字表述不相似。

结论：ALFRED 低分主要来自计划输出和场景 grounding，不是 official evaluator 出错。当前 framework 已经有 heat/cool/clean/look_at 相关的基础状态推进和 validator，剩余问题更多在模型规划质量。
