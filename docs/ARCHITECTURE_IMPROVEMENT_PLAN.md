# 架构优化计划

本文记录当前认知技能架构仍需补强的工程能力。它不是对 `COGNITIVE_SKILL_ARCHITECTURE.md` 的替代，而是面向落地的改进清单。

## 架构收敛决策

当前架构优化的主线不再是继续向各模块追加能力，而是收敛边界、统一契约和减少隐式分叉。架构总纲以 `docs/ARCHITECTURE.md` 为准，本文件只记录落地计划和缺口。

收敛后的目标是：

```text
LangGraph Runtime Orchestrator
  -> Brain Planning Facade
  -> Safety / Sandbox / Evaluator
  -> Task Management
  -> PrimitiveTool Executor
  -> Trace / Evidence / Benchmark Report
```

关键决策：

- `graph/` 保留编排权，但不拥有动作语义和 benchmark 语义。
- `Brain Planning Facade` 统一 baseline LLM planner 与 cognitive planner，两条路径都输出同一份 `todo_list` 契约。
- `cognitive/` 提供 KG、Scene Graph、TaskGraph、SkillLibrary、SafetyPolicyEngine 等认知规划服务，但不直接执行动作。
- `skills/` 继续作为 PrimitiveTool 的唯一语义真理源，CognitiveSkill 只能展开为现有 PrimitiveTool。
- `benchmark/` 只做适配、映射、评测和报告，不向主框架注入特殊语义。
- trace / evidence / lifecycle gate 是架构能力，不是调试附属品。

下一轮优化应优先做架构债收敛：

- 将 `graph/planning/node.py` 中过厚的任务模板、语义推断和认知路径选择逐步外移到 `Brain Planning Facade` 或 `cognitive/` 服务；当前已先拆出 grounding、LLM fallback、cognitive planning bridge、任务已满足判定、语义辅助和 planning config 模块，`node.py` 仅保留主入口编排。
- 将 planning normalizer 的“自动补动作”降级为兼容层，长期策略应来自 CognitiveSkill、SafetyPolicyEngine 或 evaluator finding。
- 将 Understanding 实体抽取改成“相关性排序 + 场景清单校验 + 增量修复 + 最大重试后删除非法实体并 fail-soft 继续”的明确契约，避免把可恢复的实体幻觉直接升级为整轮理解失败。
- 将 failure repair 的 checkpoint、BT recovery、execution reflection 和 planning repair 统一成一个结构化 `RepairContext` 契约，减少 `GlobalState` 中陈旧路由字段互相污染。
- 将 benchmark cognitive eval、JSONL trace 和 skill lifecycle metrics 串成固定 CI/dashboard artifact，避免每次实验重新定义指标口径。
- 将所有 learning 写入路径默认保持 candidate-only，commit 必须经过 evidence、validation 和 regression gate。

### Understanding 实体筛选契约缺口

目标流程已经写入 `docs/ARCHITECTURE.md` 的“语义理解实体筛选流”。当前需要把实现收敛到该契约：

```text
task + scene_entities
  -> LLM relevance classification
  -> directly_related / indirectly_related / possibly_related
  -> flatten by category priority and score
  -> validate against scene_entities
  -> retry incremental repair if invalid names exist
  -> drop remaining invalid names after max retries
  -> pass validated relevant_item_names to Planning
```

实现要求：

- LLM 不输出 `irrelevant` 实体，不相关对象不进入 `relevant_item_names`。
- `directly_related`、`indirectly_related`、`possibly_related` 内部都要按相关性排序。
- 校验层必须保存 `invalid_entity_names`、repair attempt count 和每轮增量修复记录，便于 trace 审计。
- repair prompt 必须明确告诉 LLM：哪些实体不存在；若是任务必需实体，优先从场景清单里找替代；若不是任务必需实体，删除。
- 达到最大重试次数后不应默认让 Understanding 失败，而应删除仍不存在的实体，把剩余已验证实体继续传给 Planning。
- 只有核心必需实体全部缺失时，才设置 `needs_clarification=True` 反问用户。

建议测试覆盖：

- 所有输出实体都存在时，`relevant_item_names` 保持分类和相关性排序。
- 直接相关实体不存在但有替代实体时，repair 输出替换实体并继续。
- 可能相关实体不存在时，repair 删除该实体并继续。
- repair 多轮后仍有不存在实体时，达到上限后删除非法实体并继续。
- 删除后缺失全部直接相关必需实体时，触发 clarification。

## 总体判断

当前架构方向是健康的：

```text
PrimitiveTool / CognitiveSkill 分层清晰
KG / Scene Graph / TaskGraph 边界清楚
大模型不直接写 KG
todo_list 作为规划契约，后续可编译为行为树
技能更新走 candidate -> validation -> deploy
```

但它仍是“合理的架构草案”，还不能称为成熟的优秀工程架构。

主要差距在于：

```text
形式化接口不够硬
评测和消融体系不足
运行时安全层尚未独立
TaskGraph 构建策略尚未确定性化
技能库缺少完整生命周期和测试体系
KG 更新治理还不够严格
全链路可观测性不足
```

## 当前实现进展

截至当前实现，已完成以下最小工程锚点：

