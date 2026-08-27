from __future__ import annotations

import json
import os
import queue
import threading
import time
from pathlib import Path
from typing import Any, Protocol, runtime_checkable
from uuid import uuid4

from datetime import datetime, timezone


_CANCEL_KEYWORDS = (
    "取消",
    "终止",
    "停止",
    "结束",
    "不要",
    "别做",
    "不用",
    "cancel",
    "stop",
    "terminate",
    "abort",
)

_PAUSE_KEYWORDS = (
    "暂停",
    "等一下",
    "先停",
    "pause",
    "hold",
)

_RESUME_KEYWORDS = (
    "继续",
    "恢复",
    "接着",
    "resume",
    "continue",
)

_CANONICAL_KEYS = {
    "behavior_tree",
    "command_id",
    "created_at",
    "kind",
    "metadata",
    "new_todo_list",
    "source",
    "text",
    "intent",
    "is_cancel",
    "is_cancel_all",
}

_DEFAULT_COMMAND_FILE = "/tmp/ouragent_commands.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _new_command_id() -> str:
    return f"cmd-{uuid4().hex[:12]}"


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _looks_like_cancel(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered or keyword in text for keyword in _CANCEL_KEYWORDS)


def _looks_like_pause(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered or keyword in text for keyword in _PAUSE_KEYWORDS)


def _looks_like_resume(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered or keyword in text for keyword in _RESUME_KEYWORDS)


def _normalize_kind(kind: str, text: str, is_cancel: bool) -> str:
    raw = str(kind or "").strip().lower()
    if raw in {"cancel", "cancel_all", "cancel-all", "stop", "terminate", "abort"}:
        return "cancel_all"
    if raw in {"cancel_current", "pause", "resume"}:
        return raw
    if is_cancel or _looks_like_cancel(text):
        return "cancel_all"
    if _looks_like_pause(text):
        return "pause"
    if _looks_like_resume(text):
        return "resume"
    if raw in {"interrupt", "new_task", "task", "command", "text", "input", ""}:
        if _looks_like_cancel(text):
            return "cancel_all"
        if _looks_like_pause(text):
            return "pause"
        if _looks_like_resume(text):
            return "resume"
        return "new_task"
    return raw


def _as_todo_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(step) for step in value if isinstance(step, dict)]


def _command_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    metadata = payload.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    extra = {
        key: value
        for key, value in payload.items()
        if key not in _CANONICAL_KEYS
    }
    if extra:
        metadata = {**metadata, "extra_payload": extra}
    return metadata


def default_interrupt_command_file() -> Path:
    return Path(os.environ.get("OURAGENT_COMMAND_FILE", _DEFAULT_COMMAND_FILE)).expanduser()


def normalize_interrupt_command(payload: Any, *, source: str = "unknown") -> dict[str, Any]:
    if isinstance(payload, str):
        text = _normalize_text(payload)
        kind = _normalize_kind("", text, False)
        return {
            "command_id": _new_command_id(),
            "kind": kind,
            "text": text,
            "intent": text or ("取消当前任务" if kind == "cancel_all" else "新任务"),
            "source": source,
            "created_at": _now_iso(),
            "new_todo_list": [],
            "behavior_tree": None,
            "is_cancel": kind == "cancel_all",
            "is_cancel_all": kind == "cancel_all",
            "metadata": {},
        }

    if not isinstance(payload, dict):
        raise TypeError(f"interrupt command must be str or dict, got {type(payload)!r}")

    raw = dict(payload)
    text = _normalize_text(
        raw.get("text") or raw.get("intent") or raw.get("instruction") or raw.get("command")
    )
    kind = _normalize_kind(
        str(raw.get("kind") or raw.get("type") or ""),
        text,
        bool(raw.get("is_cancel") or raw.get("is_cancel_all")),
    )
    behavior_tree = raw.get("behavior_tree")
    if not isinstance(behavior_tree, dict):
        behavior_tree = None
    return {
        "command_id": _normalize_text(raw.get("command_id")) or _new_command_id(),
        "kind": kind,
        "text": text,
        "intent": _normalize_text(raw.get("intent")) or text or (
            "取消当前任务" if kind == "cancel_all" else "新任务"
        ),
        "source": _normalize_text(raw.get("source")) or source,
        "created_at": _normalize_text(raw.get("created_at")) or _now_iso(),
        "new_todo_list": _as_todo_list(raw.get("new_todo_list") or raw.get("todo_list")),
        "behavior_tree": behavior_tree,
        "is_cancel": bool(raw.get("is_cancel")) or kind == "cancel_all",
        "is_cancel_all": bool(raw.get("is_cancel_all")) or kind == "cancel_all",
        "metadata": _command_metadata(raw),
    }


