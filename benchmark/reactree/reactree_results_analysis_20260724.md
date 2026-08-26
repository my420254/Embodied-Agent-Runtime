# ReAcTree 结果分析

日期：2026-07-24

范围：只分析 ReAcTree 论文相关结果，包括 WAH 和 ALFRED 两个 framework run。未修改公共框架代码。

续接来源：

- session id：`019f825b-6930-7862-9cab-218c19e52b51`
- rollout：`/data/zmy/.codex_runtime/sessions/2026/07/21/rollout-2026-07-21T01-47-36-019f825b-6930-7862-9cab-218c19e52b51.jsonl`

## 结果目录

WAH full：

- `reactree/wah/framework/results/framework_full_20260723_134002_reactree_wah_18003_5shards`
- `summary.json` 修改时间：2026-07-23 14:33:59 +0000
- 当前 `reactree/wah/framework/code/case_executor.py` 修改时间：2026-07-24 06:59:17 +0000

ALFRED full：

- `reactree/alfred/framework/results/framework_full_20260723_134002_reactree_alfred_18004_5shards`
- `summary.json` 修改时间：2026-07-23 22:27:36 +0000
- 当前 `reactree/alfred/framework/code/case_executor.py` 修改时间：2026-07-24 07:03:49 +0000

注意：WAH full 结果早于当前 executor 的空动作兜底修复，所以 39 个空动作失败不能直接代表当前代码重跑后的分数。

## 总结结论

1. WAH 结果本身是 100 例，summary GSR 32.0；官方可用 92 例，official GSR 34.78，official SSR 48.53。8 例官方评测不可用，原因是 Unity timeout 或端口占用，不应算作方法本身失败。
2. WAH 的 SDA 有正向作用证据：有 7 个 case 是 SDA 修改计划后本地 feasible 且官方成功。但也有 39 个 case 在旧结果里变成空动作提交，且这些 case 的 `original_native_action_plan` 都存在，需要用当前代码重跑确认兜底后的真实官方分数。
3. ALFRED full 的 3.29% 不能简单理解为模型能力极低。820 例中只有 4 例同时满足“本地 sandbox/SDA 闭环通过”和“官方成功”。另外 23 例官方成功来自 executor 把本地判失败的 native/original plan 仍提交给官方。
4. ALFRED 的主要问题是 ReAcTree-ALFRED 适配层，而不是公共 planning/SDA 主体：500/820 缺少可比较最终态，157/820 是本地 sandbox 误报 `unknown ALFRED instance`，132/820 是空动作或序列解析失败。
5. 初步修复可以只动 ReAcTree 自己的 ALFRED framework 代码：`task_environment.py`、`final_state.py`、ALFRED skills 和 prompts/config。除非要改公共环境闭包策略，否则不需要动 `graph/` 或公共 bridge。

## WAH 详细分析

### 分数

- full count：100
- summary GSR：32.0
- summary SSR：44.65
- official 可用：92
- official GSR：34.78
- official SSR：48.53
- real5：5/5，GSR 100，SSR 100
- startup smoke：1/1，GSR 100，SSR 100

按任务类型看 full run：

| task_name | success | failed | official unavailable |
| --- | ---: | ---: | ---: |
| prepare_food | 5 | 13 | 2 |
| prepare_snack | 10 | 8 | 2 |
| put_dishwasher | 9 | 10 | 1 |
| put_fridge | 4 | 14 | 2 |
| setup_table | 4 | 15 | 1 |

### 失败分布

按 feedback bucket：

- `valid_by_sandbox`：41
- `sequence_parse_or_empty`：39
- `physical_reachability`：19
- `position precondition failed`：1

SDA/计划变化分布：

- `changed + success + feasible`：7
- `changed + fail + feasible`：2
- `empty_after_orig + fail + infeasible`：39
- `triggered_no_change + success + infeasible`：11
- `triggered_no_change + fail + infeasible`：9
- `not_triggered + success + feasible`：14
- `not_triggered + fail + feasible`：18

### 关键证据

正向 SDA 例子：`cases/12__0`

- 原问题：第 1 步 `pick up apple 1` 前置位置不满足。
- SDA 修复：加了 `go to coffee table 1`。
- 最终 native plan 9 步，validated 9 步，官方 trace 9 步。
- 最终 GSR/SSR 都是 1.0。

空动作旧结果例子：`cases/20__0`