- `interfaces/contracts.py`：定义 KG、Scene Graph、TaskGraph、PlanStep、TodoList、Evidence、CandidateUpdate 等 typed contracts；`TaskGraph` 显式携带 relation allowlist、max hops、node/edge budget 与 phase view 等构图策略字段，并在节点/边扩展时执行预算和关系白名单约束；`EvidenceRecord` 要求 source provenance、合法 confidence 与可选 ISO-8601 duration TTL，`CandidateUpdate` 保留 candidate -> validated -> committed 的不可变状态流转，并要求携带 evidence ids、provenance、confidence 与 ISO-8601 duration TTL 等治理元数据后才能进入 validation。
- `interfaces/services.py`：定义 BrainOrchestrator、KGService、SceneGraphService、TaskGraphBuilder、LLMReasoner、SafetyPolicyEngine 等服务边界。
- `cognitive/kg_service.py`：提供确定性的静态 KG prototype，支持 `CutIngredient`、`MakeTea`、`DoLaundry`、`TurnOnDevice`、`TurnOffDevice`、`TypeOnDevice`、`OpenContainer`、`CloseContainer`、`PutObjectIntoContainer`、`CleanObject`、`PickUpObject`、`ReadObject`、`ObserveObject`、`SleepOnObject`、`TouchObject`、`DrinkObject`、`SitOnObject` 的任务语义合同查询；KG 更新路径会先记录 `EvidenceRecord`，再只接受引用已知 evidence ids 且携带 provenance / confidence / ISO-8601 TTL 治理元数据的 candidate update，并继续禁止未 validated 的 update commit。
- `cognitive/evaluation.py`：提供 cognitive planning 消融评测 scaffold 和 eval case runner，支持按 `baseline_todo`、`kg_contract`、`kg_task_graph`、`kg_task_graph_lightweight`、`kg_task_graph_repair`、`bt_execution` 聚合规划合法率、sandbox 通过率、任务成功率、重规划次数、幻觉动作数、KG/Scene 查询数、token、延迟、orchestration route counts、route-level planning/sandbox/task/query/latency 指标、BehaviorTree 编译率、执行率、成功率、attempt 数、action/condition event 数、replan request 数、BT recovery hint 消费率、BT recovery retry budget 耗尽率、execution reflection retry 次数、reflection retry limit 命中率、checkpoint/suffix 一致性检查率、对齐率、validated prefix 复用率、平均 validated prefix 长度和平均 suffix 长度；`kg_task_graph_lightweight` 会开启 `cognitive_lightweight_path`，用于和标准 `kg_task_graph` 横向比较低风险单目标任务的 KG 查询开销、路径选择和成功率；failure explainability rate 与 failure category counts 会以 sandbox reject 和 runtime task failure 为失败分母，避免 BT/runtime 失败被 sandbox pass 掩盖，也避免成功 case 的陈旧 category 污染失败分类；`baseline_todo` 变体会直接评估 case 中给定的 todo_list，并关闭 cognitive planning / BT / checkpoint flags，从而作为真正的非 KG/TaskGraph baseline；`bt_execution` 变体会在规划和 sandbox 审计通过后通过 Task Management 的 BT 执行路径跑出 runtime monitor trace，sandbox 拦截时不会执行 BT，当前 eval 覆盖 `CutIngredient`、`MakeTea`、`DoLaundry`、`TurnOnDevice`、`TurnOffDevice`、`TypeOnDevice`、`OpenContainer`、`CloseContainer`、`PutObjectIntoContainer`、`CleanObject`、`PickUpObject`、`ReadObject`、`ObserveObject`、`SleepOnObject`、`TouchObject`、`DrinkObject`、`SitOnObject` 十七个垂直任务族，并覆盖十七个任务族真实 primitive execution failure；当 BT recovery 请求 `Retry_Planning` 时按 `feature_flags.cognitive_bt_direct_replan_budget`（默认 1）做 bounded direct replan，把首次失败与重试执行 attempt 合并纳入 case result，并将 budget decision 写入 trace，且 eval budget accounting 会同时消费 `direct_replan_count` 与运行时 `bt_recovery_direct_replan_count`，避免预先消耗过的 recovery budget 被重复使用；当 direct replan 后的第二次 BT attempt 再触发 execution reflection 时，attempt 与 reflection 指标也会继续合并统计；当 invalid execution reflection 先落到 planning repair，且第三次 BT attempt 再次落入 Reflection_Module 时，eval runner 现在会继续消费这条 follow-up reflection，而不是在 planning repair 后过早停止；当 BT primitive action 在执行层失败时保留 execution-layer failure，不触发 direct replan；当 `feature_flags.cognitive_bt_execution_reflection_retry=True` 时可做一次 bounded execution reflection retry，并把 reflection attempt 写入 trace。
- `cognitive/reasoner.py` / `graph/planning/node.py`：在 cognitive replanning 时会从 BT recovery 的结构化 `action_result.failed_step` / hint 中提取修复上下文，写入 `BrainTask.context.bt_recovery`，并让 deterministic reasoner 生成从失败 step 开始的 suffix repair plan；当 execution reflection 给出无效 `corrected_execution` 并退回 planning repair 时，也会从反馈文本中解析 `failed step`，避免退化成整任务重规划；当 `feature_flags.checkpoint_repair=True` 且 sandbox 或 runtime checkpoint repair 已保留 `validated_steps` / `checkpoint_robot` / `checkpoint_env` 时，cognitive planning 会把这些断点状态真正注入当前 scene/robot 上下文，再校验 `bt_failed_step == len(validated_steps)+1`，对齐时复用 validated prefix，否则不盲目拼接；checkpoint-aligned 场景下 deterministic suffix 已基于断点 scene 生成时不会再用原全局 failed step 二次裁剪，避免丢掉断点后的清洁/放置前置动作；trace 的 `planning_node.bt_recovery`、`planning_node.checkpoint_suffix_repair` 和 `plan_summary.bt_recovery` 会记录本轮消费的 recovery hint 与一致性判断。
- `cognitive/scene_graph_service.py`：提供最小 Runtime Scene Graph 查询服务，只处理实例和状态。
- `cognitive/task_graph_builder.py`：提供确定性 TaskGraphBuilder prototype；builder 构造时可配置 max_hops、node_budget、edge_budget、relation_allowlist 与 phase_view，并把这些策略写入 KGQuery、TaskGraph、goal node metadata 与 trace stats，使扩图预算不再只是文档约定。
- `cognitive/task_graph_visualization.py`：提供 TaskGraph 调试视图导出，可生成结构化 JSON、Mermaid 和 GraphViz DOT，并写入 cognitive planning trace；JSON 视图除节点/边/缺失事实外，也会导出 max_hops、node/edge budget、relation_allowlist 与 phase_view 等构图策略，便于复现和审计扩图过程。
- `cognitive/behavior_tree.py`：提供最小 `todo_list -> BehaviorTree` schema/compiler scaffold，将已审计 primitive step 编译为 `Sequence -> Recovery -> Fallback/Action` 结构，并保留 precondition、success check、failure/retry policy；支持从 trace payload 重建 typed BehaviorTree。
- `cognitive/behavior_tree_executor.py`：提供最小 BehaviorTree executor / runtime monitor scaffold，支持 `Sequence`、`Fallback`、`Recovery`、`Condition`、`Action` 解释执行，并通过注入 action runner / condition checker 与真实执行后端解耦；runtime monitor 会记录节点状态、message 和 action_result，供执行 trace/debug 使用；执行期对 `context` 的更新会保留给调用方，避免 BT 前缀成功动作丢失最新 `env_state`。
- `cognitive/skill_library.py`：不再维护静态高层任务族合同；`StaticSkillLibrary` 仅作为兼容包装，从 `config/skills.json` 当前 profile 和 `skills/*` 元数据动态生成 PrimitiveTool 级 `CognitiveSkillContract`。
- `cognitive/skill_lifecycle.py`：提供 CognitiveSkill lifecycle validation prototype，检查 lifecycle status contract、metadata contract、sandbox eval evidence、regression eval evidence 和高风险 primitive failure policy；每个 report 会记录 eval evidence case 数、suite 覆盖/pass rate、failed case ids 与 failure category counts，同时可聚合 deployable rate、status counts、failed gate counts、failed gate skill ids、gate pass rates、suite pass rates 和 failure category counts，作为 `metrics.json`/CI dashboard 的最小数据形态；`cognitive/skill_eval_cases.json` 已提供十七个任务族最小 sandbox/regression evidence。
- `cognitive/orchestrator.py`：提供 `PrototypeBrainOrchestrator`，串联 KG、Scene Graph、TaskGraphBuilder、模板 reasoner 和 safety 检查；当 planner 处于 BT suffix repair 模式时，safety 校验会基于 `validated_steps + suffix` 或“去掉 bt_recovery 后的完整基线计划”做上下文校验，避免把合法续写误判成缺少刀具/开盖/清洗等前缀步骤；Scene Graph 绑定当前也会把 grounded instance 的直接父容器一并补进 TaskGraph，使 deterministic planner 能对 closed-container 内的 pickup/read/drink/clean/put-source acquisition 做显式开盖；KG contract query 现在还会把 `target_name` / `container_name` / `water_source_name` / `ingredient_name` / `cup_name` / `heating_device_name` / `load_name` / `washer_name` / `detergent_name` 显式注入 scene query name hint，避免多实例同类型场景退化成按 scene order 选错对象，并让 `make_tea` / `laundry` 这类复合 planner 真正消费具名二级资源；同时新增 feature-flagged `cognitive_lightweight_path` 轻量路径决策，低风险单目标 `turn_on` / `turn_off` / `open` / `close` / `observe` / `touch` / `type` / `sleep` / `sit` 可跳过 KG contract enrichment，直接走 Scene Graph 绑定 + skill selection + safety validation，`pickup` / `read` / `drink` / `put` / `clean` / `cut` / `make` / `do` 等需要容器、手部状态、复合资源或高风险治理的任务仍显式保留 `kg_task_graph` 路径；`PlanTrace.orchestration` 会记录 route path、reason 与 eligibility，便于 ablation 和 runtime trace 审计。
- `cognitive/reasoner.py`：原 deterministic planner 仍作为 legacy prototype / benchmark 对照保留，但不再是当前规划入口的动作生成来源；主规划路径改为 LLM 根据当前 `skill_profile` 的 PrimitiveTool 技能说明生成 `todo_list`，再由 sandbox / semantic audit / state diff audit 校验。
- `cognitive/trace_store.py`：提供可选 JSONL trace recorder，在 `feature_flags.cognitive_trace_write=True` 时记录完整 cognitive planning trace；支持按 `trace_id` 查询最近持久化记录；`JsonlTraceRecorder.summarize_recent()` 可从最近 trace 中聚合 selected skill usage、orchestration route counts、route-level safety/sandbox pass rate、route-level KG/Scene query count、sandbox failure category、BT execution attempt、BT recovery retry budget exhaustion、平均/最大 recovery budget used、execution reflection limit count/rate、checkpoint/suffix alignment、validated prefix reuse、平均 validated prefix 长度和平均 suffix 长度等 runtime dashboard 指标。
- `cognitive/safety.py`：提供最小结构性 SafetyPolicyEngine prototype；除既有的 `Slice` / `ToggleOn` / `Heat` 约束外，现已补上对刀具拾取、水源绑定/可用性、便携清洁物体先 Pickup（固定表面/fixture 可原地清洁，不再误判为可拾取物体），以及 closed openable-container 上 `Pickup` / `Put` 前必须 `Open` 的硬约束；安全状态读取已支持 `isOpen/open/closed`、`isToggled/isOn/off`、`available/isAvailable/unavailable` 等 scene state alias，且 `isClean/clean`、human/environment hazard、fixed/portable 等 flag 也会归一化字符串/布尔值，避免同一事实因数据命名或编码差异被误判；`Slice` / `Heat` / `ToggleOn` / `Clean` 这类高风险动作还会读取绑定 scene instance 的显式 human/environment hazard flags，其中 `Clean` 会同时检查待清洁目标和 water_source，缺少人员/环境清场时直接拦截；`Slice` 会分别追踪目标食材和切割表面的 scene-proven / plan-proven 清洁状态，通用无关 `Clean` 不能再满足切割表面前置条件；`ToggleOn` 对容器式设备会按 scene 初始状态和当前计划内最近的 `Open` / `Close` 推导有效开合状态，避免已关闭设备被迫生成冗余 `Close`，同时仍拦截打开后未关闭就启动设备的危险 todo；`Heat` 也会按 scene 和计划前缀推导目标是否已在加热设备内、设备是否关闭并开启，从而允许 scene-proven ready-to-heat suffix，同时继续拦截打开后未关闭或未开机的加热动作。
- `interfaces/contracts.py`：提供 `PlanTrace`，将 KG query、Scene binding、TaskGraph 规模、计划摘要、safety 结果和 sandbox outcome 组织成可查询结构。
- `graph/planning/failure_taxonomy.py`：提供 evaluator failure taxonomy，将空计划、格式错误、无效动作、导航前置、可达性、容器状态、机械臂状态、安全前置、设备状态、语义审计和迭代超限映射为稳定类别。
- `graph/planning/node.py`：在 `feature_flags.cognitive_planning=True` 时，不再按 `operation_type` 进入静态任务族模板；规划仍走统一 LLM decomposition，prompt 中的动作空间由当前 `skill_profile` 的 `skills/*/prompt.md` 决定，并在 `cognitive_planning_trace` 中记录 `llm_skill_profile` 路径、启用技能、实体上下文和生成步骤；在 `feature_flags.cognitive_bt_compile=True` 时，可继续将 normalized `todo_list` 编译为 BehaviorTree 并写入 trace。
- `graph/planning/grounding.py` / `graph/planning/llm_decomposer.py` / `graph/planning/cognitive_decomposer.py` / `graph/planning/satisfaction.py` / `graph/planning/semantic.py`：Planning 入口已按职责拆分；任务分解 grounding 优先消费 Understanding 输出的排序后 `relevant_item_names`，再补齐 `structured_task.required_item_names`，保证语义理解的相关性排序能传递到后续场景实体解析和任务分解；`satisfaction.py` 只按显式 `goal_state` / `desired_state` / `target_state` 比对环境和机器人状态，不再维护基于 `operation_type` 的动作完成白名单。
- `graph/planning/config.py` / `config/settings.json`：规划层 feature flags 已集中到 `planning.features`，由 `with_planning_config()` 在 `decompose_task()` 与 `evaluate_feasibility()` 入口统一归一化；配置默认值可被运行态 `state.feature_flags` 覆盖，保持 sandbox、semantic audit、state diff audit、cognitive planning、checkpoint repair、playbook、trace 等能力全部可配置；其中 `state_diff_audit` 会在沙盒模拟通过后由代码比较全部实体状态差异，并将 diff 交给 LLM 判断差异是否属于任务目标或不可恢复的必要条件。
- `graph/task_management/node.py`：在 `feature_flags.cognitive_bt_execute=True` 且当前任务带有已编译 BehaviorTree trace 时，走 BT executor 实验路径执行整棵树；默认仍保持原逐步 `todo_list` 执行路径。BT recovery 中的 `RepairOrReplan` 会产生结构化重规划信号，写入 `next_routing=retry_planning`、`corrected_plan_hint` 和 `behavior_tree_execution`；若先出现 primitive action execution failure，则该执行失败优先于后续 recovery action，用于进入 execution reflection；当 BT 在中途 primitive step 失败时，会把任务栈中的 `todo_list` 裁成从失败 step 开始的剩余 suffix，避免 execution reflection retry 误改或重放已成功前缀，同时把运行时已成功前缀沉淀为 `validated_steps/checkpoint_robot/checkpoint_env`，其中 `checkpoint_env` 现在来自真实 runtime scene 快照而非旧规划态，供后续 planning repair 继续做 composite suffix repair；当 planning repair 产出“validated prefix + repaired suffix”的合并 `todo_list` 时，Task Management 现在只把 suffix 作为真实执行 payload 压栈，并为该 suffix 重新编译运行时 BT，从而让 checkpoint prefix reuse 不只停留在 planner/trace，而会真正从 runtime checkpoint 续跑；BT 执行结果会合并回 `cognitive_planning_trace`，并在 `cognitive_trace_write=True` 时持久化到 JSONL。
- `graph/routes.py` / `graph/graph.py`：在 `feature_flags.cognitive_bt_recovery_direct_replan=True` 且未超过 `feature_flags.cognitive_bt_direct_replan_budget`（默认 1）时，Task Management 可将 BT recovery 的重规划信号直接路由到 `Retry_Planning`；当 execution reflection 给出无效 `corrected_execution` 时，也会直接转 `Retry_Planning` 做 planning repair；不开启相关开关或 budget 已耗尽时仍保持原 failed -> Reflection/END 行为。
- `graph/nodes.py`：注入式执行派发会保留规划 trace 中的 BehaviorTree payload，支持中断/插单场景继续走 BT 实验路径；execution reflection 的 `Retry_Execution` 只接受有效 `corrected_execution`，成功替换当前 primitive action 时会丢弃不再匹配的旧 BT payload，若反思输出无效则转入 planning repair，避免静默重跑已失败动作；对 BT 中途失败场景，升级到 planning repair 时会把失败 step 编进 `corrected_plan_hint`，供 replanner 继续做 suffix repair；`Retry_Planning` 还会主动清空过期的 `next_routing` / `failure_reason` / `corrected_execution` / `correction_strategy`，避免上一轮 invalid reflection 的陈旧故障元数据污染后续 BT retry 路由。
- `scripts/validate_cognitive_skills.py`：提供 CognitiveSkill lifecycle gate CLI，可在 CI/benchmark pipeline 中校验当前技能库是否满足 deploy gates，并输出 per-skill reports 与 aggregate lifecycle summary；同时支持 `--output` 写出同一份 metrics JSON，作为 CI/dashboard artifact。
- `benchmark/reporting.py`：提供 benchmark cognitive eval artifact rollup，可聚合多个 JSON artifact 的 dataset-level counts、variant summary、weighted variant comparison deltas、unsupported reason counts、case comparison counts、task-family comparison counts 与 improved/regressed/missing task hotspots；variant summary rollup 会保留 `orchestration_route_counts` 并按 route case_count 加权聚合 planning/sandbox/task/query/latency 指标，便于跨运行比较 `lightweight_scene` 与 `kg_task_graph`，共享 artifact 的 `variant_comparisons` 现在还会记录相对 anchor variant 的 route share deltas，rollup 端会进一步聚合这些 route-level delta，帮助判断 lightweight path 究竟替代了哪些旧路径；同时新增 `route_hotspots` 直接列出各 variant 最高流量、最低成功率和最高延迟的 orchestration routes，减少人工翻表；同时会输出按 baseline output source / anchor variant / model label 分组的 `context_groups`，并保留 `artifact_index` 与 `context_counts` 这类 per-artifact provenance / context 元数据（如 source path、model label、runner output path、anchor variant、input dataset、scene id、baseline output source），作为跨运行/跨 benchmark 的最小报表骨架。
- `benchmark/delta/cognitive_eval.py` / `benchmark/delta/runner.py`：DELTA benchmark 现已接入共享 cognitive eval artifact path；在不伪造整任务支持面的前提下，将可识别的自然语言 `subgoals` 扩成 subgoal-level synthetic benchmark cases（如 `pc:allensville#sg0`），支持 `bring X to room` 映射为 room-anchor placement、以及 `open/close/pickup/put/clean/read/observe/type/sleep/touch/drink/sit` 等已覆盖任务族的 DELTA 子任务认知评测，并对 `assemble my_pc` 这类超出当前认知合同的子任务显式记录 unsupported reason；`baseline_todo` 仅在固定 `--subgoal-index` 时启用，确保基线 todo 与单个 DELTA 子任务一一对应。
- `benchmark/eai/runner.py` / `benchmark/eai/cognitive_eval.py`：EAI / VirtualHome framework mode 已开启 `feature_flags.cognitive_planning=True`，使已覆盖的 benchmark task（如 turn on light、turn on computer、turn off light、type on computer、write email and switch off computer、open freezer、close freezer、put groceries in fridge、put groceries in fridge and close freezer、wash clothes、wash hands、pick up book、read book、watch television、sleep on bed、touch cat、drink cup、sit on chair、cut beef）可进入 KG/TaskGraph cognitive planning path；runner 现在可通过 `--cognitive-eval-output` 对 supported EAI cases 写出 cognitive ablation summary / per-case result JSON artifact，`--cognitive-eval-variant` 支持逗号分隔的多 variant fan-out（当前支持 `baseline_todo` / `kg_task_graph` / `kg_task_graph_lightweight` / `kg_contract` / `kg_task_graph_repair` / `bt_execution`，并提供 `all` 别名），artifact 还会按 case 聚合 variant 结果并输出相对 anchor variant 的 summary delta，同时记录 total/supported/unsupported case counts、support coverage rate、supported/unsupported task-name counts、unsupported case 明细、unsupported case ids 与 variant-specific unsupported reasons，便于和 VirtualHome action sequencing 结果并行留档、审计覆盖率以及做 baseline/KG/TaskGraph/BT 横向对比；artifact 还会按 `task_success -> sandbox_passed -> planning_legal` 的优先级输出 `case_comparisons`，列出每个 variant 相对 anchor 的 improved/regressed/tied/missing case ids，并进一步聚合为 `task_comparisons`，按 task name 汇总每个任务族的 compared/improved/regressed/tied/missing 计数，让 summary delta 之外的 case-level 与 task-family 级收益/退化都可以直接审计；artifact 顶层现在还会显式记录 `model_label` 与 `runner_output_path`，方便跨运行比较时区分 OurAgent 输出来源。EAI `baseline_todo` 现在只在实际 benchmark action-sequencing outputs 可用时启用，可通过 `--cognitive-baseline-output` 从独立 action-sequencing artifact 提供 baseline 来源，未请求 `baseline_todo` 时不会读取该文件；同时通过保留重复 action key、可提取 fenced JSON / 文本中 JSON object 的解析器，把 VirtualHome `WALK` / `GRAB` / `PUTIN` / `PUTBACK` 等输出稳定映射回 todo baseline，缺少 outputs、空 outputs 或无法映射的动作（如 `PLUGIN`）会以 unsupported reason 显式记录，而不是伪造空 baseline；support accounting 按 variant 分别记录，并让 artifact 顶层 supported/unsupported 字段跟随 anchor variant，避免 baseline 与 KG 支持面不一致时互相污染。与此同时提供 supported-case converter，可将确定性识别出的 EAI turn-on-device、turn-off-device、SWITCHON/SWITCHOFF action-goal（含 `HAS_SWITCH` 非 lamp/computer 类物体）、TYPE action-goal、TYPE+SWITCHOFF 复合 office task、open-container/OPEN action-goal、close-container/CLOSE action-goal、put-into-container+close-container 复合 storage task、PUTIN/PUTBACK/PUTON action-goal placement、put-on-surface placement task、laundry-style WASH clothes task、held-object pickup、GRAB/PICKUP/TAKE action-goal、WASH action-goal、READ action-goal（含 `READABLE` 非 book 类物体）、WATCH/LOOKAT action-goal、SLEEP/LIE node-goal / character-on-edge / action-goal case、TOUCH action-goal（含非动物类普通物体）、DRINK action-goal（含 `DRINKABLE` 非 cup 类物体）、SIT node-goal / character-on-edge / action-goal case 与 CUT action-goal（当前限定为可绑定 beef + knife + cutting_board 的切割任务）转为 `CognitivePlanningEvalCase` 并纳入 cognitive ablation eval；其中 `object.read` / `object.drink` 已补到更贴近真实 benchmark 的“必要时先 Pickup 再 Read/Drink”序列，并对历史 smoke 形态的 `address_book` tabletop READ 与 tabletop cup DRINK 输出加了 `GRAB` 回归，`object.pickup` 会把内部 `Pickup(target_item=...)` 渲染为 VirtualHome `GRAB`，`object.sleep_on` 会把内部 `Sleep(target_bed=...)` 渲染为 VirtualHome 目标动作 `LIE`，`cooking.cut_ingredient` 会把内部 `Slice(target_item=...)` 渲染为 VirtualHome `CUT`，`object.put_into_container` 也已补到可选 `Close` 后置步骤、action-goal-only `PUTIN` 和 surface `PUTBACK` 渲染以覆盖 freezer storage / surface placement，并锁住 freezer 已打开、目标已在手中的 held-object storage case 及其 VirtualHome 渲染结果，避免真实 benchmark 负载重复 `GRAB`；`laundry.do_laundry` 也已接入真实 `Wash clothes` benchmark 入口，且 benchmark laundry converter / planning contract 现已对齐为优先使用 `tools.primary` 中的 detergent name，避免真实 benchmark 负载在 washer+detergent 同时出现在 payload 时退化成错误绑定；`device.turn_on` 也已用真实 office `Turn on computer` case 和 action-goal-only `SWITCHON` case 锁住回归，未覆盖任务显式跳过而不是伪装成已支持。
- `tests/test_planning_node.py` / `tests/test_cognitive_services.py`：当前回归重点改为验证 `cognitive_decomposer` 不再输出静态 `operation` 合同、`cognitive_planning=True` 走 skill-profile + LLM 分解 trace，以及 `StaticSkillLibrary` 只暴露当前 profile 启用的 PrimitiveTool；旧十七任务族 deterministic cognitive planner 用例已标记为 legacy skip。
- `tests/test_task_graph_visualization.py`：验证 TaskGraph 可视化 JSON、Mermaid 和 GraphViz DOT 输出契约。
- `tests/test_behavior_tree.py`：验证 BehaviorTree compiler 的 guard、action、recovery、legacy todo 输入契约和 trace payload round-trip。
- `tests/test_behavior_tree_executor.py`：验证 BehaviorTree executor 的顺序执行、已满足条件跳过 action、前置失败 recovery、runtime monitor action_result 和无 runner 安全失败。
- `tests/test_execution_node.py` / `tests/test_graph_nodes.py`：验证 `cognitive_bt_execute` 执行开关、BT backend dispatch、`RepairOrReplan` 触发 retry planning、BT primitive action failure 进入 execution reflection、execution reflection retry 替换当前动作、无效 corrected action 转 planning repair、reflection retry 上限终止、BT recovery direct-replan runtime budget、BT 条件检查、direct replan 路由、BT execution trace 合并/持久化、默认旧路径和注入式 BT payload 保留，以及 BT 中途失败时只保留剩余 suffix 供 execution reflection retry 使用；当 planning repair 输出 prefix+suffix 合并计划且 checkpoint reuse 对齐时，也验证真实执行只消费 suffix 而不会重放前缀，并且若该 suffix 再次失败，后续 planning repair 仍使用原始全局 step 编号而不是 suffix 局部编号；当 BT execution reflection 输出无效修复动作时，主图会直接转 `Retry_Planning` 而不是再回反思层绕一圈，并会把运行时已成功前缀携带到 planning repair；同时锁住 `Retry_Planning` 会清空旧的 recovery routing 元数据，防止下一次 BT 失败被陈旧 `next_routing`/`failure_reason` 误导。

