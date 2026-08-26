from __future__ import annotations
from importlib import import_module

from config.llms import llm_trace_context
from config.module_loader import call_configured_module_function
from .base import FeatureContext, FeatureResult

try:
    from langchain_core.messages import SystemMessage
except Exception:  # pragma: no cover - fallback for lean test environments
    class _Message:  # type: ignore[no-redef]
        def __init__(self, content: str):
            self.content = content

    class SystemMessage(_Message):
        pass


def _understanding_node():
    # Import lazily so tests that monkeypatch graph.understanding.node keep working.
    return import_module("graph.understanding.node")


def _parse_llm_json(content: str) -> dict:
    node = _understanding_node()
    try:
        parsed = node.parse_json_from_llm(content, fallback={})
    except TypeError:
        parsed = node.parse_json_from_llm(content)
    except Exception:
        parsed = {}
    return parsed if isinstance(parsed, dict) else {}


PROMPT_INPUTS_MODULE = "graph.prompt_inputs"


def run(context: FeatureContext, result: FeatureResult) -> FeatureResult:
    if result.get("stop_pipeline"):
        return {}

    node = _understanding_node()
    system_inputs = call_configured_module_function(
        ("files", "prompt_inputs_module"),
        PROMPT_INPUTS_MODULE,
        "build_understanding_system_inputs",
        context,
        result,
    )
    system_prompt = node.render_prompt(
        "understanding.system",
        **system_inputs,
    )

    valid_messages = [msg for msg in context.get("messages", []) if hasattr(msg, "content")]
    if len(valid_messages) > 4:
        valid_messages = valid_messages[-4:]

    with llm_trace_context(
        process_name="understanding",
        prompt_name="understanding.system",
        call_stage="llm_extract",
    ):
        response = node.get_understanding_llm().invoke([SystemMessage(content=system_prompt)] + valid_messages)
    parsed = _parse_llm_json(response.content)

    if not parsed:
        print("[理解层] JSON解析异常。")
        return {
            "is_complete": False,
            "clarification_question": "抱歉，系统没听清，请再说一遍您的指令。",
        }

    return parsed
