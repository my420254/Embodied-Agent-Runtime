import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from adapters.command_bus import (  # noqa: E402 - support direct script execution
    JsonlInterruptBus,
    default_interrupt_command_file,
    publish_interrupt_command,
)
from agent_runtime.process_registry import find_active_runtime  # noqa: E402
from agent_runtime.engine import run_engine  # noqa: E402
from agent_runtime.logging_setup import configure_logging, console_mirror  # noqa: E402
from scripts.renderer import print_banner, print_divider, render_stream  # noqa: E402

# 主程序 (Terminal Shell)
# =====================================================================
def run_system(
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
):
    run_engine(
        plan_only=plan_only,
        initial_instruction=initial_instruction,
        once=once,
        command_file=command_file,
        interrupt_prompt=interrupt_prompt,
        listen=listen,
        auto_accept_feedback=auto_accept_feedback,
        register_runtime=register_runtime,
        ready_event=ready_event,
        render_stream=render_stream,
        print_banner=print_banner,
        print_divider=print_divider,
        task_source="interactive_console",
    )

def _command_payload_from_args(args: argparse.Namespace) -> object:
    if args.send_command_json:
        try:
            return json.loads(args.send_command_json)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"--send-command-json 不是合法 JSON: {exc}") from exc
    return args.send_command


def _send_command_and_exit(args: argparse.Namespace) -> None:
    if args.send_command and args.send_command_json:
        raise SystemExit("--send-command 与 --send-command-json 只能选择一个")
    payload = _command_payload_from_args(args)
    command_file = Path(args.command_file).expanduser() if args.command_file else default_interrupt_command_file()
    bus = JsonlInterruptBus(command_file.resolve(), start_at_end=False)
    command = publish_interrupt_command(payload, bus)
    print(f"[CommandBus] 已写入命令: {command.get('kind')} | {command.get('text') or command.get('intent')}")


def _forward_task_to_active_runtime(args: argparse.Namespace) -> bool:
    if not args.task or not args.execute or args.once or args.force_new_runtime:
        return False
    runtime = find_active_runtime()
    if runtime is None:
        return False

    requested_command_file = (
        Path(args.command_file).expanduser().resolve()
        if args.command_file
        else default_interrupt_command_file().resolve()
    )
    if runtime.command_file.resolve() != requested_command_file:
        return False

    bus = JsonlInterruptBus(runtime.command_file.resolve(), start_at_end=False)
    command = publish_interrupt_command({"kind": "new_task", "text": args.task}, bus)
    print(
        "[Runtime] 已检测到正在运行的 OurAgent 执行进程 "
        f"(pid={runtime.pid})，本次 --task 已作为新任务投递: "
        f"{command.get('text')}"
    )
    return True


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="OurAgent interactive console")
    parser.add_argument(
        "--task",
        type=str,
        default=None,
        help="启动时直接注入第一条任务指令字符串",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="规划完成后继续进入执行模块；默认只输出经过审计的 todo_list",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="只处理第一条任务后退出，适合外部脚本调用",
    )
    parser.add_argument(
        "--command-file",
        type=str,
        default=None,
        help="高级选项：指定外部中断命令 JSONL 文件；默认使用 OURAGENT_COMMAND_FILE 或 /tmp/ouragent_commands.jsonl",
    )
    parser.add_argument(
        "--send-command",
        type=str,
        default=None,
        help="向默认 CommandBus 通道写入一条文本中断命令后退出",
    )
    parser.add_argument(
        "--send-command-json",
        type=str,
        default=None,
        help="向默认 CommandBus 通道写入一条结构化 JSON 中断命令后退出",
    )
    parser.add_argument(
        "--no-interrupt-prompt",
        action="store_true",
        help="兼容旧参数；现在执行模式默认不阻塞等待控制台中断输入",
    )
    parser.add_argument(
        "--interrupt-prompt",
        action="store_true",
        help="开启动作间隙的控制台中断输入提示；一般前端/ROS 控制时不需要",
    )
    parser.add_argument(
        "--force-new-runtime",
        action="store_true",
        help="即使已有执行进程，也强制启动一个新的独立 runtime 进程",
    )
    args = parser.parse_args(argv)
    configure_logging(frontend_port=os.environ.get("GENESIS_WEB_PORT"))
    if args.send_command or args.send_command_json:
        _send_command_and_exit(args)
        raise SystemExit(0)
    if _forward_task_to_active_runtime(args):
        raise SystemExit(0)
    with console_mirror():
        run_system(
            plan_only=not args.execute,
            initial_instruction=args.task,
            once=args.once,
            command_file=args.command_file,
            interrupt_prompt=args.interrupt_prompt and not args.no_interrupt_prompt,
        )


if __name__ == "__main__":
    main()
