from __future__ import annotations

import copy
import json
from dataclasses import dataclass

from ..contracts import (
    RepairAssembly,
    RepairContext,
    RepairDiagnosis,
    RepairStrategy,
)
from .assembly import assemble_vcr_plan
from .core import (
    analyze_counterfactual_failure_windows,
    merge_causal_repair_windows,
)


@dataclass(frozen=True)
class VCRRepairStrategy(RepairStrategy):
    max_segment_actions: int = 24
    max_backtrack_depth: int = 0
    merge_gap_actions: int = 0
    name: str = "vcr"

    def find_errors(self, context: RepairContext) -> RepairDiagnosis:
        steps = [
            copy.deepcopy(step)
            for step in context.todo_list
            if isinstance(step, dict)
        ]
        failed_index = _step_index(steps, context.failed_step)
        if failed_index is None:
            return _failure(self.name, "VCR 无法在完整 todo_list 中定位失败步骤")
        if context.skill_catalog is None:
            return _failure(self.name, "VCR 缺少技能规划目录")
        skill_closure = _validated_skill_closure(context, context.skill_catalog)
        if not skill_closure:
            return _failure(self.name, "理解层未提供可用于 VCR 的技能闭包")

        analysis = analyze_counterfactual_failure_windows(
            steps=steps,
            first_failed_index=failed_index,
            first_issue_type=context.issue_type,
            first_fix_advice=context.fix_advice,
            failure_env=context.failure_env,
            failure_robot=context.failure_robot,
            trajectory_records=context.trajectory_records,
            sandbox_start_env=context.sandbox_start_env,
            sandbox_start_robot=context.sandbox_start_robot,
            apply_action=context.apply_action,
            max_backtrack_depth=self.max_backtrack_depth,
            skill_profile=context.skill_profile,
            skill_catalog=context.skill_catalog,
            skill_closure=skill_closure,
            skill_handlers=context.skill_handlers,
            goal_test=context.goal_test,
            apply_effect=getattr(context, "apply_effect", None),
        )
        if not analysis.get("success"):
            reason = str(analysis.get("reason", "counterfactual_analysis_failed"))
            if reason == "counterfactual_task_not_completed":
                completion = copy.deepcopy(
                    (analysis.get("details") or {}).get("task_completion") or {}
                )
                completion.update(
                    {
                        "status": "not_completed",
                        "handled": False,
                    }
                )
                return RepairDiagnosis(
                    strategy_name=self.name,
                    prompt="",
                    error="反事实模拟后任务未完成，后续处理接口已预留",
                    disposition="deferred",
                    artifacts={
                        "counterfactual_task_completion": completion,
                    },
                )
            return _failure(self.name, f"VCR 多错误因果诊断失败: {reason}")
        causal_windows = analysis.get("windows") or []
        if not causal_windows:
            return _failure(self.name, "VCR 未生成任何因果修复窗口")
        repair_windows = merge_causal_repair_windows(
            causal_windows,
            self.merge_gap_actions,
        )
        if not repair_windows:
            return _failure(self.name, "VCR 未生成任何可替换窗口")

        # Earlier repairs change the entry state of later counterfactual windows.
        # Select by failed action, not rollback depth: a later failure may have a
        # deeper causal checkpoint but must still wait for a real replay.
        repair_windows = [
            min(
                repair_windows,
                key=lambda window: (
                    int(window["anchor_index"]),
                    int(window["start_index"]),
                ),
            )
        ]
        repair_windows, containment_error = _resolve_containment_handoff_windows(
            repair_windows=repair_windows,
            steps=steps,
            analysis=analysis,
            skill_catalog=context.skill_catalog,
        )
        if containment_error:
            return _failure(self.name, containment_error)
        relevant_entities = _semantic_relevant_entities(context)

        window_artifacts = _build_repair_window_payloads(
            steps=steps,
            repair_windows=repair_windows,
            causal_windows=causal_windows,
            analysis=analysis,
            skill_catalog=context.skill_catalog,
            skill_closure=skill_closure,
            relevant_entities=relevant_entities,
        )
        window_payloads = [artifact[0] for artifact in window_artifacts]
        missing_entities = sorted(
            {
                entity
                for _, _, missing in window_artifacts
                for entity in missing
            }
        )
        if missing_entities:
            return _failure(
                self.name,
                "理解层未提供窗口出口所需实体: " + ", ".join(missing_entities),
            )
        validation_contexts = [
            _window_validation_context(window, payload, exit_contract)
            for window, (payload, exit_contract, _missing) in zip(
                repair_windows, window_artifacts
            )
        ]
        prompt = _build_prompt(context=context, window_payload=window_payloads[0])
        return RepairDiagnosis(
            strategy_name=self.name,
            prompt=prompt,
            merge_context={
                "original_todo_list": copy.deepcopy(steps),
                "repair_windows": [
                    {
                        "window_id": _window_id(index),
                        "start_index": int(window["start_index"]),
                        "end_index": int(window["anchor_index"]),
                    }
                    for index, window in enumerate(repair_windows, start=1)
                ],
                "window_validation": validation_contexts,
            },
        )

    def reassemble(
        self,
        diagnosis: RepairDiagnosis,
        generated_todo_list: list[dict],
    ) -> RepairAssembly:
        return assemble_vcr_plan(diagnosis, generated_todo_list)