这些实现仍是原型，不替代当前 LangGraph 主流程。它们的作用是把 P0/P1 架构边界固化为可测试接口，为后续接入真实 planning prompt、sandbox 和执行层做准备。

## 优秀架构目标

目标架构应从“LLM 中心”升级为“Orchestrator 中心”：

```text
Brain Orchestrator
  ├── LLM Reasoner
  ├── KG Query Planner
  ├── TaskGraph Builder
  ├── Skill Selector
  ├── Plan Generator
  ├── SafetyPolicyEngine
  └── Repair Controller

Persistent KG
  ├── Ontology
  ├── Skill Metadata
  ├── Affordance Rules
  ├── Safety Rules
  ├── User Preferences
  └── Evidence Graph

Scene Graph
  ├── Object Instances
  ├── Location
  ├── Runtime State
  └── Robot State

TaskGraph
  ├── Goal
  ├── Bound Entities
  ├── Relevant KG Rules
  ├── Relevant Scene Facts
  ├── Candidate Skills
  ├── Missing Facts
  └── Plan Trace

SkillLibrary
  ├── CognitiveSkill
  ├── Eval Cases
  ├── Versioning
  └── Validation Metrics

Execution Layer
  ├── todo_list
  ├── optional BT compiler
  ├── PrimitiveTool executor
  └── Runtime Monitor
```

