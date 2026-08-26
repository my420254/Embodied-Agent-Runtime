# Baseline Accuracy Fairness Branch

更新日期：2026-08-07

2026-08-07 配置审计补充：LLM 配置统一细节见 `llm_config_and_baseline_io_audit_20260807.md`。当前实验端口口径为 DELTA 使用 `18004/Qwen3.5-9B`，其他四个数据集使用 `18003/Qwen3.6-27B`；实验 LLM 温度统一为 `0`，planning `max_tokens=4096`。根配置和五套 framework 配置已禁用 `18001/18002`，避免漏传端口时自动跑到旧服务。

这条分线只负责三篇基线论文、五个数据集和 OurAgent framework 的精度公平性口径。核心问题不是“能不能跑”，而是每个结果表到底在比什么：输入信息是否对等，模型是否对等，任务 denominator 是否对等，指标是否来自同一个 evaluator。

## 总原则

严格公平主表只放满足以下条件的结果：

1. 同一张表内所有方法使用同一个 LLM 后端。
2. 同一张表内所有方法拿到同等初始信息。
3. 同一张表内所有方法用同一个任务集合和 evaluator。
4. paper original number 只能作为 literature reference；如果模型、输入或 denominator 不一致，不能写成公平主结论。

EAI 是例外处理：它要对齐的是 Action Sequencing 精度和官方 evaluator，不是输入完全公平。EAI-AS paper_method 必须标注为 `oracle-conditioned`，因为它已经拿到 Goal Interpretation 和 Subgoal Decomposition 的完整答案；OurAgent framework 则标注为 `native-info`。

本项目当前统一模型口径：

| 范围 | 主模型 | 说明 |
| --- | --- | --- |
| DELTA | `Qwen3.5-9B` | DELTA paper_method 和 OurAgent DELTA framework 都用这个模型。 |
| ReAcTree WAH-NL | `Qwen3.6-27B` | ReAcTree paper_method adapted baseline 和 OurAgent framework 都用这个模型。 |
| ReAcTree ALFRED | `Qwen3.6-27B` | ReAcTree paper_method adapted baseline 和 OurAgent framework 都用这个模型。 |
| EAI VirtualHome | `Qwen3.6-27B` | EAI Action Sequencing 对比和 OurAgent framework 都用这个模型。 |
| EAI BEHAVIOR | `Qwen3.6-27B` | EAI Action Sequencing 对比和 OurAgent framework 都用这个模型。 |

注意：当前根配置和五套 framework 配置都只启用 `18003/Qwen3.6-27B` 与 `18004/Qwen3.5-9B`。正式公平实验仍建议显式写 `--ports 18003` 或 `--ports 18004`，以便 manifest 直接记录端口。不能把 DELTA 的 Qwen3.5 结果和 ReAcTree/EAI 的 Qwen3.6 结果混成“同模型总表”。

## 五个数据集主表口径

| 论文 | 数据集 | 主对比实验 | 输入/信息口径 | 主指标 | 主模型 | 当前状态 |
| --- | --- | --- | --- | --- | --- | --- |
| DELTA | DELTA 4 domains | 官方 DELTA paper_method vs OurAgent-DELTA | full scene graph / full symbolic environment；可另列 task-closure ablation | VAL task success rate，按 PC/Dining/Cleaning/Office 和 overall 600 trials | Qwen3.5-9B | 需要 full 600 同模型结果；不能用 1-case smoke。 |
| ReAcTree | WAH-NL | `ReAcTree+WM+FO` vs OurAgent-WAH full/structured scene | full initial scene，包含 rooms、objects、receptacles、ON/INSIDE、states；不使用 gold plan | GSR、SSR；主 denominator 用 task-level 100 tasks | Qwen3.6-27B | `--full-observable` adapted baseline 已实现。 |
| ReAcTree | ALFRED valid_seen | `ReAcTree+WM+FO` vs OurAgent-ALFRED full/structured scene | full initial AI2-THOR scene，包含 object instances、parentReceptacles、properties/states | GSR；valid_seen 820 annotations | Qwen3.6-27B | `--full-observable` adapted baseline 已实现；完整 820 仍需跑。 |
| EAI | VirtualHome | EAI Action Sequencing accuracy vs OurAgent-EAI-VH action plan accuracy | 指标对齐 Action Sequencing；EAI paper_method 的 AS prompt 已包含前两步完整答案，OurAgent framework 只用原生数据集信息，输入不严格对等 | Task SR、Execution SR；Table 11 goal satisfaction 可附表 | Qwen3.6-27B | 主表用 338 valid-goal；342-all 只能补充报告。 |
| EAI | BEHAVIOR | EAI Action Sequencing accuracy vs OurAgent-EAI-BEHAVIOR action plan accuracy | 指标对齐 Action Sequencing；EAI paper_method 的 AS prompt 已包含前两步完整答案，OurAgent framework 只用原生数据集信息，输入不严格对等 | Task SR、Execution SR；Table 11 goal satisfaction 可附表 | Qwen3.6-27B | 100 tasks；必须说明 EAI-AS 是 oracle-conditioned module accuracy。 |

