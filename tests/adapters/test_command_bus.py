from types import SimpleNamespace

import pytest

from adapters.command_bus import (
    InMemoryInterruptBus,
    InterruptController,
    JsonlInterruptBus,
    configure_default_interrupt_bus,
    default_interrupt_command_file,
    normalize_interrupt_command,
    poll_interrupt_command,
)
from adapters.ros_bridge import publish_ros_interrupt_command


@pytest.fixture(autouse=True)
def reset_interrupt_bus():
    configure_default_interrupt_bus(InMemoryInterruptBus())
    yield
    configure_default_interrupt_bus(InMemoryInterruptBus())


def test_normalize_interrupt_text_commands():
    assert normalize_interrupt_command("先去拿杯子", source="test")["kind"] == "new_task"
    assert normalize_interrupt_command("不要做了", source="test")["kind"] == "cancel_all"
    assert normalize_interrupt_command("暂停一下", source="test")["kind"] == "pause"
    assert normalize_interrupt_command("继续", source="test")["kind"] == "resume"


def test_default_interrupt_command_file_can_be_overridden(monkeypatch):
    monkeypatch.setenv("OURAGENT_COMMAND_FILE", "/tmp/custom_ouragent_commands.jsonl")

    assert str(default_interrupt_command_file()) == "/tmp/custom_ouragent_commands.jsonl"


def test_jsonl_bus_ignores_stale_lines_and_reads_appended_commands(tmp_path):
    path = tmp_path / "commands.jsonl"
    path.write_text("旧命令\n", encoding="utf-8")

    bus = JsonlInterruptBus(path)

    assert bus.poll() is None
    bus.publish("先去拿杯子")

    command = bus.poll()
    assert command is not None
    assert command["kind"] == "new_task"
    assert command["text"] == "先去拿杯子"


def test_interrupt_controller_wraps_injectable_bus():
    controller = InterruptController()

    controller.publish({"kind": "pause", "text": "暂停"})

    assert controller.poll()["kind"] == "pause"


def test_ros_interrupt_callback_payload_goes_to_command_bus():
    command = publish_ros_interrupt_command(SimpleNamespace(data='{"kind":"pause","text":"暂停"}'))

    assert command["kind"] == "pause"
    assert poll_interrupt_command()["kind"] == "pause"
