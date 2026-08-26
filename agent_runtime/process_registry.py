from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_DEFAULT_STATUS_FILE = "/tmp/ouragent_runtime.json"


@dataclass(frozen=True)
class RuntimeProcess:
    pid: int
    command_file: Path
    status_file: Path


def default_runtime_status_file() -> Path:
    return Path(os.environ.get("OURAGENT_RUNTIME_STATUS_FILE", _DEFAULT_STATUS_FILE)).expanduser()


def _process_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _read_status(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def find_active_runtime(status_file: str | Path | None = None) -> RuntimeProcess | None:
    path = Path(status_file).expanduser() if status_file else default_runtime_status_file()
    data = _read_status(path)
    try:
        pid = int(data.get("pid") or 0)
    except (TypeError, ValueError):
        pid = 0
    command_file = str(data.get("command_file") or "").strip()
    if not pid or not command_file or not _process_is_alive(pid):
        return None
    return RuntimeProcess(pid=pid, command_file=Path(command_file).expanduser(), status_file=path)


def register_runtime_process(
    command_file: str | Path,
    *,
    status_file: str | Path | None = None,
    pid: int | None = None,
) -> RuntimeProcess:
    path = Path(status_file).expanduser() if status_file else default_runtime_status_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    command_path = Path(command_file).expanduser()
    runtime = RuntimeProcess(
        pid=int(pid or os.getpid()),
        command_file=command_path,
        status_file=path,
    )
    payload = {
        "pid": runtime.pid,
        "command_file": str(command_path),
    }
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp_path.replace(path)
    return runtime


def clear_runtime_process(
    *,
    status_file: str | Path | None = None,
    pid: int | None = None,
) -> None:
    path = Path(status_file).expanduser() if status_file else default_runtime_status_file()
    data = _read_status(path)
    if pid is not None:
        try:
            recorded_pid = int(data.get("pid") or 0)
        except (TypeError, ValueError):
            recorded_pid = 0
        if recorded_pid and recorded_pid != pid:
            return
    try:
        path.unlink()
    except FileNotFoundError:
        return
