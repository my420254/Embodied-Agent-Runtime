from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
import os
from ipaddress import ip_address
from typing import Any
from urllib.parse import urlparse, urlunparse

import httpx
from config.settings import active_config_file, get_config, get_model_config
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI, OpenAI
from openai import OpenAI as OpenAIClient

_LLM_CACHE = {}
_LLM_TRACE = []
_LLM_TRACE_CONTEXT: ContextVar[dict] = ContextVar("llm_trace_context", default={})


def _is_local_model_base_url(base_url: str | None) -> bool:
    value = str(base_url or "").strip()
    if not value:
        return False
    try:
        host = (urlparse(value).hostname or "").strip()
    except Exception:
        return False
    if not host:
        return False
    if host in {"localhost", "127.0.0.1"}:
        return True
    try:
        return ip_address(host).is_private
    except ValueError:
        return False


def _resolve_request_timeout(config: dict) -> float:
    """Read-timeout budget for a single LLM request. Falls back to 300s."""
    try:
        value = float(config.get("timeout") or 0.0)
    except (TypeError, ValueError):
        value = 0.0
    return value if value > 0 else 300.0


def _with_local_http_client(config: dict) -> dict:
    patched = dict(config)
    if patched.get("base_url"):
        patched["base_url"] = _normalize_base_url(str(patched.get("base_url")))
    if _is_local_model_base_url(patched.get("base_url")) and "http_client" not in patched:
        read_timeout = _resolve_request_timeout(patched)
        patched["http_client"] = httpx.Client(
            trust_env=False,
            timeout=httpx.Timeout(read_timeout, connect=15.0),
        )
        patched.setdefault("max_retries", 0)
    return patched


def _normalize_base_url(base_url: str | None) -> str:
    value = str(base_url or "").strip()
    if not value:
        return value
    preferred_host = str(
        os.getenv("OURAGENT_LLM_STICKY_HOST")
        or os.getenv("OURAGENT_LLM_BASE_HOST")
        or ""
    ).strip()
    if not preferred_host:
        return value
    try:
        parsed = urlparse(value)
    except Exception:
        return value
    current_host = (parsed.hostname or "").strip()
    if not current_host or current_host == preferred_host or parsed.port is None:
        return value
    if not _is_local_model_base_url(value):
        return value
    return urlunparse(parsed._replace(netloc=f"{preferred_host}:{parsed.port}"))


def model_root_config() -> dict[str, Any]:
    value = get_config("model", default={}) or {}
    return value if isinstance(value, dict) else {}


def configured_endpoints() -> dict[str, Any]:
    value = model_root_config().get("endpoints", {})
    return value if isinstance(value, dict) else {}


def api_base_for_port(port: int) -> str:
    cfg = model_root_config()
    host = str(cfg.get("base_host") or "192.168.27.250")
    template = str(cfg.get("base_path_template") or "http://{host}:{port}/v1")
    return _normalize_base_url(template.format(host=host, port=int(port)))


def default_api_model(module: str = "planning") -> str:
    module_cfg = get_model_config(module)
    return str(module_cfg.get("model") or model_root_config().get("model_name") or "").strip()


def generation_defaults(module: str = "planning") -> dict[str, Any]:
    module_cfg = get_model_config(module)
    return {
        "max_tokens": int(module_cfg.get("max_tokens", 4096)),
        "temperature": float(module_cfg.get("temperature", 0.0)),
    }


def endpoint_for_port(port: int) -> dict[str, Any]:
    endpoint = configured_endpoints().get(str(int(port)), {})
    return endpoint if isinstance(endpoint, dict) else {}


def api_model_for_port(port: int, *, module: str = "planning", fallback: str = "") -> str:
    return str(endpoint_for_port(port).get("model_name") or fallback or default_api_model(module)).strip()


