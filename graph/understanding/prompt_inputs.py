from __future__ import annotations

import json
from importlib import import_module
from typing import Any

from skills.loader import load_enabled_skill_specs

def _understanding_node():
    return import_module("graph.understanding.node")


def _feature_flags(context: dict[str, Any]) -> dict[str, Any]:
    runtime_options = context.get("runtime_options", {}) or {}
    flags = runtime_options.get("feature_flags") if isinstance(runtime_options, dict) else {}
    return flags if isinstance(flags, dict) else {}


def _scene_entities_json(context: dict[str, Any]) -> str:
    return json.dumps(list(context.get("scene_entities", [])), ensure_ascii=False)


def _json_pretty(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def _runtime_options(context: dict[str, Any]) -> dict[str, Any]:
    options = context.get("runtime_options", {})
    return options if isinstance(options, dict) else {}


def _available_skills_json() -> str:
    skills = []
    try:
        specs = load_enabled_skill_specs()
    except Exception:
        specs = []
    for spec in specs:
        skills.append(
            {
                "name": spec.name,
                "description": spec.description,
                "planning_contract": dict(getattr(spec, "planning_contract", {}) or {}),
            }
        )
    return json.dumps(skills, ensure_ascii=False, indent=2, default=str)


def build_understanding_system_inputs(context: dict[str, Any], result: dict[str, Any] | None = None) -> dict[str, Any]:
    node = _understanding_node()
    flags = _feature_flags(context)
    playbook = "" if not bool(flags.get("playbook_retrieval", True)) else node.load_understanding_playbook()
    options = _runtime_options(context)
    task_context = options.get("task_context", {})
    return {
        "valid_names_json": _scene_entities_json(context),
        "system_rules": node.load_system_rules(),
        "playbook": playbook,
        "task_context_json": _json_pretty(task_context if isinstance(task_context, dict) else {}),
        "available_skills_json": _available_skills_json(),
    }


UNDERSTANDING_PROMPT_INPUT_BUILDERS = {
    "understanding.system": build_understanding_system_inputs,
}
