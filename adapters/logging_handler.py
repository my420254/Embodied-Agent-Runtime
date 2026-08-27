from __future__ import annotations

import logging
from typing import Protocol


class LogSink(Protocol):
    def emit(self, message: str) -> None:
        ...


class LogSinkHandler(logging.Handler):
    """Forward formatted log records to a ``LogSink`` (e.g. the frontend).

    Delivery failures are swallowed via ``handleError`` so that a slow or
    unreachable sink never breaks the emitting code path. Wrap this handler in a
    ``logging.handlers.QueueHandler``/``QueueListener`` pair to make delivery
    fully non-blocking for the caller.
    """

    def __init__(self, sink: LogSink, level: int = logging.NOTSET) -> None:
        super().__init__(level)
        self._sink = sink

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = self.format(record)
            self._sink.emit(message)
        except Exception:  # noqa: BLE001 - logging handlers must not raise
            self.handleError(record)
