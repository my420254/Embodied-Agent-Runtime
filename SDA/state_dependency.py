from __future__ import annotations

import copy
from typing import Any

from SDA.skill_catalog import SkillRepairCatalog, load_repair_catalog


SDA_SCHEMA_VERSION = "sda_v1"
MODE_SDA_CAUSAL_REPAIR = "sda_causal_repair"
EMPTY_HAND_VALUE = "空"

PredicateKey = tuple[str, str, str]


def _step_num(step: dict | None) -> int | None:
    if not isinstance(step, dict):
        return None
    try:
        return int(step.get("step"))
    except (TypeError, ValueError):
        return None


def _execution(step: dict | None) -> dict[str, Any]:
    if not isinstance(step, dict):
        return {}
    execution = step.get("execution", {})
    return execution if isinstance(execution, dict) else {}


def _compact_step(step: dict | None) -> dict[str, Any] | None:
    if not isinstance(step, dict):
        return None
    execution = _execution(step)
    return {
        "step": step.get("step"),
        "skill": execution.get("skill", ""),
        "parameters": copy.deepcopy(execution.get("parameters", {}) or {}),
    }


def _compact_todo_list(todo_list: list | None) -> list[dict[str, Any]]:
    compact = []
    for step in todo_list or []:
        item = _compact_step(step if isinstance(step, dict) else None)
        if item:
            compact.append(item)
    return compact


def _action_from_step(step: dict | None) -> dict[str, Any]:
    execution = _execution(step)
    return {
        "skill": str(execution.get("skill", "") or ""),
        "parameters": copy.deepcopy(execution.get("parameters", {}) or {}),
    }


def _predicate_id(key: PredicateKey) -> str:
    return ".".join(str(part) for part in key if part != "")


def _state_predicates(env: dict | None, robot: dict | None) -> dict[PredicateKey, Any]:
    predicates: dict[PredicateKey, Any] = {}
    if isinstance(robot, dict):
        for key, value in robot.items():
            predicates[("robot", "robot", str(key))] = copy.deepcopy(value)

    if not isinstance(env, dict):
        return predicates

    for entity, info in env.items():
        entity_name = str(entity)
        predicates[("entity", entity_name, "__exists__")] = True
        if not isinstance(info, dict):
            predicates[("entity", entity_name, "value")] = copy.deepcopy(info)
            continue
        for key in ("type", "direct_parent", "is_container"):
            if key in info:
                predicates[("entity", entity_name, key)] = copy.deepcopy(info.get(key))
        states = info.get("states", {})
        if isinstance(states, dict):
            for key, value in states.items():
                predicates[("state", entity_name, str(key))] = copy.deepcopy(value)
    return predicates


def _changed_predicates(
    before_env: dict | None,
    before_robot: dict | None,
    after_env: dict | None,
    after_robot: dict | None,
) -> list[dict[str, Any]]:
    before = _state_predicates(before_env, before_robot)
    after = _state_predicates(after_env, after_robot)
    changes = []
    for key in sorted(set(before) | set(after), key=_predicate_id):
        before_value = before.get(key)
        after_value = after.get(key)
        if before_value == after_value:
            continue
        changes.append(
            {
                "predicate": _predicate_id(key),
                "key": key,
                "before": copy.deepcopy(before_value),
                "after": copy.deepcopy(after_value),
            }
        )
    return changes


def _compact_changes(changes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "predicate": change["predicate"],
            "before": copy.deepcopy(change.get("before")),
            "after": copy.deepcopy(change.get("after")),
        }
        for change in changes
    ]


def _record_step(record: dict[str, Any]) -> dict:
    step = record.get("step", {})
    return step if isinstance(step, dict) else {}


