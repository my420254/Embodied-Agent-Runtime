from __future__ import annotations

import copy
import json
from importlib import import_module
from typing import Any

from config.llms import llm_trace_context
from .base import FeatureContext, FeatureResult
from .entity_relevance import flatten_entity_relevance, unique_names
from .normalize import collect_proposed_entities, normalize_name_bucket, normalize_structured_task

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


PROMPT_INPUTS_MODULE = "graph.prompt_inputs"
PROMPT_NAME = "understanding.entity_repair"

BUCKETS = ("targets", "tools", "receptacles")


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


def _feature_flags(context: FeatureContext) -> dict[str, Any]:
    runtime_options = context.get("runtime_options", {})
    if not isinstance(runtime_options, dict):
        return {}
    flags = runtime_options.get("feature_flags", {})
    return flags if isinstance(flags, dict) else {}


def _feature_settings(context: FeatureContext) -> dict[str, Any]:
    settings = context.get("feature_settings", {})
    if not isinstance(settings, dict):
        return {}
    raw = settings.get("entity_repair", {})
    return raw if isinstance(raw, dict) else {}


def _enabled(settings: dict[str, Any], flags: dict[str, Any]) -> bool:
    if "entity_repair" in flags:
        return bool(flags.get("entity_repair"))
    return bool(settings.get("enabled", True))


def _scene_entities(context: FeatureContext) -> list[str]:
    return [str(name) for name in context.get("scene_entities", []) if str(name or "").strip()]


def _scene_entity_set(context: FeatureContext) -> set[str]:
    return set(_scene_entities(context))


def _runtime_task_context(context: FeatureContext) -> dict[str, Any]:
    runtime_options = context.get("runtime_options", {})
    if not isinstance(runtime_options, dict):
        return {}
    task_context = runtime_options.get("task_context", {})
    return task_context if isinstance(task_context, dict) else {}


def _current_structured_task(result: FeatureResult) -> dict[str, Any]:
    structured = result.get("structured_task", {})
    return structured if isinstance(structured, dict) else {}


def _name_bucket(value: Any) -> dict[str, list[str]]:
    bucket = normalize_name_bucket(value)
    return {
        "primary": unique_names(bucket.get("primary", [])),
        "alternatives": unique_names(bucket.get("alternatives", [])),
    }


def _required_item_names(structured: dict[str, Any]) -> dict[str, Any]:
    required = structured.get("required_item_names", {})
    required = required if isinstance(required, dict) else {}
    return {
        "targets": _name_bucket(required.get("targets", {})),
        "tools": _name_bucket(required.get("tools", {})),
        "receptacles": _name_bucket(required.get("receptacles", {})),
    }


def _collect_entity_references(structured: dict[str, Any]) -> list[str]:
    refs = []
    refs.extend(collect_proposed_entities(structured.get("required_item_names", {}) if isinstance(structured.get("required_item_names", {}), dict) else {}))
    return unique_names(refs)


def _initial_entity_selection(result: FeatureResult) -> list[str]:
    structured = _current_structured_task(result)
    names: list[str] = []
    names.extend(_collect_entity_references(structured))
    names.extend(flatten_entity_relevance(result.get("entity_relevance", {})))
    relevant = result.get("relevant_item_names", [])
    if isinstance(relevant, list):
        names.extend(str(name) for name in relevant if name)
    return unique_names(names)


def _filter_names(names: list[str], valid_names: set[str]) -> list[str]:
    return unique_names([name for name in names if name in valid_names])


def _required_candidate_names(required_item_names: dict[str, Any], *, include_alternatives: bool) -> list[str]:
    names: list[str] = []
    for bucket_name in BUCKETS:
        bucket = required_item_names.get(bucket_name, {})
        if not isinstance(bucket, dict):
            bucket = {}
        normalized = _name_bucket(bucket)
        names.extend(normalized.get("primary", []))
        if include_alternatives:
            names.extend(normalized.get("alternatives", []))
    return unique_names(names)


def _quantity_constraints(structured: dict[str, Any]) -> list[dict[str, Any]]:
    raw = structured.get("quantity_constraints", [])
    if isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def _quantity_bucket_name(role: Any) -> str:
    normalized = str(role or "targets").strip().lower()
    if normalized in {"target", "targets", "object", "objects"}:
        return "targets"
    if normalized in {"tool", "tools"}:
        return "tools"
    if normalized in {"receptacle", "receptacles", "container", "containers", "location", "locations"}:
        return "receptacles"
    return "targets"


