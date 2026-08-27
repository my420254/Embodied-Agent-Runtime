from __future__ import annotations

import copy
import json
from importlib import import_module
from typing import Any

from config.llms import llm_trace_context
from .base import FeatureContext, FeatureResult

try:
    from langchain_core.messages import HumanMessage, SystemMessage
except Exception:  # pragma: no cover - fallback for lean test environments

    class _Message:  # type: ignore[no-redef]
        def __init__(self, content: str):
            self.content = content

    class HumanMessage(_Message):
        pass

    class SystemMessage(_Message):
        pass


PROMPT_NAME = "understanding.final_state"


def _understanding_node():
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


def _json_pretty(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def _feature_settings(context: FeatureContext) -> dict[str, Any]:
    settings = context.get("feature_settings", {})
    if not isinstance(settings, dict):
        return {}
    raw = settings.get("goal_state_extract", {})
    return raw if isinstance(raw, dict) else {}


def _enabled(settings: dict[str, Any]) -> bool:
    return bool(settings.get("enabled", False))


def _scene_entities(context: FeatureContext) -> list[str]:
    return [
        str(name)
        for name in context.get("scene_entities", [])
        if str(name or "").strip()
    ]


def _runtime_task_context(context: FeatureContext) -> dict[str, Any]:
    runtime_options = context.get("runtime_options", {})
    if not isinstance(runtime_options, dict):
        return {}
    task_context = runtime_options.get("task_context", {})
    return task_context if isinstance(task_context, dict) else {}


def _current_structured_task(result: FeatureResult) -> dict[str, Any]:
    structured = result.get("structured_task", {})
    return structured if isinstance(structured, dict) else {}


def _current_final_state(structured: dict[str, Any]) -> Any:
    value = structured.get("final_state")
    if value not in (None, "", {}, []):
        return value
    return {}


def _extract_final_state(parsed: dict[str, Any]) -> Any:
    if not isinstance(parsed, dict):
        return {}
    structured = parsed.get("structured_task", {})
    if isinstance(structured, dict):
        value = structured.get("final_state")
        if value not in (None, "", {}, []):
            return copy.deepcopy(value)
        if structured:
            return copy.deepcopy(structured)
    value = parsed.get("final_state")
    if value not in (None, "", {}, []):
        return copy.deepcopy(value)
    return copy.deepcopy(parsed) if parsed else {}


def _build_prompt_inputs(
    context: FeatureContext, result: FeatureResult, *, feedback: str, attempt: int
) -> dict[str, str]:
    from graph.understanding.prompt_inputs import environment_closure_json

    structured = _current_structured_task(result)
    selection = {
        "structured_task": structured,
        "current_final_state": _current_final_state(structured),
        "scene_entities": _scene_entities(context),
    }
    return {
        "task": str(context.get("task", "")),
        "scene_entities_json": _json_pretty(_scene_entities(context)),
        "environment_closure_json": environment_closure_json(context),
        "current_structured_task_json": _json_pretty(structured),
        "current_selection_json": _json_pretty(selection),
        "task_context_json": _json_pretty(_runtime_task_context(context)),
        "attempt_feedback": feedback,
        "attempt_index": str(attempt),
    }


def run(context: FeatureContext, result: FeatureResult) -> FeatureResult:
    if result.get("stop_pipeline") or result.get("is_cancel_all"):
        return {}
    if result.get("needs_clarification") or result.get("is_complete") is False:
        return {}

    settings = _feature_settings(context)
    if not _enabled(settings):
        return {}

    structured = copy.deepcopy(_current_structured_task(result))
    existing_final_state = _current_final_state(structured)
    if existing_final_state and not bool(settings.get("force", False)):
        structured["final_state"] = existing_final_state
        return {
            "structured_task": structured,
            "goal_state_extract": {
                "enabled": True,
                "source": "existing",
            },
        }

    max_attempts = int(settings.get("max_attempts", 2) or 2)
    if max_attempts < 1:
        max_attempts = 1

    node = _understanding_node()
    feedback = str(settings.get("initial_feedback", "") or "")
    last_parsed: dict[str, Any] = {}
    last_final_state: Any = {}
    used_attempts = 0
    for attempt in range(1, max_attempts + 1):
        used_attempts = attempt
        prompt_inputs = _build_prompt_inputs(
            context, result, feedback=feedback, attempt=attempt
        )
        system_prompt = node.render_prompt(PROMPT_NAME, **prompt_inputs)
        with llm_trace_context(
            process_name="understanding",
            prompt_name=PROMPT_NAME,
            call_stage="goal_state_extract",
            attempt=attempt,
        ):
            response = node.get_understanding_llm().invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(
                        content="请抽取任务完成后的关键 final_state，并只返回 JSON。"
                    ),
                ]
            )
        parsed = _parse_llm_json(response.content)
        if not parsed:
            feedback = "模型输出不是可解析 JSON，请只返回 JSON。"
            if attempt < max_attempts:
                continue
            return {}

        final_state = _extract_final_state(parsed)
        last_parsed = parsed
        last_final_state = final_state
        if not final_state:
            feedback = "请输出 final_state。"
            if attempt < max_attempts:
                continue
            return {}
        break

    structured["final_state"] = copy.deepcopy(last_final_state)
    return {
        "structured_task": structured,
        "goal_state_extract": {
            "enabled": True,
            "source": "llm",
            "attempts": used_attempts if last_parsed else 0,
            "raw": last_parsed,
        },
    }


__all__ = ["run"]