一句话结论：

- DELTA 本身就是 full/symbolic planning 口径，重点是模型、denominator、evaluator 对齐。
- EAI 要对比的是 Action Sequencing 精度和 evaluator 指标，不是声称输入完全公平；EAI paper_method 的 AS 输入已经拿到前两步模块的完整答案，而 OurAgent framework 只用原生数据集信息。
- ReAcTree 原论文主方法是 partial observation；OurAgent 当前是 full/structured initial scene。公平主表不能直接引用原论文 partial-observation 数字，必须跑 `Full Observable adapted` baseline。
- ReAcTree 的 `ZSP`、`Tree Planner` 是原论文外部对比，不是 ReAcTree 方法本体。除非目标是复刻原论文整张表，否则主表不优先跑它们。

## ReAcTree

### 原论文输入假设

ReAcTree 原论文主实验有两个 dataset-simulator pair：

- WAH-NL with VirtualHome。
- ALFRED with AI2-THOR。

原论文主方法 `ReAct`、`ReAct+WM`、`ReAcTree`、`ReAcTree+WM` 运行在 partial-observation embodied setting：agent 初始只看到当前位置附近可见对象，每次动作后根据 simulator observation 更新文本观察和 working memory。闭合容器内物体、远处房间物体不会在初始 prompt 里直接暴露。

原论文的 `ZSP` 和 `Tree Planner` 不是这个信息条件：

- `ZSP` 在 WAH-NL 上拿初始 global environment information，开环生成完整 plan，不访问中间 observation。
- `Tree Planner` 在采样阶段拿 initial global environment information，执行阶段再按 observation 从预生成 tree 中选择动作。

所以 ReAcTree 论文内部至少有两类输入条件：partial-observation closed-loop 方法，以及 global-initial baselines。OurAgent 当前 full/structured scene 不应直接和原论文 partial-observation 数字写成公平对比。

### 公平输入定义

如果 OurAgent 在 ReAcTree 两个数据集上使用 full/structured initial scene，则 ReAcTree paper_method baseline 也必须拿同等 full scene。公平输入不是“给答案”，而是给完整初始环境：

WAH-NL full-observable input：

- 所有 room 实例。
- 所有 relevant simulator object/receptacle 实例。
- 每个对象的 `INSIDE` / `ON` 父关系。
- 每个对象所在 room。
- `OPEN` / `CLOSED` / `ON` / `OFF` 等初始状态。
- agent 初始房间。
- 合法动作集合基于全量对象，而不是只基于可见对象。
- `working_memory=True` 时，初始化时预加载 object -> room/location/receptacle。

WAH-NL 不允许给：

- gold action plan。
- evaluator-only completion result。
- 由 `task_goal` 反推出来的最短计划或目标答案式动作序列。

ALFRED full-observable input：

- `restore_scene()` 和 `init_action` 后，从 AI2-THOR `last_event.metadata['objects']` 读取所有 object instances。
- 每个对象的 `parentReceptacles`。
- `pickupable`、`receptacle`、`openable`、`toggleable`、`sliceable` 等属性。
- `isOpen`、`isToggled`、`isDirty`、`isSliced` 等初始状态。
- 合法动作集合基于全场景对象，而不是只基于当前可见对象。
- `working_memory=True` 时，初始化时预加载 object -> parent receptacle/location。