def _build_prompt(
    *,
    context: RepairContext,
    window_payload: dict,
) -> str:
    payload = {
        "task_goal": str(context.structured_task.get("intent", "") or ""),
        "repair_window": window_payload,
    }
    return (
        "你是 VCR 局部状态转换规划器。只为唯一的 repair_window 生成完整替换 actions，"
        "窗口外动作由系统保留。使用 skill_contracts 中的技能，将 current_state 规划到 "
        "target_state；target_state 是窗口后的相关目标状态。动作数量可以不同于原窗口步数，"
        "可以插入临时放置、取回或导航等必要动作。每个 action 都必须从当前模拟状态满足对应"
        " requires，再产生 effects；"
        "必须按 repair_strategies 中的一种方法处理 failure_obligations："
        "要么保持 root_action 并在 failed_action 前补足前置条件，要么替换 root_action；"
        "动作参数中的实体名只能来自输入 JSON。"
        "只输出 JSON：{\"repair_window_id\": \"window_1\", "
        "\"actions\": [{\"execution\": {\"skill\": \"...\", "
        "\"parameters\": {...}}}, ...]}。\n\n"
        + json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    )


def _build_repair_window_payloads(
    *,
    steps: list[dict],
    repair_windows: list[dict],
    causal_windows: list[dict],
    analysis: dict,
    skill_catalog: object,
    skill_closure: list[str],
    relevant_entities: list[str],
) -> list[tuple[dict, list[dict], list[str]]]:
    window_payloads = []
    for index, window in enumerate(repair_windows, start=1):
        window_payloads.append(
            _repair_window_payload(
                window_id=_window_id(index),
                window=window,
                causal_windows=causal_windows,
                steps=steps,
                analysis=analysis,
                skill_catalog=skill_catalog,
                skill_closure=skill_closure,
                relevant_entities=relevant_entities,
            )
        )
    return window_payloads