def _quantity_count(value: Any) -> int:
    try:
        count = int(value)
    except (TypeError, ValueError):
        return 0
    return max(count, 0)


def _quantity_constraint_issues(structured: dict[str, Any], valid_names: set[str]) -> list[str]:
    required = structured.get("required_item_names", {}) if isinstance(structured, dict) else {}
    if not isinstance(required, dict):
        required = {}
    issues: list[str] = []
    for constraint in _quantity_constraints(structured):
        count = _quantity_count(constraint.get("count"))
        if count <= 1:
            continue
        bucket_name = _quantity_bucket_name(constraint.get("role"))
        bucket = required.get(bucket_name, {})
        bucket = bucket if isinstance(bucket, dict) else {}
        selected: list[Any] = []
        primary = bucket.get("primary", [])
        if isinstance(primary, list):
            selected.extend(primary)
        constraint_selected = constraint.get("selected_entities", [])
        if isinstance(constraint_selected, list):
            selected.extend(constraint_selected)
        valid_selected = unique_names([str(name) for name in selected if str(name) in valid_names])
        if len(valid_selected) < count:
            object_type = str(constraint.get("object_type") or bucket_name)
            issues.append(f"{bucket_name}/{object_type} 需要 {count} 个不同实体，但只选到 {len(valid_selected)} 个")
    return issues


def _repair_required_item_names(
    structured: dict[str, Any],
    required_item_names: dict[str, Any],
    valid_names: set[str],
    *,
    max_alternatives_per_bucket: int,
) -> dict[str, Any]:
    repaired = copy.deepcopy(structured)
    repaired_required = repaired.setdefault("required_item_names", {})
    if not isinstance(repaired_required, dict):
        repaired_required = {}
        repaired["required_item_names"] = repaired_required

    for bucket_name in BUCKETS:
        bucket = required_item_names.get(bucket_name, {})
        if not isinstance(bucket, dict):
            bucket = {}
        primary = _filter_names(unique_names(bucket.get("primary", [])), valid_names)
        alternatives = _filter_names(unique_names(bucket.get("alternatives", [])), valid_names)
        alternatives = [name for name in alternatives if name not in primary][:max_alternatives_per_bucket]
        repaired_required[bucket_name] = {
            "primary": primary,
            "alternatives": alternatives,
        }

    return repaired


def _alternatives_enabled(settings: dict[str, Any], flags: dict[str, Any]) -> bool:
    if "entity_repair_alternatives" in flags:
        return bool(flags.get("entity_repair_alternatives"))
    if bool(flags.get("drop_benchmark_alternatives", False)):
        return False
    return bool(settings.get("alternatives_enabled", True))


def _max_alternatives_per_bucket(settings: dict[str, Any], flags: dict[str, Any]) -> int:
    if not _alternatives_enabled(settings, flags):
        return 0
    try:
        value = int(settings.get("max_alternatives_per_bucket", 2) or 0)
    except (TypeError, ValueError):
        value = 2
    return max(value, 0)


def _alternatives_instruction(max_alternatives_per_bucket: int) -> str:
    if max_alternatives_per_bucket <= 0:
        return "不要输出备选物品；targets/tools/receptacles 的 alternatives 必须都是空数组。"
    return f"每类最多给 {max_alternatives_per_bucket} 个替代品；替代品必须是真实存在且能承担同一任务角色的场景实体。"