ALFRED 不允许给：

- gold low-level plan。
- ALFRED expert trajectory。
- `get_goal_satisfied()` 的结果或 evaluator-only success 信息。

### 当前已做的公平改动

已在 OurAgent-he1 中实现 ReAcTree `paper_method` 的 full-observable adapted baseline，且不改 `/data/zmy/ReAcTree` 官方源码：

| 文件 | 作用 |
| --- | --- |
| `benchmark/reactree/external_reactree_runner.py` | 新增 `--full-observable` 和 `--paper-override`；子进程环境显式写入 `OURAGENT_REACTREE_FULL_OBSERVABLE=1`、`OURAGENT_PROJECT_ROOT`、`OURAGENT_REACTREE_ROOT`。 |
| `benchmark/reactree/wah/paper_method/code/evaluate_wrapper.py` | WAH full-observable 时从 wrapper 进入官方 `src/evaluate.py`，插入 overlay path。 |
| `benchmark/reactree/wah/paper_method/code/overrides/wah/wah_env.py` | WAH overlay：把 partial graph 改成 full scene graph；初始 observation 追加全场景摘要；WM 预加载全对象位置。 |
| `benchmark/reactree/alfred/paper_method/code/evaluate_wrapper.py` | ALFRED wrapper 显式设置项目路径和 ReAcTree 路径，避免读旧默认路径。 |
| `benchmark/reactree/alfred/paper_method/code/overrides/src/alfred/alfred_env.py` | ALFRED overlay：从 AI2-THOR metadata 构造全场景摘要；合法动作对象改为全场景对象；WM 预加载对象位置。 |
| `benchmark/reactree/alfred/paper_method/code/overrides/llm_agent.py` | 保留已有 OpenAI-compatible Qwen 后端适配和 action parsing 适配。 |

验证已做：

- `py_compile` 通过。
- WAH/ALFRED `--dry-run --full-observable` 通过。
- import 检查确认 `OURAGENT_REACTREE_FULL_OBSERVABLE=1` 时实际加载 `_FullObservableWahUnityEnv` / `_FullObservableThorConnector`，不开时回到原类。

### 主对比实验

主表只跑 ReAcTree 论文方法本体的最强 baseline：

| 数据集 | 主表 baseline | 为什么只跑这个 |
| --- | --- | --- |
| WAH-NL | `ReAcTree+WM+FO` | 这是 ReAcTree 方法本体 + working memory + 与 OurAgent 同等 full scene。 |
| ALFRED | `ReAcTree+WM+FO` | 原论文 ALFRED 主要报 WM 版本；与 OurAgent full scene 比时必须加 FO。 |

推荐命令形态：

```bash
cd /data/zmy/OurAgent-he1/benchmark/reactree/wah/paper_method/code
python run.py \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --workers 5 \
  --run-name wah_paper_reactree_wm_fullobs_qwen36 \
  --official-port-ids 0 1 2 3 4 \
  --config-name wah_headless_reactree_wm \
  --full-observable

cd /data/zmy/OurAgent-he1/benchmark/reactree/alfred/paper_method/code
python run.py \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --workers 1 \
  --run-name alfred_paper_reactree_wm_fullobs_qwen36 \
  --x-displays 0 \
  --config-name alfred_reactree \
  --full-observable
```

如果要做消融，再跑四组，全部必须加 `--full-observable`：

| 变体 | WAH | ALFRED |
| --- | --- | --- |
| ReAct+FO | `--config-name wah_headless_react` | `--config-name alfred_react --paper-override llm_agent.working_memory=False` |
| ReAct+WM+FO | `--config-name wah_headless_react --paper-override llm_agent.working_memory=True` | `--config-name alfred_react` |
| ReAcTree+FO | `--config-name wah_headless_reactree` | `--config-name alfred_reactree --paper-override llm_agent.working_memory=False` |
| ReAcTree+WM+FO | `--config-name wah_headless_reactree_wm` | `--config-name alfred_reactree` |

`ZSP` 和 `Tree Planner` 不作为当前主表必跑项。它们只有在“复刻 ReAcTree 原论文全部 baseline”时才需要跑，而且也必须在同模型、同 full-initial-scene 输入下重跑，不能直接引用论文原数字当 Qwen3.6 公平对比。

