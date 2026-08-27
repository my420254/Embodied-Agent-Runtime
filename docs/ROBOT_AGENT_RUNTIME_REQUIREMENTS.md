# 机器人任务大脑运行时：工程需求与落地案例

本文把 Embodied Agent Runtime 的工程目标、需求来源、核心设计和典型任务链路整理成一份对外可读的项目说明。项目关注的是“自然语言任务如何稳定进入机器人或仿真执行闭环”，因此重点不在单次 prompt 生成动作，而在常驻运行、任务状态、外部中断、执行审计、失败恢复和评测对齐。

## 项目定位

机器人任务系统不是普通聊天应用。用户发出的命令会改变环境状态，例如拿取、放置、打开、切片、加热、清洗等动作都存在前置条件、执行风险和失败反馈。一个可用的任务大脑至少要解决以下问题：

- 外部文本命令如何从 ROS、前端或 CLI 进入同一套任务处理链路；
- 自然语言如何转成结构化任务、目标物体、目标状态和技能参数；
- 计划进入执行层前如何做可行性审计，避免模型直接驱动高风险动作；
- 执行中来了新任务、停止命令或补充说明时如何不中断状态一致性；
- 执行失败后如何判断错误发生在理解、规划、可行性审计还是执行层；
- 不同 benchmark、论文方法和裸模型基线如何使用同一份输入，保证对比公平。

因此，本项目把 LLM 放在“理解和规划”位置，把执行层收敛到技能契约、状态推进和反馈回写，而不是让模型自由输出任意动作。

## 从单步模型到运行时

本项目对应具身任务研发链路中的后期运行时阶段。前期可以先用 VLM/VLA 做一步一观测的闭环预研，也可以用 ALFRED 轨迹训练下一步动作模型，但这两类方案都不能单独覆盖完整运行时需求：

| 路线 | 解决的问题 | 暴露的不足 |
| --- | --- | --- |
| VLM/VLA 一步一观测 | 根据当前视觉或仿真 observation 给出下一步动作 | 每步都要调用多模态模型，延迟高；历史状态弱；失败归因困难 |
| ALFRED SFT 下一步动作模型 | 学习 `Goal + History + Observation -> Next Action` 的宏动作决策 | 更像专家轨迹预测，缺少外部中断、任务恢复、取消暂停和失败反思 |
| Embodied Agent Runtime | 将任务理解、规划、审计、执行、反思和外部入口组成常驻系统 | 需要更清晰的状态设计、模块边界和工程测试 |

运行时框架的价值在于：把“模型会不会给出一个动作”升级成“系统能不能长期接收任务、管理状态、处理失败并可复盘”。

## 核心需求拆解

| 工程需求 | 当前实现位置 | 设计要点 |
| --- | --- | --- |
| 正式文本入口 | `main.py`、`adapters/ros_text_command_service.py` | ROS2 `TextCommand.command` 进入服务回调，再发布到 CommandBus |
| 统一命令总线 | `adapters/command_bus.py` | CLI、ROS、前端适配层都转成 `new_task/cancel/pause/resume` 等结构化事件 |
| 常驻运行循环 | `agent_runtime/engine.py`、`agent_runtime/service.py` | 启动后等待外部任务，避免每条任务都重新初始化 graph 和上下文 |
| 任务理解 | `graph/understanding/` | 抽取意图、相关实体、目标状态，并在信息不足时生成澄清问题 |
| 结构化规划 | `graph/planning/` | 输出统一 `todo_list`，并根据场景、技能 profile 和反馈做规划修复 |
| 技能契约 | `skills/*/skill.yaml`、`skills/*/handler.py` | 低层动作的参数、前提、效果和状态推进由技能层定义 |
| 执行前审计 | `domain/sandbox.py`、`graph/planning/evaluation/` | 对规划结果做 sandbox、state-diff 和语义审计 |
| 任务栈中断恢复 | `graph/task_management/node.py` | 新任务压栈，完成后弹栈恢复下层任务；支持多层嵌套 |
| 取消暂停控制 | `adapters/command_bus.py`、`graph/task_management/node.py` | `cancel_current`、`cancel_all`、`pause`、`resume` 独立于普通任务文本 |
| 失败反思 | `graph/reflection/node.py` | 按 `failure_layer` 分诊到理解、规划、可行性或执行层修复 |
| 可观测与评测 | `benchmark/`、`re_trac/`、`cognitive/trace_store.py` | 保留 trace、状态差异、规划输出和 benchmark 汇总 |

## 典型链路 1：把土豆切成片

用户从 ROS 或前端发送：

```text
把土豆切成片
```

系统处理链路：

```text
TextCommand.command
  -> CommandBus(new_task)
  -> Understanding: 识别目标物体 potato，操作类型 slice，目标状态 sliced
  -> Planning: 生成 NavigateTo / Pickup / Slice / Put 等结构化步骤
  -> Sandbox: 检查土豆、刀具、台面、机器人手持状态等约束
  -> Task Management: 将 todo_list 压入任务栈
  -> Execution: 按技能契约执行每一步并更新 env_state
  -> Reflection: 如果某一步失败，按 failure_layer 决定局部重试或重新规划
```

