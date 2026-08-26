from __future__ import annotations

import os
from typing import Any

try:
    import rclpy
    from rclpy.node import Node
except ImportError:  # pragma: no cover - ROS is optional in non-ROS environments
    rclpy = None
    Node = object  # type: ignore[assignment]

try:
    from genesis_msgs.srv import TextCommand
except ImportError:  # pragma: no cover - genesis_msgs is only present after sourcing ROS workspace
    TextCommand = None

from adapters.ros_bridge import publish_ros_interrupt_command


RECEIVED_TEXT_COMMANDS: list[str] = []


def instance_namespace() -> str:
    """Resolve the genesis instance suffix used by the TextCommand service."""
    inst = os.environ.get("GENESIS_INSTANCE", "").strip()
    if inst:
        return inst
    port = os.environ.get("GENESIS_WEB_PORT", "5000").strip()
    return "" if not port or port == "5000" else port


def text_command_service_name() -> str:
    ns = instance_namespace()
    return f"/genesis_arm{('_' + ns) if ns else ''}/send_text_command"


def apply_ros_domain_id() -> None:
    """Default ROS_DOMAIN_ID to the genesis instance mapping when unset."""
    if os.environ.get("ROS_DOMAIN_ID"):
        return
    try:
        port = int(instance_namespace() or "5000")
        os.environ["ROS_DOMAIN_ID"] = (
            str(port - 5000) if 5000 <= port <= 5101 else str(port % 102)
        )
    except ValueError:
        os.environ["ROS_DOMAIN_ID"] = "0"


def publish_text_command(command: str) -> dict[str, Any]:
    return publish_ros_interrupt_command(command)


class TextCommandReceiver(Node):  # type: ignore[misc]
    """ROS service node that forwards text commands into the OurAgent command bus."""

    def __init__(self) -> None:
        if rclpy is None:
            raise RuntimeError("无法导入 rclpy：请先 source ROS 环境。")
        if TextCommand is None:
            raise RuntimeError(
                "无法导入 genesis_msgs.srv.TextCommand：请先 source 包含 "
                "genesis_msgs 的 ROS 工作区（如 genesis_test/install/setup.bash）"
            )
        super().__init__("text_command_receiver")
        service_name = text_command_service_name()
        self._srv = self.create_service(TextCommand, service_name, self._on_command)
        self.get_logger().info(
            f"文本命令接收服务已就绪：{service_name} "
            f"（ROS_DOMAIN_ID={os.environ.get('ROS_DOMAIN_ID', '默认')}）"
        )

    def _on_command(self, request, response):
        cmd = (request.command or "").strip()
        if cmd:
            RECEIVED_TEXT_COMMANDS.append(cmd)
            published = publish_text_command(cmd)
            self.get_logger().info(
                "ROS 文本指令已投递到 CommandBus: "
                f"{published.get('kind')} | {published.get('text') or published.get('intent')}"
            )

        response.received = True
        response.message = cmd
        self.get_logger().info(f"收到文本指令[{len(RECEIVED_TEXT_COMMANDS)}]: {cmd!r}")
        return response
