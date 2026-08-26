# Benchmark Environment Contract

本文档只定义 benchmark 和 OurAgent 框架之间的环境口径。原生数据集可以保留各自格式，但进入 framework 的环境必须统一；否则 understanding、planning、sandbox、official evaluator 会互相污染，后续很难判断结果是否公平。

## 总原则

环境分五层，不能混用：

1. `native environment`：论文或原始数据集发布的原生环境。这里只作为重建 extracted cache 和官方评测的来源，不直接喂给 framework prompt。
2. `extracted runtime environment`：从 native 环境离线抽出来的固定缓存。目标统一格式是 `runtime_initial_environment.scene/env_state/object_map`。
3. `framework prepared environment`：各数据集 `prepare_environment()` 把 extracted cache 转成 `PreparedTaskEnvironment(scene, env_state, entity_catalog, task_context)`。
4. `planning task environment`：understanding 选出实体后，由 `build_task_environment()` 从完整 `scene` 里取出任务相关的扁平环境子图，传给 planning 和 sandbox。
5. `official/simulator evaluation environment`：最终测分用的官方 evaluator 或仿真器环境。它可以读 native evaluator 必需字段，但不能反向进入 framework prompt。

统一目标不是把 DELTA、VirtualHome、BEHAVIOR、WAH、ALFRED 的原生文件改成同一种格式；统一目标是所有数据集进入 framework 前都落到同一个运行时契约：

```json
{
  "runtime_initial_environment": {
    "scene": {},
    "env_state": {},
    "object_map": {}
  }
}
```

其中：

- `scene`：完整初始世界，使用 OurAgent 树状 scene 格式，保留房间、容器、承载关系、物体状态、可交互属性。
- `env_state`：机器人自身状态，例如 `robot_location`、`robot_holding`、`robot_hands`、电量等。
- `object_map`：可选。只用于 evaluator 输出格式映射，例如把框架实体名映射回 VirtualHome/BEHAVIOR 官方对象 id 或官方名称；不能作为规划答案。
- `flat_initial_environment`：可选调试视图，不能作为 framework 唯一输入。真正输入应以 `runtime_initial_environment.scene/env_state` 为准。

## Framework 统一入口

所有 framework benchmark run 的入口都应是：

1. launcher 读取 `benchmark/datasets/extracted/.../cases.json`。
2. worker 调 dataset-local `case_executor.run_case()`。
3. `case_executor` 加载 dataset-local `config/settings.json`，然后调用 dataset-local `prepare_environment()`。
4. `prepare_environment()` 返回 `PreparedTaskEnvironment`。
5. `benchmark/framework_task_bridge.py` 负责调用 understanding，再根据 understanding 输出调用 `build_task_environment()`，最后调用 planning。
6. planning 输出 `todo_list`，其中每个 step 都是 dataset 原生动作对象。
7. worker 把 `todo_list` 中的原生动作转成 paper method 的 evaluator 输入，交给该数据集自己的 evaluator 测分。

相关代码入口：

- 统一桥接：`benchmark/framework_task_bridge.py`
- 统一环境对象：`benchmark/task_environment_bridge.py:PreparedTaskEnvironment`
- understanding：`graph/understanding/node.py`
- planning：`graph/planning/node.py`
- dataset config：`benchmark/*/**/framework/code/config/settings.json`

## Understanding 看到什么

understanding 不是环境裁剪器，也不应该读取完整最终答案。它只需要：

- `raw_instruction` / `messages`：任务文本。
- `task_context`：与 paper method 同等信息量的任务上下文，例如 task id、PDDL goal 条件、BEHAVIOR goal 条件、WAH init_room 等。
- `available_entities` / `entity_catalog`：从完整 `scene` 提取的合法实体名列表。
- `available_skills_json`：当前 dataset config 选择的 skill 契约摘要。

understanding 输出：

- `structured_task.intent`
- `structured_task.required_item_names`
- `structured_task.goal_state`，仅当输入材料明确给了最终态时才输出
- `skill_closure`，一次性选择完成任务语义所需 skill
- `relevant_item_names`

understanding 不负责补全路径，不负责扫描全场景替代实体，不负责判定任务已经完成。

## Planning/Sandbox 看到什么

planning 不应该直接吃全部原生数据。planning 看到的是：

- `structured_task`：understanding 输出并经 dataset-local `align_structured_task()` 做 schema 对齐。
- `env_state`：机器人初始状态。
- `environment`：由 `build_task_environment()` 从完整 `scene` 生成的任务相关扁平子图。
- `task_context`：与任务相关但不是答案的上下文。
- `skill_closure`：understanding 选出的 skill 集合，用于缩小 skill prompt。
- `todo_output_parser` / `todo_step_adapter`：要求 `todo_list` 直接使用对应数据集动作格式，并把该格式接入沙盒审计。

sandbox 使用同一个 `environment` 做技能前置条件和状态变化检查。sandbox 不是官方仿真器替代品；它只做本地契约拦截，最终分数仍由各数据集 official evaluator 给出。

## 各数据集环境口径

