from __future__ import annotations

import hashlib
import json
import os
import re
import signal
import subprocess
import time
import fcntl
import socket
import atexit
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable

from config.llms import (
    api_base_for_port as llm_api_base_for_port,
    api_key_for_port as llm_api_key_for_port,
    api_model_for_port as llm_api_model_for_port,
    chat_completion_text,
    configured_endpoints as llm_configured_endpoints,
    default_api_model as llm_default_api_model,
    enabled_ports_for_model as llm_enabled_ports_for_model,
    generation_defaults as llm_generation_defaults,
    model_root_config as llm_model_root_config,
    resolve_llm_endpoint_slots,
)
from benchmark.reporting.compact import compact_worker_result


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = Path(os.getenv("OURAGENT_WORKSPACE_ROOT", str(PROJECT_ROOT.parent))).resolve()
PYTHON = os.getenv("OURAGENT_PYTHON", str(WORKSPACE_ROOT / "envs" / "ouragent" / "bin" / "python"))

_PROXY_KEYS = ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy")


class ExperimentTimer:
    """Append-only active runtime accounting across pause/resume sessions."""

    def __init__(self, run_root: str | Path, metadata: dict[str, Any] | None = None):
        self.run_root = Path(run_root)
        self.path = self.run_root / "experiment_timing.json"
        self.session_id = f"{os.getpid()}-{uuid.uuid4().hex[:12]}"
        self.started_epoch = time.time()
        self.started_monotonic = time.monotonic()
        self.finished = False
        self._old_handlers: dict[int, Any] = {}
        self._append_session(metadata or {})
        atexit.register(self._atexit_finish)
        self._install_signal_handlers()

    def _load(self) -> dict[str, Any]:
        payload = read_json(self.path, {})
        return payload if isinstance(payload, dict) else {}

    def _write(self, payload: dict[str, Any]) -> None:
        sessions = payload.get("sessions", [])
        completed = [item for item in sessions if isinstance(item, dict) and item.get("active_elapsed_s") is not None]
        payload.update({
            "schema_version": "experiment_timing_v1",
            "run_root": str(self.run_root),
            "session_count": len(sessions),
            "completed_session_count": len(completed),
            "cumulative_active_wall_s": round(sum(float(item.get("active_elapsed_s", 0.0) or 0.0) for item in completed), 3),
            "updated_at": timestamp(),
            "updated_at_epoch": time.time(),
        })
        write_json(self.path, payload)

    def _append_session(self, metadata: dict[str, Any]) -> None:
        payload = self._load()
        sessions = payload.get("sessions", [])
        if not isinstance(sessions, list):
            sessions = []
        sessions.append({
            "session_id": self.session_id,
            "pid": os.getpid(),
            "status": "running",
            "started_at": timestamp(),
            "started_at_epoch": self.started_epoch,
            "active_elapsed_s": None,
            "metadata": dict(metadata),
        })
        payload["sessions"] = sessions
        self._write(payload)

    def _install_signal_handlers(self) -> None:
        if threading.current_thread() is not threading.main_thread():
            return
        for signum in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            self._old_handlers[signum] = signal.getsignal(signum)

            def handler(received: int, _frame: Any, *, _signum: int = signum) -> None:
                self.finish("interrupted", {"signal": signal.Signals(received).name})
                raise KeyboardInterrupt(f"experiment interrupted by {signal.Signals(received).name}")

            signal.signal(signum, handler)

    def finish(self, status: str = "completed", extra: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.finished:
            return self._load()
        self.finished = True
        ended_epoch = time.time()
        elapsed = max(0.0, time.monotonic() - self.started_monotonic)
        payload = self._load()
        sessions = payload.get("sessions", [])
        for item in sessions if isinstance(sessions, list) else []:
            if isinstance(item, dict) and item.get("session_id") == self.session_id:
                item.update({
                    "status": str(status),
                    "completed_at": timestamp(),
                    "completed_at_epoch": ended_epoch,
                    "active_elapsed_s": round(elapsed, 3),
                })
                if extra:
                    item["result"] = dict(extra)
                break
        self._write(payload)
        for signum, old_handler in self._old_handlers.items():
            signal.signal(signum, old_handler)
        self._old_handlers.clear()
        return payload

    def _atexit_finish(self) -> None:
        if not self.finished:
            self.finish("interrupted", {"reason": "process_exit_without_normal_completion"})


def timestamp() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S %z")


def safe_name(value: str) -> str:
    label = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value).strip()).strip("._-")
    return label or "run"


def safe_case_name(value: str) -> str:
    return safe_name(str(value).replace("/", "__").replace(":", "__"))


