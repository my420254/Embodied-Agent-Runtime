# Embodied-Agent-Runtime：具身智能机器人任务大脑运行时

本仓库是面向具身智能机器人的任务规划与执行运行时。项目目标不是做一个普通聊天机器人，而是把用户的自然语言指令转成可检查、可执行、可恢复的机器人任务流：先做意图理解和实体补全，再生成技能级计划，通过 LangGraph 组织任务管理、执行反馈和反思修复，最后把动作交给仿真或 ROS/前端链路。

这个版本是 `/data/zmy/OurAgent-he1` 的面试展示增强副本，原始运行仓库未被改动。展示版移除了部分历史探索目录，补充了更适合生产化讲解的工程模块：

- `Trace Harness`：记录理解、规划、工具、执行、反思的可观测轨迹，支持失败定位、回放和 A/B 对比。
- `Redis CommandBus`：支持多进程、多前端、ROS 同时投递任务，适合讲并发任务接入和消息队列。
- `MCP Skill Adapter`：把机器人技能库导出成 MCP 风格工具清单，说明技能如何被 Agent 标准化调用。
- `JSONL CommandBus`：保留轻量本地部署方式，不需要 Redis 也能完成命令投递和中断。

详细增强说明见 [docs/INTERVIEW_RUNTIME_ENHANCEMENTS.md](/data/zmy/OurAgent-he1-interview/docs/INTERVIEW_RUNTIME_ENHANCEMENTS.md)。

## 项目主线

这个项目可以按四层理解：

1. **输入接入层**：`main.py` 提供正式 ROS 文本服务入口；`scripts/run_agent.py` 提供本地 CLI 调试入口；所有外部文本都会进入统一 CommandBus。
2. **任务管理层**：负责新任务、插单、暂停、恢复、取消，以及任务栈维护。执行中收到新任务时，先把当前任务挂起，再处理新任务，之后恢复旧任务。
3. **智能规划层**：负责自然语言理解、实体修复、技能闭包、任务规划、sandbox 检查、失败反思和重规划。
4. **执行适配层**：默认可跑 simulation backend；正式部署时通过 ROS/前端把动作交给机器人系统。

模型侧依旧使用 OpenAI-compatible 接口，Qwen 3.5 / Qwen 3.6 / vLLM 均可接入。新增工程模块不绑定具体模型。

# 原始框架与控制台使用说明

本文只说明当前仓库里已经存在、并且默认会走的能力，以及如何从命令行启动。

## 先说结论

- 核心运行循环是 `agent_runtime/engine.py`；推荐 CLI 入口是 `scripts/run_agent.py`（参数解析）+ `scripts/renderer.py`（终端渲染）。
- 正式 ROS/前端联调入口是 `main.py`：它启动后常驻监听文本命令，并把命令交给同一个任务 runtime。
- 控制台默认是 `plan_only`，也就是只做理解 + 规划，默认不会进入执行层。
- 你说的“把字符串直接注入 console”已经实现了，入口是 `--task`。
- 如果已有执行中的 runtime，再运行一次 `scripts/run_agent.py --task ... --execute`，这次调用会自动变成“投递新任务”，不会再启动第二套 agent。
- `adapters/agent_log_client.py` 已经和框架适配好了：运行时的控制台输出会写进本地 `logs/ouragent.log`，并在设置了前端端口（`GENESIS_WEB_PORT`）时，非阻塞地 POST 到前端 `/agent_log`。详见下面《日志与前端出站链路》。

## 当前有哪些功能

### 面试展示版新增工程能力

#### Trace Harness

用于定位 Agent 运行过程中的失败层级，示例：

```python
from adapters.tracing import TraceHarness

harness = TraceHarness()
harness.record_node("understanding", input_summary="把土豆切片", output_summary="intent=Slice")
harness.record_tool("Pickup", arguments={"target_item": "土豆_1"}, observation="ok")
harness.record_failure("execution", "刀具不可达", node="Slice")

events = harness.replay()
summary = TraceHarness.summarize(events)
```

