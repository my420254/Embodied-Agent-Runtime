from __future__ import annotations

import traceback
from pathlib import Path
from typing import Any, Callable

from langchain_core.messages import HumanMessage

from adapters.command_bus import (
    JsonlInterruptBus,
    configure_default_interrupt_bus,
    default_interrupt_command_file,
    wait_for_interrupt_command,
)
from agent_runtime.process_registry import clear_runtime_process, register_runtime_process
from config.scene_state import INITIAL_SCENE_FILE, get_runtime_session, reset_runtime_from_initial
from domain.scene import flatten_scene, get_all_entity_names_from_scene_data
from graph import build_main_graph
from re_trac import initial_trace_state


RuntimeRenderer = Callable[[list[Any], dict, Any], None]
OutputFn = Callable[[str], None]
InputFn = Callable[[str], str]

# 外部驱动（ROS/前端/CLI CommandBus）模式下，澄清循环允许的最大轮数。
# 超过后放弃当前任务并回到空闲等待，避免“LLM 不可达 -> 每次理解都失败 ->
# 每次都要求补全”的无限循环。
MAX_CLARIFICATION_ATTEMPTS = 3


def _robot_holding_from_scene(scene: dict) -> str:
    holding = scene.get("robot_inventory")
    if isinstance(holding, list):
        return "; ".join(str(item) for item in holding if str(item).strip()) or "空"
    return str(holding) if holding else "空"


def current_runtime_env_state() -> dict:
    scene = get_runtime_session()
    return {
        "robot_location": scene.get("robot_location", "客厅"),
        "robot_holding": _robot_holding_from_scene(scene),
    }


def current_runtime_scene_context(*, task_source: str = "runtime") -> dict:
    scene = get_runtime_session()
    environment = flatten_scene(scene)
    entity_catalog = sorted(get_all_entity_names_from_scene_data(scene))
    return {
        "environment": environment,
        "entity_catalog": entity_catalog,
        "task_context": {
            "source": task_source,
            "scene_name": scene.get("scene_name", ""),
            "environment_source": f"runtime_scene:{INITIAL_SCENE_FILE}",
            "available_entities": entity_catalog,
        },
        "environment_source": {
            "builder": "agent_runtime.engine.current_runtime_scene_context",
            "scene": INITIAL_SCENE_FILE,
        },
        "env_state": {
            "robot_location": scene.get("robot_location", "客厅"),
            "robot_holding": _robot_holding_from_scene(scene),
        },
    }


def build_runtime_input(
    user_input: str,
    *,
    plan_only: bool = True,
    allow_interrupt_input: bool = True,
    task_source: str = "runtime",
) -> dict:
    scene_context = current_runtime_scene_context(task_source=task_source)
    return {
        "messages": [HumanMessage(content=user_input)],
        "raw_instruction": user_input,
        "original_instruction": user_input,
        "task_source_text": user_input,
        "task_input_payload": {
            "source": task_source,
            "llm_prompt": user_input,
            "plan_only": plan_only,
        },
        "is_complete": False,
        "clarification_question": "",
        "structured_task": {},
        "todo_list": [],
        "task_stack": [],
        "waiting_for_evaluation": False,
        "human_feedback": "",
        "feature_flags": {
            "allow_clarification": True,
            "plan_only": plan_only,
        },
        "execution_status": "running",
        "allow_interrupt_input": allow_interrupt_input,
        "iteration_count": 0,
        "reflection_retry_count": 0,
        "interrupt_signal": None,
        "failure_layer": "tool",
        **scene_context,
        **initial_trace_state(),
    }


def runtime_config(session_index: int) -> dict:
    return {"configurable": {"thread_id": f"runtime_session_{session_index:03d}"}}


def command_task_text(command: dict | None) -> str:
    if not isinstance(command, dict):
        return ""
    kind = str(command.get("kind") or "").strip()
    if kind in {"cancel_all", "cancel_current", "pause", "resume"}:
        return ""
    return str(command.get("text") or command.get("intent") or "").strip()


def _default_banner(title: str, output_fn: OutputFn) -> None:
    output_fn("\n" + "=" * 70)
    output_fn(title)
    output_fn("=" * 70)