核心原则：

```text
LLM 是推理组件，不是流程控制器
KG 是结构化知识服务，不是 KG Agent
Scene Graph 是当前世界状态源
TaskGraph 是临时工作记忆
SafetyPolicyEngine 是硬约束层，不依赖 prompt
```

## 改进方向

### 1. Brain Orchestrator

当前文档中容易把“大脑”理解为大模型。后续应明确：

```text
Brain = Orchestrator + LLM + Tools + Policies
```

Brain Orchestrator 负责：

- 控制任务主循环
- 决定何时查询 KG
- 决定何时查询 Scene Graph
- 构建和更新 TaskGraph
- 选择 CognitiveSkill
- 触发计划生成与修复
- 调用 SafetyPolicyEngine
- 调用 Sandbox/Evaluator

LLM 只负责：

- 语义理解
- 查询意图生成
- 计划候选生成
- 失败解释与修复建议

### 2. Typed Interfaces

需要把组件接口形式化，而不是只在文档中描述概念。

至少应定义：

```text
TaskGraph
KGQuery
KGQueryResult
SceneQuery
SceneQueryResult
CognitiveSkillContract
PrimitiveToolContract
PlanStep
TodoList
ValidationResult
EvidenceRecord
CandidateUpdate
```

这些结构应回答：