def build_state_dependency_graph(
    *,
    todo_list: list,
    trajectory_records: list[dict[str, Any]],
    failed_step: dict | None = None,
    issue_type: str = "",
    fix_advice: str = "",
    failure_env: dict | None = None,
    failure_robot: dict | None = None,
    repair_catalog: SkillRepairCatalog | None = None,
) -> dict[str, Any]:
    catalog = repair_catalog or load_repair_catalog()
    nodes = []
    writer_by_predicate: dict[PredicateKey, dict[str, Any]] = {}
    for record in trajectory_records or []:
        step = _record_step(record)
        changes = _changed_predicates(
            record.get("before_env", {}),
            record.get("before_robot", {}),
            record.get("after_env", {}),
            record.get("after_robot", {}),
        )
        node = {
            "step": _step_num(step),
            "action": _compact_step(step),
            "writes": _compact_changes(changes),
        }
        nodes.append(node)
        for change in changes:
            writer_by_predicate[change["key"]] = {
                "step": _step_num(step),
                "action": _compact_step(step),
                "predicate": change["predicate"],
                "before": copy.deepcopy(change.get("before")),
                "after": copy.deepcopy(change.get("after")),
            }

    failed_predicates = _infer_failed_predicates(
        failed_step=failed_step,
        failure_env=failure_env,
        failure_robot=failure_robot,
        repair_catalog=catalog,
    )
    causal_candidates = []
    for predicate in failed_predicates:
        writer = writer_by_predicate.get(predicate)
        if writer:
            causal_candidates.append(copy.deepcopy(writer))

    return {
        "version": SDA_SCHEMA_VERSION,
        "nodes": nodes,
        "failure": {
            "issue_type": issue_type,
            "fix_advice": fix_advice,
            "failed_step": _compact_step(failed_step),
            "failed_predicates": [_predicate_id(predicate) for predicate in failed_predicates],
        },
        "causal_candidates": causal_candidates,
        "original_todo_list": _compact_todo_list(todo_list),
    }


def _target_candidates_from_step(
    step: dict | None,
    repair_catalog: SkillRepairCatalog,
    env: dict | None = None,
) -> list[str]:
    action = _action_from_step(step)
    candidates: list[str] = []
    spec = repair_catalog.get(action["skill"])
    if spec:
        for getter in (
            spec.target_value,
            spec.item_value,
            spec.destination_value,
            spec.location_value,
            spec.device_value,
        ):
            value = getter(action)
            if value and value not in candidates:
                candidates.append(value)

    params = action.get("parameters", {})
    if isinstance(params, dict):
        env_index = env if isinstance(env, dict) else {}
        for value in params.values():
            if isinstance(value, str) and value and value not in candidates:
                if not env_index or value in env_index:
                    candidates.append(value)
    return candidates


def _state_predicates_for_expected_values(
    *,
    targets: list[str],
    expected_values: dict[str, Any],
    env: dict | None,
) -> list[PredicateKey]:
    if not isinstance(env, dict) or not expected_values:
        return []
    predicates: list[PredicateKey] = []
    for target in targets:
        info = env.get(target)
        if not isinstance(info, dict):
            continue
        states = info.get("states", {})
        if not isinstance(states, dict):
            continue
        for state_key, expected in expected_values.items():
            if state_key in states and states.get(state_key) != expected:
                predicates.append(("state", target, state_key))
    return predicates


def _declared_state_constraints(
    *,
    failed_step: dict | None,
    repair_catalog: SkillRepairCatalog,
) -> dict[str, Any]:
    spec = repair_catalog.get(_action_from_step(failed_step)["skill"])
    if not spec:
        return {}
    return {
        key: value
        for key, value in (
            (spec.container_state_key, spec.container_state_value),
            (spec.device_state_key, spec.device_state_value),
        )
        if key
    }


def _parent_chain(entity: str, env: dict | None) -> list[str]:
    if not isinstance(env, dict):
        return []
    chain: list[str] = []
    seen = set()
    current = entity
    while current in env and current not in seen:
        seen.add(current)
        info = env.get(current, {})
        if not isinstance(info, dict):
            break
        parent = str(info.get("direct_parent", "") or "")
        if not parent or parent in {EMPTY_HAND_VALUE, "robot_hand", "未知环境"}:
            break
        chain.append(parent)
        current = parent
    return chain


def _interaction_locations_for_item(item: str, env: dict | None) -> list[str]:
    if not item or not isinstance(env, dict) or item not in env:
        return []
    locations: list[str] = []
    for candidate in _parent_chain(item, env):
        if candidate in env and candidate not in locations:
            locations.append(candidate)
    if not locations and item in env:
        locations.append(item)
    return locations


def _is_inside(item: str, holder: str, env: dict | None) -> bool:
    return bool(item and holder and holder in _parent_chain(item, env))


