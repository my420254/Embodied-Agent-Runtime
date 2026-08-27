from __future__ import annotations

import threading
from pathlib import Path
from typing import Any, Callable

from adapters.command_bus import default_interrupt_command_file


class AgentRuntimeThread:
    """Background wrapper for the graph engine.

    The engine consumes the same CommandBus used by ROS callbacks and CLI
    clients. It is intentionally thin; graph execution lives in
    agent_runtime.engine.

    Optional render callbacks are forwarded to :func:`run_engine`; when supplied
    (e.g. by ``main.py``) the ROS-driven runtime renders to the console just like
    the interactive CLI, so its output can also be mirrored to the frontend.
    """

    def __init__(
        self,
        *,
        plan_only: bool = False,
        command_file: str | Path | None = None,
        auto_accept_feedback: bool = True,
        render_stream: Callable[..., Any] | None = None,
        print_banner: Callable[[str], None] | None = None,
        print_divider: Callable[[str], None] | None = None,
    ) -> None:
        self.plan_only = plan_only
        self.command_file = Path(command_file).expanduser() if command_file else default_interrupt_command_file()
        self.auto_accept_feedback = auto_accept_feedback
        self.render_stream = render_stream
        self.print_banner = print_banner
        self.print_divider = print_divider
        self._thread: threading.Thread | None = None
        self._ready = threading.Event()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._ready.clear()
        self._thread = threading.Thread(target=self._run, name="ouragent-runtime", daemon=True)
        self._thread.start()
        if not self._ready.wait(timeout=30):
            raise RuntimeError("OurAgent runtime did not become ready within 30 seconds")

    def _run(self) -> None:
        from agent_runtime.engine import run_engine

        run_engine(
            plan_only=self.plan_only,
            initial_instruction=None,
            once=False,
            command_file=str(self.command_file),
            interrupt_prompt=False,
            listen=True,
            auto_accept_feedback=self.auto_accept_feedback,
            ready_event=self._ready,
            render_stream=self.render_stream,
            print_banner=self.print_banner,
            print_divider=self.print_divider,
        )