```text
LLM 输入什么
LLM 输出什么
KG 返回什么
Scene Graph 返回什么
Skill Expander 返回什么
Sandbox 拦截什么
失败如何编码
证据如何提交
```

### 3. TaskGraphBuilder

TaskGraph 不应完全由 LLM 自由多跳查询构建。

推荐由 TaskGraphBuilder 提供确定性扩图策略，大模型只补充查询意图。

示例策略：

```text
cutting_task policy:
  1. 查 target category
  2. 查 required tools
  3. 查 required surfaces
  4. 查 safety constraints
  5. 查 candidate skills
  6. 查 user preferences
  7. 生成 missing scene queries
```

扩图应带预算：

```text
max_hops
node_budget
edge_budget
relation_allowlist
phase_view
```

### 4. Evaluation And Ablation

架构必须通过实验验证收益。

需要比较：

```text
baseline: 直接 todo_list
variant A: todo_list + KG semantic contract
variant B: todo_list + KG + TaskGraph
variant C: todo_list + KG + TaskGraph + repair loop
variant D: todo_list + KG + TaskGraph + BT execution
```

建议指标：

```text
规划合法率
sandbox 通过率
任务成功率
平均重规划次数
幻觉动作数量
KG 查询次数
token 成本
端到端延迟
失败可解释率
技能更新后 regression rate
```