### 报告口径

WAH-NL：

- 主 denominator：100 个 task-level test tasks。
- 指标：GSR、SSR。
- 195 instruction-level cases 可以作为内部分析或附表，不要和论文 Table 1 的 100 task-level 口径混合。

ALFRED：

- 主 denominator：valid_seen 820 annotations。
- 指标：GSR。
- valid_unseen 如后续跑，单独列。

论文原版 partial-observation Table 1/Table 2 可以放在 reference 表，标题必须写清楚：

`Original ReAcTree paper, partial-observation setting, literature reference only.`

## DELTA

### 原论文输入假设

DELTA 原文 problem statement 明确假设 scene graph fully observable。它的输入包括：

- 完整 scene graph。
- natural-language domain/problem description。
- action knowledge。
- LLM 生成 PDDL domain/problem。
- LLM 分解 long-term goal 为 sub-goals。
- automated task planner 对每个 sub-problem 求解。
- 最终用 VAL 验证 plan 是否 correct and executable。

因此，在 DELTA 上给完整任务环境不是作弊；反而应尽量贴近 full scene graph。真正需要警惕的是 OurAgent 的 task-closure/pruning 是否把目标相关实体以 oracle 方式提前筛出来。

### 公平输入定义

DELTA 主公平输入：

- 完整 SG 或等价完整符号环境。
- 当前 domain 的 action predicates/action knowledge。
- task instruction / problem description。
- initial objects、rooms/locations、properties、states。
- 不给 `subgoal_pddl`、`gt_cost`、reference plan。
- 不给 VAL 结果或 evaluator-only success 信息。

OurAgent 可以另列 task-closure 输入：

- `OurAgent-DELTA-task-closure` 是框架裁剪/效率版本。
- 它可以作为 ablation，但如果裁剪来自 gold target names 或 evaluator-only 信息，就不能作为 DELTA full-SG 主公平输入。

### 当前已做的公平改动

| 文件/机制 | 作用 |
| --- | --- |
| `benchmark/delta/external_delta_runner.py` | 用本仓库 runner 调官方 `/data/zmy/DELTA/delta.py`，按 domain/scene/episode 组织结果。 |
| `benchmark/delta/paper_method/shims/llm/llm.py` | 把 DELTA 官方代码里的 LLM 调用接到本地 OpenAI-compatible Qwen 服务。 |
| `DELTA_VLLM_BASE_URL` / `DELTA_VLLM_MODEL` | 子进程中显式指定本地模型后端。 |
| `DELTA_RESULT_ROOT` | 把官方 DELTA 输出隔离到本仓库结果目录，不污染 `/data/zmy/DELTA`。 |

DELTA 不改 `/data/zmy/DELTA` 源码。当前记录里已有 Qwen3.5 full-600 paper_method 结果目录，但主表仍要确认与 OurAgent framework 的任务集合、模型和 VAL 口径一致后再引用。

### 主对比实验

主实验：

| 方法 | 输入 | 模型 | denominator | 指标 |
| --- | --- | --- | --- | --- |
| DELTA paper_method rerun | 官方 full SG | Qwen3.5-9B | 4 domains x 3 scenes x 50 episodes = 600 | VAL success rate |
| OurAgent-DELTA-full-SG | 完整 SG/完整符号环境 | Qwen3.5-9B | 同 600 | VAL task success |
| OurAgent-DELTA-task-closure | task-relevant closure | Qwen3.5-9B | 同 600 | VAL task success；作为 ablation |

推荐命令形态：

```bash
cd /data/zmy/OurAgent-he1/benchmark/delta/paper_method/code
python run.py \
  --ports 18004 \
  --api-model Qwen3.5-9B \
  --workers <n> \
  --run-name delta_paper_full600_qwen35 \
  --episodes 50
```

报告时按域给出：

- PC。
- Dining。
- Cleaning。
- Office。
- Overall 600。

主指标只用 VAL official success / task success。Plan length、planning time、expanded nodes 可以附表，但不能当 accuracy 主表，因为 OurAgent 的框架管线和 DELTA 的 Fast Downward subproblem timing 不完全同构。

