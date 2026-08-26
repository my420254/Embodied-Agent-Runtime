from __future__ import annotations

import copy

from ..contracts import RepairAssembly, RepairDiagnosis


def assemble_vcr_plan(
    diagnosis: RepairDiagnosis,
    generated_todo_list: list[dict],
) -> RepairAssembly:
    if not generated_todo_list:
        return RepairAssembly(
            strategy_name=diagnosis.strategy_name,
            success=False,
            error="VCR 未生成可重组的替换窗口",
        )
    original = diagnosis.merge_context.get("original_todo_list", [])
    windows = diagnosis.merge_context.get("repair_windows", [])
    if not isinstance(original, list) or not isinstance(windows, list) or not windows:
        return _failure(diagnosis, "VCR 缺少原计划或修复窗口上下文")

    normalized_windows, error = _validated_windows(windows, len(original))
    if error:
        return _failure(diagnosis, error)
    active_window_ids, error = _active_window_ids(
        diagnosis.merge_context,
        normalized_windows,
    )
    if error:
        return _failure(diagnosis, error)
    accepted_by_window, error = _accepted_window_steps(
        diagnosis.merge_context,
        normalized_windows,
        active_window_ids,
    )
    if error:
        return _failure(diagnosis, error)
    generated_by_window, error = _group_generated_steps(
        generated_todo_list,
        normalized_windows,
        active_window_ids,
    )
    if error:
        return _failure(diagnosis, error)

    assembled = []
    provenance = []
    segment_checks = []
    validation_by_id = _validation_by_id(
        diagnosis.merge_context,
        normalized_windows,
    )
    cursor = 0
    for window in normalized_windows:
        original_prefix = original[cursor : window["start_index"]]
        assembled.extend(copy.deepcopy(original_prefix))
        provenance.extend(_original_provenance(original_prefix))
        window_id = window["window_id"]
        generated_segment = generated_by_window.get(window_id)
        if generated_segment is None:
            generated_segment = accepted_by_window[window_id]
        assembled.extend(item["step"] for item in generated_segment)
        provenance.extend(item["provenance"] for item in generated_segment)
        if window_id in active_window_ids:
            validation = validation_by_id.get(window_id)
            if validation is None:
                return _failure(diagnosis, f"VCR 缺少窗口 {window_id} 的验证边界")
            segment_checks.append(
                {
                    **copy.deepcopy(validation),
                    "steps": [
                        copy.deepcopy(item["step"])
                        for item in generated_segment
                    ],
                }
            )
        cursor = window["end_index"] + 1
    original_suffix = original[cursor:]
    assembled.extend(copy.deepcopy(original_suffix))
    provenance.extend(_original_provenance(original_suffix))
    return RepairAssembly(
        strategy_name=diagnosis.strategy_name,
        success=True,
        todo_list=_reindex(assembled),
        step_provenance=copy.deepcopy(provenance),
        segment_checks=segment_checks,
    )


def _validated_windows(
    windows: list[dict],
    original_count: int,
) -> tuple[list[dict], str]:
    parsed = []
    identifiers = set()
    for raw in windows:
        if not isinstance(raw, dict):
            return [], "VCR 修复窗口必须是对象"
        window_id = str(raw.get("window_id", "") or "").strip()
        try:
            start_index = int(raw.get("start_index"))
            end_index = int(raw.get("end_index"))
        except (TypeError, ValueError):
            return [], "VCR 修复窗口索引无效"
        if not window_id or window_id in identifiers:
            return [], "VCR 修复窗口 ID 缺失或重复"
        if start_index < 0 or end_index < start_index or end_index >= original_count:
            return [], f"VCR 修复窗口 {window_id} 超出原计划范围"
        parsed.append(
            {
                "window_id": window_id,
                "start_index": start_index,
                "end_index": end_index,
            }
        )
        identifiers.add(window_id)

    normalized = sorted(parsed, key=lambda item: item["start_index"])
    previous_end = -1
    for window in normalized:
        if window["start_index"] <= previous_end:
            return [], "VCR 修复窗口重叠但未在诊断阶段合并"
        previous_end = window["end_index"]
    return normalized, ""