def api_key_for_port(port: int, *, module: str = "planning", fallback: str = "") -> str:
    module_cfg = get_model_config(module)
    return str(endpoint_for_port(port).get("api_key") or fallback or module_cfg.get("api_key") or model_root_config().get("api_key") or "EMPTY")


def enabled_ports_for_model(model_name: str) -> list[int]:
    target = str(model_name or "").strip()
    found: list[int] = []
    for port_str, endpoint in sorted(configured_endpoints().items(), key=lambda item: int(item[0])):
        if not isinstance(endpoint, dict) or not bool(endpoint.get("enabled", False)):
            continue
        if target and str(endpoint.get("model_name", "") or "").strip() != target:
            continue
        try:
            found.append(int(port_str))
        except ValueError:
            continue
    return found


def resolve_llm_endpoint_slots(
    ports: list[int],
    *,
    workers: int = 1,
    module: str = "planning",
    api_model: str = "",
    api_key: str = "",
    allow_auto_ports: bool = False,
) -> list[dict[str, Any]]:
    desired_model = str(api_model or default_api_model(module) or "").strip()
    resolved_ports = [int(port) for port in ports]
    if not resolved_ports and allow_auto_ports:
        resolved_ports = enabled_ports_for_model(desired_model)
    if not resolved_ports:
        raise SystemExit(f"需要至少一个端口，例如 --ports 18003；当前默认模型为 {desired_model or '<empty>'}")

    generation = generation_defaults(module)
    slot_count = max(1, int(workers or 1), len(resolved_ports))
    slots: list[dict[str, Any]] = []
    for index in range(slot_count):
        port = int(resolved_ports[index % len(resolved_ports)])
        slots.append(
            {
                "index": index,
                "port": port,
                "api_base": api_base_for_port(port),
                "api_key": str(api_key or api_key_for_port(port, module=module)),
                "api_model": str(api_model or api_model_for_port(port, module=module, fallback=desired_model) or desired_model),
                "max_tokens": int(generation.get("max_tokens", 4096)),
                "temperature": float(generation.get("temperature", 0.0)),
            }
        )
    return slots


def chat_completion_text(
    *,
    prompt: str,
    api_base: str,
    api_key: str,
    model_name: str,
    max_tokens: int,
    temperature: float,
    timeout: float = 900.0,
    module: str = "planning",
) -> str:
    client = OpenAIClient(
        base_url=_normalize_base_url(api_base),
        api_key=api_key,
        timeout=timeout,
        max_retries=1,
        http_client=httpx.Client(timeout=timeout, trust_env=False),
    )
    request = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    extra_body = get_model_config(module).get("extra_body")
    if isinstance(extra_body, dict):
        request["extra_body"] = extra_body
    response = client.chat.completions.create(**request)
    return response.choices[0].message.content or ""


def _is_transient_connection_error(exc: Exception) -> bool:
    """True for connect/network errors worth one quick retry; False for
    generation timeouts (retrying those just burns another full budget)."""
    if isinstance(exc, (httpx.ConnectError, httpx.ConnectTimeout, httpx.RemoteProtocolError)):
        return True
    if isinstance(exc, (httpx.ReadTimeout, httpx.WriteTimeout, httpx.PoolTimeout)):
        return False
    message = str(exc).lower()
    if "connection error" in message or "connection refused" in message:
        return True
    if "timed out" in message or "timeout" in message:
        return False
    return False


def llm_trace_enabled() -> bool:
    value = os.getenv("OURAGENT_TRACE_LLM_IO", "")
    if value.strip().lower() in {"1", "true", "yes", "on"}:
        return True
    return bool(get_config("benchmark", "trace_llm_io", default=False))


def reset_llm_trace() -> None:
    _LLM_TRACE.clear()


def get_llm_trace() -> list:
    return list(_LLM_TRACE)


@contextmanager
def llm_trace_context(**metadata):
    cleaned = {str(key): value for key, value in metadata.items() if value not in (None, "")}
    current = _LLM_TRACE_CONTEXT.get() or {}
    token = _LLM_TRACE_CONTEXT.set({**current, **cleaned})
    try:
        yield
    finally:
        _LLM_TRACE_CONTEXT.reset(token)