论文 Table II 的 GPT-4o / Llama 等原始数字可以放 literature reference，不是同模型公平结果。真正公平主表应使用 Qwen3.5 对 DELTA paper_method 和 OurAgent-DELTA 同时重跑。

## EAI

### 原论文输入假设

EAI 是 benchmark/interface 论文，不是单一 planner 方法。它拆成四个模块：

- Goal Interpretation：`s0 + natural language goal -> LTL goal`。
- Subgoal Decomposition：`s0 + goal -> subgoal trajectory`。
- Action Sequencing：`s0 + goal + transition model -> action trajectory`。
- Transition Modeling：`s0 + goal + operator -> preconditions/effects`。

OurAgent 当前输出 benchmark 原生 action plan，因此精度指标应对齐 EAI 的 Action Sequencing 模块，不应对齐 Goal Interpretation 或 Transition Modeling。

但这里要明确：EAI paper_method 的 Action Sequencing 不是“只给原生数据集信息然后自己理解任务”的端到端方法。它是模块化 oracle-conditioned 评测：前两个步骤的答案已经给完整了，包括任务理解得到的 symbolic goal，以及任务分解/目标结构相关信息；Action Sequencing 只负责在这些答案已知的条件下生成动作序列。

Action Sequencing prompt/input 通常包括：

- initial world state `s0`。
- symbolic goal / target environment state，也就是前面 Goal Interpretation 的完整答案。
- subgoal / goal decomposition / related goal structure，也就是前面模块产物的答案式输入。
- action vocabulary。
- predicate vocabulary。
- transition/action semantics。
- interactable objects。

OurAgent-EAI framework 不是这个输入条件。OurAgent framework 只使用原生数据集信息和 runtime initial environment，经自己的 understanding/planning 生成原生 action plan；它没有直接拿 EAI paper_method Action Sequencing prompt 里“前两个模块已经完成”的整套答案。因此 EAI 比较的正确写法是：

- 可以比较 Task SR / Execution SR / goal satisfaction，因为 evaluator 和任务目标可对齐到 Action Sequencing 精度。
- 不能写成“输入信息完全公平”。EAI-AS 是 oracle-conditioned module accuracy，OurAgent 是 native-info framework accuracy。
- 如果 reviewer 问公平性，要主动说明 EAI-AS 在输入侧更强，比较体现的是 OurAgent 在更少预解信息下达到的 action-sequencing task accuracy。

### EAI 输入差异定义

VirtualHome EAI-AS paper_method 输入：

- official initial graph / runtime initial environment。
- action sequencing 的 node/edge/action goals 或 PDDL-equivalent goal clauses，属于前序模块答案。
- related goal objects / goal structure / decomposition hints，属于前序模块答案。
- interactable object list / object mapping。
- VirtualHome action vocabulary 和 precondition/effect semantics。
- 不把空 goal case 当正常 goal-satisfaction 样本混入主 denominator。

VirtualHome OurAgent framework 输入：

- 原生任务信息。
- runtime initial environment。
- object mapping / official action space。
- framework 自己的 understanding/planning 输出。
- 不直接使用 EAI-AS prompt cache 中完整的前序模块答案作为 planner 输入。

BEHAVIOR EAI-AS paper_method 输入：

- official initial environment / runtime cache。
- raw goal condition / goal clauses，属于 action sequencing 的答案式目标输入。
- related goal structure / object categories，属于前序模块答案或原生 oracle 信息。
- object name category / object mapping。
- BEHAVIOR action vocabulary 和 transition semantics。

BEHAVIOR OurAgent framework 输入：

- 原生任务信息。
- runtime initial environment。
- object mapping / official action space。
- framework 自己的 understanding/planning 输出。

如果启用 OurAgent 的 state-diff repair、feedback replanning 或多轮 correction，必须单独列为 `feedback/replan variant`，不能和 EAI one-shot Action Sequencing 主表混在一起。

### 当前已做或需要保持的公平改动