def _resolve_containment_handoff_windows(
    *,
    repair_windows: list[dict],
    steps: list[dict],
    analysis: dict,
    skill_catalog: object,
) -> tuple[list[dict], str]:
    """Replace synthetic multi-hand exits with a proven containment handoff.

    Counterfactual analysis deliberately applies failed action effects so it can
    find later causal failures. Those effects can temporarily violate the
    single-arm model. A hard repair target must never retain that impossible
    state. We only repair it when a later placement action explicitly proves
    that each extra hand item belongs inside the physical hand-held root.
    """

    states_after = analysis.get("states_after") or {}
    if not isinstance(states_after, dict):
        return [], "VCR 缺少反事实出口状态"

    resolved = []
    for raw_window in repair_windows:
        window = copy.deepcopy(raw_window)
        anchor_index = int(window.get("anchor_index", -1))
        raw_exit = _snapshot_at(states_after, anchor_index)
        ownership = _hand_ownership(raw_exit)
        if ownership["valid"]:
            resolved.append(window)
            continue

        held_root = ownership["held_root"]
        extra_items = ownership["extra_hand_items"]
        if not held_root or not extra_items:
            return [], _ownership_error(ownership)

        handoff_index = anchor_index
        for child in extra_items:
            placement_index = _find_containment_placement(
                steps=steps,
                start_index=handoff_index + 1,
                child=child,
                destination=held_root,
                skill_catalog=skill_catalog,
            )
            if placement_index is None:
                return [], (
                    "VCR 反事实出口违反单臂承载不变量，且后续没有明确将 "
                    f"{child} 放入 {held_root} 的技能动作"
                )
            handoff_index = placement_index

        handoff_exit = _snapshot_at(states_after, handoff_index)
        target_snapshot = _restore_containment_holding(
            handoff_exit,
            held_root=held_root,
            children=extra_items,
        )
        if target_snapshot is None:
            return [], _ownership_error(_hand_ownership(handoff_exit))

        window["anchor_index"] = handoff_index
        window["target_snapshot"] = target_snapshot
        window["containment_handoff"] = {
            "held_root": held_root,
            "children": list(extra_items),
            "handoff_end_index": handoff_index,
        }
        resolved.append(window)
    return resolved, ""


def _snapshot_at(states_after: dict, index: int) -> dict:
    snapshot = states_after.get(index, states_after.get(str(index), {}))
    return copy.deepcopy(snapshot) if isinstance(snapshot, dict) else {}


def _hand_ownership(snapshot: dict) -> dict:
    environment = snapshot.get("environment", {}) if isinstance(snapshot, dict) else {}
    robot = snapshot.get("robot", {}) if isinstance(snapshot, dict) else {}
    environment = environment if isinstance(environment, dict) else {}
    robot = robot if isinstance(robot, dict) else {}
    hand_items = sorted(
        name
        for name, info in environment.items()
        if isinstance(info, dict) and info.get("direct_parent") == "robot_hand"
    )
    held_root = str(robot.get("robot_holding", "空") or "空")
    valid = (
        (not hand_items and held_root == "空")
        or (len(hand_items) == 1 and hand_items[0] == held_root)
    )
    return {
        "valid": valid,
        "held_root": held_root if held_root != "空" else "",
        "hand_items": hand_items,
        "extra_hand_items": [item for item in hand_items if item != held_root],
    }


def _find_containment_placement(
    *,
    steps: list[dict],
    start_index: int,
    child: str,
    destination: str,
    skill_catalog: object,
) -> int | None:
    catalog_get = getattr(skill_catalog, "get", None)
    if not callable(catalog_get):
        return None
    for index in range(max(0, start_index), len(steps)):
        action = _action_from_step(steps[index])
        spec = catalog_get(action["skill"])
        if (
            spec is not None
            and bool(getattr(spec, "can_place_item", False))
            and spec.item_value(action) == child
            and spec.destination_value(action) == destination
        ):
            return index
    return None


def _restore_containment_holding(
    snapshot: dict,
    *,
    held_root: str,
    children: list[str],
) -> dict | None:
    normalized = copy.deepcopy(snapshot) if isinstance(snapshot, dict) else {}
    environment = normalized.get("environment")
    robot = normalized.get("robot")
    if not isinstance(environment, dict) or not isinstance(robot, dict):
        return None
    if any(
        environment.get(child, {}).get("direct_parent") != held_root
        for child in children
    ):
        return None
    hand_items = sorted(
        name
        for name, info in environment.items()
        if isinstance(info, dict) and info.get("direct_parent") == "robot_hand"
    )
    if hand_items != [held_root]:
        return None
    robot["robot_holding"] = held_root
    return normalized


