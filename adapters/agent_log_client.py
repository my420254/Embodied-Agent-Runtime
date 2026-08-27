from __future__ import annotations

import json
import urllib.error
import urllib.request


class AgentLogSender:
    """提示日志发送客户端（HTTP 直推到 genesis_arm 的 /agent_log）。

    实现 ``interfaces.LogSink`` 协议（``emit(text) -> (ok, msg)``）。传输是同步
    HTTP，设计上由上层 QueueListener 在后台线程调用，避免阻塞 agent 主流程；
    因此这里保持简单同步实现，并用较短超时避免后台线程长时间挂起。
    """

    def __init__(self, host: str = "localhost", port: int = 5001, timeout: float = 2.0) -> None:
        self.url = "http://%s:%d/agent_log" % (host, port)
        self.timeout = timeout
        # The frontend is an internal same-host service; never route these POSTs
        # through an HTTP proxy (http_proxy/all_proxy would otherwise misdirect
        # localhost traffic and silently drop every log line).
        self._opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def emit(self, text: str) -> tuple[bool, str]:
        """推送一条提示日志，返回 (ok: bool, msg: str)。"""
        if not isinstance(text, str):
            try:
                text = str(text)
            except Exception:
                return False, "text 无法转为字符串"
        text = text.strip()
        if not text:
            return False, "日志内容为空"

        payload = json.dumps({"text": text}).encode("utf-8")
        req = urllib.request.Request(
            self.url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self._opener.open(req, timeout=self.timeout) as resp:
                return True, "%d %s" % (resp.status, resp.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            return False, "HTTP %s: %s" % (e.code, e.read().decode("utf-8", "replace"))
        except Exception as e:  # noqa: BLE001
            return False, str(e)