#### Redis CommandBus

默认不启用 Redis。需要多进程、多前端或多机器人统一投递命令时再启用：

```bash
export OURAGENT_COMMAND_BUS=redis
export OURAGENT_REDIS_URL=redis://localhost:6379/0
export OURAGENT_REDIS_STREAM=ouragent:commands
python main.py
```

如果不设置上述变量，仍然走原有内存/JSONL 命令通道。

#### MCP 技能导出

把 `skills/` 下的机器人技能导出为 MCP 风格工具清单：

```bash
python scripts/export_skill_mcp_manifest.py --include-all
```

输出文件：

```text
docs/mcp_skill_manifest.json
```

这部分用于说明项目如何从“内部技能函数”升级到“可被 Agent 标准化发现、选择、调用的工具协议”。

### 理解层

当前 `config/settings.json` 里启用的理解层特征是：

- `cancel`
- `llm_extract`
- `normalize`
- `entity_repair`
- `goal_state_extract`
- `skill_closure`
- `relevant_items`
- `clarification`

其中：

- `entity_repair` 默认开启。
- `goal_state_extract` 代码里有实现，但默认关闭。
- 其余理解特征默认都会进入主流程。

### 规划层

当前规划层默认会用到：

- `sandbox_evaluator`
- `state_diff_audit`
- `playbook_retrieval`
- `playbook_write`
- `reflection`

当前默认关闭：

- `cognitive_planning`
- `cognitive_lightweight_path`
- `cognitive_bt_compile`
- `cognitive_bt_execute`
- `cognitive_bt_recovery_direct_replan`
- `cognitive_bt_execution_reflection_retry`
- `candidate_rules`
- `cognitive_trace_write`

规划层当前的修复策略是 `retrac`。

### 执行层

当前执行层默认配置是：

- `backend = simulation`
- `sync_runtime_scene = true`
- `ros.timeout_sec = 30`

也就是说，默认是仿真执行，不是空跑。

## 框架默认会不会用到

如果你只是跑 `scripts/run_agent.py` 的默认模式：

- 会用理解层
- 会用规划层
- 不会自动进入执行层

如果你加 `--execute`：

- 会继续进入执行层
- 会走任务管理、执行、反馈闭环

如果你跑正式 benchmark：

- 会走理解层
- 会走规划层
- 会走数据集自己的 parser / adapter / skill contract
- 会走 sandbox 和 state-diff 审计
- 需要时会走 reflection / retrac

## 正式 ROS/前端文本输入链路

正式入口是 `main.py`。它的职责很窄，只做三件事：

1. 解析实例号或端口，设置 `GENESIS_WEB_PORT` 和 `ROS_DOMAIN_ID`。
2. 启动 `agent_runtime.service.AgentRuntimeThread`，让 LangGraph runtime 在后台常驻。
3. 创建 ROS 服务 `TextCommandReceiver`，对外接收 `genesis_msgs/srv/TextCommand`。

如果传 `--no-agent-runtime`，`main.py` 只保留 ROS 接收层，不会启动任务 runtime。

文本不是直接写进图里，而是先进入统一命令通道：

`TextCommand.command` -> `TextCommandReceiver._on_command` -> `publish_text_command(cmd)` -> `publish_ros_interrupt_command(cmd)` -> `publish_interrupt_command(...)` -> CommandBus -> `agent_runtime/engine.py`

你最开始贴出来的那段代码，思路本身就是“收到一条文本，再留一个后续处理入口”。其中：

- `RECEIVED_TEXT_COMMANDS` 只是调试用的历史记录。
- 旧的 `handle_text_command(cmd)` 只是一个空 hook，默认并不真正驱动任务。
- 现在真正的驱动点已经转移到 `adapters/command_bus.py` 和 `agent_runtime/engine.py`，文本会先被规范化成命令，再由任务管理层消费。