def read_json(path: str | Path, fallback: Any = None) -> Any:
    path = Path(path)
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: str | Path, payload: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _fingerprint_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        return []
    return sorted(
        candidate
        for candidate in path.rglob("*")
        if candidate.is_file()
        and "__pycache__" not in candidate.parts
        and candidate.suffix not in {".pyc", ".pyo"}
    )


def content_fingerprint(paths: dict[str, str | Path] | None) -> dict[str, Any]:
    """Build stable SHA-256 fingerprints for reproducibility-critical inputs."""
    entries: dict[str, dict[str, Any]] = {}
    combined = hashlib.sha256()
    for label, raw_path in sorted((paths or {}).items()):
        path = Path(raw_path).resolve()
        files = _fingerprint_files(path)
        digest = hashlib.sha256()
        total_bytes = 0
        for file_path in files:
            relative = file_path.name if path.is_file() else file_path.relative_to(path).as_posix()
            data = file_path.read_bytes()
            file_digest = hashlib.sha256(data).hexdigest()
            total_bytes += len(data)
            digest.update(relative.encode("utf-8"))
            digest.update(b"\0")
            digest.update(file_digest.encode("ascii"))
            digest.update(b"\n")
        entry = {
            "path": str(path),
            "exists": path.exists(),
            "kind": "file" if path.is_file() else "directory" if path.is_dir() else "missing",
            "file_count": len(files),
            "total_bytes": total_bytes,
            "sha256": digest.hexdigest() if files else None,
        }
        entries[str(label)] = entry
        combined.update(str(label).encode("utf-8"))
        combined.update(b"\0")
        combined.update(str(entry["sha256"] or "missing").encode("ascii"))
        combined.update(b"\n")
    return {
        "schema_version": "content_fingerprint_v1",
        "algorithm": "sha256",
        "combined_sha256": combined.hexdigest(),
        "entries": entries,
    }


def append_log(path: str | Path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)
        if not text.endswith("\n"):
            handle.write("\n")


def clear_proxy_env(env: dict[str, str] | None = None) -> dict[str, str]:
    cleaned = dict(os.environ if env is None else env)
    for key in _PROXY_KEYS:
        cleaned.pop(key, None)
    cleaned["NO_PROXY"] = "127.0.0.1,localhost,192.168.27.250"
    cleaned["no_proxy"] = cleaned["NO_PROXY"]
    cleaned["LANGCHAIN_OPENAI_TCP_KEEPALIVE"] = "0"
    return cleaned


def load_case_ids_file(path: str | Path | None) -> list[str]:
    if not path:
        return []
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    try:
        loaded = json.loads(text)
    except json.JSONDecodeError:
        return [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
    if isinstance(loaded, list):
        return [str(item) for item in loaded if str(item).strip()]
    if isinstance(loaded, dict):
        values = loaded.get("case_ids") or loaded.get("cases") or []
        return [str(item) for item in values if str(item).strip()] if isinstance(values, list) else []
    return []


def model_root_config() -> dict[str, Any]:
    return llm_model_root_config()


def configured_endpoints() -> dict[str, Any]:
    return llm_configured_endpoints()


def api_base_for_port(port: int) -> str:
    return llm_api_base_for_port(port)


def endpoint_slots(
    ports: list[int],
    *,
    workers: int = 1,
    module: str = "planning",
    api_model: str = "",
    api_key: str = "",
) -> list[dict[str, Any]]:
    return resolve_llm_endpoint_slots(
        ports,
        workers=workers,
        module=module,
        api_model=api_model,
        api_key=api_key,
        allow_auto_ports=False,
    )


def chat_completion(
    *,
    prompt: str,
    api_base: str,
    api_key: str,
    model_name: str,
    max_tokens: int,
    temperature: float,
    timeout: float = 900.0,
) -> str:
    return chat_completion_text(
        prompt=prompt,
        api_base=api_base,
        api_key=api_key,
        model_name=model_name,
        max_tokens=max_tokens,
        temperature=temperature,
        timeout=timeout,
        module="planning",
    )


def run_subprocess(
    command: list[str],
    *,
    env: dict[str, str],
    log_path: str | Path,
    cwd: str | Path | None = None,
    append: bool = True,
    timeout_s: int | float | None = None,
) -> int:
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with log_path.open(mode, encoding="utf-8") as log_file:
        log_file.write(f"\n\n=== START {timestamp()} ===\n")
        log_file.write("CMD: " + " ".join(command) + "\n")
        log_file.flush()
        process = subprocess.Popen(
            command,
            cwd=str(cwd or PROJECT_ROOT),
            env=env,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
        )
        timed_out = False
        try:
            returncode = process.wait(timeout=float(timeout_s) if timeout_s else None)
        except subprocess.TimeoutExpired:
            timed_out = True
            log_file.write(f"=== TIMEOUT {timestamp()} timeout_s={timeout_s} ===\n")
            log_file.flush()
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
            returncode = 124
        suffix = f" returncode={returncode}"
        if timed_out:
            suffix += " timed_out=true"
        log_file.write(f"=== END {timestamp()}{suffix} ===\n")
    return int(returncode)


def add_common_launch_args(parser: Any) -> Any:
    parser.add_argument("--ports", nargs="*", type=int, default=None)
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--run-name", default="")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--case-ids-file", default="")
    parser.add_argument("--launch-shards", type=int, default=None)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--expected-count", type=int, default=None)
    parser.add_argument("--worker-timeout-s", type=int, default=None)
    parser.add_argument("--api-model", default="")
    parser.add_argument("--api-key", default="")
    parser.add_argument("--no-trace-llm-io", action="store_true")
    return parser


