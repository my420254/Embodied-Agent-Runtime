import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from adapters.command_bus import (
    JsonlInterruptBus,
    default_interrupt_command_file,
    publish_interrupt_command,
)


def _payload_from_args(args: argparse.Namespace) -> object:
    if args.json_payload:
        try:
            return json.loads(args.json_payload)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"--json 不是合法 JSON: {exc}") from exc
    text = " ".join(args.command).strip()
    if not text:
        raise SystemExit("请提供一条命令文本，或使用 --json 传结构化命令")
    if args.kind:
        return {"kind": args.kind, "text": text}
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description="Send an interrupt command to OurAgent")
    parser.add_argument("command", nargs="*", help="命令文本，例如：先去拿杯子")
    parser.add_argument(
        "--kind",
        default="",
        help="结构化命令类型，例如 new_task / cancel_all / cancel_current / pause / resume",
    )
    parser.add_argument("--json", dest="json_payload", default="", help="完整 JSON 命令载荷")
    parser.add_argument(
        "--command-file",
        default="",
        help="高级选项：覆盖默认命令通道文件",
    )
    args = parser.parse_args()

    path = Path(args.command_file).expanduser() if args.command_file else default_interrupt_command_file()
    bus = JsonlInterruptBus(path.resolve(), start_at_end=False)
    command = publish_interrupt_command(_payload_from_args(args), bus)
    print(f"[CommandBus] 已写入命令: {command.get('kind')} | {command.get('text') or command.get('intent')}")


if __name__ == "__main__":
    main()