### 外部怎么提供文本

ROS 侧的标准调用形式是：

```bash
ros2 service call /genesis_arm/send_text_command genesis_msgs/srv/TextCommand "{command: '把土豆切成片'}"
```

如果你启动的是实例端口 `5001`，服务名会变成：

```bash
/genesis_arm_5001/send_text_command
```

请求只需要填 `command` 字段。服务回包会带 `received` 和 `message`，用于确认收到的原始文本。

如果前端不是 ROS-native，就要先通过 ROS2 client、rosbridge 或你自己的适配层，把文本转成同一个 `TextCommand` 请求，再走上面的链路。

### 部署机器必须能访问 LLM 端点

理解层/规划层都会调用本地 LLM。默认配置在 `config/settings.json` 的 `model` 段：

```json
{
  "api_base": "http://192.168.27.250:18003/v1",
  "model_name": "Qwen3.6-27B",
  "base_host": "192.168.27.250"
}
```

**注意：`192.168.27.250` 是内网地址。** 如果 ROS/前端跑在另一台机器上，那台机器必须能连通这个 IP:端口，否则每次理解都会失败，表现为“命令进去后一直要求指令补全”（澄清），因为 LLM 调用抛 `Connection error`，理解层兜底为 `needs_clarification=True`。

**另一个更隐蔽的原因：LLM 端点拥塞/超时。** 理解层默认 `timeout=120s`。如果同一时间有别的实验（例如 alfred/virtualhome benchmark 并行 worker）在打同一个 vLLM 端口，单次 LLM 调用可能要 20~60s 甚至更久；一旦超过 120s 或排队过长，`llm_extract` / `entity_repair` 就会抛 `APITimeoutError`，理解层兜底为 `needs_clarification=True`，话术是“抱歉，指令理解模块执行异常，请重新说明任务。”——这**不是代码 bug，也不是实体对齐问题**，纯粹是 LLM 太忙。判断方法：

```bash
# 看端口当前负载（running/waiting 高就说明在排队）
curl --noproxy '*' -s http://192.168.27.250:18003/metrics | grep -E "num_requests_(running|waiting)"
# 实测单次调用耗时（明显大于 20s 就是拥塞）
time curl --noproxy '*' -s http://192.168.27.250:18003/v1/chat/completions \
  -H "Authorization: Bearer qwen-local-key" -H "Content-Type: application/json" \
  -d '{"model":"Qwen3.6-27B","messages":[{"role":"user","content":"hi"}]}'
```

排查时注意：“拿土豆要补全、拿鸡蛋可以”这类**随机/间歇性**现象，几乎总是 LLM 拥塞导致偶发超时，而不是指令本身有问题。

部署到别的机器时，按下面任一方式改：

1. 改 `config/settings.json` 里 `model.base_host` / `model.api_base`，指向测试机能访问的地址（例如 vLLM 所在机器对外的 IP）。
2. 或启动前设置环境变量覆盖（优先级高于 settings.json）：
   - `OURAGENT_LLM_BASE_HOST=<可达IP>`：覆盖 base_host。
   - `OURAGENT_LLM_STICKY_HOST=<可达IP>`：强制所有本地端点的请求都打到这个 host。
   - `OURAGENT_COMMAND_FILE=<路径>`：覆盖命令通道文件（多实例时才需要）。

验证连通性（不带代理直接测）：

```bash
curl --noproxy '*' http://<可达IP>:18003/v1/models -H "Authorization: Bearer qwen-local-key"
```

### 指令补全（澄清）在正式链路里怎么工作

当理解层认为指令信息不足（或 LLM 调用失败）时，会设置 `needs_clarification=True` 和 `clarification_question`。