class CompletionLLMAdapter:
    def __init__(self, **config):
        self._config = dict(config)
        self.llm = OpenAI(**_with_local_http_client(config))

    @classmethod
    def _to_prompt(cls, messages) -> str:
        if isinstance(messages, str):
            return messages
        if hasattr(messages, "content"):
            messages = [messages]

        sections = []
        latest_user = ""
        prior_outputs = []
        for message in messages or []:
            content = getattr(message, "content", str(message))
            message_type = str(getattr(message, "type", "") or "").lower()
            if message_type == "system":
                sections.append(str(content).strip())
            elif message_type == "ai":
                prior_outputs.append(str(content).strip())
            else:
                latest_user = str(content).strip()
        if prior_outputs:
            sections.append("Validated plan prefix JSON:\n" + "\n".join(prior_outputs))
        if latest_user:
            sections.append("Current request:\n" + latest_user)
        sections.append("Output exactly one JSON object below and stop after the closing brace:\n")
        return "\n\n".join(section for section in sections if section)

    def invoke(self, messages):
        prompt = self._to_prompt(messages)
        try:
            return AIMessage(content=self.llm.invoke(prompt))
        except Exception as exc:
            if not _is_transient_connection_error(exc):
                raise
            refreshed = _with_local_http_client(self._config)
            self.llm = OpenAI(**refreshed)
            return AIMessage(content=self.llm.invoke(prompt))

    def trace_input(self, messages):
        return self._to_prompt(messages)


def _message_to_trace(message) -> dict:
    return {
        "type": str(getattr(message, "type", "")),
        "content": getattr(message, "content", str(message)),
    }


class TracedLLMAdapter:
    def __init__(self, *, name: str, style: str, llm):
        self.name = name
        self.style = style
        self.llm = llm

    def invoke(self, messages):
        if hasattr(self.llm, "trace_input"):
            trace_input = self.llm.trace_input(messages)
        else:
            trace_input = messages if isinstance(messages, str) else [_message_to_trace(message) for message in (messages or [])]
        response = self.llm.invoke(messages)
        entry = {
            "module": self.name,
            "api_style": self.style,
            "input": trace_input,
            "output": getattr(response, "content", str(response)),
        }
        context = _LLM_TRACE_CONTEXT.get() or {}
        if context:
            entry["trace_context"] = dict(context)
            for key in ("process_name", "prompt_name", "call_stage", "attempt", "planning_iteration"):
                if key in context:
                    entry[key] = context[key]
        _LLM_TRACE.append(entry)
        return response


class ResilientChatLLMAdapter:
    def __init__(self, **config):
        self._config = dict(config)
        self.llm = ChatOpenAI(**_with_local_http_client(config))

    def invoke(self, messages):
        try:
            return self.llm.invoke(messages)
        except Exception as exc:
            if not _is_transient_connection_error(exc):
                raise
            refreshed = _with_local_http_client(self._config)
            self.llm = ChatOpenAI(**refreshed)
            return self.llm.invoke(messages)


def get_llm(name: str):
    config = get_model_config(name)
    style = str(config.pop("api_style", "chat") or "chat").strip().lower()
    cache_key = f"{active_config_file()}:{name}:{style}"
    if cache_key not in _LLM_CACHE:
        llm_class = CompletionLLMAdapter if style == "completion" else ResilientChatLLMAdapter
        llm = llm_class(**config)
        _LLM_CACHE[cache_key] = TracedLLMAdapter(name=name, style=style, llm=llm) if llm_trace_enabled() else llm
    return _LLM_CACHE[cache_key]


def get_understanding_llm():
    return get_llm("understanding")


def get_planning_llm():
    return get_llm("planning")


def get_execution_llm():
    return get_llm("execution")


def get_reflection_llm():
    return get_llm("reflection")