没有消融实验，就无法判断 KG 和 TaskGraph 是否真的带来收益。

### 5. SafetyPolicyEngine

安全层应独立为硬约束组件，不依赖 prompt。

高风险场景包括：

```text
刀具
热源
水
电器
人体附近动作
清洁剂
食物安全
```

安全策略示例：

```text
high_risk_action requires safety_check
candidate_skill cannot execute in real world
raw_meat task requires contamination policy
heat task requires human/environment clearance
```

SafetyPolicyEngine 应在以下阶段生效：

- CognitiveSkill 选择
- todo_list 生成后
- sandbox 审计前
- 小脑执行前
- runtime monitor 检测到危险状态时

### 6. Skill Lifecycle

CognitiveSkill 不能只是 `prompt.md + yaml`。

每个技能建议包含：

```text
skill.yaml
expansion.md
eval_cases.yaml
regression_cases.yaml
failure_cases.yaml
history.json
metrics.json
```

上线条件：

```text
通过 unit eval
通过 sandbox eval
通过 regression eval
没有破坏已有任务
高风险技能经过额外安全检查
```

状态流转：

```text
draft -> candidate -> validated -> deployed -> deprecated
```

### 7. KG Update Governance

KG 更新应区分不同类型：

```text
事实更新：牛肉_1 已经被切片
偏好更新：用户喜欢用蓝色砧板切肉
规则更新：生肉切前必须清洁砧板
技能更新：CutIngredient 新增清洁步骤
```

每类更新都应记录：

```text
provenance
confidence
timestamp
ttl
evidence_ids
candidate / validated 状态
```

LLM 只能提出 candidate update，不能直接 commit。

### 8. Observability And Trace

系统必须能解释每个关键决策。

需要记录：

```text
为什么选择这个技能
为什么查这些 KG 边
为什么加 Clean(砧板)
为什么没有直接 Slice
哪个 KG 规则影响了计划
哪个 Scene Graph 状态触发了重规划
```