- 纯交互控制台（`scripts/run_agent.py` 不带 `--listen`）：runtime 会打印 `[指令补全] >>> ` 并在终端等你补输入。
- 正式 ROS/前端链路（`main.py`，即外部驱动模式）：runtime **不会**阻塞在终端 stdin 上等输入。它会：
  1. 把澄清问题打印到日志；
  2. 等待下一条外部 CommandBus 命令作为补充说明（你可以再用 `ros2 service call` 或 `send_command.py` 补发一条更完整的命令）；
  3. 如果连续 `MAX_CLARIFICATION_ATTEMPTS`（当前为 3）次都无法完成澄清，放弃当前任务，回到空闲等待下一条命令，而不是无限循环或挂死。

所以，正式联调里如果机器人“要求补全”，按顺序排查：

1. 命令是否真的进了 CommandBus（看 `/tmp/ouragent_commands.jsonl`）。
2. 部署机能不能访问 LLM 端点（`curl --noproxy '*'`）。
3. **LLM 是不是正被其他实验占满**（看 metrics 的 running/waiting，实测单次调用耗时）——这是“某些指令偶尔要补全、另一些指令正常”的头号原因。

### 命令会不会存储

会，但分三层，含义不一样：

- ROS 接收层会把本进程收到的原始文本追加到 `RECEIVED_TEXT_COMMANDS`，这是内存列表，只用于调试；进程退出后就没了。
- CommandBus 会把规范化后的命令写到默认 jsonl 文件 `/tmp/ouragent_commands.jsonl`，也可以用 `OURAGENT_COMMAND_FILE` 改路径。
- 执行阶段不会直接执行原始字符串，而是先经过理解和规划，生成 `todo_list`，再由任务管理层保存到 `task_stack`。

因此，`TextCommand.command` 是原始输入；CommandBus 保存的是统一命令；`task_stack` 保存的是正在执行或被插单挂起的任务状态。

这个 jsonl 文件不是完整任务数据库。runtime 启动时默认从文件末尾开始监听，所以旧命令不会因为重启而自动重放。

### 现在谁负责什么

- `main.py`：只负责启动常驻监听和 runtime，不负责业务推理。
- `adapters/ros_text_command_service.py`：ROS 文本服务适配层，负责接收和转发。
- `adapters/ros_bridge.py`：把 ROS payload 归一化成普通命令对象。
- `adapters/command_bus.py`：统一 `new_task`、`cancel_all`、`cancel_current`、`pause`、`resume` 等命令。
- `agent_runtime/engine.py`：常驻消费 CommandBus，驱动 LangGraph 执行。
- `graph/task_management/node.py`：处理插单、压栈、恢复、取消和暂停。

### 插单和取消怎么工作

执行中收到第二条任务时，会进入同一个 CommandBus。任务管理层会把它当作新的 `new_task` 放进 `task_stack`，先处理新任务，再恢复旧任务。

取消类文本会走同一条通道：

- `cancel_all`：清空任务栈，停止当前链路。
- `cancel_current`：取消栈顶任务，恢复下层任务。
- `pause` / `resume`：暂停或恢复任务栈。

这不是硬件级强杀。当前动作如果本身是阻塞的，系统只能在该动作返回后进入下一次调度，再消费新的中断命令。

### 反思和失败

第三阶段或执行阶段出错时，任务会先标成 `failed`，并带上 `failure_layer`。

如果开启了 reflection：

- `failure_layer=understanding` 会回到理解重试。
- `failure_layer=planning` 会回到规划重试。
- `failure_layer=execution` 可以回到执行重试，必要时也会退回规划。

如果同一层反复失败，反思层会逐级升级，直到超过 `max_retries` 并停止自动修复。

当前没有一个单独的全局 `impossible` 标志。也就是说，框架会根据失败层和重试次数尽量修复；如果你想显式标记“本身不可完成”，需要再加一层独立状态或策略。

### 标准启动方式

正式 ROS / 前端联调用这个：

```bash
/data/zmy/envs/ouragent/bin/python main.py
```