def _ownership_error(ownership: dict) -> str:
    hand_items = ", ".join(ownership.get("hand_items", [])) or "无"
    held_root = ownership.get("held_root") or "空"
    return (
        "VCR 反事实出口违反单臂承载不变量："
        f"robot_holding={held_root}，direct_parent=robot_hand 的实体={hand_items}"
    )


def _action_from_step(step: dict | None) -> dict:
    execution = step.get("execution", {}) if isinstance(step, dict) else {}
    execution = execution if isinstance(execution, dict) else {}
    parameters = execution.get("parameters", {})
    return {
        "skill": str(execution.get("skill", "") or ""),
        "parameters": copy.deepcopy(parameters) if isinstance(parameters, dict) else {},
    }


def _window_validation_context(
    window: dict,
    payload: dict,
    exit_contract: list[dict],
) -> dict:
    checkpoint = window.get("checkpoint") or {}
    entry_environment = checkpoint.get("checkpoint_env", {})
    entry_robot = checkpoint.get("checkpoint_robot", {})
    return {
        "segment_id": str(payload.get("id", "") or ""),
        "entry_environment": copy.deepcopy(
            entry_environment if isinstance(entry_environment, dict) else {}
        ),
        "entry_robot": copy.deepcopy(
            entry_robot if isinstance(entry_robot, dict) else {}
        ),
        "exit_contract": copy.deepcopy(exit_contract),
    }


def _repair_window_payload(
    *,
    window_id: str,
    window: dict,
    causal_windows: list[dict],
    steps: list[dict],
    analysis: dict,
    skill_catalog: object,
    skill_closure: list[str],
    relevant_entities: list[str],
) -> tuple[dict, list[dict], list[str]]:
    sources = {
        (int(source["start_index"]), int(source["anchor_index"]))
        for source in window.get("source_windows", [])
    }
    causes = [
        source
        for source in causal_windows
        if (int(source["start_index"]), int(source["anchor_index"])) in sources
    ]
    if not causes:
        causes = [window]
    cause_failures = [
        (cause, failure)
        for cause in causes
        for failure in cause.get("failures", [])
        if isinstance(failure, dict)
    ]
    if not cause_failures:
        cause_failures = [(window, {})]
    causal_groups = []
    for index, (cause, failure) in enumerate(cause_failures, start=1):
        error_id = f"{window_id}_error_{index}"
        group = _matching_causal_group(causal_groups, cause, steps)
        if group is None:
            group = _causal_group_payload(cause, steps)
            causal_groups.append(group)
        group["errors"].append(
            _causal_error_payload(
                cause,
                failure,
                error_id=error_id,
            )
        )

    start_index = int(window["start_index"])
    anchor_index = int(window["anchor_index"])
    checkpoint = window.get("checkpoint") or {}
    entry_snapshot = {
        "environment": copy.deepcopy(checkpoint.get("checkpoint_env", {})),
        "robot": copy.deepcopy(checkpoint.get("checkpoint_robot", {})),
    }
    exit_snapshot = copy.deepcopy(
        window.get("target_snapshot")
        or (analysis.get("states_after") or {}).get(anchor_index, {})
    )
    exit_contract = _counterfactual_exit_contract(
        exit_snapshot=exit_snapshot,
        entry_snapshot=entry_snapshot,
        causal_groups=causal_groups,
        entities=relevant_entities,
    )
    missing_entities = _missing_exit_entities(
        exit_contract,
        relevant_entities,
        entry_snapshot,
        exit_snapshot,
    )
    prompt_payload = {
        "id": window_id,
        "position": {
            "start_step": _step_number(steps[start_index]),
            "end_step": _step_number(steps[anchor_index]),
        },
        "current_state": _compact_relevant_state(entry_snapshot, relevant_entities),
        "target_state": _compact_relevant_state(exit_snapshot, relevant_entities),
        "failure_obligations": _failure_obligations_payload(causal_groups),
        "repair_strategies": _repair_strategies_payload(),
        "skill_contracts": _compact_skill_contracts(
            skill_catalog,
            skill_closure,
        ),
    }
    return prompt_payload, exit_contract, missing_entities