def _normalize_output(
    parsed: dict[str, Any],
    result: FeatureResult,
    valid_names: set[str],
    *,
    max_alternatives_per_bucket: int,
) -> tuple[dict[str, Any], list[str], list[str], list[str]]:
    structured = _current_structured_task(result)
    parsed_structured = parsed.get("structured_task", {})
    if not isinstance(parsed_structured, dict):
        parsed_structured = {}

    merged = copy.deepcopy(structured)
    existing_final_state = copy.deepcopy(structured.get("final_state")) if isinstance(structured, dict) else {}
    if parsed_structured.get("intent"):
        merged["intent"] = str(parsed_structured.get("intent"))
    if isinstance(parsed_structured.get("quantity_constraints"), (dict, list)):
        merged["quantity_constraints"] = copy.deepcopy(parsed_structured.get("quantity_constraints"))

    parsed_required = parsed_structured.get("required_item_names", parsed.get("required_item_names", {}))
    if not isinstance(parsed_required, dict):
        parsed_required = {}
    invalid_required = [
        name
        for name in _required_candidate_names(parsed_required, include_alternatives=max_alternatives_per_bucket > 0)
        if name not in valid_names
    ]
    merged = _repair_required_item_names(
        merged,
        {
            "targets": parsed_required.get("targets", {}),
            "tools": parsed_required.get("tools", {}),
            "receptacles": parsed_required.get("receptacles", {}),
        },
        valid_names,
        max_alternatives_per_bucket=max_alternatives_per_bucket,
    )

    parsed_final_state = parsed_structured.get("final_state", parsed.get("final_state", {}))
    merged = normalize_structured_task(merged)
    if parsed_final_state not in (None, "", {}, []):
        merged["final_state"] = copy.deepcopy(parsed_final_state)
    elif existing_final_state not in (None, "", {}, []):
        merged["final_state"] = copy.deepcopy(existing_final_state)
    required = merged.get("required_item_names", {}) if isinstance(merged, dict) else {}
    all_names: list[str] = []
    for bucket_name in BUCKETS:
        bucket = required.get(bucket_name, {}) if isinstance(required, dict) else {}
        if isinstance(bucket, dict):
            all_names.extend(bucket.get("primary", []))
            all_names.extend(bucket.get("alternatives", []))
    all_names = unique_names(all_names)

    quantity_issues = _quantity_constraint_issues(merged, valid_names)
    return merged, all_names, invalid_required, quantity_issues


def _build_prompt_inputs(
    context: FeatureContext,
    result: FeatureResult,
    *,
    feedback: str,
    attempt: int,
    max_alternatives_per_bucket: int,
) -> dict[str, str]:
    node = _understanding_node()
    structured = _current_structured_task(result)
    selection = {
        "structured_task": structured,
        "entity_relevance": result.get("entity_relevance", {}),
        "relevant_item_names": result.get("relevant_item_names", []),
        "required_item_names": _required_item_names(structured),
        "scene_entity_count": len(_scene_entities(context)),
        "scene_entities": _scene_entities(context),
    }
    task_context = _runtime_task_context(context)
    return {
        "task": str(context.get("task", "")),
        "scene_entities_json": _json_pretty(_scene_entities(context)),
        "current_structured_task_json": _json_pretty(structured),
        "current_selection_json": _json_pretty(selection),
        "task_context_json": _json_pretty(task_context),
        "attempt_feedback": feedback,
        "attempt_index": str(attempt),
        "max_alternatives_per_bucket": str(max_alternatives_per_bucket),
        "alternatives_instruction": _alternatives_instruction(max_alternatives_per_bucket),
        "system_rules": node.load_system_rules(),
    }


def _parse_attempt_result(
    parsed: dict[str, Any],
    result: FeatureResult,
    valid_names: set[str],
    *,
    max_alternatives_per_bucket: int,
) -> tuple[dict[str, Any], list[str], list[str], list[str]]:
    return _normalize_output(
        parsed,
        result,
        valid_names,
        max_alternatives_per_bucket=max_alternatives_per_bucket,
    )


def _feedback_text(
    *,
    invalid_required: list[str],
    quantity_issues: list[str],
    valid_names: set[str],
) -> str:
    parts: list[str] = []
    if invalid_required:
        parts.append(f"required_item_names 含有不在场景里的名字: {', '.join(invalid_required[:8])}")
    if quantity_issues:
        parts.append(f"数量约束未满足: {'; '.join(quantity_issues[:4])}")
    if valid_names:
        sample = ", ".join(sorted(valid_names)[:12])
        parts.append(f"请只从以下场景实体中选名: {sample}")
    return "；".join(parts)