带实例号时：

```bash
/data/zmy/envs/ouragent/bin/python main.py 5001
```

CLI 调试仍然用这个：

```bash
/data/zmy/envs/ouragent/bin/python scripts/run_agent.py --task '你的任务' --execute
```

`scripts/run_agent.py` 是唯一 CLI 入口（参数解析 + 调引擎），终端渲染在 `scripts/renderer.py`（原 `run_console.py` 已并入）。

## 日志与前端出站链路（`/agent_log`）

上一节讲的是“前端把文本命令**发进来**”。这一节讲反方向：框架把运行时的控制台输出/关键日志**推回前端**，让 UI 能实时显示 agent 状态。这条出站链路现在已经和 `adapters/agent_log_client.py` 完整适配。

### 链路组成（谁负责什么）

- `interfaces/services.py` 里的 `LogSink`：端口协议 `emit(text) -> (ok, msg)`。
- `adapters/agent_log_client.py` 里的 `AgentLogSender`：`LogSink` 的实现，HTTP POST JSON `{"text": ...}` 到前端 `http://<host>:<port>/agent_log`。
- `adapters/logging_handler.py` 里的 `LogSinkHandler`：把一条 logging record 转成 `emit(text)`。
- `agent_runtime/logging_setup.py` 里的中央装配 `configure_logging(...)`：
  - root logger 挂 stderr + 滚动文件（`logs/ouragent.log`，10MB × 5 份）。
  - 专用 `ouragent.console` logger（`propagate=False`）负责把控制台内容镜像出去；一旦检测到前端端口，就加一对**非阻塞**的 `QueueHandler` / `QueueListener`，由后台线程把每条记录交给 `AgentLogSender` POST 出去，**不阻塞 agent 主流程**。
  - `console_mirror()` 上下文管理器：把 `sys.stdout` 换成一个 tee，既照常打印到终端，又按“整行”转发到 `ouragent.console`（从而进前端）。
  - `shutdown_logging()`：退出前 flush 并 join 后台 `QueueListener`，保证队列里的日志都发完再退出。

### 什么时候才真的往前端发

只有设置了前端端口才会启用出站 HTTP，开关是环境变量 `GENESIS_WEB_PORT`：

- `main.py`（正式 ROS/前端入口）会按实例号自动设置 `GENESIS_WEB_PORT`（见 `main.py:46`），再 `configure_logging(...)` + `console_mirror()`。所以**正式联调时这条链路默认就是开的**。
- CLI（`scripts/run_agent.py`）默认不设这个变量，只写本地 `logs/ouragent.log` + 打到终端，不会往前端发。想在 CLI 下也测出站链路，启动前手动 `export GENESIS_WEB_PORT=<前端端口>` 即可。
- 没有前端端口时，`configure_logging` 只装 stderr + 文件 handler，`AgentLogSender` 完全不参与，也不会有任何多余的网络请求。

### 本次适配时发现并修掉的两个坑

1. **代理把 localhost 请求带偏了**：本机 `http_proxy` / `https_proxy` 指向 `127.0.0.1:7899` 时，`urllib` 会把发往前端的 `localhost` POST 也塞进代理，结果前端一条都收不到（静默失败）。已在 `AgentLogSender` 里用 `urllib.request.build_opener(ProxyHandler({}))` 强制绕过代理，前端才真正收到日志。
2. **`renderer.py` 少了一个 import**：`scripts/renderer.py` 计划审计（Evaluator）的熔断分支用了 `get_config` 却没导入，会抛 `NameError` 让整轮渲染崩溃。已补 `from config import get_config`。

（注：LLM 调用本身走的是 `httpx` + `trust_env=False`，天生绕过代理，不受第 1 条影响；被代理坑到的只有 `urllib` 那条出站日志链路。）

### 怎么在本机自测这条出站链路（不依赖真前端）