示例 trace：

```json
{
  "task": "切牛肉",
  "selected_skill": "cooking.cut_ingredient",
  "kg_rules_used": ["raw_meat_requires_clean_board"],
  "scene_facts_used": ["砧板_1.clean=false"],
  "plan_edits": ["insert Clean(砧板_1) before Slice"],
  "validation_result": "passed"
}
```

### 9. Lightweight Path

不是所有任务都需要完整 KG + TaskGraph。

简单任务可以走轻量路径：

```text
Intent -> Scene Graph -> PrimitiveTool -> Execute
```

适用任务：

```text
打开灯
关门
导航到厨房
拿起桌上的杯子
```

复杂任务才走完整路径：

```text
做饭
切牛肉
洗衣服
整理餐桌
泡茶
```

是否走完整路径应由 Orchestrator 根据任务复杂度和风险判断。

### 10. Behavior Tree Interface

短期继续使用 `todo_list`，但 `PlanStep` 应提前支持行为树编译所需字段：

```text
preconditions
expected_effects
success_check
failure_policy
retry_policy
```

未来可编译为：

```text
Sequence
  Fallback
    Condition already_satisfied
    Action primitive
  Recovery
    Repair / Replan
```

## 优先级

### P0：必须先做

- 定义 typed interfaces
- 明确 Brain Orchestrator 边界
- 明确 KG / Scene Graph / TaskGraph schema
- 明确 candidate update 不能直接 commit，并要求候选更新携带 evidence/provenance/confidence/TTL 等治理字段

### P1：第一轮原型

- 实现 TaskGraphBuilder 最小版本
- 支持 `CutIngredient`、`MakeTea`、`DoLaundry`、`TurnOnDevice`、`TurnOffDevice`、`TypeOnDevice`、`OpenContainer`、`CloseContainer`、`PutObjectIntoContainer`、`CleanObject`、`PickUpObject`、`ReadObject`、`ObserveObject`、`SleepOnObject`、`TouchObject`、`DrinkObject`、`SitOnObject` 十七个任务族
- 建立 KG typed APIs
- 建立 Scene Graph 查询接口
- 建立 sandbox eval cases

### P2：验证收益

- 做 baseline vs KG+TaskGraph 消融
- 加入 trace logging
- 加入 failure taxonomy
- 统计 token、延迟、查询次数和成功率

### P3：工程增强

- 独立 SafetyPolicyEngine
- 完善 CognitiveSkill 生命周期
- 加入 regression eval
- 引入 TaskGraph 可视化

### P4：长期优化

- SkillOpt 式技能文本优化
- PiEvo 式 principle space 管理
- todo_list -> BehaviorTree 编译器
- 多任务长期记忆治理

## 当前推荐下一步

`CutIngredient`、`MakeTea`、`DoLaundry`、`TurnOnDevice`、`TurnOffDevice`、`TypeOnDevice`、`OpenContainer`、`CloseContainer`、`PutObjectIntoContainer`、`CleanObject`、`PickUpObject`、`ReadObject`、`ObserveObject`、`SleepOnObject`、`TouchObject`、`DrinkObject`、`SitOnObject` 十七个垂直任务族已经建立最小闭环：

```text
用户提出已覆盖任务
  ↓
Orchestrator 解析任务
  ↓
Scene Graph 解析任务相关实例
  ↓
KG 返回任务语义合同
  ↓
TaskGraphBuilder 构建任务图
  ↓
模板 reasoner 生成 todo_list
  ↓
SafetyPolicyEngine 检查
  ↓
Sandbox 验证
  ↓
小脑执行
  ↓
记录 trace 和 evidence
```

后续重点应从“继续堆任务模板”转向验证和工程增强：