这条链路体现了项目的核心思想：用户只提供自然语言，系统内部必须把它变成可审计、可执行、可恢复的状态机。

## 典型链路 2：执行中插入新任务

如果系统正在执行“把土豆切成片”，中途又收到：

```text
先去拿杯子
```

CommandBus 会把新文本规范化为 `new_task`。任务管理层在下一个调度边界保存当前任务栈状态，并把新任务放到栈顶：

```text
task_stack:
  - 把土豆切成片
  - 先去拿杯子
```

栈顶任务完成后弹出，系统恢复下层任务：

```text
先去拿杯子完成
  -> pop stack
  -> 继续执行“把土豆切成片”的剩余步骤
```

当前实现支持多层嵌套压栈，测试覆盖了任务 1、任务 2、任务 3 被任务 4 插入后逐层恢复的场景。需要注意的是，这里的中断是运行时调度层中断，不是操作系统级强杀；如果底层 ROS action 或外部工具调用本身阻塞，需要由执行后端提供 timeout、cancel 或安全停止接口。

## 典型链路 3：停止、取消和暂停

普通用户不会总是说标准控制词，因此 CommandBus 会把中文或英文控制语义归一化：

| 用户文本或 kind | 归一化命令 | 运行时行为 |
| --- | --- | --- |
| `停止`、`不要做了`、`stop` | `cancel_all` | 清空任务栈，结束当前任务链路 |
| `取消当前任务` | `cancel_current` | 弹出栈顶任务，恢复下层任务 |
| `暂停`、`等一下` | `pause` | 保留任务栈，运行时进入暂停状态 |
| `继续`、`resume` | `resume` | 从暂停状态恢复执行 |

控制命令与普通任务共用 CommandBus，但在任务管理层走不同分支，避免把“停止”误当成新的机器人任务。

## 典型链路 4：执行失败后的分层恢复

机器人或仿真执行可能失败，例如：

- 目标物体不存在或识别名不一致；
- 容器未打开，导致放置动作不可执行；
- 机器人手上已有物体，不能继续抓取；
- planner 漏掉必要前置动作；
- sandbox 发现计划会产生不符合目标的状态变化；
- 底层执行返回 timeout 或动作失败。

系统不会简单从头重跑，而是记录 `failure_layer` 并进入反思分诊：

| failure_layer | 典型原因 | 修复方向 |
| --- | --- | --- |
| `understanding` | 意图或实体抽取错误 | 回到理解层，重新抽取目标、约束和相关实体 |
| `planning` | 步骤缺失、顺序错误、技能参数不合法 | 回到规划层，结合错误反馈重新生成或续写计划 |
| `feasibility` | sandbox / evaluator 反复拦截 | 分析约束冲突，写入 planning playbook 后再规划 |
| `execution` | 单个技能执行失败 | 优先替换当前动作或参数，必要时升级到规划层 |

反思层有最大重试次数，超过预算后停止自动修复并返回失败状态。这样可以避免 Agent 死循环，也能把“不可能完成”的任务显式暴露出来。

## 典型链路 5：指令补全

当用户指令缺少必要信息时，理解层会生成 `clarification_question`。在正式 ROS/前端链路中，runtime 不会等待终端输入，而是将下一条外部命令作为补充说明。

例如：

```text
用户：把它放到那里
系统：需要补充“它”和“那里”分别指什么
用户：把土豆放到厨房台面上
```

为了避免模型不可达或理解失败导致无限补全，常驻外部驱动模式设置了最大澄清轮数。连续多次无法完成澄清时，系统会放弃当前任务并回到空闲等待。

## 工程设计取舍

### Agent 与 Workflow

本项目没有把所有决策都交给开放式 Agent Loop。机器人任务具有副作用，动作必须可审计，因此主链路更接近可控 Workflow：

```text
Understanding -> Planning -> Audit -> Task Management -> Execution -> Reflection
```

LLM 负责理解和规划，技能层负责动作契约，执行层负责状态推进。这样既保留了语言模型的泛化能力，又避免低层动作完全失控。

### ReAct 与 Plan-and-Execute

纯 ReAct 每一步都动态思考和调用工具，适合开放信息检索类任务；具身任务更需要计划可检查、步骤可追踪、失败可定位。本项目采用“先规划、执行中反馈、失败后反思修复”的混合模式：

- 任务开始时先生成结构化计划；
- 计划进入执行前做 sandbox 和 state-diff 审计；
- 执行失败后把错误反馈交给 Reflection；
- Reflection 可以回到执行、规划或理解层。

### Function Calling / MCP 边界

项目中的 `skills/` 类似机器人领域的工具契约层。每个技能包含名称、参数、前提、效果和 handler。未来如果接 MCP，可以把这些技能进一步封装成 MCP tool/server，但当前设计已经遵守“模型只能选择白名单技能、参数必须校验、执行结果必须结构化返回”的原则。