- 任务：把 fork、wine glass、water glass 放进 dishwasher 并打开。
- `native_action_plan` 长度 0，`validated_native_actions` 长度 0。
- `sda_state.native_trajectory.original_native_action_plan` 长度 24。
- 旧结果提交 `official_actions=[]`，所以 GSR/SSR 都是 0。
- 当前 WAH executor 已有兜底逻辑，若重跑应不会再提交空动作；但这只是防止空提交，不代表 SDA 修复已经正向完成任务。

物理失败例子：`cases/10__0`

- 最终 native plan 26 步，validated 15 步。
- SDA issue：第 16 步 `pick up apple 1` 物理可达性受限。
- 官方 SSR 0.75，说明部分子目标完成，但整体失败。

### WAH 当前判断

WAH 不是完全坏掉，SDA 能修一部分前置位置和手部冲突。但 full run 有两个口径问题必须先处理：

1. 旧 full 结果早于当前空动作兜底代码，39 个空动作 case 需要重跑确认。
2. 8 个 Unity official unavailable 是环境/端口问题，不应和方法失败混在一起。

WAH 下一步建议：

```bash
./reactree/wah/framework/code/run.sh \
  --case-id '20:0' \
  --expected-count 1 \
  --run-name reactree_wah_case20_after_executor_fallback \
  --worker-timeout-s 1800
```

然后再抽 3 类 case 对照：

- SDA 成功：`12:0`
- 空动作旧失败：`20:0`
- 物理可达失败：`10:0`

## ALFRED 详细分析

### 分数

- full count：820
- GSR：3.2927，也就是 27/820
- SSR：3.2927
- official evaluator 全部可用
- real5：0/5
- startup smoke：0/1

但这 27 个成功里：

- 4 个是本地 sandbox/SDA feasible 且官方成功。
- 23 个是本地 sandbox 判失败，但 executor 仍把 native/original plan 交给官方后成功。

因此，当前 ALFRED 结果的真实含义是：官方偶尔能跑通模型动作，但本地 SDA/最终态闭环大面积不可信。

### 失败分布

按 feedback bucket：

- `missing_goal_state`：500
- `unknown_alfred_instance`：160
- `sequence_parse_or_empty`：132
- `valid_by_sandbox`：13
- `position_precondition`：12
- 其他少量：3

按任务类型：

| task type | count | 主要失败 |
| --- | ---: | --- |
| look_at_obj_in_light | 94 | missing goal、unknown instance、空动作 |
| pick_and_place_simple | 142 | missing goal 107 |
| pick_and_place_with_movable_recep | 115 | missing goal 72、unknown 28 |
| pick_clean_then_place_in_recep | 112 | missing goal 45、空动作 36、unknown 29 |
| pick_cool_then_place_in_recep | 126 | missing goal 65、unknown 31、空动作 28 |
| pick_heat_then_place_in_recep | 107 | missing goal 80、unknown 23 |
| pick_two_obj_and_place | 124 | missing goal 98 |

### 问题 1：最终态目标缺失

820 例中，understanding 或 external goal 状态：

- `has_understanding_goal=false` 且 `has_external_goal=false` 的 `missing_goal_state`：500
- 只有 `look_at_obj_in_light` 有少量 goal_state，其他任务类型几乎都没有。

例子：`look_at_obj_in_light-AlarmClock...__ann_0`

- understanding 生成了 `goal_state.robot.looking_at = AlarmClock`。
- 但 ALFRED skills 没有设置 `robot.looking_at`，所以 state diff audit 最终失败。

同一任务的 `ann_1`：

- understanding 没有生成 `goal_state`。
- 结果直接失败为“缺少可比较的最终态目标”。

结论：ALFRED 不能依赖 LLM 随机生成 `structured_task.goal_state`。ReAcTree ALFRED 的原生 task 字符串已经包含 task type、target、movable receptacle、destination，应在 ReAcTree-ALFRED 自己的 `align_structured_task` 或 `final_state.py` 里确定性生成/比较目标。

### 问题 2：本地 sandbox 环境被过度裁剪

典型例子：`look_at_obj_in_light-Bowl-None-DeskLamp-301__ann_0`

- `prepared_environment_summary` 的 ALFRED scene 有 42 个实体，`entity_catalog` 包含 `Desk (1)`。
- `planning_input_summary.task_environment_override` 只剩 `bedroom` 和 `bedroom_anchor` 两个实体。
- 模型输出第一步 `go to Desk (1)`。
- 本地 sandbox 报 `unknown ALFRED instance 'Desk (1)'`。
- 官方 trace 显示 `go to Desk (1)` 是可执行的，并且能看到 Bowl、AlarmClock 等对象。