def run(context: FeatureContext, result: FeatureResult) -> FeatureResult:
    if result.get("stop_pipeline") or result.get("is_cancel_all"):
        return {}
    if result.get("needs_clarification") or result.get("is_complete") is False:
        return {}

    flags = _feature_flags(context)
    settings = _feature_settings(context)
    if not _enabled(settings, flags):
        return {}

    scene_entities = _scene_entity_set(context)
    if not scene_entities:
        return {}

    initial_names = _initial_entity_selection(result)
    invalid_initial = [name for name in initial_names if name not in scene_entities]
    initial_quantity_issues = _quantity_constraint_issues(_current_structured_task(result), scene_entities)
    valid_initial = _filter_names(initial_names, scene_entities)
    if initial_names and not invalid_initial and not initial_quantity_issues and not bool(settings.get("always_run", False)):
        return {
            "relevant_item_names": valid_initial,
            "entity_repair": {
                "needed": False,
                "invalid_names": [],
                "valid_names": valid_initial,
            },
        }

    max_attempts = int(settings.get("max_attempts", 2) or 2)
    if max_attempts < 1:
        max_attempts = 1
    max_alternatives_per_bucket = _max_alternatives_per_bucket(settings, flags)

    node = _understanding_node()
    if invalid_initial:
        feedback = f"初始实体名不在场景中: {', '.join(invalid_initial[:8])}"
    elif initial_quantity_issues:
        feedback = f"初始实体数量不满足任务要求: {'; '.join(initial_quantity_issues[:4])}"
    else:
        feedback = str(settings.get("initial_feedback", "") or "初始理解没有给出可校验的实体名，请从场景实体表中补齐关键对象。")
    last_parsed: dict[str, Any] = {}
    last_structured = _current_structured_task(result)
    last_all_names: list[str] = []
    last_invalid_required: list[str] = []
    last_quantity_issues: list[str] = []
    for attempt in range(1, max_attempts + 1):
        prompt_inputs = _build_prompt_inputs(
            context,
            result,
            feedback=feedback,
            attempt=attempt,
            max_alternatives_per_bucket=max_alternatives_per_bucket,
        )
        system_prompt = node.render_prompt(PROMPT_NAME, **prompt_inputs)
        with llm_trace_context(
            process_name="understanding",
            prompt_name=PROMPT_NAME,
            call_stage="entity_repair",
            attempt=attempt,
        ):
            response = node.get_understanding_llm().invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content="请按上述要求修正实体选择，并只返回 JSON。"),
                ]
            )
        parsed = _parse_llm_json(response.content)
        if not parsed:
            feedback = "模型输出不是可解析 JSON，请重新按要求只返回 JSON。"
            if attempt < max_attempts:
                continue
            return {
                "is_complete": False,
                "needs_clarification": True,
                "clarification_question": "抱歉，实体修复模块返回异常，请重新说明任务。",
            }

        normalized_structured, all_names, invalid_required, quantity_issues = _parse_attempt_result(
            parsed,
            result,
            scene_entities,
            max_alternatives_per_bucket=max_alternatives_per_bucket,
        )
        last_parsed = parsed
        last_structured = normalized_structured
        last_all_names = all_names
        last_invalid_required = invalid_required
        last_quantity_issues = quantity_issues
        if invalid_required or quantity_issues:
            feedback = _feedback_text(
                invalid_required=invalid_required,
                quantity_issues=quantity_issues,
                valid_names=scene_entities,
            )
            if attempt < max_attempts:
                continue
            return {
                "is_complete": False,
                "needs_clarification": True,
                "clarification_question": "实体名称无法与当前场景对齐，请重新确认关键对象。",
                "structured_task": normalized_structured,
                "relevant_item_names": all_names,
                "entity_repair": {
                    "attempts": attempt,
                    "invalid_required_names": invalid_required,
                    "quantity_constraint_issues": quantity_issues,
                    "raw": parsed,
                    "max_alternatives_per_bucket": max_alternatives_per_bucket,
                },
            }
        break

    is_complete = bool(last_parsed.get("is_complete", True)) and not last_invalid_required and not last_quantity_issues
    relevant_names = unique_names(
        _filter_names(last_all_names, scene_entities)
        + _filter_names(flatten_entity_relevance(last_parsed.get("entity_relevance", {})), scene_entities)
        + _filter_names(result.get("relevant_item_names", []) if isinstance(result.get("relevant_item_names", []), list) else [], scene_entities)
    )
    if not relevant_names:
        relevant_names = _filter_names(_collect_entity_references(last_structured), scene_entities)

    update: FeatureResult = {
        "structured_task": last_structured,
        "relevant_item_names": relevant_names,
        "entity_repair": {
            "attempts": attempt,
            "invalid_required_names": last_invalid_required,
            "quantity_constraint_issues": last_quantity_issues,
            "raw": last_parsed,
            "max_alternatives_per_bucket": max_alternatives_per_bucket,
        },
        "is_complete": is_complete,
    }
    if not is_complete and bool(settings.get("clarification_when_unresolved", True)):
        update.update(
            {
                "needs_clarification": True,
                "clarification_question": "关键实体未能与场景精确对齐，请重新确认对象名称。",
            }
        )
    return update


__all__ = ["run"]