def _compact_skill_contracts(
    skill_catalog: object,
    skill_closure: list[str],
) -> list[dict]:
    specs = getattr(skill_catalog, "specs", None)
    if not isinstance(specs, list):
        return []
    by_name = {
        str(getattr(spec, "name", "") or ""): spec
        for spec in specs
        if str(getattr(spec, "name", "") or "")
    }
    contracts = []
    for name in skill_closure:
        spec = by_name.get(str(name))
        if spec is None:
            continue
        contract = _compact_action_contract(spec)
        if contract:
            contracts.append(contract)
    return contracts


def _validated_skill_closure(context: RepairContext, skill_catalog: object) -> list[str]:
    raw = getattr(context, "skill_closure", [])
    names = raw if isinstance(raw, list) else []
    specs = getattr(skill_catalog, "specs", None)
    available = {
        str(getattr(spec, "name", "") or "")
        for spec in (specs if isinstance(specs, list) else [])
    }
    return list(
        dict.fromkeys(
            str(name).strip()
            for name in names
            if str(name).strip() in available
        )
    )


def _compact_relevant_state(snapshot: dict, relevant_entities: list[str]) -> dict:
    if not isinstance(snapshot, dict):
        snapshot = {}
    environment = snapshot.get("environment", {})
    robot = snapshot.get("robot", {})
    compact_entities = {}
    if isinstance(environment, dict):
        for entity in relevant_entities:
            info = environment.get(entity)
            if not isinstance(info, dict):
                continue
            facts = {}
            for key in ("type", "is_container", "direct_parent"):
                if key in info:
                    facts[key] = copy.deepcopy(info.get(key))
            states = info.get("states", {})
            if isinstance(states, dict):
                scalar_states = {
                    str(key): copy.deepcopy(value)
                    for key, value in states.items()
                    if isinstance(value, (bool, int, float, str)) or value is None
                }
                if scalar_states:
                    facts["states"] = scalar_states
            compact_entities[entity] = facts
    return {
        "robot": _compact_robot_state(robot),
        "entities": compact_entities,
    }


def _semantic_relevant_entities(context: RepairContext) -> list[str]:
    raw_names = getattr(context, "relevant_item_names", [])
    names = raw_names if isinstance(raw_names, list) else []
    environment = getattr(context, "environment", {})
    if isinstance(environment, dict):
        names = [
            *names,
            *(
                name
                for name, info in environment.items()
                if not isinstance(info, dict) or info.get("type") != "room"
            ),
        ]
    return list(dict.fromkeys(str(name).strip() for name in names if str(name).strip()))


def _missing_exit_entities(
    exit_contract: list[dict],
    relevant_entities: list[str],
    *snapshots: dict,
) -> list[str]:
    relevant = set(relevant_entities)
    known_entities = {
        str(name)
        for snapshot in snapshots
        if isinstance(snapshot, dict)
        for name in (
            snapshot.get("environment", {}).keys()
            if isinstance(snapshot.get("environment"), dict)
            else []
        )
    }
    missing = []
    for item in exit_contract:
        if not isinstance(item, dict):
            continue
        predicate = str(item.get("predicate", "") or "")
        entity = ""
        if predicate.startswith("entity."):
            entity = predicate.removeprefix("entity.").split(".", 1)[0]
        elif predicate.startswith("state."):
            entity = predicate.removeprefix("state.").split(".", 1)[0]
        if entity and entity not in relevant:
            missing.append(entity)
        value = item.get("required_value")
        references_entity = (
            predicate in {
                "robot.robot.robot_location",
                "robot.robot.robot_holding",
            }
            or predicate.endswith(".direct_parent")
        )
        if (
            references_entity
            and isinstance(value, str)
            and value in known_entities
            and value not in relevant
        ):
            missing.append(value)
    return list(dict.fromkeys(missing))


