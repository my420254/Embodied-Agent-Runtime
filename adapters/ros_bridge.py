import json
from typing import Any

from adapters.command_bus import publish_interrupt_command


class ROSBridgeClient:
    """No-op ROS bridge adapter used until a real hardware transport is wired in."""

    def send_to_hardware(self, node_name: str, topic: str, payload: dict) -> tuple[bool, str]:
        return True, ""


_DEFAULT_CLIENT = ROSBridgeClient()


def get_ros_bridge() -> ROSBridgeClient:
    return _DEFAULT_CLIENT


def publish_ros_interrupt_command(message: Any) -> dict:
    payload = getattr(message, "data", message)
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")
    if isinstance(payload, str):
        text = payload.strip()
        if text.startswith("{"):
            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                payload = text
        else:
            payload = text
    return publish_interrupt_command(payload)