def _default_divider(output_fn: OutputFn, char: str = "-") -> None:
    output_fn(char * 70)


def _wait_for_idle_task_command(output_fn: OutputFn) -> str:
    while True:
        output_fn("\n[系统进程] 运行器空闲，等待 ROS/前端/CLI 任务命令。")
        command = wait_for_interrupt_command()
        task_text = command_task_text(command)
        if task_text:
            return task_text
        label = (command or {}).get("kind") if isinstance(command, dict) else command
        output_fn(f"[CommandBus] 空闲状态忽略控制命令: {label}")


def run_engine(
    *,
    plan_only: bool = True,
    initial_instruction: str | None = None,
    once: bool = False,
    command_file: str | None = None,
    interrupt_prompt: bool = False,
    listen: bool = False,
    auto_accept_feedback: bool = False,
    register_runtime: bool = True,
    ready_event=None,
    render_stream: RuntimeRenderer | None = None,
    print_banner: Callable[[str], None] | None = None,
    print_divider: Callable[[str], None] | None = None,
    input_fn: InputFn = input,
    output_fn: OutputFn = print,
    task_source: str = "runtime",
    app: Any | None = None,
) -> None:
    """Run the long-lived LangGraph control loop.

    ROS, CLI, and future API entrypoints should call this runtime instead of
    embedding their own app.stream loop.
    """

    graph_app = app or build_main_graph()
    title = (
        "具身智能代理 (Agent) 系统终端 | 只规划模式"
        if plan_only
        else "具身智能代理 (Agent) 系统终端 | 控制台与状态监视器"
    )
    if print_banner is not None:
        print_banner(title)
    else:
        _default_banner(title, output_fn)

    external_control_path = Path(command_file).expanduser() if command_file else None
    if external_control_path is None and (listen or not plan_only):
        external_control_path = default_interrupt_command_file()
    if external_control_path is not None:
        path = external_control_path.resolve()
        configure_default_interrupt_bus(JsonlInterruptBus(path))
        output_fn(f"[CommandBus] 外部中断命令文件: {path}")
        output_fn("[CommandBus] ROS/前端/CLI 新任务会写入同一条默认通道。")

    reset_runtime_from_initial()

    registered_runtime = None
    if register_runtime and external_control_path is not None and not plan_only:
        registered_runtime = register_runtime_process(external_control_path.resolve())
        output_fn(f"[Runtime] 当前执行进程已登记: pid={registered_runtime.pid}")
    if ready_event is not None:
        ready_event.set()

    source_for_first_task = task_source
    try:
        if initial_instruction is not None:
            user_input = str(initial_instruction).strip()
            output_fn(f"\n[控制台输入] >>> {user_input}")
            source_for_first_task = task_source if task_source != "runtime" else "cli"
        elif listen:
            user_input = _wait_for_idle_task_command(output_fn)
            output_fn(f"\n[外部任务] >>> {user_input}")
            source_for_first_task = "command_bus"
        else:
            user_input = input_fn("\n[控制台输入] >>> ").strip()
            source_for_first_task = "interactive_console"
        if user_input.lower() in ("quit", "exit", ""):
            return

        session_index = 1
        config = runtime_config(session_index)
        clarification_attempts = 0
        current_input = build_runtime_input(
            user_input,
            plan_only=plan_only,
            allow_interrupt_input=interrupt_prompt,
            task_source=source_for_first_task,
        )

        if print_divider is not None:
            print_divider("=")
        else:
            _default_divider(output_fn, "=")
        output_fn("[系统进程] 工作流图引擎初始化成功，开始分发指令...\n")

        while True:
            for output in graph_app.stream(current_input, config, subgraphs=True):
                if render_stream is not None:
                    render_stream([output], config, graph_app)

            cur_state = graph_app.get_state(config).values

            if once:
                return

            if cur_state.get("waiting_for_evaluation"):
                if auto_accept_feedback:
                    output_fn("\n[验收结果输入] 常驻运行模式自动确认任务完成。")
                    current_input = {"human_feedback": ""}
                    continue
                user_feedback = input_fn("\n[验收结果输入] >>> ").strip()
                if user_feedback.lower() in ("quit", "exit"):
                    break
                current_input = {"human_feedback": user_feedback}
                continue

            if not cur_state.get("is_complete") and cur_state.get("clarification_question"):
                question = str(cur_state.get("clarification_question") or "").strip() or "指令信息不足，请补充说明。"
                external_mode = bool(
                    external_control_path is not None
                    and (listen or initial_instruction is not None or command_file is not None)
                )
                if external_mode:
                    # 外部驱动（ROS/前端/CLI CommandBus）模式：
                    # 澄清问题不阻塞 stdin，而是打印到日志，并把下一条外部命令当作澄清答案。
                    # 这样即使 LLM 不可达导致反复要求补全，也不会挂死或无限循环。
                    clarification_attempts += 1
                    output_fn(f"\n[指令补全] {question}")
                    if clarification_attempts >= MAX_CLARIFICATION_ATTEMPTS:
                        output_fn(
                            f"[指令补全] 连续 {clarification_attempts} 次未能完成澄清，"
                            "放弃当前任务，回到空闲等待。"
                        )
                        clarification_attempts = 0
                        # 不 continue：落入下方空闲等待逻辑，等一条新的外部命令。
                    else:
                        output_fn(
                            "[CommandBus] 请通过 ROS/前端 或 send_command.py 下发补充命令作为澄清答案。"
                        )
                        command = wait_for_interrupt_command()
                        ans = command_task_text(command)
                        if not ans:
                            # 控制命令（取消/暂停等）或空命令：放弃当前任务。
                            label = (command or {}).get("kind") if isinstance(command, dict) else command
                            output_fn(f"[CommandBus] 澄清等待收到控制命令 {label}，放弃当前任务。")
                            clarification_attempts = 0
                        else:
                            current_input = {"messages": [HumanMessage(content=ans)]}
                            continue
                else:
                    ans = input_fn(f"\n[指令补全] >>> {question}\n").strip()
                    if ans.lower() in ("quit", "exit"):
                        break
                    current_input = {"messages": [HumanMessage(content=ans)]}
                    continue

            has_suspended_task = bool(cur_state.get("task_stack"))
            wait_for_external_idle_command = listen or initial_instruction is not None or command_file is not None
            if external_control_path is not None and (has_suspended_task or wait_for_external_idle_command):
                output_fn("\n[系统进程] 主干工作流已休眠，等待外部 CommandBus 命令。")
                command = wait_for_interrupt_command()
                if not command:
                    continue

                if has_suspended_task:
                    current_input = {
                        "interrupt_signal": command,
                        "execution_status": "running",
                    }
                    continue

                next_cmd = command_task_text(command)
                if not next_cmd:
                    output_fn(f"[CommandBus] 空闲状态忽略控制命令: {command.get('kind')}")
                    continue
                next_source = "command_bus"
            else:
                output_fn("\n[系统进程] 主干工作流已休眠。")
                next_cmd = input_fn("\n[控制台输入] (输入新指令 或 quit 退出) >>> ").strip()
                next_source = "interactive_console"

            if not next_cmd:
                continue
            if next_cmd.lower() in ("quit", "exit"):
                break

            session_index += 1
            config = runtime_config(session_index)
            clarification_attempts = 0
            current_input = build_runtime_input(
                next_cmd,
                plan_only=plan_only,
                allow_interrupt_input=interrupt_prompt,
                task_source=next_source,
            )
            if print_divider is not None:
                print_divider("=")
            else:
                _default_divider(output_fn, "=")
            output_fn("[系统进程] 上下文重置完毕，启动新任务列队...\n")

    except KeyboardInterrupt:
        output_fn("\n\n[系统进程] 捕获中断信号 (SIGINT)，控制台安全关闭。")
    except EOFError:
        output_fn("\n[系统进程] 输入流已结束，控制台安全关闭。")
    except Exception as exc:  # noqa: BLE001
        output_fn(f"\n[内核异常] 发生未处理异常: {exc}")
        traceback.print_exc()
    finally:
        if registered_runtime is not None:
            clear_runtime_process(pid=registered_runtime.pid)