def _compact_action_contract(spec: object) -> dict:
    name = str(getattr(spec, "name", "") or "")
    if not name:
        return {}
    parameter_names = []
    for attribute in (
        "target_param",
        "item_param",
        "destination_param",
        "location_param",
        "device_param",
    ):
        value = str(getattr(spec, attribute, "") or "")
        if value and value not in parameter_names:
            parameter_names.append(value)

    requires = []
    effects = []
    location_param = str(getattr(spec, "location_param", "") or "")
    target_param = str(getattr(spec, "target_param", "") or "")
    item_param = str(getattr(spec, "item_param", "") or "")
    destination_param = str(getattr(spec, "destination_param", "") or "")
    device_param = str(getattr(spec, "device_param", "") or "")

    if bool(getattr(spec, "can_move_robot", False)):
        requires.append({"robot_location": {"not": f"${location_param}"}})
        effects.append({"robot_location": f"${location_param}"})
    elif bool(getattr(spec, "can_grasp_item", False)):
        requires.extend(
            [
                {"robot_location": f"$accessible_parent({item_param})"},
                {"robot_holding": "空"},
                {f"${item_param}.accessible": True},
            ]
        )
        effects.append({"robot_holding": f"${item_param}"})
    elif bool(getattr(spec, "can_place_item", False)):
        requires.extend(
            [
                {"robot_location": f"${destination_param}"},
                {"robot_holding": f"${item_param}"},
                {f"${destination_param}.isOpen": "若存在该状态则不得为 false"},
            ]
        )
        effects.extend(
            [
                {"robot_holding": "空"},
                {f"${item_param}.direct_parent": f"${destination_param}"},
            ]
        )
    else:
        interaction_param = location_param or device_param or target_param
        if interaction_param:
            requires.append({"robot_location": f"${interaction_param}"})
        if bool(getattr(spec, "requires_empty_hand", False)):
            requires.append({"robot_holding": "空"})

    state_key = str(getattr(spec, "state_key", "") or "")
    state_value = getattr(spec, "state_value", None)
    if state_key and target_param:
        requires.append({f"${target_param}.{state_key}": not state_value})
        effects.append({f"${target_param}.{state_key}": state_value})

    container_state_key = str(getattr(spec, "container_state_key", "") or "")
    if container_state_key and device_param:
        requires.append(
            {
                f"${device_param}.{container_state_key}": getattr(
                    spec, "container_state_value", None
                )
            }
        )
    device_state_key = str(getattr(spec, "device_state_key", "") or "")
    if device_state_key and device_param:
        requires.append(
            {
                f"${device_param}.{device_state_key}": getattr(
                    spec, "device_state_value", None
                )
            }
        )
    effect_state_key = str(getattr(spec, "effect_state_key", "") or "")
    if effect_state_key and item_param:
        effects.append(
            {
                f"${item_param}.{effect_state_key}": getattr(
                    spec, "effect_state_value", None
                )
            }
        )
    return {
        "skill": name,
        "parameters": parameter_names,
        "requires": requires,
        "effects": effects,
    }


def _counterfactual_exit_contract(
    *,
    exit_snapshot: dict,
    entry_snapshot: dict,
    causal_groups: list[dict],
    entities: list[str],
) -> list[dict]:
    """Extract the repair boundary from the counterfactual trace.

    The trace is the source of truth for the expected post-window state. Keep
    every changed state key and mutable entity field, rather than hard-coding
    a small set such as ``isOpen`` and ``isToggled``.
    """
    contracts = _counterfactual_state_delta(
        entry_snapshot=entry_snapshot,
        exit_snapshot=exit_snapshot,
        entities=entities,
    )
    causal_predicates = {
        _canonical_predicate(
            str(group.get("causal_relation", {}).get("predicate", "") or "")
        )
        for group in causal_groups
        if isinstance(group, dict)
    }
    # A counterfactual snapshot contains the old root action's effect. It cannot
    # constrain the predicate that the replacement is specifically meant to fix.
    return [
        contract
        for contract in contracts
        if str(contract.get("predicate", "") or "") not in causal_predicates
    ]