### 记忆与上下文管理

运行时状态不是只保存聊天记录，而是拆成不同用途的上下文：

- `raw_instruction`：原始用户任务；
- `structured_task`：理解后的任务结构；
- `todo_list`：规划后的可执行步骤；
- `task_stack`：当前任务和被中断任务；
- `env_state`：机器人位置、手持物、环境状态；
- `failure_layer/error_feedback`：失败归因与反馈；
- trace/playbook：可复盘的执行经验和修复规则。

这种 Context Engineering 设计使路由和恢复有明确依据，而不是依赖模型从长对话中猜测当前状态。

### RAG 的位置

机器人任务大脑中的 RAG 不一定是问答知识库，而可以用于检索：

- 技能说明和使用约束；
- 失败案例和历史修复策略；
- 任务模板和 playbook；
- benchmark 中相似任务的状态迁移；
- 设备或场景文档。

当前仓库已经有 ACE playbook、trace、skill prompt 和 benchmark case 等知识来源，后续可以进一步升级为检索增强的 planning context。

### 高并发与消息队列扩展

当前版本是单机 CommandBus，适合 ROS/CLI/前端联调和 benchmark 运行。若扩展到多用户、多机器人或大规模任务队列，可以按以下方向演进：

```text
Frontend / ROS / API
  -> API Gateway
  -> Task Submit Service
  -> Redis: session、cancel flag、rate limit、robot lock
  -> Kafka / Redis Stream: task events、node events、tool events
  -> Runtime Worker Pool
  -> vLLM Model Gateway
  -> ROS / Simulation Execution Backend
```

Redis 更适合低延迟状态、取消标记、会话和资源锁；Kafka 或 Redis Stream 更适合高吞吐、可回放的任务事件流。对于具身任务，还需要按 `robot_id` 做资源互斥，避免多个任务同时控制同一台机器人。

### 可观测与评测

Agent 失败不能只看最终答案。项目通过 trace、benchmark adapter、状态差异和 failure layer 记录以下信息：

- 每个节点的输入输出；
- 规划出的 `todo_list`；
- sandbox / evaluator 发现的问题；
- 执行动作、状态变化和错误反馈；
- 反思层选择的修复路线；
- benchmark case 的成功率、失败层和对比方法。

这些信息可以用于离线复盘，也可以作为后续质量看板、灰度发布和回归测试的基础。

## 当前实现边界

已经实现或保留核心代码的位置：

- ROS 文本服务入口和 `main.py` 常驻启动；
- CommandBus jsonl / memory 双模式；
- LangGraph 主流程和多阶段状态；
- 任务栈式中断、恢复、取消、暂停；
- 执行层 simulation / ROS backend 抽象；
- 技能契约、handler 和状态推进；
- sandbox、state-diff、planner repair 和反思分诊；
- 多 benchmark 数据抽取、清洗、评测和 reporting；
- vLLM OpenAI-compatible 端点、多 worker benchmark 配置。

当前不把以下内容表述为已完整生产化：

- 未在公开仓库中提供真实硬件全链路验收记录；
- 未把底层 SLAM、路径规划、机械臂逆解、抓取姿态估计算法作为本项目核心贡献；
- 当前 CommandBus 不是生产级分布式消息队列；
- RAG / MCP / 多租户权限可作为后续扩展，不应写成已经大规模上线。

这也是项目边界的关键：本仓库聚焦机器人任务大脑和智能体运行时，底层感知、导航和控制由仿真环境或 ROS 后端以宏动作接口提供。

## 公开参考

项目设计可参考以下开源系统的工程思路，但本仓库的代码组织和任务语义围绕自己的具身任务 runtime 实现：

| 开源项目 | 可参考内容 |
| --- | --- |
| [LangGraph](https://github.com/langchain-ai/langgraph) | 有状态图、条件路由、循环、checkpoint 和 Agent 编排 |
| [OpenVLA](https://github.com/openvla/openvla) | VLA 路线如何把视觉语言模型连接到机器人动作 |
| [VoxPoser](https://github.com/huangwl18/VoxPoser) | 用语言模型和 3D 表征组合机器人操作约束 |
| [ReKep](https://github.com/huangwl18/ReKep) | 通过关系关键点约束做具身操作规划 |
| [Dify](https://github.com/langgenius/dify) | 工作流、工具、知识库和模型接入的平台化思路 |
| [GraphRAG](https://github.com/microsoft/graphrag) | 图谱化检索、证据组织和全局/局部搜索 |
| [AgentScope Runtime](https://github.com/agentscope-ai/agentscope-runtime) | Agent 应用服务化、沙箱、可观测和部署思路 |
| [Yuxi](https://github.com/xerrors/Yuxi) | 知识智能体、多租户、RAG、工具和权限的工程分层 |

参考这些项目的价值不在复制代码，而在明确真实 Agent 系统需要解决的问题：状态、工具、权限、失败、观测、评测和部署。