前端和 ROS 那边由你们自己联调；本机可以用一个 mock 前端，验证“agent 到底有没有把日志 POST 出去”。

1. 起一个最简 HTTP 服务，把收到的 `/agent_log` body 落盘（`GET` 当健康检查）：

```python
# mock_frontend.py：POST /agent_log 落盘，GET 当健康检查
import http.server, json, sys
OUT = "/tmp/mock_frontend_agentlog.txt"
open(OUT, "w").close()
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0) or 0)
        body = self.rfile.read(n) if n else b""
        try: txt = json.loads(body.decode("utf-8", "replace")).get("text", "")
        except Exception: txt = "<non-json>"
        open(OUT, "a", encoding="utf-8").write(txt + "\n")
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
    def log_message(self, *a): pass
if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5599
    http.server.HTTPServer(("127.0.0.1", port), H).serve_forever()
```

2. 起 mock 前端，设 `GENESIS_WEB_PORT` 指向它，再正常跑一次 `切土豆` plan-only：

```bash
cd /data/zmy/OurAgent-he1
export OURAGENT_WORKSPACE_ROOT=/data/zmy
PY=/data/zmy/envs/ouragent/bin/python

# 起 mock 前端（后台）
nohup "$PY" mock_frontend.py 5599 >/tmp/mock_frontend.stdout 2>&1 &
# 等它能连上
for i in $(seq 1 25); do curl --noproxy '*' -s --max-time 1 -o /dev/null http://127.0.0.1:5599/health && break; sleep 0.2; done

# 打开出站链路（GENESIS_WEB_PORT）跑一次规划
GENESIS_WEB_PORT=5599 "$PY" scripts/run_agent.py --task '把土豆切成片' --once
```

3. 跑完看 mock 落盘的行数——有内容就说明出站链路通了：

```bash
wc -l < /tmp/mock_frontend_agentlog.txt   # >0 即代表前端确实收到了日志
```

实测结论(本机 mock 前端 + 18002 plan-only 真跑一次):mock 前端收到 **169 行**,完整覆盖了理解层实体、5 轮 sandbox 物理审计(依次拦下了单臂约束、工具依赖、卫生前置、位置前置)以及逐步动作序列,最终因累计 10 次物理拦截触发熔断、转入反思——**重点是整个过程的日志都原样 POST 到了 `/agent_log`**,确认出站链路在真实框架里可用。(这一跑没有产出"通过"的锁定计划,而是走到熔断,那是规划收敛的问题,不是日志/出站链路的问题。)

### 后台日志在哪看

无论连不连前端，后台日志都会写到：

```
/data/zmy/OurAgent-he1/logs/ouragent.log
```

滚动策略 10MB × 5 份。想实时跟：

```bash
tail -f /data/zmy/OurAgent-he1/logs/ouragent.log
```

## 怎么用控制台

先切到仓库根目录：

```bash
cd /data/zmy/OurAgent-he1
export OURAGENT_WORKSPACE_ROOT=/data/zmy
```

### 只跑理解 + 规划

```bash
/data/zmy/envs/ouragent/bin/python scripts/run_agent.py --task '把土豆切成片' --once
```

说明：

- `--task` 把第一条任务字符串直接注入控制台
- `--once` 处理完第一轮就退出，适合脚本调用
- 这是默认的 `plan_only` 模式，不会继续执行动作

### 跑到执行层

```bash
/data/zmy/envs/ouragent/bin/python scripts/run_agent.py --task '把土豆切成片' --execute
```

说明：

- `--execute` 会关闭 `plan_only`
- 规划通过后会继续进入执行层
- 如果你只想看理解和 todo_list，不要加 `--execute`

### 外部中断 / 插单

CLI 调试时，也可以直接用同一条启动命令模拟这个行为。第一个进程启动主任务：

```bash
/data/zmy/envs/ouragent/bin/python scripts/run_agent.py --task '去拿土豆' --execute
```