| 论文/数据集 | native 环境来源 | extracted 环境缓存 | framework 使用环境 | official/simulator 测评环境 | 当前状态 |
| --- | --- | --- | --- | --- | --- |
| DELTA | `benchmark/datasets/native/delta/scene_graph.py`，任务来自 `example.py` | `benchmark/datasets/extracted/delta/initial_envs/<scene>.json`，当前保存 `scene_graph` | `benchmark/delta/framework/code/task_environment.py::prepare_environment()` 把 `scene_graph` 转成 OurAgent `scene/env_state`；planning 默认再裁成任务子图 | `evaluate_delta_goals()` 用原生 scene graph 做符号目标检查；可选 `VAL` 用导出的 PDDL plan 测 | 可跑，但缓存格式还没完全统一成 `runtime_initial_environment`，需要补一层标准字段 |
| EAI VirtualHome | `id2task.json`、`problem_pddl`、原生 `init_graphs` | `benchmark/datasets/extracted/eai/virtualhome/initial_envs/<case_id>.json`，已有 `runtime_initial_environment.scene/env_state/object_map` | `benchmark/eai/virtualhome/framework/code/task_environment.py::prepare_environment()` 读取 runtime cache，task context 带 PDDL goal/hints | EAI VirtualHome action sequencing evaluator；输出前用 `object_map`/official object table 映射回官方动作格式 | 已基本统一，可直接按 runtime contract 跑 |
| EAI BEHAVIOR | `behavior_bddl_info`、`demo_stats.json`、iGibson/BEHAVIOR assets、相关 task mapping | `benchmark/datasets/extracted/eai/behavior/initial_envs/<case_id>.json`，已有 `runtime_initial_environment.scene/env_state/object_map` | `benchmark/eai/behavior/framework/code/task_environment.py::prepare_environment()` 读取 runtime cache，task context 带 raw goal condition/name category | EAI BEHAVIOR action sequencing evaluator；输出前映射回官方对象名 | 已基本统一，可直接按 runtime contract 跑 |
| ReAcTree-WAH | `benchmark/datasets/native/reactree/wah/wah_nl_test_rev.json`，包含 `init_graph/init_room/task_goal/nl_instructions` | `benchmark/datasets/extracted/reactree/wah/initial_envs/<task_id>.json`，已有 `runtime_initial_environment.scene/env_state` | `benchmark/reactree/wah/framework/code/task_environment.py::prepare_environment()` 读取 runtime cache；planning 输出 WAH official action | ReAcTree WAH official Unity evaluator；必要时可用 graph replay 作调试 fallback | 已基本统一。`cases.json` 有 195 条 instruction-level，launcher 默认取每个 task 的第 0 条，共 100 条 |
| ReAcTree-ALFRED | `oct21.json` split 和 `json_2.1.0/<task>/pp/ann_<repeat>.json`；环境需通过 AI2-THOR reset/restore/init 从原生 annotation 得到 | `benchmark/datasets/extracted/reactree/alfred/initial_envs/<case_id>.json`，当前保存 `initial_scene`，还不是标准 `runtime_initial_environment` | `benchmark/reactree/alfred/framework/code/task_environment.py::prepare_environment()` 运行时把 `initial_scene` 转成 OurAgent `scene/env_state` | ReAcTree/ALFRED official evaluator 进入 AI2-THOR 测动作 | 未完全整理：820 条 valid_seen 中目前 686 个 cache 可用，116 个缺失，18 个空/坏 JSON；还需要补齐并统一 cache schema |

## 必须修正的统一缺口

当前最不统一的地方有两个：

1. DELTA extracted cache 仍保存 `scene_graph`，运行时再转 `scene/env_state`。这可以跑，但不符合统一 cache contract。应在 `build_delta_extracted_cases.py` 或独立迁移脚本里同时写入 `runtime_initial_environment.scene/env_state`，保留 `scene_graph` 只作为 debug/native provenance。
2. ALFRED extracted cache 仍保存 `initial_scene`，运行时再转 `scene/env_state`，而且缓存不完整。应先用 AI2-THOR 补齐 116 个缺失和 18 个坏文件，再把每个 cache 写成标准 `runtime_initial_environment.scene/env_state`，保留 `initial_scene` 只作为 native extraction evidence。

统一后的 case input 也建议收敛成一个公共字段：

```json
{
  "environment_cache_path": ".../initial_envs/<case>.json",
  "environment_source": "native_source_label"
}
```

旧的 `scene_graph_cache_path`、`initial_environment_cache_path`、`init_graph_cache_path`、`initial_scene_cache_path` 可以在迁移期间保留在 metadata 或 provenance 里，但 framework 主路径只应读取 `environment_cache_path`。这样五个数据集启动时不会再有五套环境字段名。

## 不能进入 framework prompt 的内容

以下内容只能用于 evaluator 或离线抽取，不允许进入 understanding/planning prompt：

- paper method 的中间 LLM prompt cache。
- gold action sequence。
- final graph / target final state，除非原生任务输入本来就是 goal condition，且 paper method 同阶段也拿到同等 goal 信息。
- official evaluator result。
- 为了让本地 sandbox 通过而反向生成的实体替换、动作补偿或答案式 pruning。

## 当前检查结果

当前 `benchmark/datasets/extracted` 的 case 数量：

- DELTA：600 cases，3 个 scene cache。
- EAI VirtualHome：342 cases，342 个 runtime cache。
- EAI BEHAVIOR：100 cases，100 个 runtime cache。
- ReAcTree-WAH：195 instruction-level cases，100 个 task-level runtime cache；默认评测 100 个 task。
- ReAcTree-ALFRED：820 valid_seen cases；686 个 cache 可用，116 个缺失，18 个坏 cache。

因此，若现在直接测五个数据集：DELTA、EAI VirtualHome、EAI BEHAVIOR、ReAcTree-WAH 可以按当前入口启动；ALFRED 只能跑已缓存且 JSON 正常的 case，完整 820 条必须先补缓存。