def _expected_robot_locations(
    *,
    failed_step: dict | None,
    repair_catalog: SkillRepairCatalog,
    env: dict | None,
) -> list[str]:
    action = _action_from_step(failed_step)
    spec = repair_catalog.get(action["skill"])
    if not spec:
        return []
    if spec.can_grasp_item:
        return _interaction_locations_for_item(spec.item_value(action), env)

    candidates = [
        spec.location_value(action),
        spec.destination_value(action),
        spec.target_value(action),
        spec.device_value(action),
    ]
    return [candidate for candidate in candidates if candidate]


def _location_predicate_if_unsatisfied(
    *,
    failed_step: dict | None,
    repair_catalog: SkillRepairCatalog,
    env: dict | None,
    robot: dict | None,
) -> list[PredicateKey]:
    actual = str((robot or {}).get("robot_location", "") or "")
    expected = _expected_robot_locations(failed_step=failed_step, repair_catalog=repair_catalog, env=env)
    if expected and actual not in expected:
        return [("robot", "robot", "robot_location")]
    return []


def _access_state_targets(
    *,
    failed_step: dict | None,
    repair_catalog: SkillRepairCatalog,
    env: dict | None,
) -> list[str]:
    action = _action_from_step(failed_step)
    spec = repair_catalog.get(action["skill"])
    if not spec:
        return []

    targets: list[str] = []
    if spec.can_grasp_item:
        targets.extend(_parent_chain(spec.item_value(action), env))
    if spec.can_place_item:
        targets.append(spec.destination_value(action))
    for value in (spec.target_value(action), spec.device_value(action), spec.location_value(action)):
        if value:
            targets.append(value)
    return [target for index, target in enumerate(targets) if target and target not in targets[:index]]


def _unsatisfied_access_state_predicates(
    *,
    failed_step: dict | None,
    repair_catalog: SkillRepairCatalog,
    env: dict | None,
) -> list[PredicateKey]:
    access_state_keys = repair_catalog.access_state_keys()
    if not isinstance(env, dict) or not access_state_keys:
        return []
    predicates: list[PredicateKey] = []
    for target in _access_state_targets(failed_step=failed_step, repair_catalog=repair_catalog, env=env):
        states = env.get(target, {}).get("states", {}) if isinstance(env.get(target, {}), dict) else {}
        if not isinstance(states, dict):
            continue
        for key in sorted(access_state_keys):
            if states.get(key) is False:
                predicates.append(("state", target, key))
    return predicates


def _relationship_predicates_if_unsatisfied(
    *,
    failed_step: dict | None,
    repair_catalog: SkillRepairCatalog,
    env: dict | None,
) -> list[PredicateKey]:
    action = _action_from_step(failed_step)
    spec = repair_catalog.get(action["skill"])
    if not spec or not spec.can_transform_item:
        return []
    item = spec.item_value(action)
    device = spec.device_value(action)
    if item and device and not _is_inside(item, device, env):
        return [("entity", item, "direct_parent")]
    return []


def _infer_failed_predicates(
    *,
    failed_step: dict | None,
    failure_env: dict | None,
    failure_robot: dict | None,
    repair_catalog: SkillRepairCatalog,
) -> list[PredicateKey]:
    predicates: list[PredicateKey] = []
    action = _action_from_step(failed_step)
    spec = repair_catalog.get(action["skill"])

    robot_hold = (failure_robot or {}).get("robot_holding")
    if spec and spec.requires_empty_hand and robot_hold and robot_hold != EMPTY_HAND_VALUE:
        predicates.append(("robot", "robot", "robot_holding"))
    if spec and spec.can_place_item and robot_hold != spec.item_value(action):
        predicates.append(("robot", "robot", "robot_holding"))

    predicates.extend(
        _location_predicate_if_unsatisfied(
            failed_step=failed_step,
            repair_catalog=repair_catalog,
            env=failure_env,
            robot=failure_robot,
        )
    )

    predicates.extend(
        _unsatisfied_access_state_predicates(
            failed_step=failed_step,
            repair_catalog=repair_catalog,
            env=failure_env,
        )
    )
    predicates.extend(
        _state_predicates_for_expected_values(
            targets=_target_candidates_from_step(failed_step, repair_catalog, failure_env),
            expected_values=_declared_state_constraints(
                failed_step=failed_step,
                repair_catalog=repair_catalog,
            ),
            env=failure_env,
        )
    )
    predicates.extend(
        _relationship_predicates_if_unsatisfied(
            failed_step=failed_step,
            repair_catalog=repair_catalog,
            env=failure_env,
        )
    )

    deduped = []
    seen = set()
    for predicate in predicates:
        if predicate not in seen:
            deduped.append(predicate)
            seen.add(predicate)
    return deduped