def _canonical_predicate(predicate: str) -> str:
    if predicate in {"robot_location", "robot_holding"}:
        return f"robot.robot.{predicate}"
    return predicate


def _matching_causal_group(
    groups: list[dict],
    window: dict,
    steps: list[dict],
) -> dict | None:
    checkpoint = window.get("checkpoint") or {}
    root_step = _step_number(steps[int(window.get("start_index", 0))])
    predicate = str(checkpoint.get("causal_predicate", "") or "")
    for group in groups:
        if (
            group.get("root_cause_step") == root_step
            and group.get("causal_relation", {}).get("predicate") == predicate
        ):
            return group
    return None


def _causal_group_payload(
    window: dict,
    steps: list[dict],
) -> dict:
    checkpoint = window.get("checkpoint") or {}
    start_index = int(window.get("start_index", 0))
    root_cause_step = _step_number(steps[start_index])
    root_action = (
        checkpoint.get("causal_action")
        or checkpoint.get("rollback_step")
        or steps[start_index]
    )
    return {
        "root_cause_step": root_cause_step,
        "root_cause_action": _compact_step(root_action),
        "causal_relation": {
            "predicate": str(checkpoint.get("causal_predicate", "") or ""),
            "before": copy.deepcopy(checkpoint.get("causal_before")),
            "after": copy.deepcopy(checkpoint.get("causal_after")),
        },
        "errors": [],
    }


def _causal_error_payload(
    window: dict,
    failure: dict,
    *,
    error_id: str,
) -> dict:
    checkpoint = window.get("checkpoint") or {}
    error_step = _step_number(failure.get("step"))
    return {
        "error_id": error_id,
        "error_step": error_step,
        "error_action": _compact_step(failure.get("step")),
        "error_reason": {
            "issue_type": str(failure.get("issue_type", "") or ""),
        },
        "failed_preconditions": copy.deepcopy(
            checkpoint.get("failed_preconditions", [])
        ),
    }


def _failure_obligations_payload(causal_groups: list[dict]) -> list[dict]:
    obligations = []
    for group in causal_groups:
        if not isinstance(group, dict):
            continue
        relation = group.get("causal_relation")
        relation = relation if isinstance(relation, dict) else {}
        root_action = group.get("root_cause_action")
        root_action = root_action if isinstance(root_action, dict) else {}
        for error in group.get("errors", []):
            if not isinstance(error, dict):
                continue
            obligation = {
                "error_id": str(error.get("error_id", "") or ""),
                "root_action": copy.deepcopy(root_action),
                "failed_action": copy.deepcopy(error.get("error_action") or {}),
                "failed_action_preconditions": copy.deepcopy(
                    error.get("failed_preconditions") or []
                ),
            }
            if relation.get("predicate"):
                obligation["root_state_change"] = copy.deepcopy(relation)
            obligations.append(obligation)
    return obligations


def _repair_strategies_payload() -> list[dict]:
    return [
        {
            "name": "preserve_root_action",
            "instruction": (
                "保持 failure_obligations.root_action；在 failed_action 之前插入或调整动作，"
                "使 failed_action_preconditions 在执行 failed_action 前成立。"
            ),
        },
        {
            "name": "replace_root_action",
            "instruction": (
                "替换 failure_obligations.root_action；重新生成完整窗口 actions，"
                "使 failed_action_preconditions 在执行 failed_action 前成立。"
            ),
        },
    ]


