from __future__ import annotations

import copy
import importlib
from dataclasses import dataclass, field
from typing import Any

from domain.task_environment import (
    add_goal_entities_to_required_item_names,
    build_task_environment_closure,
    scene_entity_catalog,
)

__all__ = [
    "PreparedTaskEnvironment",
    "add_goal_entities_to_required_item_names",
    "align_structured_task_for_environment",
    "build_sandbox_environment",
    "build_task_environment",
    "prepared_evaluation_context",
    "prepared_task_context",
    "scene_entity_catalog",
]


@dataclass(frozen=True)
class PreparedTaskEnvironment:
    instruction: str
    scene: dict[str, Any] | None
    env_state: dict[str, Any]
    entity_catalog: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    task_environment_module: str = ""


def _load_task_environment_module(prepared: PreparedTaskEnvironment):
    module_name = str(getattr(prepared, "task_environment_module", "") or "").strip()
    if not module_name:
        return None
    return importlib.import_module(module_name)


# 构建任务环境。benchmark 可覆盖 build_task_environment；默认实现只用
# understanding 输出的实体名称，从 benchmark 全量原始环境中查出任务闭包环境。
def build_task_environment(
    case_input: dict[str, Any],
    structured_task: dict[str, Any],
    prepared: PreparedTaskEnvironment,
) -> dict[str, Any]:
    module = _load_task_environment_module(prepared)
    if module is not None and hasattr(module, "build_task_environment"):
        return module.build_task_environment(
            case_input,
            structured_task,
            prepared,
        )

    return build_task_environment_closure(
        prepared.scene,
        structured_task,
        prepared.env_state,
    )


def build_sandbox_environment(
    case_input: dict[str, Any],
    structured_task: dict[str, Any],
    prepared: PreparedTaskEnvironment,
    task_environment: dict[str, Any],
) -> dict[str, Any]:
    module = _load_task_environment_module(prepared)
    if module is not None and hasattr(module, "build_sandbox_environment"):
        return module.build_sandbox_environment(
            case_input,
            structured_task,
            prepared,
            task_environment,
        )
    return task_environment


def align_structured_task_for_environment(
    case_input: dict[str, Any],
    structured_task: dict[str, Any],
    prepared: PreparedTaskEnvironment,
) -> dict[str, Any]:
    module = _load_task_environment_module(prepared)
    if module is not None and hasattr(module, "align_structured_task"):
        return module.align_structured_task(case_input, structured_task, prepared)
    return structured_task


def prepared_task_context(prepared: PreparedTaskEnvironment) -> dict[str, Any]:
    context = prepared.context if isinstance(prepared.context, dict) else {}
    value = context.get("task_context")
    task_context = dict(value) if isinstance(value, dict) else {}
    task_context.setdefault("available_entities", list(prepared.entity_catalog or []))
    return task_context


def prepared_evaluation_context(prepared: PreparedTaskEnvironment) -> dict[str, Any]:
    context = prepared.context if isinstance(prepared.context, dict) else {}
    value = context.get("evaluation_context")
    return copy.deepcopy(value) if isinstance(value, dict) else {}