| 机制 | 作用 |
| --- | --- |
| extracted `runtime_initial_environment` cache | 把 EAI 原生环境统一转成 OurAgent runtime scene/env_state，但保留 official object mapping。 |
| EAI framework official evaluator | 规划动作最终映射回官方 action format，再用 EAI/VirtualHome 或 BEHAVIOR evaluator 计分。 |
| VirtualHome 338/342 split 标记 | 避免 4 个空 goal case 让 denominator 和 goal satisfaction 失真。 |
| one-shot vs replan 分离 | 保证和 EAI Table 6/11 Action Sequencing 的 one-shot 口径一致。 |

当前仓库里 EAI 主要是 framework entry；如果后续补 EAI paper_method runner，也必须使用同一 Action Sequencing prompt cache、同一 Qwen3.6 模型、同一 evaluator 和同一 split。但报告时要把它命名为 `EAI-AS oracle-conditioned paper_method`，不能命名为与 OurAgent 输入完全相同的 fair baseline。

### VirtualHome denominator

已核查：

- `id2task.json`：342 个任务。
- action-sequencing prompt/resource：342 个。
- `problem_pddl`：338 个。
- `task_state_LTL_formula_accurate.json`：342 个，其中 338 个有非空 `vh_goal`，4 个为空。
- 4 个空 goal case：`339_1`、`627_1`、`84_1`、`93_1`。

主表必须用：

- `VH-AS-338-valid-goal`：去掉 4 个空 goal case，对齐论文表格 338 口径。

补充表可以用：

- `VH-AS-342-all`：官方 action-sequencing 资源全集，但 4 个空 goal case 要显式标注为 degenerate/empty-goal。

不能把 342-all 的结果直接和论文 338 表逐项比较。

### 主对比实验

| 数据集 | 方法 | 输入 | 模型 | denominator | 指标 |
| --- | --- | --- | --- | --- | --- |
| VirtualHome | EAI-AS oracle-conditioned / OurAgent-EAI-VH native-info | 同 Action Sequencing evaluator；EAI-AS 含前两步完整答案，OurAgent 只用原生数据集信息 | Qwen3.6-27B | 338 valid-goal 主表；342-all 补充 | Task SR、Execution SR、goal satisfaction |
| BEHAVIOR | EAI-AS oracle-conditioned / OurAgent-EAI-BEHAVIOR native-info | 同 Action Sequencing evaluator；EAI-AS 含前两步完整答案，OurAgent 只用原生数据集信息 | Qwen3.6-27B | 100 tasks | Task SR、Execution SR、goal satisfaction |

对齐论文表：

- Table 6：Task SR、Execution SR、错误分类。
- Table 11：state/relation/action/total goal satisfaction breakdown。
- Table 17：只有在最多 3 次 feedback replanning 且 feedback 结构对齐时，才能作为 replan 参考；不要和 one-shot 主表混。

## 最终主表建议

建议论文/报告里拆成三张表：

### Table A: Same-Model Main Results

DELTA 和 ReAcTree 在这张表里要求输入对等；EAI 在这张表里要求同模型、同 Action Sequencing evaluator、同 denominator，但必须标注输入强度不同。

| Dataset | Method | Model | Input setting | Metric |
| --- | --- | --- | --- | --- |
| DELTA | DELTA paper_method / OurAgent | Qwen3.5-9B | full SG | VAL success |
| WAH-NL | ReAcTree+WM+FO / OurAgent | Qwen3.6-27B | full initial scene | GSR/SSR |
| ALFRED | ReAcTree+WM+FO / OurAgent | Qwen3.6-27B | full initial scene | GSR |
| EAI VirtualHome | EAI-AS oracle-conditioned / OurAgent native-info | Qwen3.6-27B | same AS evaluator, different input strength | Task SR / Exec SR |
| EAI BEHAVIOR | EAI-AS oracle-conditioned / OurAgent native-info | Qwen3.6-27B | same AS evaluator, different input strength | Task SR / Exec SR |

### Table B: Information Assumption Ablations

| Dataset | Ablation |
| --- | --- |
| DELTA | full-SG vs task-closure |
| WAH-NL | ReAct+FO / ReAct+WM+FO / ReAcTree+FO / ReAcTree+WM+FO |
| ALFRED | ReAct+WM+FO / ReAcTree+WM+FO；可选 non-WM |
| VirtualHome | EAI-AS oracle-conditioned vs OurAgent native-info；338 valid-goal vs 342 all |
| BEHAVIOR | EAI-AS oracle-conditioned vs OurAgent native-info；one-shot vs feedback/replan，如启用 |