def _compact_robot_state(robot: object) -> dict:
    if not isinstance(robot, dict):
        return {}
    return {
        key: copy.deepcopy(robot.get(key))
        for key in ("robot_location", "robot_holding")
        if key in robot
    }


def _counterfactual_state_delta(
    *,
    entry_snapshot: dict,
    exit_snapshot: dict,
    entities: list[str],
) -> list[dict]:
    entry_robot = entry_snapshot.get("robot", {}) if isinstance(entry_snapshot, dict) else {}
    exit_robot = exit_snapshot.get("robot", {}) if isinstance(exit_snapshot, dict) else {}
    entry_environment = (
        entry_snapshot.get("environment", {}) if isinstance(entry_snapshot, dict) else {}
    )
    exit_environment = (
        exit_snapshot.get("environment", {}) if isinstance(exit_snapshot, dict) else {}
    )
    entry_robot = entry_robot if isinstance(entry_robot, dict) else {}
    exit_robot = exit_robot if isinstance(exit_robot, dict) else {}
    entry_environment = entry_environment if isinstance(entry_environment, dict) else {}
    exit_environment = exit_environment if isinstance(exit_environment, dict) else {}
    contracts = []
    for key, value in sorted(exit_robot.items()):
        contracts.append(
            {
                "predicate": f"robot.robot.{key}",
                "required_value": copy.deepcopy(value),
            }
        )
    for entity in entities:
        entry_info = entry_environment.get(entity, {})
        exit_info = exit_environment.get(entity, {})
        if not isinstance(exit_info, dict):
            continue
        entry_info = entry_info if isinstance(entry_info, dict) else {}
        for key, value in sorted(exit_info.items()):
            if key == "states" or entry_info.get(key) == value:
                continue
            if key == "direct_parent" and _is_room_level(
                exit_environment.get(str(value or ""), {})
            ):
                continue
            contracts.append(
                {
                    "predicate": f"entity.{entity}.{key}",
                    "required_value": copy.deepcopy(value),
                }
            )
        entry_states = entry_info.get("states", {})
        exit_states = exit_info.get("states", {})
        entry_states = entry_states if isinstance(entry_states, dict) else {}
        exit_states = exit_states if isinstance(exit_states, dict) else {}
        for key, value in sorted(exit_states.items()):
            if entry_states.get(key) == value:
                continue
            contracts.append(
                {
                    "predicate": f"state.{entity}.{key}",
                    "required_value": copy.deepcopy(value),
                }
            )
    return contracts


def _is_room_level(info: object) -> bool:
    return isinstance(info, dict) and (
        info.get("type") == "room"
        or (
            info.get("direct_parent") == "未知环境"
            and not info.get("full_path")
        )
    )


def _compact_step(step: dict | None) -> dict:
    if not isinstance(step, dict):
        return {}
    execution = step.get("execution", {})
    if isinstance(execution, dict) and execution:
        return {
            "step": _step_number(step),
            "skill": str(execution.get("skill", "") or ""),
            "parameters": copy.deepcopy(execution.get("parameters", {})),
        }
    return copy.deepcopy(step)


def _window_id(index: int) -> str:
    return f"window_{index}"


def _failure(strategy_name: str, error: str) -> RepairDiagnosis:
    return RepairDiagnosis(strategy_name=strategy_name, prompt="", error=error)


def _step_number(step: dict | None) -> int | None:
    if not isinstance(step, dict):
        return None
    try:
        return int(step.get("step"))
    except (TypeError, ValueError):
        return None


def _step_index(steps: list[dict], target: dict | None) -> int | None:
    target_number = _step_number(target)
    if target_number is not None:
        return _step_index_by_number(steps, target_number)
    for index, step in enumerate(steps):
        if step == target:
            return index
    return None


def _step_index_by_number(steps: list[dict], number: int) -> int | None:
    for index, step in enumerate(steps):
        if _step_number(step) == number:
            return index
    return None


__all__ = ["VCRRepairStrategy"]