def _selected_causal_candidate(
    graph: dict[str, Any],
    failed_step_num: int | None,
    max_backtrack_depth: int | None,
) -> dict[str, Any] | None:
    candidates = [
        candidate
        for candidate in graph.get("causal_candidates", [])
        if isinstance(candidate, dict) and isinstance(candidate.get("step"), int)
    ]
    if failed_step_num is not None:
        candidates = [candidate for candidate in candidates if candidate["step"] < failed_step_num]
    if max_backtrack_depth and max_backtrack_depth > 0 and failed_step_num is not None:
        candidates = [
            candidate
            for candidate in candidates
            if failed_step_num - int(candidate["step"]) <= max_backtrack_depth
        ]
    if not candidates:
        return None
    return max(candidates, key=lambda item: int(item["step"]))


def _step_by_num(steps: list, step_num: int | None) -> dict:
    if step_num is None:
        return {}
    for step in steps or []:
        if isinstance(step, dict) and _step_num(step) == step_num:
            return step
    return {}


def _checkpoint_before_step(
    *,
    rollback_step_num: int,
    trajectory_records: list[dict[str, Any]],
    fallback_env: dict,
    fallback_robot: dict,
) -> tuple[dict, dict]:
    for record in trajectory_records or []:
        step = _record_step(record)
        if _step_num(step) == rollback_step_num:
            return (
                copy.deepcopy(record.get("before_env", {})),
                copy.deepcopy(record.get("before_robot", {})),
            )
    return copy.deepcopy(fallback_env), copy.deepcopy(fallback_robot)


def _rollback_reason(
    *,
    issue_type: str,
    fix_advice: str,
    causal_candidate: dict[str, Any] | None,
    failed_step_num: int | None,
    rollback_step_num: int,
) -> str:
    if not causal_candidate:
        return f"未找到明确因果写入动作，回滚到失败步 {rollback_step_num}。"
    action = causal_candidate.get("action") or {}
    predicate = causal_candidate.get("predicate", "")
    return (
        f"第 {failed_step_num} 步失败前置条件由第 {rollback_step_num} 步改变的状态触发；"
        f"冲突谓词: {predicate}; 因果动作: {action}; "
        f"失败类型: {issue_type}; 修复建议: {fix_advice}"
    )


def _build_sda_repair_state(
    *,
    graph: dict[str, Any],
    todo_list: list,
    validated_steps: list,
    failed_step: dict | None,
    rollback_step: dict,
    rollback_step_num: int,
    causal_candidate: dict[str, Any] | None,
    checkpoint_env: dict,
    checkpoint_robot: dict,
    issue_type: str,
    fix_advice: str,
    failure_kind: str,
) -> dict[str, Any]:
    failed_step_num = _step_num(failed_step)
    verified_prefix = _compact_todo_list(validated_steps)
    return {
        "version": SDA_SCHEMA_VERSION,
        "mode": MODE_SDA_CAUSAL_REPAIR,
        "failure_kind": failure_kind,
        "issue_type": issue_type,
        "failure": {
            "issue": f"第 {failed_step_num} 步物理拦截: {issue_type}" if failed_step_num else issue_type,
            "fix_advice": fix_advice,
            "failed_step": _compact_step(failed_step),
            "causal_step": copy.deepcopy(causal_candidate.get("action")) if causal_candidate else None,
            "rollback_step": _compact_step(rollback_step),
        },
        "state_dependency_graph": copy.deepcopy(graph),
        "trajectory": {
            "original_todo_list": _compact_todo_list(todo_list),
            "verified_prefix": verified_prefix,
            "validated_prefix": verified_prefix,
            "validated_step_count": len(validated_steps),
            "next_step_num": len(validated_steps) + 1,
            "prefix_is_valid": True,
            "rollback_step": _compact_step(rollback_step),
            "discarded_suffix": _compact_todo_list(
                [
                    step
                    for step in (todo_list or [])
                    if isinstance(step, dict) and (_step_num(step) or 0) >= rollback_step_num
                ]
            ),
        },
        "current_simulated_state": {
            "robot": copy.deepcopy(checkpoint_robot),
            "environment": copy.deepcopy(checkpoint_env),
            "note": "This is a sandbox simulated state selected by SDA causal rollback, not the real runtime scene.",
        },
        "frontier": {
            "type": "regenerate_suffix_from_causal_rollback",
            "next_step_num": len(validated_steps) + 1,
            "instruction": (
                "Keep only the verified prefix fixed. Discard the rollback step and all later original actions. "
                "Regenerate a suffix that avoids the causal conflict recorded in state_dependency_graph. "
                "If the discarded action is still necessary for the task, reorder it or add legal prerequisite/recovery actions."
            ),
        },
    }