def _group_generated_steps(
    generated_todo_list: list[dict],
    windows: list[dict],
    active_window_ids: set[str],
) -> tuple[dict[str, list[dict]], str]:
    expected = set(active_window_ids)
    grouped = {window_id: [] for window_id in expected}
    only_window = next(iter(expected)) if len(expected) == 1 else ""
    for generated_index, raw_step in enumerate(generated_todo_list, start=1):
        if not isinstance(raw_step, dict):
            continue
        window_id = str(raw_step.get("repair_window_id", "") or "").strip()
        if not window_id and only_window:
            window_id = only_window
        if window_id not in expected:
            if window_id and any(
                window_id == window["window_id"] for window in windows
            ):
                continue
            return {}, "VCR 多窗口输出缺少有效的 repair_window_id"
        step = copy.deepcopy(raw_step)
        step.pop("repair_window_id", None)
        grouped[window_id].append(
            {
                "step": step,
                "provenance": {
                    "source": "generated",
                    "repair_window_id": window_id,
                    "window_action_index": len(grouped[window_id]) + 1,
                    "generated_action_index": generated_index,
                },
            }
        )

    missing = sorted(window_id for window_id, steps in grouped.items() if not steps)
    if missing:
        return {}, f"VCR 未生成窗口 {', '.join(missing)} 的替换动作"
    return grouped, ""


def _active_window_ids(
    merge_context: dict,
    windows: list[dict],
) -> tuple[set[str], str]:
    expected = {window["window_id"] for window in windows}
    raw_active = merge_context.get("active_window_ids")
    if raw_active is None:
        return expected, ""
    if not isinstance(raw_active, list):
        return set(), "VCR active_window_ids 必须是列表"
    active = {str(window_id or "").strip() for window_id in raw_active}
    if not active or not active <= expected:
        return set(), "VCR active_window_ids 包含未知窗口或为空"
    return active, ""


def _accepted_window_steps(
    merge_context: dict,
    windows: list[dict],
    active_window_ids: set[str],
) -> tuple[dict[str, list[dict]], str]:
    raw_accepted = merge_context.get("accepted_window_steps", {})
    if raw_accepted is None:
        raw_accepted = {}
    if not isinstance(raw_accepted, dict):
        return {}, "VCR accepted_window_steps 必须是对象"
    expected = {window["window_id"] for window in windows}
    accepted: dict[str, list[dict]] = {}
    for window_id, raw_steps in raw_accepted.items():
        identifier = str(window_id or "").strip()
        if identifier not in expected or identifier in active_window_ids:
            return {}, "VCR 已采纳窗口与待修复窗口不一致"
        if not isinstance(raw_steps, list) or not raw_steps:
            return {}, f"VCR 已采纳窗口 {identifier} 缺少动作"
        steps = []
        for index, raw_step in enumerate(raw_steps, start=1):
            if not isinstance(raw_step, dict):
                continue
            step = copy.deepcopy(raw_step)
            step.pop("repair_window_id", None)
            steps.append(
                {
                    "step": step,
                    "provenance": {
                        "source": "accepted_window",
                        "repair_window_id": identifier,
                        "window_action_index": index,
                    },
                }
            )
        if not steps:
            return {}, f"VCR 已采纳窗口 {identifier} 缺少有效动作"
        accepted[identifier] = steps
    missing = expected - active_window_ids - set(accepted)
    if missing:
        return {}, f"VCR 已采纳窗口缺失: {', '.join(sorted(missing))}"
    return accepted, ""


def _validation_by_id(
    merge_context: dict,
    windows: list[dict],
) -> dict[str, dict]:
    raw_contexts = merge_context.get("window_validation", [])
    if not isinstance(raw_contexts, list):
        return {}
    expected = {window["window_id"] for window in windows}
    return {
        str(context.get("segment_id", "") or ""): copy.deepcopy(context)
        for context in raw_contexts
        if isinstance(context, dict)
        and str(context.get("segment_id", "") or "") in expected
    }


def _original_provenance(steps: list[dict]) -> list[dict]:
    return [
        {
            "source": "original",
            "original_step": step.get("step"),
        }
        for step in steps
        if isinstance(step, dict)
    ]


def _failure(diagnosis: RepairDiagnosis, error: str) -> RepairAssembly:
    return RepairAssembly(
        strategy_name=diagnosis.strategy_name,
        success=False,
        error=error,
    )


def _reindex(steps: list[dict]) -> list[dict]:
    return [
        {**copy.deepcopy(step), "step": index}
        for index, step in enumerate(steps, start=1)
        if isinstance(step, dict)
    ]


__all__ = ["assemble_vcr_plan"]
