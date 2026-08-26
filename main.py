from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from adapters.ros_text_command_service import (
    RECEIVED_TEXT_COMMANDS,
    TextCommandReceiver,
    apply_ros_domain_id,
    rclpy,
)
from agent_runtime.service import AgentRuntimeThread


def _parse_main_args(argv: list[str]) -> tuple[list[str], bool, bool, Path | None]:
    rest = []
    enable_agent_runtime = True
    plan_only = False
    command_file: Path | None = None
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--no-agent-runtime":
            enable_agent_runtime = False
            index += 1
            continue
        if arg == "--plan-only":
            plan_only = True
            index += 1
            continue
        if arg == "--command-file":
            if index + 1 >= len(argv):
                raise SystemExit("--command-file 需要一个路径参数")
            command_file = Path(argv[index + 1]).expanduser()
            index += 2
            continue
        if (
            not os.environ.get("GENESIS_WEB_PORT")
            and not os.environ.get("GENESIS_INSTANCE")
            and re.fullmatch(r"\d{2,5}", arg)
        ):
            os.environ["GENESIS_WEB_PORT"] = arg
            index += 1
            continue
        rest.append(arg)
        index += 1
    return rest, enable_agent_runtime, plan_only, command_file


def main(argv=None) -> None:
    # 用法：python3 main.py 5001 -> 服务 /genesis_arm_5001/send_text_command
    argv = list(sys.argv[1:] if argv is None else argv)
    rest, enable_agent_runtime, plan_only, command_file = _parse_main_args(argv)

    apply_ros_domain_id()
    if rclpy is None:
        raise RuntimeError("无法导入 rclpy：请先 source ROS 环境。")

    runtime_thread = None
    if enable_agent_runtime:
        runtime_thread = AgentRuntimeThread(
            plan_only=plan_only,
            command_file=command_file,
            auto_accept_feedback=True,
        )
        runtime_thread.start()

    rclpy.init(args=rest if rest else None)
    node = TextCommandReceiver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

    del runtime_thread
    print(f"[main] 共收到 {len(RECEIVED_TEXT_COMMANDS)} 条文本指令")


if __name__ == "__main__":
    main()
