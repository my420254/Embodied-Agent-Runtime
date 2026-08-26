import os

from agent_runtime.process_registry import (
    clear_runtime_process,
    find_active_runtime,
    register_runtime_process,
)


def test_register_find_and_clear_runtime_process(tmp_path, monkeypatch):
    status_file = tmp_path / "runtime.json"
    command_file = tmp_path / "commands.jsonl"
    monkeypatch.setenv("OURAGENT_RUNTIME_STATUS_FILE", str(status_file))

    runtime = register_runtime_process(command_file, pid=os.getpid())

    active = find_active_runtime()
    assert active is not None
    assert active.pid == runtime.pid
    assert active.command_file == command_file

    clear_runtime_process(pid=os.getpid())

    assert find_active_runtime() is None


def test_stale_runtime_process_is_ignored(tmp_path, monkeypatch):
    status_file = tmp_path / "runtime.json"
    monkeypatch.setenv("OURAGENT_RUNTIME_STATUS_FILE", str(status_file))
    status_file.write_text('{"pid": 0, "command_file": "/tmp/commands.jsonl"}\n', encoding="utf-8")

    assert find_active_runtime() is None
