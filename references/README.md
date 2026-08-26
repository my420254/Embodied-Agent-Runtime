# References

本目录保存 OurAgent 当前参考的 ReAct、RE-TRAC、Sda-Planner 三篇论文原文 PDF，并提供一份快速说明。后续需要查实现细节时，优先打开本目录中的 PDF 原文。

## 文件索引

| 方法 | 原文 PDF | 官方链接 |
| --- | --- | --- |
| ReAct | [react_2210.03629.pdf](./react_2210.03629.pdf) | https://arxiv.org/abs/2210.03629 |
| RE-TRAC | [re_trac_2602.02486.pdf](./re_trac_2602.02486.pdf) | https://arxiv.org/abs/2602.02486 |
| Sda-Planner | [sda_planner_2509.26375.pdf](./sda_planner_2509.26375.pdf) | https://arxiv.org/abs/2509.26375 |

## ReAct: Synergizing Reasoning and Acting in Language Models

ReAct 的核心思想是让大语言模型在同一条轨迹中交替生成 reasoning trace 和 task-specific action。reasoning trace 用来维护任务进度、更新计划、处理异常；action 用来调用外部工具、查询信息或和环境交互。它避免把“思考”和“行动”拆成两个孤立模块，使模型可以边观察、边推理、边修正下一步动作。

对 OurAgent 的借鉴点：

- planning 不只输出静态 todo list，而应把环境反馈、动作结果和失败原因纳入下一轮规划上下文。
- 执行动作后产生的 observation / sandbox feedback 是后续 reasoning 的输入，不应被当作日志丢弃。
- ReAct 适合作为最小闭环基线：任务理解 -> 计划一步或几步 -> 执行/观察 -> 继续规划。

查细节时建议看：

- prompt 中 thought/action/observation 的轨迹格式。
- ALFWorld 和 WebShop 部分，尤其是交互式决策任务中的错误恢复方式。
- 论文对 hallucination、error propagation、interpretability 的分析。

## RE-TRAC: REcursive TRAjectory Compression for Deep Search Agents

RE-TRAC 针对 ReAct 线性轨迹的局限：长任务中所有内容都顺序塞进上下文，模型很难回到早期状态、分叉探索、维护全局搜索视角，容易重复探索或陷入局部最优。它的做法是在每轮轨迹后生成结构化 state representation，压缩证据、不确定性、失败、未来计划等信息，再把这个压缩状态传给下一轮轨迹，让 agent 进行跨轨迹探索和迭代反思。

对 OurAgent 的借鉴点：

- [../re_trac/](../re_trac/) 中的状态不只是普通记忆，而是把 validated steps、checkpoint env/robot、失败经验和待修复 frontier 压缩成下一轮规划可消费的结构。
- 失败后不必整条计划重来；可以从已验证 checkpoint 继续，丢弃错误后缀并让规划器只修复剩余部分。
- 失败教训要结构化沉淀，避免下一轮重复生成刚被 sandbox 拦截过的同类动作。

查细节时建议看：

- RE-TRAC state representation 如何组织 evidence、uncertainties、failures、future plans。
- cross-trajectory exploration 如何区别于单条 ReAct 轨迹内的继续推理。
- 论文关于减少 tool calls 和 token usage 的实验分析。

## Sda-Planner: State-Dependency Aware Adaptive Planner for Embodied Task Planning

Sda-Planner 面向具身任务规划，重点解决固定规划范式、动作序列约束不足、执行错误感知不足三个问题。它用 State-Dependency Graph 显式建模动作的前置条件和效果；当执行出错时，通过 Error Backtrack and Diagnosis 找到受影响的计划片段，再通过 Adaptive Action SubTree Generation 只局部重建该片段，而不是全局重算。

对 OurAgent 的借鉴点：

- [../SDA/](../SDA/) 中的 state dependency graph 用来追踪每一步写入了哪些状态谓词，并据此定位失败可能依赖的上游动作。
- 当 sandbox 发现状态冲突或前置条件不满足时，SDA 可以选择更靠前的 causal checkpoint，而不是简单重试失败动作。
- adaptive subtree 对应“局部替换后缀”：保留已验证前缀，从 checkpoint 的真实状态出发生成新的可执行动作子树。

查细节时建议看：

- State-Dependency Graph 对 action preconditions/effects 的建模方式。
- Error Backtrack and Diagnosis 如何确定回滚位置。
- Adaptive Action SubTree Generation 如何在当前环境状态下重建受影响计划片段。

## 项目阅读顺序

如果只是理解 OurAgent 的方法来源，建议按这个顺序读：

1. ReAct：理解最基础的 reasoning/action/observation 闭环。
2. RE-TRAC：理解为什么需要把轨迹压缩成跨轮状态，而不是无限延长上下文。
3. Sda-Planner：理解为什么具身规划需要显式状态依赖、因果回滚和局部子树修复。

如果是在调代码，可对应阅读：

- ReAct 思路：planning prompt、执行反馈、sandbox feedback 的闭环。
- RE-TRAC 实现：[../re_trac/](../re_trac/)。
- SDA 实现：[../SDA/](../SDA/) 和 [../graph/planning/evaluator.py](../graph/planning/evaluator.py) 中的修复分支。