- 做 baseline todo_list vs KG+TaskGraph path 的消融评测；`baseline_todo` eval path 现已直接消费给定 todo_list，不再隐式调用 cognitive replanner。
- 当前已具备消融评测 scaffold、真实 cognitive eval case runner 和 failure taxonomy，可从 `decompose_task -> evaluate_feasibility` 输出生成 case result 并按 variant / failure category / orchestration route 聚合指标；EAI runner 可把 supported cases 的 cognitive ablation summary 写成独立 artifact，支持一次运行逗号分隔的多个 ablation variant、`all` 别名、多 variant per-case 结果聚合、相对 anchor variant 的 summary delta、per-case improved/regressed/tied/missing comparison ids、variant-specific unsupported reasons，以及按 task name 汇总的 comparison counts，并显式记录 unsupported case ids、support coverage rate、按 task name 聚合的 supported/unsupported counts 与 unsupported case 明细以审计覆盖率；artifact 顶层现在还会带 `dataset/input_dataset/eval_type/scene_id/model_label/runner_output_path` 等上下文元数据，case result 会记录 `orchestration_route`，variant summary 会记录 route counts 与 route-level planning/sandbox/task/query/latency 指标，`benchmark/reporting.py` 可进一步把多份 artifact 聚合成跨运行/跨 benchmark rollup，汇总 dataset-level counts、variant summary、weighted `variant_comparison_summary` deltas、unsupported reason counts、case comparison counts、task-family comparison counts、improved/regressed/missing task hotspots、按 baseline output source / anchor variant / model label 分组的 `context_groups`，以及 `artifact_index/context_counts` 这类跨 artifact provenance 元数据；EAI / VirtualHome framework mode 已开始接入 cognitive planning flags，且 supported-case converter 已能把 turn-on-device / turn-off-device / SWITCHON/SWITCHOFF action-goal（含 `HAS_SWITCH` 非 lamp/computer 类物体）/ TYPE action-goal / TYPE+SWITCHOFF office workflow / open-container/OPEN action-goal / close-container/CLOSE action-goal / put-into-container+close-container storage workflow / PUTIN-PUTBACK-PUTON action-goal placement / put-on-surface placement workflow / laundry-style WASH clothes workflow / held-object pickup / GRAB-PICKUP-TAKE action-goal / WASH action-goal / READ action-goal（含 `READABLE` 非 book 类物体）/ WATCH-LOOKAT action-goal（含非电视类可观察目标）/ SLEEP-LIE node-goal / action-goal / TOUCH action-goal（含 phone 等普通物体）/ DRINK action-goal（含 `DRINKABLE` 非 cup 类物体）/ SIT node-goal / character-on-edge / action-goal case / CUT action-goal（beef + knife + cutting_board）转为 cognitive eval case，并把 tabletop `read` / `drink` 任务扩到先抓取再执行、把 `pickup_book` 渲染对齐为 `GRAB`、把 `sleep_bed` 渲染对齐为目标化 `LIE`、把 `cut_beef` 渲染对齐为 `CUT`、把 `put_groceries` 任务扩到放入后再关闭 freezer、把 action-goal-only `PUTIN` 与 surface placement 渲染为 `PUTBACK`、把真实 `Wash clothes` 任务接到 `laundry.do_laundry` 的认知路径上；benchmark-facing `baseline_todo` 对比现在已从真实 action-sequencing output 稳定映射回 todo baseline，可通过独立 baseline output source 做跨模型/跨运行对比，并保留重复 action key，且能从 fenced JSON / 带说明文本的 LLM 输出中提取 action-sequencing object，后续仍需要扩大到更多真实任务集、LLM baseline 和跨 benchmark 报表。
- 将 trace payload 进一步持久化为可查询运行记录。目前 KG query、scene binding、selected skill、TaskGraph visualization、safety finding、sandbox outcome 已进入 `cognitive_planning_trace`，并可通过 `feature_flags.cognitive_trace_write=True` 写入 `logs/cognitive_planning_traces.jsonl`；JSONL recorder 现已支持按 `trace_id` 查询，并可从最近记录汇总 selected skill usage、safety/sandbox pass rate、sandbox failure category、BT attempt、recovery budget exhaustion/used、execution reflection limit count/rate 与 checkpoint/suffix reuse 指标。
- 继续验证 lightweight path 的收益和边界。目前 `cognitive_lightweight_path` 已能让低风险单目标任务记录 `lightweight_scene` route 并跳过 KG 查询，JSONL trace dashboard、cognitive eval artifact 与 benchmark rollup 都能按 route 汇总 KG/Scene query count、planning/safety/sandbox/task success 与 latency；后续仍需要在真实 benchmark 中对比 latency、query count 与失败率，再决定是否在更多 profile 中默认开启。
- 强化 `SafetyPolicyEngine` 的任务无关硬约束，特别是热源、容器设备、水源、刀具以及人员/环境清场。
- 完善 CognitiveSkill 生命周期：当前已加入 lifecycle validation prototype，`StaticSkillLibrary` 默认只选择 `deployed` 技能，eval/regression evidence 已文件化为 `cognitive/skill_eval_cases.json`，并提供 `scripts/validate_cognitive_skills.py` 作为 CI/benchmark gate 入口；CLI 现在也会输出 deployable rate、failed gate counts、failed gate skill ids、gate pass rates、suite coverage/pass rates 和 failure category counts 等 aggregate lifecycle metrics，并可通过 `--output` 写出 `metrics.json` 风格 dashboard artifact。
- 最小 `todo_list -> BehaviorTree` schema / compiler scaffold、BehaviorTree executor / runtime monitor scaffold、task management 实验接入路径、`RepairOrReplan` 重规划触发信号、BT recovery direct replan 路由、十七个任务族 BT compile/execute 回归、三任务族 BT direct-replan 回归、BT execution trace 持久化、ablation runtime metrics、`bt_execution` eval runner 的真实 BT 执行路径、`bt_execution` 十七个任务族 eval 覆盖、sandbox 拦截后不执行 BT 的 gating、BT recovery 触发的 bounded direct replan eval loop、三任务族 replanner 消费 BT recovery hint 生成 suffix repair plan、suffix repair 与 sandbox checkpoint repair 的一致性校验、checkpoint/suffix trace 指标纳入 ablation summary、`bt_execution` recovery/checkpoint aligned 与 mismatch eval family 用例、BT action 执行失败后进入 execution reflection 的 eval family 用例（覆盖 `cut_beef` 的真实 Slice primitive failure、`make_tea` 的真实 Heat primitive failure、`laundry` 的真实 ToggleOn device failure、`turn_on_light` 的真实 ToggleOn device failure、`turn_off_light` 的真实 ToggleOff device failure、`open_freezer` 的真实 Open primitive failure、`close_freezer` 的真实 Close primitive failure、`put_groceries` 的真实 Put primitive failure、`wash_hands` 的真实 Clean primitive failure、`pickup_book` 的真实 Pickup primitive failure、`read_book` 的真实 Read primitive failure、`observe_tv` 的真实 Observe primitive failure、`type_computer` 的真实 Type primitive failure、`sleep_bed` 的真实 Sleep primitive failure、`touch_cat` 的真实 Touch primitive failure、`drink_cup` 的真实 Drink primitive failure 和 `sit_chair` 的真实 Sit primitive failure），并新增 “BT execution failure -> invalid execution reflection -> planning repair suffix replan”、“BT execution failure -> runtime prefix checkpoint -> planning repair suffix replan”、“BT recovery direct replan -> runtime checkpoint -> prefix reuse repair”、“BT recovery direct replan -> runtime checkpoint -> suffix-only execution handoff”、“BT recovery direct replan -> second BT attempt execution failure -> execution reflection retry”、“BT recovery direct replan -> invalid execution reflection -> planning repair -> third BT attempt execution reflection retry” 和 “BT recovery direct replan -> invalid execution reflection -> planning repair -> third BT attempt reflection retry limit” 组合 recovery family；`TurnOnDevice`/`device.turn_on`、`TurnOffDevice`/`device.turn_off`、`TypeOnDevice`/`device.type_on`、`OpenContainer`/`container.open`、`CloseContainer`/`container.close`、`PutObjectIntoContainer`/`object.put_into_container`、`CleanObject`/`object.clean`、`PickUpObject`/`object.pickup`、`ReadObject`/`object.read`、`ObserveObject`/`object.observe`、`SleepOnObject`/`object.sleep_on`、`TouchObject`/`object.touch`、`DrinkObject`/`object.drink` 与 `SitOnObject`/`object.sit_on` 的 KG contract、deterministic planner、sandbox/BT eval 与 lifecycle evidence、多次 BT execution attempt 的聚合指标、execution reflection retry 的动作替换/无效输出防护、bounded execution reflection retry eval runner 路径与指标、reflection retry 上限终止 trace/summary 覆盖、BT recovery/direct-replan retry budget 硬约束与 exhaustion 指标、eval/runtime 两侧 recovery budget 计数对齐、主图运行时 recovery budget 路由防护，以及 runtime recovery budget 统计并入 JSONL trace dashboard 已实现；下一步工程主线建议继续推进 P4：继续接入更大真实任务集并补齐更复杂 BT failure family。