另一个例子：`pick_clean_then_place_in_recep-ButterKnife-None-Drawer-2__ann_1`

- 本地 sandbox 第 3 步报 `unknown ALFRED instance 'SinkBasin (1)'`。
- 官方 trace 中 `go to SinkBasin (1)` 成功，后续 cleaning 计划也官方成功。

unknown instance 类别统计：

- `Fridge`：41
- `SinkBasin`：24
- `Desk`：20
- `Microwave`：13
- `CounterTop`：13
- `Dresser`：7
- `FloorLamp`：7
- `DiningTable`：6

结论：ALFRED 的 `build_task_environment_closure` 输入主要依赖 understanding 抽出的 exact entity names。一旦 understanding 没抽到工具/容器/中间交互物，sandbox 就会拿到过小环境，误把官方存在的实体判为 unknown。这个应在 ReAcTree-ALFRED 的 `build_task_environment` 里修，不必先动公共 bridge。

### 问题 3：ALFRED skills 缺少若干任务状态效果

当前 ALFRED skills 已有部分效果：

- `slice` 会生成同 base class 的切片实例。
- `turn_on` 对 Microwave/StoveBurner/Toaster/Oven 的 descendants 标记 cooked。

但从任务类型看还缺：

- clean：目标放入 SinkBasin 后开 Faucet，应能让目标进入 clean 状态。
- cool：目标放入 Fridge 后，应能让目标进入 cooled 状态。
- look_at：需要 ALFRED-specific comparator 或技能效果，不能只要求通用 `robot.looking_at` 字段，因为当前动作层没有这个字段。

如果只补 goal_state 而不补这些 effect/comparator，state_diff_audit 会从“缺目标”变成“目标永远不满足”。

### 配置口径

ReAcTree 当时的配置存在重复口径。当前已统一到每个数据集自己的
`framework/code/config/settings.json`，不再使用单独的 benchmark 配置文件：

- 旧口径：独立 benchmark 配置里启用最终态检查。
- 当前口径：`reactree/*/framework/code/config/settings.json` 中的
  `benchmark.feature_flags.state_diff_audit` 是唯一入口。

后续排查只看当前 settings；旧分析里的重复配置结论只保留为历史背景。

## 建议修复顺序

不动公共代码的前提下：

1. WAH：先用当前代码重跑 `20:0`，确认空动作兜底是否生效。再决定是否需要修 SDA repair 让它真正补齐缺失 task_goal，而不是依靠 executor fallback。
2. ALFRED：在 `reactree/alfred/framework/code/task_environment.py` 中，根据 ALFRED task signature 确定性补 `required_item_names` 和可比较目标，不再依赖 LLM 随机生成 goal_state。
3. ALFRED：在 ReAcTree-ALFRED 自己的 `build_task_environment` 中扩大 sandbox 环境。建议先使用完整 prepared scene 或 task signature 扩展闭包，避免官方存在实体被本地误判 unknown。
4. ALFRED：在 `reactree/alfred/framework/code/final_state.py` 加 ALFRED task signature comparator，覆盖 pick/place、two_obj、movable_recep、clean、heat、cool、look_at。
5. ALFRED：补 ReAcTree-ALFRED skills 的 clean/cool/look_at 相关模拟效果，使 SDA 的最终态审计有可验证状态。
6. 只在第 3 步发现公共 `benchmark/task_environment_bridge.py` 无法支持“prompt 用 compact、sandbox 用 full closure”时，再单独确认是否动公共 bridge。

## 复现实验建议

WAH targeted：

```bash
./reactree/wah/framework/code/run.sh \
  --case-id '20:0' \
  --expected-count 1 \
  --run-name reactree_wah_case20_after_executor_fallback \
  --worker-timeout-s 1800
```

ALFRED targeted：

```bash
./reactree/alfred/framework/code/run.sh \
  --case-id 'pick_clean_then_place_in_recep-ButterKnife-None-Drawer-2__trial_T20190908_121728_511866__ann_1' \
  --expected-count 1 \
  --run-name reactree_alfred_butterknife_clean_debug \
  --worker-timeout-s 1800
```

ALFRED 环境裁剪 targeted：

```bash
./reactree/alfred/framework/code/run.sh \
  --case-id 'look_at_obj_in_light-Bowl-None-DeskLamp-301__trial_T20190909_150719_492274__ann_0' \
  --expected-count 1 \
  --run-name reactree_alfred_env_closure_debug \
  --worker-timeout-s 1800
```