def list_values(*values: Any) -> list[str]:
    items: list[str] = []
    for value in values:
        if isinstance(value, list):
            items.extend(str(item) for item in value if str(item).strip())
        elif value:
            items.append(str(value))
    return items


def load_launch_config(path: str | Path) -> dict[str, Any]:
    payload = read_json(path, {})
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid launch config: {path}")
    payload["_config_path"] = str(Path(path))
    return payload


def launch_defaults(launch_config: dict[str, Any]) -> dict[str, Any]:
    defaults = launch_config.get("defaults", {}) if isinstance(launch_config.get("defaults"), dict) else {}
    return defaults


def launch_run_name(args: Any, defaults: dict[str, Any], fallback: str) -> str:
    return str(getattr(args, "run_name", "") or defaults.get("run_name") or fallback)


def launch_results_root(launch_config: dict[str, Any], default_relative: str) -> Path:
    path = Path(str(launch_config.get("results_root") or default_relative))
    return path if path.is_absolute() else PROJECT_ROOT / path


def launch_run_root(launch_config: dict[str, Any], run_name: str, default_relative: str) -> Path:
    return launch_results_root(launch_config, default_relative) / run_name


def launch_case_ids(args: Any, defaults: dict[str, Any]) -> list[str]:
    return list_values(defaults.get("case_ids", []), getattr(args, "case_id", []), load_case_ids_file(getattr(args, "case_ids_file", "")))


def launch_limit(args: Any, defaults: dict[str, Any]) -> int | None:
    value = getattr(args, "limit", None)
    return value if value is not None else defaults.get("limit")


def launch_expected_count(args: Any, defaults: dict[str, Any], *, default_enabled: bool = True) -> int | None:
    value = getattr(args, "expected_count", None)
    if value is not None:
        return int(value)
    if not default_enabled:
        return None
    if launch_limit(args, defaults) is not None:
        return None
    if launch_case_ids(args, defaults):
        return None
    default_value = defaults.get("expected_count")
    return int(default_value) if default_value is not None else None


def launch_worker_timeout_s(args: Any, defaults: dict[str, Any]) -> int | None:
    value = getattr(args, "worker_timeout_s", None)
    if value is None:
        value = defaults.get("worker_timeout_s")
    if value is None:
        return None
    return int(value) if int(value) > 0 else None


def assert_expected_case_count(
    cases: list[Any],
    expected_count: int | None,
    benchmark_name: str,
    *,
    details: str = "",
) -> None:
    if expected_count is None:
        return
    actual_count = len(cases)
    if actual_count == int(expected_count):
        return
    message = f"{benchmark_name} selected case count mismatch: selected={actual_count}, expected={int(expected_count)}"
    if details:
        message = f"{message}; {details}"
    raise SystemExit(message)


def launch_workers(args: Any, defaults: dict[str, Any]) -> int:
    return int(getattr(args, "workers", None) if getattr(args, "workers", None) is not None else defaults.get("workers", 1) or 1)


def launch_ports(args: Any, defaults: dict[str, Any]) -> list[int]:
    ports = getattr(args, "ports", None)
    return list(ports) if ports is not None else [int(port) for port in defaults.get("ports", [])]


def _launch_shards_per_interface(defaults: dict[str, Any]) -> int:
    for key in ("shards_per_interface", "shards_per_endpoint", "shards_per_port"):
        value = defaults.get(key)
        if value is None:
            continue
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            continue
        if parsed > 0:
            return parsed
    return 1


def _launch_interface_count(endpoint_slots_: list[dict[str, Any]]) -> int:
    return max(1, len({str(slot.get("port", "")) for slot in endpoint_slots_ if slot.get("port") is not None}))


