from __future__ import annotations

import atexit
import contextlib
import logging
import logging.handlers
import queue
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG_FILE = PROJECT_ROOT / "logs" / "ouragent.log"

# Dedicated logger for mirrored console/print output. It is kept separate from
# the root logger (propagate=False) so rendered console text is not re-emitted
# on stderr (the tee already wrote it to the real stdout) and does not recurse
# back into the stdout stream we are tee-ing.
CONSOLE_LOGGER_NAME = "ouragent.console"

_STD_FORMAT = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"
_STD_DATEFMT = "%Y-%m-%d %H:%M:%S"

_configured = False
_atexit_registered = False
_added_handlers: list[tuple[logging.Logger, logging.Handler]] = []
_queue_listener: logging.handlers.QueueListener | None = None


def _attach(logger: logging.Logger, handler: logging.Handler) -> None:
    logger.addHandler(handler)
    _added_handlers.append((logger, handler))


def configure_logging(
    *,
    frontend_host: str = "localhost",
    frontend_port: int | str | None = None,
    enable_frontend: bool | None = None,
    log_file: str | Path | None = None,
    level: int = logging.INFO,
    force: bool = False,
) -> None:
    """Install the project-wide logging configuration.

    Idempotent: safe to call from every entrypoint. The root logger gains a
    stderr handler and a rotating file handler (``logs/ouragent.log``) so that
    ``logging.getLogger(__name__)`` works everywhere and the backend is
    inspectable after the fact. When a frontend port is available, mirrored
    console output is additionally forwarded to the UI through a non-blocking
    ``QueueHandler``/``QueueListener`` pair (see :func:`console_mirror`).

    ``frontend_port`` accepts the raw ``GENESIS_WEB_PORT`` string; a falsy value
    disables frontend forwarding unless ``enable_frontend`` is set explicitly.
    """

    global _configured, _atexit_registered, _queue_listener

    if _configured and not force:
        return
    if _configured and force:
        shutdown_logging()

    try:
        port = int(frontend_port) if frontend_port else None
    except (TypeError, ValueError):
        port = None
    if enable_frontend is None:
        enable_frontend = port is not None

    log_path = Path(log_file).expanduser() if log_file else DEFAULT_LOG_FILE
    log_path.parent.mkdir(parents=True, exist_ok=True)

    std_formatter = logging.Formatter(_STD_FORMAT, _STD_DATEFMT)

    root = logging.getLogger()
    root.setLevel(level)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(std_formatter)
    _attach(root, stderr_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        log_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(std_formatter)
    _attach(root, file_handler)

    console_logger = logging.getLogger(CONSOLE_LOGGER_NAME)
    console_logger.setLevel(level)
    console_logger.propagate = False
    # Persist mirrored console output to the same rotating file as the rest of
    # the backend, but never to stderr (avoids double-printing on the terminal).
    _attach(console_logger, file_handler)

    if enable_frontend and port is not None:
        from adapters.agent_log_client import AgentLogSender
        from adapters.logging_handler import LogSinkHandler

        frontend_handler = LogSinkHandler(AgentLogSender(host=frontend_host, port=port))
        # The frontend UI wants the raw rendered line, not a log-prefixed one.
        frontend_handler.setFormatter(logging.Formatter("%(message)s"))

        log_queue: queue.Queue = queue.Queue(-1)
        queue_handler = logging.handlers.QueueHandler(log_queue)
        _queue_listener = logging.handlers.QueueListener(
            log_queue, frontend_handler, respect_handler_level=True
        )
        _queue_listener.start()
        _attach(console_logger, queue_handler)

    if not _atexit_registered:
        atexit.register(shutdown_logging)
        _atexit_registered = True

    _configured = True


def shutdown_logging() -> None:
    """Stop the frontend listener thread and detach handlers we installed."""

    global _configured, _queue_listener

    if _queue_listener is not None:
        try:
            _queue_listener.stop()
        except Exception:  # noqa: BLE001 - shutdown must not raise
            pass
        for handler in _queue_listener.handlers:
            with contextlib.suppress(Exception):
                handler.close()
        _queue_listener = None

    for logger, handler in _added_handlers:
        with contextlib.suppress(Exception):
            logger.removeHandler(handler)
            handler.close()
    _added_handlers.clear()

    _configured = False


class _TeeStream:
    """A ``sys.stdout`` proxy that echoes to the real stream and forwards
    completed lines to a callback.

    The real stream still receives everything (so the developer keeps their
    terminal output verbatim); each complete line is additionally handed to the
    callback, which routes it to the ``ouragent.console`` logger. Unknown
    attribute access is delegated to the wrapped stream so the proxy stays
    duck-type compatible (``encoding``, ``isatty``, ``fileno`` ...).
    """

    _INTERNAL = {"_base", "_callback", "_buffer"}

    def __init__(self, base, callback) -> None:
        object.__setattr__(self, "_base", base)
        object.__setattr__(self, "_callback", callback)
        object.__setattr__(self, "_buffer", "")

    def write(self, s):
        if not isinstance(s, str):
            s = str(s)
        written = self._base.write(s)
        with contextlib.suppress(Exception):
            self._base.flush()
        buffer = self._buffer + s
        while True:
            newline = buffer.find("\n")
            if newline < 0:
                break
            self._forward(buffer[:newline])
            buffer = buffer[newline + 1 :]
        object.__setattr__(self, "_buffer", buffer)
        return written if written is not None else len(s)

    def writelines(self, lines) -> None:
        for line in lines:
            self.write(line)

    def _forward(self, line: str) -> None:
        line = line.rstrip("\r")
        if not line:
            return
        try:
            self._callback(line)
        except Exception:  # noqa: BLE001 - mirroring must never break stdout
            pass

    def drain(self) -> None:
        """Flush any buffered partial line (no trailing newline) to the callback."""
        buffer = self._buffer
        if buffer:
            object.__setattr__(self, "_buffer", "")
            self._forward(buffer)

    def flush(self) -> None:
        with contextlib.suppress(Exception):
            self._base.flush()

    def __getattr__(self, name):
        if name in _TeeStream._INTERNAL:
            raise AttributeError(name)
        return getattr(self._base, name)


@contextlib.contextmanager
def console_mirror(logger_name: str = CONSOLE_LOGGER_NAME):
    """Temporarily tee ``sys.stdout`` into the console logger.

    Console/print output continues to reach the real terminal unchanged while
    each complete line is forwarded to ``logger_name`` (and from there to the
    rotating file and, when configured, the frontend). Restores the original
    stream on exit, flushing any trailing partial line first.
    """

    console_logger = logging.getLogger(logger_name)
    base = sys.stdout
    tee = _TeeStream(base, console_logger.info)
    sys.stdout = tee
    try:
        yield
    finally:
        with contextlib.suppress(Exception):
            tee.drain()
        sys.stdout = base
