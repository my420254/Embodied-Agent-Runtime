# Codex 续接状态（DSH 接手 · 更新 2）

- 原 session id: `01a01e91-b786-7d71-a39e-c361650bdf6a`
- rollout: `/data/zmy/.codex_runtime/sessions/2026/08/20/rollout-2026-08-20T09-47-41-01a01e91-b786-7d71-a39e-c361650bdf6a.jsonl`
- 工作区: `/data/zmy/OurAgent-he1`
- 更新时间: 2026-08-21

## 问题现象（用户最后追问）

测试机（另一台有 ROS 的机器，跑打包的 `OurAgent-he1_code_2026-08-20.tar.gz`）用 `ros2 service call /genesis_arm/send_text_command ... "{command: '拿土豆'}"` 发指令，终端出现 `[指令补全]` 卡住；但发“拿鸡蛋”就正常。本地 CLI `run_agent.py --task '去拿土豆' --execute` 成功。

## 真正的根因（已确认，不是代码 bug）

1. **澄清原文是“抱歉，指令理解模块执行异常，请重新说明任务。”** —— 这是 `graph/understanding/pipeline.py` 的 **feature 异常兜底话术**，只在某个理解 feature（`llm_extract` / `entity_repair`）调用 **LLM 抛异常**时出现。
2. **LLM 端口拥塞导致超时**：用户自己的 alfred benchmark 实验（`benchmark/reactree/alfred/paper_method/code/continue_alfred_shards.py --port-override 18002 --parallel 5`）正在打 18002（也可能影响 18003）。实测单次 LLM 调用要 **19~43 秒**，vLLM metrics 显示 running=3~4。
3. **理解层 timeout=120s**（`config/settings.json` → `model.modules.understanding.timeout`）。当多个请求排队时，`llm_extract`/`entity_repair` 很容易超过 120s 抛 `APITimeoutError` → pipeline 兜底 `needs_clarification=True` → 旧版 runtime 打印 `[指令补全]` 并卡在 stdin。
4. **“拿鸡蛋可以”是运气**：鸡蛋那次调用恰好没超时；土豆/切土豆需要 entity_repair 第二次 LLM 调用，更易累计超时。这解释了“同一台机器、同一接口、同一时段，土豆不行鸡蛋行”的随机性。

## 已做修改

- `agent_runtime/runtime.py`（之前）：外部驱动模式澄清不再阻塞 stdin；`MAX_CLARIFICATION_ATTEMPTS=3` 上限，避免无限循环/挂死/EOFError 崩溃。（这是健壮性修复，保留；但**不是**本次根因。）
- `README.md`：补充“LLM 端点拥塞/超时也是导致指令补全的原因”，给出 metrics 查看和单次调用耗时实测命令，以及排查顺序（CommandBus → 连通性 → LLM 负载）。

## 验证

- 18002/18003（屏蔽代理）上“拿土豆/把土豆切成片/拿鸡蛋”理解层全部 `is_complete=True`，无 feature 异常（含 `raise_feature_exceptions=True`）。
- tar 与当前仓库的理解层代码、settings.json、prompts.json 全部一致；CommandBus 规范化正确（new_task）。
- 唯一复现出的异常路径：LLM 调用超时（`APITimeoutError`）→ 兜底话术与用户看到的完全一致。
- 系统里正在跑 alfred 5 并行实验打 18002（08:08 启动），vLLM running=3~4、单次调用 19~43s。

## 下一步建议

- 等 alfred 实验跑完（或用空闲端口）再让测试机重测“拿土豆”。
- 如需缓解：把 `model.modules.understanding.timeout` 调大（如 300s），或让 alfred 实验用专用端口、降低并行度。
- 若想彻底避免“机器人要求补全但无人应答”，可把 runtime 澄清行为升级为“把澄清问题写回 CommandBus/ROS 响应”，当前是“打印日志 + 等下一条命令，3 次放弃”。