它还在执行或休眠监听时，第二个终端继续运行：

```bash
/data/zmy/envs/ouragent/bin/python scripts/run_agent.py --task '切番茄' --execute
```

第二个进程会检测到已登记的 runtime，把 `切番茄` 投递为 `new_task` 后退出；第一个进程里的任务管理层负责中断、压栈、恢复。

手工发控制命令仍然可以用：

```bash
/data/zmy/envs/ouragent/bin/python scripts/send_command.py --kind cancel_all '不要做了'
```

常见 `kind`：

- `new_task`：插入新任务；执行完后恢复原任务栈。
- `cancel_all`：清空任务栈并停止。
- `cancel_current`：取消栈顶任务，恢复下面的任务。
- `pause` / `resume`：暂停或恢复已保留的任务栈。

本机多进程默认通道是 `/tmp/ouragent_commands.jsonl`，也可以用 `OURAGENT_COMMAND_FILE` 环境变量覆盖。正常使用不需要传 `--command-file`；只有同时跑多个 agent 实例时才需要显式区分通道。

ROS 文本服务接收逻辑见上面的正式链路说明；它收到 `TextCommand.command` 后会进入同一个 CommandBus，任务管理层只消费统一的命令，不依赖 ROS 版本。

### 纯交互

```bash
/data/zmy/envs/ouragent/bin/python scripts/run_agent.py
```

说明：

- 先读 stdin 里的第一条输入
- 之后按控制台提示继续输入

## 环境复原

当前控制台不是“每个任务自动回到初始场景”的模式。

- `agent_runtime/engine.py` 只在启动时调用一次 `reset_runtime_from_initial()`。
- 同一个控制台会话里，后续新任务会继承上一次已经被执行修改过的 runtime scene。
- `config/scene_state.py` 里有 `snapshot_scene()` / `restore_scene()` / `reset_runtime_from_initial()` 这组接口，但默认没有接到任务结束自动回滚。
- `Slice` 这类技能会真实改变环境状态，比如把刀弄脏，所以如果你想复原，就必须显式追加 cleanup 步骤。

现在可用的解决法有三种：

1. 每次 demo 重新启动控制台。
2. 在任务结束后显式调用 `reset_runtime_from_initial()` 或 `restore_scene(snapshot)`。
3. 如果你要让模型自己收尾，就把“归位、清洁、关门、恢复现场”写进任务目标或规则里。

benchmark 侧已经有更强的恢复链路，比如 `state_diff_audit` 的修复分支和 `state_recovery`，但那不是 agent runtime 的默认路径。

## 正式 benchmark 怎么跑

正式入口是各数据集自己的 `framework/code/run.py`，不要直接跑 `launcher.py` 或 `_case_worker.py`。

通用形式：

```bash
/data/zmy/envs/ouragent/bin/python benchmark/<paper>/<dataset>/framework/code/run.py \
  --run-name <run_name> \
  --expected-count <count> \
  --workers <n> \
  --launch-shards 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key
```

常见端口：

- `18003` -> `Qwen3.6-27B`
- `18004` -> `Qwen3.5-9B`
- `8005` -> `Qwen3.5-9B-alfred`

一个 EAI VirtualHome 示例：

```bash
/data/zmy/envs/ouragent/bin/python benchmark/eai/virtualhome/framework/code/run.py \
  --run-name eai_virtualhome_full_example \
  --expected-count 342 \
  --workers 1 \
  --launch-shards 1 \
  --ports 18003 \
  --api-model Qwen3.6-27B \
  --api-key qwen-local-key
```

## 你问的字符串注入

已实现。

实现方式不是改死文件常量，而是直接用命令行参数：

```bash
--task '你的第一条任务字符串'
```

内部会把它传给 `run_engine(initial_instruction=args.task, ...)`，作为第一条输入使用。

如果你要的是“从环境变量自动读字符串”，那不是当前实现；现在支持的是 CLI 注入。