@runtime_checkable
class InterruptBus(Protocol):
    supports_prompt_fallback: bool

    def publish(self, command: Any) -> dict[str, Any]:
        ...

    def poll(self) -> dict[str, Any] | None:
        ...

    def wait(self, timeout: float | None = None) -> dict[str, Any] | None:
        ...


class InMemoryInterruptBus:
    supports_prompt_fallback = True

    def __init__(self) -> None:
        self._queue: queue.Queue[dict[str, Any]] = queue.Queue()

    def publish(self, command: Any) -> dict[str, Any]:
        normalized = normalize_interrupt_command(command, source="memory")
        self._queue.put(normalized)
        return normalized

    def poll(self) -> dict[str, Any] | None:
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def wait(self, timeout: float | None = None) -> dict[str, Any] | None:
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None


class JsonlInterruptBus:
    supports_prompt_fallback = False

    def __init__(self, path: str | Path, *, start_at_end: bool = True) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)
        self._lock = threading.Lock()
        self._offset = self.path.stat().st_size if start_at_end else 0

    def publish(self, command: Any) -> dict[str, Any]:
        normalized = normalize_interrupt_command(command, source="jsonl")
        line = json.dumps(normalized, ensure_ascii=False)
        with self._lock:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")
                handle.flush()
        return normalized

    def poll(self) -> dict[str, Any] | None:
        with self._lock:
            if not self.path.exists():
                return None
            size = self.path.stat().st_size
            if size < self._offset:
                self._offset = 0
            with self.path.open("r", encoding="utf-8") as handle:
                handle.seek(self._offset)
                line = handle.readline()
                if not line:
                    self._offset = handle.tell()
                    return None
                self._offset = handle.tell()
        text = line.strip()
        if not text:
            return None
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = text
        return normalize_interrupt_command(payload, source="jsonl")

    def wait(self, timeout: float | None = None) -> dict[str, Any] | None:
        deadline = None if timeout is None else time.monotonic() + max(timeout, 0.0)
        while True:
            command = self.poll()
            if command is not None:
                return command
            if deadline is not None and time.monotonic() >= deadline:
                return None
            time.sleep(0.1)


def _decode_redis_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value