def select_repair_checkpoint(
    *,
    todo_list: list,
    validated_steps: list,
    failed_step: dict | None,
    issue_type: str,
    fix_advice: str,
    failure_env: dict,
    failure_robot: dict,
    trajectory_records: list[dict[str, Any]],
    sandbox_start_env: dict,
    sandbox_start_robot: dict,
    failure_kind: str = "sandbox_failure",
    max_backtrack_depth: int | None = None,
    repair_catalog: SkillRepairCatalog | None = None,
) -> dict[str, Any]:
    failed_step_num = _step_num(failed_step) or len(validated_steps) + 1
    catalog = repair_catalog or load_repair_catalog()
    graph = build_state_dependency_graph(
        todo_list=todo_list,
        trajectory_records=trajectory_records,
        failed_step=failed_step,
        issue_type=issue_type,
        fix_advice=fix_advice,
        failure_env=failure_env,
        failure_robot=failure_robot,
        repair_catalog=catalog,
    )
    causal_candidate = _selected_causal_candidate(graph, failed_step_num, max_backtrack_depth)
    rollback_step_num = int(causal_candidate["step"]) if causal_candidate else failed_step_num
    rollback_step = _step_by_num(todo_list, rollback_step_num) or _step_by_num(validated_steps, rollback_step_num)
    if not rollback_step and failed_step_num == rollback_step_num:
        rollback_step = failed_step or {}

    repair_validated_steps = [
        copy.deepcopy(step)
        for step in (validated_steps or [])
        if isinstance(step, dict) and (_step_num(step) or 0) < rollback_step_num
    ]
    checkpoint_env, checkpoint_robot = _checkpoint_before_step(
        rollback_step_num=rollback_step_num,
        trajectory_records=trajectory_records,
        fallback_env=sandbox_start_env,
        fallback_robot=sandbox_start_robot,
    )
    reason = _rollback_reason(
        issue_type=issue_type,
        fix_advice=fix_advice,
        causal_candidate=causal_candidate,
        failed_step_num=failed_step_num,
        rollback_step_num=rollback_step_num,
    )
    sda_state = _build_sda_repair_state(
        graph=graph,
        todo_list=todo_list,
        validated_steps=repair_validated_steps,
        failed_step=failed_step,
        rollback_step=rollback_step,
        rollback_step_num=rollback_step_num,
        causal_candidate=causal_candidate,
        checkpoint_env=checkpoint_env,
        checkpoint_robot=checkpoint_robot,
        issue_type=issue_type,
        fix_advice=fix_advice,
        failure_kind=failure_kind,
    )
    sda_state["rollback"] = {
        "selected_step": rollback_step_num,
        "failed_step": failed_step_num,
        "reason": reason,
        "causal_predicate": causal_candidate.get("predicate") if causal_candidate else "",
    }
    return {
        "validated_steps": repair_validated_steps,
        "checkpoint_env": checkpoint_env,
        "checkpoint_robot": checkpoint_robot,
        "failed_step": failed_step or {},
        "rollback_step": rollback_step,
        "rollback_step_num": rollback_step_num,
        "sda_state": sda_state,
        "reason": reason,
    }
