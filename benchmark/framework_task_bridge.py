from __future__ import annotations

import copy
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from langchain_core.messages import HumanMessage
from config.llms import get_llm_trace, llm_trace_enabled, reset_llm_trace
from config.project_io import load_project_json
from config.settings import activate_config, active_config_file, get_config
from graph.planning.config import with_planning_config
from benchmark.reporting.trace_payloads import (
    case_input_summary as _case_input_summary,
    compact_value as _compact_value,
    planning_input_payload as _planning_input_payload,
    planning_input_summary as _planning_input_summary,
    planning_output_payload as _planning_output_payload,
    planning_output_summary as _planning_output_summary,
    prepared_payload as _prepared_payload,
    prepared_summary as _prepared_summary,
    understanding_input_payload as _understanding_input_payload,
    understanding_input_summary as _understanding_input_summary,
    understanding_output_payload as _understanding_output_payload,
    understanding_output_summary as _understanding_output_summary,
)
from benchmark.task_environment_bridge import (
    align_structured_task_for_environment,
    build_sandbox_environment,
    build_task_environment,
    prepared_evaluation_context,
    prepared_task_context,
)
from re_trac import initial_trace_state

_UNDERSTANDING_GRAPH = None
_PLANNING_GRAPH = None


@dataclass(frozen=True)
class BenchmarkStageConfig:
    understanding: str = "enabled"
    planning: str = "enabled"
    task_management: str = "disabled"
    reflection: str = "disabled"


@dataclass(frozen=True)
class BenchmarkRuntimeConfig:
    """Benchmark-local adapter config used only to enter the core framework."""

    name: str
    module_name: str
    settings_file: str = ""
    stage_config: BenchmarkStageConfig = field(default_factory=BenchmarkStageConfig)
    todo_output_parser: str = ""
    todo_step_adapter: str = ""
    todo_list_validator: str = ""
    allowed_input_fields: dict[str, list[str]] = field(default_factory=dict)


def _settings_file_from_case_input(case_input: dict[str, Any]) -> str:
    for key in ("benchmark_settings_file", "settings_file"):
        value = str(case_input.get(key) or "").strip()
        if value:
            return value
    return ""


def _runtime_name(settings_file: str, module_name: str) -> str:
    configured = str(get_config("benchmark", "name", default="") or "").strip()
    if configured:
        return configured
    if module_name:
        return str(module_name)
    return Path(settings_file).stem if settings_file else ""


def load_benchmark_runtime_config(
    module_name: str = "",
    *,
    settings_file: str | os.PathLike[str] | None = None,
) -> BenchmarkRuntimeConfig:
    """Load benchmark runtime from an explicitly selected settings file."""

    settings_path = str(settings_file or "").strip()
    activate_config(settings_path or None)
    if not settings_path:
        return BenchmarkRuntimeConfig(name="", module_name=module_name)

    runtime_raw = get_config("benchmark", "runtime", default={}) or {}
    runtime = runtime_raw if isinstance(runtime_raw, dict) else {}
    stage_raw = runtime.get("stages", {}) if isinstance(runtime.get("stages", {}), dict) else {}
    config = BenchmarkRuntimeConfig(
        name=_runtime_name(settings_path, module_name),
        module_name=module_name,
        settings_file=settings_path,
        stage_config=BenchmarkStageConfig(
            understanding=str(stage_raw.get("understanding", "enabled")),
            planning=str(stage_raw.get("planning", "enabled")),
            task_management=str(stage_raw.get("task_management", "disabled")),
            reflection=str(stage_raw.get("reflection", "disabled")),
        ),
        todo_output_parser=str(runtime.get("todo_output_parser", "")),
        todo_step_adapter=str(runtime.get("todo_step_adapter", "")),
        todo_list_validator=str(runtime.get("todo_list_validator", "")),
        allowed_input_fields=runtime.get("allowed_input_fields", {}) if isinstance(runtime.get("allowed_input_fields", {}), dict) else {},
    )
    _validate_benchmark_prompt_coverage(config)
    return config


def _bool_flags(value: Any) -> dict[str, bool]:
    if not isinstance(value, dict):
        return {}
    return {str(key): bool(flag) for key, flag in value.items()}