class RedisStreamInterruptBus:
    """Redis Stream based CommandBus for multi-process runtime deployment.

    Redis is optional. The class imports redis-py lazily so the default local
    console path stays dependency-light.
    """

    supports_prompt_fallback = False

    def __init__(
        self,
        redis_url: str | None = None,
        *,
        stream: str | None = None,
        group: str | None = None,
        consumer: str | None = None,
        block_ms: int = 1000,
        max_messages: int = 1,
        client: Any | None = None,
    ) -> None:
        self.stream = stream or os.environ.get("OURAGENT_REDIS_STREAM", "ouragent:commands")
        self.group = group or os.environ.get("OURAGENT_REDIS_GROUP", "ouragent-runtimes")
        self.consumer = consumer or os.environ.get("OURAGENT_REDIS_CONSUMER", f"runtime-{os.getpid()}")
        self.block_ms = max(0, int(block_ms))
        self.max_messages = max(1, int(max_messages))
        self.client = client or self._connect(redis_url)
        self._ensure_group()

    @staticmethod
    def _connect(redis_url: str | None) -> Any:
        try:
            import redis  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "RedisStreamInterruptBus 需要安装 redis-py；"
                "可执行 `pip install redis`，或继续使用默认 Jsonl/InMemory CommandBus。"
            ) from exc
        return redis.Redis.from_url(redis_url or os.environ.get("OURAGENT_REDIS_URL", "redis://localhost:6379/0"))

    def _ensure_group(self) -> None:
        try:
            self.client.xgroup_create(self.stream, self.group, id="0", mkstream=True)
        except Exception as exc:
            if "BUSYGROUP" not in str(exc):
                raise

    def publish(self, command: Any) -> dict[str, Any]:
        normalized = normalize_interrupt_command(command, source="redis")
        payload = json.dumps(normalized, ensure_ascii=False, separators=(",", ":"))
        message_id = self.client.xadd(self.stream, {"payload": payload})
        metadata = dict(normalized.get("metadata") or {})
        metadata["redis_stream_id"] = str(_decode_redis_value(message_id))
        normalized["metadata"] = metadata
        return normalized

    def _parse_entry(self, entry: Any) -> dict[str, Any] | None:
        try:
            message_id, fields = entry
        except (TypeError, ValueError):
            return None
        decoded_fields = {
            str(_decode_redis_value(key)): _decode_redis_value(value)
            for key, value in dict(fields).items()
        }
        raw_payload = decoded_fields.get("payload") or decoded_fields.get("command") or ""
        try:
            payload = json.loads(str(raw_payload))
        except json.JSONDecodeError:
            payload = str(raw_payload)
        command = normalize_interrupt_command(payload, source="redis")
        metadata = dict(command.get("metadata") or {})
        metadata["redis_stream_id"] = str(_decode_redis_value(message_id))
        command["metadata"] = metadata
        return command

    def poll(self) -> dict[str, Any] | None:
        response = self.client.xreadgroup(
            self.group,
            self.consumer,
            {self.stream: ">"},
            count=self.max_messages,
            block=0,
        )
        for _stream_name, entries in response or []:
            for entry in entries:
                command = self._parse_entry(entry)
                if command is not None:
                    return command
        return None

    def wait(self, timeout: float | None = None) -> dict[str, Any] | None:
        deadline = None if timeout is None else time.monotonic() + max(timeout, 0.0)
        while True:
            command = self.poll()
            if command is not None:
                return command
            if deadline is not None and time.monotonic() >= deadline:
                return None
            time.sleep(min(self.block_ms / 1000.0 if self.block_ms else 0.1, 0.5))

    def ack(self, command: dict[str, Any]) -> int:
        message_id = (command.get("metadata") or {}).get("redis_stream_id")
        if not message_id:
            return 0
        return int(self.client.xack(self.stream, self.group, message_id))


class InterruptController:
    """Small facade for code paths that want an injectable interrupt controller."""

    def __init__(self, bus: InterruptBus | None = None) -> None:
        self.bus = bus or InMemoryInterruptBus()

    def publish(self, command: Any) -> dict[str, Any]:
        return self.bus.publish(command)

    def poll(self) -> dict[str, Any] | None:
        return self.bus.poll()

    def wait(self, timeout: float | None = None) -> dict[str, Any] | None:
        return self.bus.wait(timeout=timeout)


_DEFAULT_INTERRUPT_BUS: InterruptBus = InMemoryInterruptBus()


def configure_default_interrupt_bus(bus: InterruptBus) -> InterruptBus:
    global _DEFAULT_INTERRUPT_BUS
    _DEFAULT_INTERRUPT_BUS = bus
    return _DEFAULT_INTERRUPT_BUS


def get_default_interrupt_bus() -> InterruptBus:
    return _DEFAULT_INTERRUPT_BUS


def publish_interrupt_command(command: Any, bus: InterruptBus | None = None) -> dict[str, Any]:
    target = bus or _DEFAULT_INTERRUPT_BUS
    return target.publish(command)


def poll_interrupt_command(bus: InterruptBus | None = None) -> dict[str, Any] | None:
    target = bus or _DEFAULT_INTERRUPT_BUS
    return target.poll()


def wait_for_interrupt_command(
    timeout: float | None = None,
    bus: InterruptBus | None = None,
) -> dict[str, Any] | None:
    target = bus or _DEFAULT_INTERRUPT_BUS
    return target.wait(timeout=timeout)


def interrupt_bus_supports_prompt() -> bool:
    return bool(getattr(_DEFAULT_INTERRUPT_BUS, "supports_prompt_fallback", False))


def create_interrupt_bus_from_env() -> InterruptBus:
    backend = os.environ.get("OURAGENT_COMMAND_BUS", "memory").strip().lower()
    if backend in {"jsonl", "file"}:
        return JsonlInterruptBus(default_interrupt_command_file())
    if backend in {"redis", "redis-stream", "redis_stream"}:
        return RedisStreamInterruptBus()
    return InMemoryInterruptBus()