def launch_unit_count(args: Any, endpoint_slots_: list[dict[str, Any]], defaults: dict[str, Any] | None = None) -> int:
    defaults = defaults or {}
    interface_count = _launch_interface_count(endpoint_slots_)
    max_interfaces = defaults.get("max_interfaces")
    if max_interfaces is not None and int(max_interfaces) > 0 and interface_count > int(max_interfaces):
        raise SystemExit(f"最多允许同时使用 {int(max_interfaces)} 个 LLM 接口，当前 ports={interface_count}")
    launch_shards = getattr(args, "launch_shards", None)
    if launch_shards is None:
        launch_shards = defaults.get("launch_shards")
    if launch_shards is not None and int(launch_shards) > 0:
        return int(launch_shards)
    return interface_count * _launch_shards_per_interface(defaults)


def assert_tcp_ports_available(ports: list[int], *, label: str) -> None:
    busy: list[int] = []
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("127.0.0.1", int(port)))
        except OSError:
            busy.append(int(port))
        finally:
            sock.close()
    if busy:
        formatted = ", ".join(str(port) for port in busy)
        raise SystemExit(f"{label} 端口已被占用，不能保证仿真隔离: {formatted}")


def acquire_resource_locks(resource_type: str, resource_ids: list[str | int], *, run_root: str | Path) -> list[Any]:
    lock_dir = PROJECT_ROOT / "benchmark" / ".resource_locks" / safe_name(resource_type)
    lock_dir.mkdir(parents=True, exist_ok=True)
    handles: list[Any] = []
    for resource_id in resource_ids:
        lock_path = lock_dir / f"{safe_name(str(resource_id))}.lock"
        handle = lock_path.open("w", encoding="utf-8")
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            handle.close()
            release_resource_locks(handles)
            raise SystemExit(f"{resource_type} 已被其他当前 framework run 锁定: {resource_id}")
        handle.seek(0)
        handle.truncate()
        handle.write(json.dumps({"resource": str(resource_id), "run_root": str(run_root), "pid": os.getpid()}, ensure_ascii=False))
        handle.flush()
        handles.append(handle)
    return handles


def release_resource_locks(handles: list[Any]) -> None:
    for handle in handles:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass
        try:
            handle.close()
        except Exception:
            pass


def assert_framework_run_py_entrypoint() -> None:
    if os.getenv("OURAGENT_FRAMEWORK_ENTRYPOINT") == "run.py":
        return
    raise SystemExit("framework 实验只能通过对应数据集的 framework/code/run.py 启动，不能直接调用 launcher.py 或 worker。")


def launch_preflight_payload(
    *,
    benchmark_name: str,
    cases: list[Any],
    endpoint_slots: list[dict[str, Any]],
    unit_count: int,
    resources: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "preflight": True,
        "benchmark_name": benchmark_name,
        "selected_case_count": len(cases),
        "unit_count": int(unit_count),
        "endpoint_slots": [
            {
                "index": slot.get("index"),
                "port": slot.get("port"),
                "api_base": slot.get("api_base"),
                "api_model": slot.get("api_model"),
            }
            for slot in endpoint_slots
        ],
        "resources": resources or {},
    }


def launch_trace(defaults: dict[str, Any]) -> bool:
    return bool(defaults.get("trace", True))


def launch_trace_llm_io(args: Any, defaults: dict[str, Any]) -> bool:
    return bool(defaults.get("trace_llm_io", True)) and not bool(getattr(args, "no_trace_llm_io", False))


def case_field(case: dict[str, Any], key: str, default: Any = None) -> Any:
    return case.get(key, default) if isinstance(case, dict) else default


def case_input(case: dict[str, Any]) -> dict[str, Any]:
    value = case_field(case, "input", {})
    return value if isinstance(value, dict) else {}


def case_metadata(case: dict[str, Any]) -> dict[str, Any]:
    value = case_field(case, "metadata", {})
    return value if isinstance(value, dict) else {}


def case_to_payload(case: Any) -> dict[str, Any]:
    if not isinstance(case, dict):
        raise TypeError(f"framework case must be a dict, got {type(case).__name__}")
    case_id = str(case.get("case_id", "") or "")
    if not case_id:
        raise ValueError("framework case is missing case_id")
    return {
        "case_id": case_id,
        "dataset": str(case.get("dataset", "") or ""),
        "input": case_input(case),
        "metadata": case_metadata(case),
        "source_path": str(case.get("source_path", "") or ""),
    }


def case_result_row(case: Any, prediction: dict[str, Any] | None = None, error: str = "") -> dict[str, Any]:
    payload = case_to_payload(case)
    return {
        "case_id": payload["case_id"],
        "dataset": payload["dataset"],
        "input": payload["input"],
        "prediction": prediction or {},
        "metadata": payload["metadata"],
        "source_path": payload["source_path"],
        "error": error,
    }