def _benchmark_feature_flags() -> dict[str, bool]:
    """Return graph switches from the currently active settings.json."""
    raw_active = load_project_json(active_config_file(), fallback={})
    if isinstance(raw_active, dict):
        benchmark = raw_active.get("benchmark", {})
        if isinstance(benchmark, dict) and isinstance(benchmark.get("feature_flags"), dict):
            return _bool_flags(benchmark.get("feature_flags"))
    return _bool_flags(get_config("benchmark", "feature_flags", default={}) or {})


def _benchmark_trace_enabled() -> bool:
    value = os.getenv("OURAGENT_BENCHMARK_TRACE", "")
    if value.strip().lower() in {"1", "true", "yes", "on"}:
        return True
    return bool(get_config("benchmark", "trace", default=False))


def _benchmark_config_from_case_input(case_input: dict[str, Any]):
    module_hint = str(case_input.get("benchmark_module", "")).strip()
    settings_file = _settings_file_from_case_input(case_input)
    return load_benchmark_runtime_config(module_hint, settings_file=settings_file)


def _stage_enabled(mode: str) -> bool:
    return str(mode or "enabled").strip().lower() not in {"disabled", "off", "skip"}


def _feature_enabled_in_config(feature_name: str, *, default: bool = False) -> bool:
    value = get_config("benchmark", "feature_flags", feature_name, default=None)
    if value is None:
        value = get_config("planning", "features", feature_name, default=default)
    return bool(value)


def _understanding_feature_enabled(feature_name: str, *, default_setting: bool = True) -> bool:
    enabled = get_config("understanding", "features", "enabled_features", default=[]) or []
    if isinstance(enabled, list) and feature_name not in {str(item) for item in enabled}:
        return False
    settings = get_config("understanding", "features", "settings", feature_name, default={}) or {}
    if not isinstance(settings, dict):
        return default_setting
    return bool(settings.get("enabled", default_setting))


def _validate_benchmark_prompt_coverage(benchmark_config: BenchmarkRuntimeConfig) -> None:
    if not str(benchmark_config.settings_file or "").strip():
        return
    prompt_file = str(get_config("files", "prompts", default="") or "").strip()
    prompts = load_project_json(prompt_file, fallback={})
    if not isinstance(prompts, dict) or not prompts:
        raise ValueError(f"{benchmark_config.name} benchmark prompt file is missing or empty: {prompt_file}")

    required: list[str] = []
    if _stage_enabled(benchmark_config.stage_config.understanding):
        required.append("understanding.system")
        if _understanding_feature_enabled("entity_repair", default_setting=True):
            required.append("understanding.entity_repair")
        if _understanding_feature_enabled("goal_state_extract", default_setting=False):
            required.append("understanding.final_state")
    if _stage_enabled(benchmark_config.stage_config.planning):
        required.extend(["planning.main_system", "planning.repair_user"])
        if _feature_enabled_in_config("state_diff_audit", default=False):
            required.append("planning.state_diff_audit")
        repair_strategy = str(get_config("planning", "evaluation", "repair_strategy", default="") or "").strip().lower()
        if repair_strategy == "vcr":
            required.append("planning.counterfactual_task_completion")
        if _feature_enabled_in_config("semantic_audit", default=False):
            required.append("planning.audit")

    missing = [key for key in required if key not in prompts]
    if missing:
        raise ValueError(
            f"{benchmark_config.name} benchmark prompt file must override required prompts: "
            f"{', '.join(missing)}; prompt_file={prompt_file}"
        )


def _benchmark_mode_enabled(benchmark_config) -> bool:
    return bool(str(getattr(benchmark_config, "name", "") or "").strip())


def _validate_benchmark_scene(prepared, benchmark_config) -> None:
    if not _benchmark_mode_enabled(benchmark_config):
        return
    if not isinstance(prepared.scene, dict) or not prepared.scene:
        name = str(getattr(benchmark_config, "name", "") or "benchmark")
        raise ValueError(
            f"{name} framework run requires a benchmark-local environment source."
        )


def _allowed_benchmark_fields(benchmark_config, stage: str) -> set[str] | None:
    bucket = benchmark_config.allowed_input_fields.get(stage, [])
    if not isinstance(bucket, list) or not bucket:
        return None
    return {str(item) for item in bucket if item}