### Table C: Literature Reference

放原论文表数字，但明确标注：

- model 不同。
- input setting 可能不同。
- denominator 可能不同。
- 只用于定位，不作为 same-model fair claim。

## 当前不能写的结论

- 不能写：OurAgent 在 ReAcTree 原论文 partial-observation 主实验同条件下超过 ReAcTree，除非真的跑了 partial-observation OurAgent。
- 不能写：ReAcTree Table 1/Table 2 原数字就是当前 full-scene OurAgent 的公平 baseline。
- 不能写：ZSP/Tree Planner 不跑也等价于 ReAcTree 完整原表复刻。
- 不能写：1-case smoke 精度等价于 full benchmark 精度。
- 不能把 DELTA symbolic diagnostic success 当 DELTA 主成功率；主口径必须是 VAL official success。
- 不能把 EAI Goal Interpretation F1、Transition Modeling F1 和 framework action plan success 混成一个 accuracy。
- 不能写 EAI paper_method Action Sequencing 和 OurAgent framework 输入完全对等；EAI-AS 已经拿到 Goal Interpretation 和 Subgoal Decomposition 的完整答案。
- 不能把 EAI VirtualHome 342-all 结果直接和论文 338-case 表比较。
- 不能在同一主表里混用 DELTA Qwen3.5 与其他数据集 Qwen3.6 后声称“统一模型 across all datasets”；只能说“每个论文/数据集组内模型统一”。

## 下一步

1. ReAcTree WAH：用 Qwen3.6 跑 `wah_headless_reactree_wm --full-observable` 的 100 task-level 主结果。
2. ReAcTree ALFRED：用 Qwen3.6 跑 `alfred_reactree --full-observable` 的 valid_seen 820 主结果。
3. DELTA：确认 Qwen3.5 paper_method full 600 和 OurAgent-DELTA full 600 的模型、VAL 口径、domain split 完全一致。
4. DELTA：补或核对 `full-SG` vs `task-closure` ablation，避免 task closure 被 reviewer 质疑为 oracle pruning。
5. EAI VirtualHome：固定 `VH-AS-338-valid-goal` 主 split，并把 4 个 empty-goal case 只放补充 split。
6. EAI BEHAVIOR：确认 one-shot 与 feedback/replan 结果分表。
7. 所有 run 的 manifest 必须记录 `api_model`、`ports/api_base`、input setting、denominator 和 evaluator。

## 证据路径

- ReAcTree 原文：`/data/zmy/基线论文/2026-AAMAS-ReAcTree - Hierarchical LLM Agent Trees with Control Flow for Long-Horizon Task Planning.pdf`
- ReAcTree/ZSP 梳理：`/data/zmy/基线论文/3-2026-AAMAS-ReAcTree与ZSP基线详述.pdf`
- DELTA 原文：`/data/zmy/基线论文/2025-ICRA-DELTA - Decomposed Efficient Long-Term Robot Task Planning using Large Language Models.pdf`
- EAI 原文：`/data/zmy/基线论文/2025 - Embodied Agent Interface Benchmarking LLMs for Embodied Decision Making.pdf`
- EAI 梳理：`/data/zmy/基线论文/2-2024-NeurIPS-Oral-EAI基准详述.pdf`
- ReAcTree paper_method 入口：`/data/zmy/OurAgent-he1/benchmark/reactree/external_reactree_runner.py`
- ReAcTree WAH FO overlay：`/data/zmy/OurAgent-he1/benchmark/reactree/wah/paper_method/code/overrides/wah/wah_env.py`
- ReAcTree ALFRED FO overlay：`/data/zmy/OurAgent-he1/benchmark/reactree/alfred/paper_method/code/overrides/src/alfred/alfred_env.py`
- DELTA paper_method runner：`/data/zmy/OurAgent-he1/benchmark/delta/external_delta_runner.py`
- 环境契约：`/data/zmy/OurAgent-he1/benchmark/datasets/environment_contract.md`
- Paper method 运行说明：`/data/zmy/OurAgent-he1/benchmark/README_paper_method.md`