def worker_case_row(
    case_payload: dict[str, Any],
    prediction: dict[str, Any] | None = None,
    error: str = "",
    *,
    default_dataset: str = "",
) -> dict[str, Any]:
    return case_result_row(
        {
            "case_id": str(case_payload.get("case_id", "")),
            "dataset": str(case_payload.get("dataset", default_dataset)),
            "input": case_payload.get("input", {}) if isinstance(case_payload.get("input"), dict) else {},
            "metadata": case_payload.get("metadata", {}) if isinstance(case_payload.get("metadata"), dict) else {},
            "source_path": str(case_payload.get("source_path", "")),
        },
        prediction or {},
        error,
    )


def worker_result_payload(
    *,
    case_id: str,
    status: str,
    error: str,
    case_root_path: str | Path,
    row: dict[str, Any],
    timing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(case_root_path)
    payload = {
        "case_id": case_id,
        "status": status,
        "error": error,
        "raw_output": str(root / "raw_output.json"),
        "case_json": str(root / "case.json"),
        "report": str(root / "trace_report.md"),
        "row": compact_worker_result({"row": row}).get("row", {}),
    }
    if timing:
        payload["timing"] = dict(timing)
    return payload


def case_root(run_root: str | Path, case_id: str) -> Path:
    return Path(run_root) / "cases" / safe_case_name(case_id)


def select_cases(cases: list[Any], *, case_ids: list[str], limit: int | None) -> list[Any]:
    selected = list(cases)
    if case_ids:
        requested = {str(item) for item in case_ids}
        selected = [case for case in selected if str(case_field(case, "case_id", "")) in requested]
        found = {str(case_field(case, "case_id", "")) for case in selected}
        missing = [case_id for case_id in case_ids if case_id not in found]
        if missing:
            raise SystemExit("unknown case ids: " + ", ".join(missing))
    if limit is not None:
        selected = selected[: max(0, int(limit))]
    if not selected:
        raise SystemExit("no benchmark cases selected")
    return selected


def split_cases(
    cases: list[Any],
    count: int,
    group_key: Callable[[Any], str] | None = None,
) -> list[list[Any]]:
    chunks: list[list[dict[str, Any]]] = [[] for _ in range(max(1, int(count)))]
    if group_key is not None:
        groups: dict[str, list[Any]] = {}
        for case in cases:
            groups.setdefault(str(group_key(case)), []).append(case)
        for index, group_name in enumerate(groups):
            chunks[index % len(chunks)].extend(groups[group_name])
        return chunks
    for index, case in enumerate(cases):
        chunks[index % len(chunks)].append(case)
    return chunks


def _api_model() -> str:
    return llm_default_api_model("planning")


def _generation_defaults() -> dict[str, Any]:
    return llm_generation_defaults("planning")


def _endpoint_for_port(port: int) -> dict[str, Any]:
    endpoint = configured_endpoints().get(str(int(port)), {})
    return endpoint if isinstance(endpoint, dict) else {}


def _api_model_for_port(port: int, fallback: str) -> str:
    return llm_api_model_for_port(port, module="planning", fallback=fallback)


def _api_key_for_port(port: int, fallback: str = "") -> str:
    return llm_api_key_for_port(port, module="planning", fallback=fallback)


def _find_enabled_ports_for_model(model_name: str) -> list[int]:
    return llm_enabled_ports_for_model(model_name)


def _llm_endpoint_env(
    *,
    api_base: str,
    api_key: str,
    api_model: str,
    env: dict[str, str] | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    benchmark_name: str | None = None,
) -> dict[str, str]:
    patched = clear_proxy_env(env)
    base = str(api_base or "").strip()
    key = str(api_key or "").strip()
    model = str(api_model or "").strip()
    for name in ("LANGGRAPH_JSZN_API_BASE", "LANGGRAPH_JSZN_UNDERSTANDING_API_BASE", "LANGGRAPH_JSZN_PLANNING_API_BASE"):
        patched[name] = base
    for name in ("LANGGRAPH_JSZN_API_KEY", "LANGGRAPH_JSZN_UNDERSTANDING_API_KEY", "LANGGRAPH_JSZN_PLANNING_API_KEY"):
        patched[name] = key
    for name in ("LANGGRAPH_JSZN_API_MODEL", "LANGGRAPH_JSZN_UNDERSTANDING_API_MODEL", "LANGGRAPH_JSZN_PLANNING_API_MODEL"):
        patched[name] = model
    if max_tokens is not None:
        patched["OURAGENT_LLM_MAX_TOKENS"] = str(max_tokens)
        patched["LANGGRAPH_JSZN_MAX_TOKENS"] = str(max_tokens)
        patched["LANGGRAPH_JSZN_PLANNING_MAX_TOKENS"] = str(max_tokens)
    if temperature is not None:
        patched["OURAGENT_LLM_TEMPERATURE"] = str(temperature)
        patched["LANGGRAPH_JSZN_TEMPERATURE"] = str(temperature)
        patched["LANGGRAPH_JSZN_PLANNING_TEMPERATURE"] = str(temperature)
    if str(benchmark_name or "").startswith("eai_"):
        patched["OURAGENT_EAI_API_BASE"] = base
        patched["OURAGENT_EAI_API_KEY"] = key
        patched["OURAGENT_EAI_MODEL_NAME"] = model
    return patched


def resolve_endpoint_slots(
    *,
    benchmark_name: str,
    ports: list[int],
    workers: int,
    api_model: str = "",
    api_key: str = "",
) -> list[dict[str, Any]]:
    requested_model = str(api_model or "").strip()
    if requested_model:
        mismatches: list[str] = []
        for port in ports:
            configured_model = str(_endpoint_for_port(int(port)).get("model_name") or "").strip()
            if configured_model and configured_model != requested_model:
                mismatches.append(f"{int(port)}={configured_model}")
        if mismatches:
            details = ", ".join(mismatches)
            raise SystemExit(
                f"模型与端口配置不一致: requested={requested_model}; configured={details}. "
                "请更正 --api-model 或 --ports，禁止用命令行标签覆盖端点真实模型。"
            )
    return resolve_llm_endpoint_slots(
        ports,
        workers=workers,
        module="planning",
        api_model=api_model,
        api_key=api_key,
        allow_auto_ports=True,
    )


def worker_env(slot: dict[str, Any], *, benchmark_name: str, trace: bool, trace_llm_io: bool) -> dict[str, str]:
    env = _llm_endpoint_env(
        api_base=str(slot["api_base"]),
        api_key=str(slot["api_key"]),
        api_model=str(slot["api_model"]),
        env=os.environ,
        max_tokens=int(slot.get("max_tokens", 4096)),
        temperature=float(slot.get("temperature", 0.0)),
        benchmark_name=benchmark_name,
    )
    env["OURAGENT_INTERNAL_WORKER"] = "1"
    env["OURAGENT_BENCHMARK_TRACE"] = "1" if trace else "0"
    env["OURAGENT_TRACE_LLM_IO"] = "1" if trace_llm_io else "0"
    return env


def build_worker_command(worker_module: str, worker_input_path: str | Path) -> list[str]:
    return [PYTHON, "-m", worker_module, "--worker-input", str(worker_input_path)]


def write_row_summary(
    run_root: str | Path,
    results: list[dict[str, Any]],
    summarizer: Callable[[list[dict[str, Any]]], dict[str, Any]],
    *,
    empty_status: str = "no_completed_rows",
) -> dict[str, Any]:
    run_root = Path(run_root)
    rows = [item.get("row") for item in results if isinstance(item.get("row"), dict)]
    write_json(run_root / "merged_results.json", [compact_worker_result(item) for item in results])
    summary = summarizer(rows) if rows else {"count": 0, "status": empty_status}
    summary["_run_root"] = str(run_root)
    write_json(run_root / "summary.json", summary)
    return summary


def _worker_input_path(run_root: Path, case_id: str) -> Path:
    return case_root(run_root, case_id) / "artifacts" / "worker_input.json"


def _worker_result_path(run_root: Path, case_id: str) -> Path:
    return case_root(run_root, case_id) / "worker_result.json"


def launch_case_workers(
    *,
    benchmark_name: str,
    run_root: str | Path,
    worker_module: str,
    cases: list[Any],
    endpoint_slots: list[dict[str, Any]],
    unit_count: int,
    group_key: Callable[[Any], str] | None,
    worker_options: dict[str, Any],
    trace: bool,
    trace_llm_io: bool,
    dry_run: bool,
    resume: bool = False,
    worker_timeout_s: int | None = None,
    reproducibility_paths: dict[str, str | Path] | None = None,
) -> list[dict[str, Any]]:
    run_root = Path(run_root)
    experiment_timer = ExperimentTimer(
        run_root,
        {
            "benchmark_name": benchmark_name,
            "resume": bool(resume),
            "dry_run": bool(dry_run),
            "selected_case_count": len(cases),
            "unit_count": int(unit_count),
        },
    )
    launch_started_epoch = time.time()
    launch_started_at = timestamp()
    reproducibility = content_fingerprint(reproducibility_paths) if reproducibility_paths else None
    previous_manifest = read_json(run_root / "launch_manifest.json", {})
    reproducibility_sessions = (
        list(previous_manifest.get("reproducibility_sessions", []))
        if isinstance(previous_manifest, dict) and isinstance(previous_manifest.get("reproducibility_sessions"), list)
        else []
    )
    if reproducibility is not None:
        reproducibility_sessions.append({
            "session_id": experiment_timer.session_id,
            "started_at": launch_started_at,
            "fingerprint": reproducibility,
        })
    chunks = split_cases(cases, count=max(1, int(unit_count)), group_key=group_key)
    commands: list[dict[str, Any]] = []
    tasks: list[dict[str, Any]] = []
    skipped_results: list[dict[str, Any]] = []
    for unit_index, chunk in enumerate(chunks):
        if not chunk:
            continue
        slot = endpoint_slots[unit_index % len(endpoint_slots)]
        for case in chunk:
            case_payload = case_to_payload(case)
            case_id = str(case_payload["case_id"])
            root = case_root(run_root, case_id)
            if resume:
                existing = read_json(_worker_result_path(run_root, case_id), {})
                if isinstance(existing, dict) and str(existing.get("status", "")).lower() in {"done", "evaluation_failed"}:
                    existing["resumed"] = True
                    skipped_results.append(existing)
                    continue
            payload = {
                "benchmark_name": benchmark_name,
                "run_root": str(run_root),
                "run_name": run_root.name,
                "unit_index": unit_index,
                "case": case_payload,
                "endpoint": slot,
                "trace": bool(trace),
                "trace_llm_io": bool(trace_llm_io),
                "options": worker_options,
            }
            worker_input = _worker_input_path(run_root, case_id)
            write_json(worker_input, payload)
            command = build_worker_command(worker_module, worker_input)
            log_path = root / "run.log"
            task = {
                "case_id": case_id,
                "case": case_payload,
                "unit_index": unit_index,
                "endpoint_index": slot.get("index"),
                "port": slot.get("port"),
                "worker_input": str(worker_input),
                "log": str(log_path),
                "command": command,
            }
            commands.append(task)
            tasks.append({**task, "env": worker_env(slot, benchmark_name=benchmark_name, trace=trace, trace_llm_io=trace_llm_io)})

    def write_launch_manifest(status: str, extra: dict[str, Any] | None = None) -> None:
        endpoint_summary = [
            {
                "index": slot.get("index"),
                "port": slot.get("port"),
                "api_base": slot.get("api_base"),
                "api_model": slot.get("api_model"),
            }
            for slot in endpoint_slots
        ]
        payload = {
            "benchmark_name": benchmark_name,
            "run_name": run_root.name,
            "run_root": str(run_root),
            "worker_module": worker_module,
            "status": status,
            "dry_run": bool(dry_run),
            "resume": bool(resume),
            "selected_case_count": len(cases),
            "resumed_case_count": len(skipped_results),
            "scheduled_command_count": len(commands),
            "unit_count": int(unit_count),
            "worker_timeout_s": worker_timeout_s,
            "started_at": launch_started_at,
            "started_at_epoch": launch_started_epoch,
            "endpoint_slots": endpoint_summary,
            "resumed_cases": [str(item.get("case_id", "")) for item in skipped_results],
            "commands": commands,
        }
        if extra:
            payload.update(extra)
        if reproducibility is not None:
            payload["reproducibility"] = reproducibility
            payload["reproducibility_sessions"] = reproducibility_sessions
        write_json(Path(run_root) / "launch_manifest.json", payload)

    write_launch_manifest("dry_run" if dry_run else "running")
    if dry_run:
        print(json.dumps({"dry_run": True, "commands": commands}, ensure_ascii=False, indent=2))
        experiment_timer.finish("dry_run", {"scheduled_command_count": len(commands)})
        return skipped_results + [{"case_id": str(item["case_id"]), "status": "dry_run", "command": item["command"]} for item in commands]
    if not tasks:
        skipped_results.sort(key=lambda item: str(item.get("case_id", "")))
        write_launch_manifest(
            "completed",
            {
                "completed_at": timestamp(),
                "completed_at_epoch": time.time(),
                "elapsed_s": round(time.time() - launch_started_epoch, 3),
                "result_status_counts": {
                    "resumed": len(skipped_results),
                },
            },
        )
        experiment_timer.finish("completed", {"resumed_case_count": len(skipped_results), "executed_case_count": 0})
        return skipped_results

    def run_one(task: dict[str, Any]) -> dict[str, Any]:
        result_path = _worker_result_path(run_root, str(task["case_id"]))
        result: dict[str, Any] = {}
        rc = 1
        attempts = 0
        attempt_timings: list[dict[str, Any]] = []
        for attempt in range(2):
            attempts = attempt + 1
            attempt_started_epoch = time.time()
            attempt_started_monotonic = time.monotonic()
            rc = run_subprocess(
                task["command"],
                env=task["env"],
                log_path=task["log"],
                append=attempt > 0,
                timeout_s=worker_timeout_s,
            )
            attempt_timings.append({
                "attempt": attempts,
                "started_at_epoch": attempt_started_epoch,
                "completed_at_epoch": time.time(),
                "active_elapsed_s": round(time.monotonic() - attempt_started_monotonic, 3),
                "returncode": rc,
            })
            result = read_json(result_path, {})
            error_text = str(result.get("error", "") if isinstance(result, dict) else "")
            transient = rc == 124 or "RuntimeError:" in error_text or "APITimeout" in error_text
            if not transient or attempt == 1:
                break
            time.sleep(1.0)
        if not isinstance(result, dict):
            result = {}
        if not result:
            error = "worker_timeout" if rc == 124 else "worker_result_missing"
            if rc and rc != 124:
                error = f"worker_process_returncode={rc}"
            row = worker_case_row(task.get("case", {}), {}, error, default_dataset=benchmark_name)
            try:
                from benchmark.reporting import persist_case_bundle

                persist_case_bundle(
                    config_name=benchmark_name,
                    run_root=run_root,
                    row=row,
                    source_hint=case_root(run_root, str(task["case_id"])) / "raw_output.json",
                )
            except Exception as persist_error:  # pragma: no cover - last-resort launcher path
                error = f"{error}; result_persist_error={persist_error!r}"
                row = worker_case_row(task.get("case", {}), {}, error, default_dataset=benchmark_name)
            fallback = worker_result_payload(
                case_id=str(task["case_id"]),
                status="failed",
                error=error,
                case_root_path=case_root(run_root, str(task["case_id"])),
                row=row,
            )
            write_json(result_path, fallback)
            result = {
                "case_id": str(task["case_id"]),
                "status": "failed",
                "error": error,
                "returncode": rc,
                "log": task["log"],
                "report": fallback.get("report", ""),
                "row": fallback.get("row", {}),
            }
        result.setdefault("returncode", rc)
        result.setdefault("worker_attempts", attempts)
        result["launcher_timing"] = {
            "attempts": attempt_timings,
            "active_elapsed_s": round(sum(float(item["active_elapsed_s"]) for item in attempt_timings), 3),
        }
        result.setdefault("log", task["log"])
        write_json(result_path, result)
        return result

    tasks_by_unit: dict[int, list[dict[str, Any]]] = {}
    for task in tasks:
        tasks_by_unit.setdefault(int(task["unit_index"]), []).append(task)

    def run_unit(unit_tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        # A launch unit owns one endpoint and one simulator resource. Keep its
        # cases serial while different units run concurrently.
        return [run_one(task) for task in unit_tasks]

    results: list[dict[str, Any]] = list(skipped_results)
    max_workers = max(1, len(tasks_by_unit))
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = [pool.submit(run_unit, unit_tasks) for unit_tasks in tasks_by_unit.values()]
            for future in as_completed(futures):
                results.extend(future.result())
    except BaseException:
        experiment_timer.finish("interrupted", {"completed_result_count": len(results)})
        raise
    results.sort(key=lambda item: str(item.get("case_id", "")))
    status_counts: dict[str, int] = {}
    for item in results:
        status = str(item.get("status", "") or "missing_status")
        status_counts[status] = status_counts.get(status, 0) + 1
    write_launch_manifest(
        "completed",
        {
            "completed_at": timestamp(),
            "completed_at_epoch": time.time(),
            "elapsed_s": round(time.time() - launch_started_epoch, 3),
            "result_count": len(results),
            "result_status_counts": status_counts,
        },
    )
    experiment_timer.finish(
        "completed",
        {
            "result_count": len(results),
            "executed_case_count": len(tasks),
            "resumed_case_count": len(skipped_results),
            "case_compute_s": round(sum(float((item.get("launcher_timing") or {}).get("active_elapsed_s", 0.0) or 0.0) for item in results), 3),
            "parallel_units": max_workers,
        },
    )
    return results


def exit_if_not_internal_worker() -> None:
    if os.getenv("OURAGENT_INTERNAL_WORKER") == "1":
        return
    raise SystemExit("This is an internal case worker. Use framework/code/run.py to start experiments.")


def summarize_case_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    done = sum(1 for row in rows if row.get("status") == "done")
    failed = sum(1 for row in rows if row.get("status") in {"failed", "evaluation_failed"})
    return {
        "total_cases": total,
        "done_cases": done,
        "failed_cases": failed,
        "task_success_count": sum(1 for row in rows if bool(row.get("task_success"))),
        "cases": rows,
    }