def _filter_case_input_payload(case_input: dict[str, Any], allowed_fields: set[str] | None) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, value in case_input.items():
        if allowed_fields is not None and str(key) not in allowed_fields:
            continue
        if key in {"init_graph", "scene_graph"}:
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            payload[str(key)] = value
            continue
        if isinstance(value, (list, dict)):
            payload[str(key)] = value
            continue
        payload[str(key)] = str(value)
    return payload


def _benchmark_primary_instruction(case_input: dict[str, Any], fallback_instruction: str) -> str:
    instruction = case_input.get("instruction") or case_input.get("task_desc") or fallback_instruction
    return str(instruction or "")


def _drop_benchmark_alternatives(structured_task: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(structured_task, dict):
        return structured_task
    required = structured_task.get("required_item_names")
    if not isinstance(required, dict):
        return structured_task
    normalized = {
        **structured_task,
        "required_item_names": {
            **required,
        },
    }
    for bucket_name in ("targets", "tools", "receptacles"):
        bucket = normalized["required_item_names"].get(bucket_name)
        if not isinstance(bucket, dict):
            continue
        normalized["required_item_names"][bucket_name] = {
            "primary": list(bucket.get("primary", []) or []),
            "alternatives": [],
        }
    return normalized


def understanding_graph():
    global _UNDERSTANDING_GRAPH
    if _UNDERSTANDING_GRAPH is None:
        from graph.understanding.node import build_understanding_graph

        _UNDERSTANDING_GRAPH = build_understanding_graph()
    return _UNDERSTANDING_GRAPH


def planning_graph():
    global _PLANNING_GRAPH
    if _PLANNING_GRAPH is None:
        from graph.planning.node import build_planning_graph

        _PLANNING_GRAPH = build_planning_graph()
    return _PLANNING_GRAPH


def run_prepared_understanding_and_planning(
    *,
    case_input: dict[str, Any],
    prepared,
    understanding_graph_runner: Callable[[], Any],
    planning_graph_runner: Callable[[], Any],
    state_overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    benchmark_config = _benchmark_config_from_case_input(case_input)
    _validate_benchmark_scene(prepared, benchmark_config)
    feature_flags = _benchmark_feature_flags()
    understanding_allowed_fields = _allowed_benchmark_fields(benchmark_config, "understanding")
    planning_allowed_fields = _allowed_benchmark_fields(benchmark_config, "planning")
    trace_enabled = _benchmark_trace_enabled()
    if trace_enabled and llm_trace_enabled():
        reset_llm_trace()
    normalized_case_input = {**case_input, "instruction": prepared.instruction}
    framework_input_text = _benchmark_primary_instruction(normalized_case_input, prepared.instruction)
    if not framework_input_text:
        raise ValueError("benchmark case is missing an instruction field")
    framework_input_text = str(framework_input_text)
    state = {
        "messages": [HumanMessage(content=framework_input_text)],
        "raw_instruction": framework_input_text,
        "original_instruction": framework_input_text,
        "waiting_for_evaluation": False,
        "human_feedback": "",
        "feature_flags": feature_flags,
        "execution_status": "running",
        "iteration_count": 0,
        "reflection_retry_count": 0,
        "interrupt_signal": None,
        "allow_interrupt_input": False,
        "environment": {},
        "environment_source": {},
        **initial_trace_state(),
    }
    task_context = prepared_task_context(prepared)
    evaluation_context = prepared_evaluation_context(prepared)
    state.update(
        {
            "env_state": prepared.env_state,
            "task_source_text": framework_input_text,
            "task_input_payload": _filter_case_input_payload(normalized_case_input, understanding_allowed_fields),
            "task_context": task_context,
            "evaluation_context": evaluation_context,
            "environment": {},
            "environment_source": {},
        }
    )
    if state_overrides:
        state.update(state_overrides)

    trace = {}
    if trace_enabled:
        trace = {
            "stage_config": {
                "understanding": str(benchmark_config.stage_config.understanding),
                "planning": str(benchmark_config.stage_config.planning),
                "task_management": str(benchmark_config.stage_config.task_management),
                "reflection": str(benchmark_config.stage_config.reflection),
            },
            "case_input": _case_input_summary(normalized_case_input),
            "case_input_full": copy.deepcopy(normalized_case_input),
            "prepared_environment": _prepared_summary(prepared),
            "prepared_environment_full": _prepared_payload(prepared),
        }
    understanding_enabled = _stage_enabled(benchmark_config.stage_config.understanding)
    if not understanding_enabled:
        raise ValueError(
            f"{benchmark_config.name or 'benchmark'} framework config disables understanding; "
            "all benchmark framework runs must execute understanding before planning."
        )
    if trace_enabled:
        trace["understanding_input"] = _understanding_input_summary(state)
        trace["understanding_input_full"] = _understanding_input_payload(state)

    understood = understanding_graph_runner().invoke(state)
    if trace_enabled:
        trace["understanding_output"] = _understanding_output_summary(understood)
        trace["understanding_output_full"] = _understanding_output_payload(understood)
    if not understood.get("is_complete"):
        result = {
            **state,
            **understood,
            "todo_list": [],
            "is_feasible": False,
            "execution_status": "failed",
            "failure_layer": "understanding",
            "error_feedback": understood.get("clarification_question", "") or "understanding did not produce a complete structured task",
        }
        if trace_enabled:
            trace["planning_input"] = {}
            trace["planning_input_full"] = {}
            trace["planning_output"] = {}
            trace["planning_output_full"] = {}
            if llm_trace_enabled():
                trace["llm_io"] = get_llm_trace()
            result["benchmark_trace"] = trace
        return result

    structured_task = align_structured_task_for_environment(
        case_input,
        understood.get("structured_task", {}),
        prepared,
    )
    if feature_flags.get("drop_benchmark_alternatives", False) and not feature_flags.get("entity_repair_alternatives", False):
        structured_task = _drop_benchmark_alternatives(structured_task)
    if structured_task is not understood.get("structured_task"):
        understood = {
            **understood,
            "structured_task": structured_task,
        }
        if trace_enabled:
            trace["understanding_output"] = _understanding_output_summary(understood)
            trace["understanding_output_full"] = _understanding_output_payload(understood)

    environment_structured_task = copy.deepcopy(structured_task) if isinstance(structured_task, dict) else {}
    relevant_names = understood.get("relevant_item_names", [])
    if isinstance(relevant_names, list):
        environment_structured_task["_understanding_relevant_item_names"] = [
            str(name) for name in relevant_names if str(name or "").strip()
        ]

    task_environment = build_task_environment(
        case_input,
        environment_structured_task,
        prepared,
    )
    sandbox_environment = build_sandbox_environment(
        case_input,
        environment_structured_task,
        prepared,
        task_environment,
    )
    planning_state = {
        **state,
        **understood,
        "environment": sandbox_environment if isinstance(sandbox_environment, dict) and sandbox_environment else task_environment,
        "environment_source": {
            "builder": "build_sandbox_environment" if isinstance(sandbox_environment, dict) and sandbox_environment else "build_task_environment",
            "benchmark": str(getattr(benchmark_config, "name", "") or ""),
        },
        "todo_output_parser_path": str(getattr(benchmark_config, "todo_output_parser", "") or ""),
        "todo_step_adapter_path": str(getattr(benchmark_config, "todo_step_adapter", "") or ""),
        "todo_list_validator_path": str(getattr(benchmark_config, "todo_list_validator", "") or ""),
        "understanding_stage_executed": True,
        "benchmark_strict_feature_flags": True,
    }
    if planning_allowed_fields is not None:
        if "env_state" not in planning_allowed_fields:
            planning_state["env_state"] = {}
        if "task_environment_facts" not in planning_allowed_fields:
            planning_state["environment"] = {}
            planning_state["environment_source"] = {}
        if "task_context" not in planning_allowed_fields:
            planning_state["task_context"] = {}
        if "structured_task" not in planning_allowed_fields:
            planning_state["structured_task"] = {}
    planning_state = with_planning_config(planning_state)
    if trace_enabled:
        trace["planning_input"] = _planning_input_summary(planning_state)
        trace["planning_input_full"] = _planning_input_payload(planning_state)
    planned = planning_graph_runner().invoke(planning_state)
    result = {
        **understood,
        **planned,
    }
    if trace_enabled:
        trace["planning_output"] = _planning_output_summary(result)
        trace["planning_output_full"] = _planning_output_payload(result)
        if llm_trace_enabled():
            trace["llm_io"] = get_llm_trace()
        result["benchmark_trace"] = trace
    return result
