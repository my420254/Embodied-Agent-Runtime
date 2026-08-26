from __future__ import annotations

import copy
from typing import Any


SkillPlanningCatalog = Any


VCR_DEPENDENCY_SCHEMA_VERSION = "vcr_dependency_v1"
EMPTY_HAND_VALUE = "空"

PredicateKey = tuple[str, str, str]


class _ClosureCatalogView:
    def __init__(self, catalog: SkillPlanningCatalog, skill_closure: list[str]):
        allowed = {str(name).strip() for name in skill_closure if str(name).strip()}
        specs = getattr(catalog, "specs", [])
        self.specs = [
            spec
            for spec in (specs if isinstance(specs, list) else [])
            if str(getattr(spec, "name", "") or "") in allowed
        ]
        self.by_name = {
            str(getattr(spec, "name", "") or ""): spec
            for spec in self.specs
            if str(getattr(spec, "name", "") or "")
        }

    def get(self, skill_name: str) -> Any:
        return self.by_name.get(skill_name)

    def access_state_keys(self) -> set[str]:
        return {
            spec.state_key
            for spec in self.specs
            if getattr(spec, "can_set_state", False)
            and getattr(spec, "access_state", False)
            and getattr(spec, "state_key", "")
        }


def _catalog_for_skill_closure(
    catalog: SkillPlanningCatalog,
    skill_closure: list[str] | None,
) -> SkillPlanningCatalog:
    if skill_closure is None:
        return catalog
    return _ClosureCatalogView(catalog, skill_closure)


def _step_number(step: dict | None) -> int | None:
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


def _action_from_step(step: dict | None) -> dict[str, Any]:
    execution = _execution(step)
    parameters = execution.get("parameters", {})
    return {
        "skill": str(execution.get("skill", "") or ""),
        "parameters": copy.deepcopy(parameters) if isinstance(parameters, dict) else {},
    }


def _compact_step(step: dict | None) -> dict[str, Any] | None:
    if not isinstance(step, dict):
        return None
    action = _action_from_step(step)
    return {
        "step": _step_number(step),
        "skill": action["skill"],
        "parameters": action["parameters"],
    }


def _predicate_id(key: PredicateKey) -> str:
    return ".".join(part for part in key if part)


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
                "key": key,
                "predicate": _predicate_id(key),
                "before": copy.deepcopy(before_value),
                "after": copy.deepcopy(after_value),
            }
        )
    return changes


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


def _interaction_locations(item: str, env: dict | None) -> list[str]:
    if not item or not isinstance(env, dict) or item not in env:
        return []
    locations = [candidate for candidate in _parent_chain(item, env) if candidate in env]
    if not locations:
        locations.append(item)
    return locations


def _target_candidates(
    step: dict | None,
    catalog: SkillPlanningCatalog,
    env: dict | None,
) -> list[str]:
    action = _action_from_step(step)
    candidates: list[str] = []
    spec = catalog.get(action["skill"])
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

    env_index = env if isinstance(env, dict) else {}
    for value in action["parameters"].values():
        if isinstance(value, str) and value and value not in candidates:
            if not env_index or value in env_index:
                candidates.append(value)
    return candidates


def _expected_robot_locations(
    step: dict | None,
    catalog: SkillPlanningCatalog,
    env: dict | None,
) -> list[str]:
    action = _action_from_step(step)
    spec = catalog.get(action["skill"])
    if not spec:
        return []
    if spec.can_grasp_item:
        return _interaction_locations(spec.item_value(action), env)
    values = (
        spec.location_value(action),
        spec.destination_value(action),
        spec.target_value(action),
        spec.device_value(action),
    )
    return [value for index, value in enumerate(values) if value and value not in values[:index]]


def _access_targets(
    step: dict | None,
    catalog: SkillPlanningCatalog,
    env: dict | None,
) -> list[str]:
    action = _action_from_step(step)
    spec = catalog.get(action["skill"])
    if not spec:
        return []
    targets: list[str] = []
    if spec.can_grasp_item:
        targets.extend(_parent_chain(spec.item_value(action), env))
    if spec.can_place_item:
        destination = spec.destination_value(action)
        targets.append(destination)
        targets.extend(_parent_chain(destination, env))
    return [value for index, value in enumerate(targets) if value and value not in targets[:index]]


def _declared_state_constraints(
    step: dict | None,
    catalog: SkillPlanningCatalog,
) -> dict[str, Any]:
    spec = catalog.get(_action_from_step(step)["skill"])
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


def _infer_failed_predicates(
    *,
    failed_step: dict | None,
    failure_env: dict | None,
    failure_robot: dict | None,
    catalog: SkillPlanningCatalog,
) -> list[PredicateKey]:
    predicates: list[PredicateKey] = []
    action = _action_from_step(failed_step)
    spec = catalog.get(action["skill"])
    held = (failure_robot or {}).get("robot_holding")

    if spec and spec.requires_empty_hand and held and held != EMPTY_HAND_VALUE:
        predicates.append(("robot", "robot", "robot_holding"))
    if spec and spec.can_place_item and held != spec.item_value(action):
        predicates.append(("robot", "robot", "robot_holding"))

    actual_location = str((failure_robot or {}).get("robot_location", "") or "")
    expected_locations = _expected_robot_locations(failed_step, catalog, failure_env)
    if expected_locations and actual_location not in expected_locations:
        predicates.append(("robot", "robot", "robot_location"))

    if isinstance(failure_env, dict):
        access_keys = catalog.access_state_keys()
        for target in _access_targets(failed_step, catalog, failure_env):
            info = failure_env.get(target, {})
            states = info.get("states", {}) if isinstance(info, dict) else {}
            if not isinstance(states, dict):
                continue
            for key in sorted(access_keys):
                if states.get(key) is False:
                    predicates.append(("state", target, key))

        constraints = _declared_state_constraints(failed_step, catalog)
        for target in _target_candidates(failed_step, catalog, failure_env):
            info = failure_env.get(target, {})
            states = info.get("states", {}) if isinstance(info, dict) else {}
            if not isinstance(states, dict):
                continue
            for key, expected in constraints.items():
                if key in states and states.get(key) != expected:
                    predicates.append(("state", target, key))

    if spec and spec.can_transform_item:
        item = spec.item_value(action)
        device = spec.device_value(action)
        if item and device and device not in _parent_chain(item, failure_env):
            predicates.append(("entity", item, "direct_parent"))

    deduped: list[PredicateKey] = []
    seen = set()
    for predicate in predicates:
        if predicate not in seen:
            deduped.append(predicate)
            seen.add(predicate)
    return deduped


def _failed_precondition_contracts(
    *,
    failed_predicates: list[PredicateKey],
    failed_step: dict | None,
    failure_env: dict | None,
    failure_robot: dict | None,
    catalog: SkillPlanningCatalog,
) -> list[dict[str, Any]]:
    action = _action_from_step(failed_step)
    spec = catalog.get(action["skill"])
    expected_locations = _expected_robot_locations(failed_step, catalog, failure_env)
    declared_states = _declared_state_constraints(failed_step, catalog)
    access_state_keys = catalog.access_state_keys()
    actual_states = _state_predicates(failure_env, failure_robot)
    contracts: list[dict[str, Any]] = []

    for key in failed_predicates:
        contract: dict[str, Any] = {"predicate": _predicate_id(key)}
        if key in actual_states:
            contract["actual_value"] = copy.deepcopy(actual_states[key])
        domain, _entity, attribute = key
        if domain == "robot" and attribute == "robot_holding" and spec:
            if spec.requires_empty_hand or spec.can_grasp_item:
                contract["required_value"] = EMPTY_HAND_VALUE
            elif spec.can_place_item:
                contract["required_value"] = spec.item_value(action)
        elif domain == "robot" and attribute == "robot_location":
            if len(expected_locations) == 1:
                contract["required_value"] = expected_locations[0]
            elif expected_locations:
                contract["allowed_values"] = list(expected_locations)
        elif domain == "state":
            if attribute in declared_states:
                contract["required_value"] = copy.deepcopy(
                    declared_states[attribute]
                )
            elif attribute in access_state_keys:
                contract["required_value"] = True
        elif domain == "entity" and attribute == "direct_parent" and spec:
            device = spec.device_value(action)
            if device:
                contract["required_value"] = device
        contracts.append(contract)
    return contracts


def build_vcr_dependency_graph(
    *,
    todo_list: list,
    trajectory_records: list[dict[str, Any]],
    failed_step: dict | None,
    issue_type: str,
    fix_advice: str,
    failure_env: dict | None,
    failure_robot: dict | None,
    skill_profile: str | None = None,
    skill_catalog: SkillPlanningCatalog | None = None,
    skill_closure: list[str] | None = None,
) -> dict[str, Any]:
    if skill_catalog is None:
        raise ValueError("VCR requires an evaluation-provided skill catalog")
    catalog = _catalog_for_skill_closure(skill_catalog, skill_closure)
    allowed_writers = set(getattr(catalog, "by_name", {}).keys())
    filter_writers = skill_closure is not None
    nodes = []
    writer_by_predicate: dict[PredicateKey, dict[str, Any]] = {}
    for record in trajectory_records or []:
        step = record.get("step", {}) if isinstance(record, dict) else {}
        action = _action_from_step(step)
        changes = _changed_predicates(
            record.get("before_env", {}),
            record.get("before_robot", {}),
            record.get("after_env", {}),
            record.get("after_robot", {}),
        )
        nodes.append(
            {
                "step": _step_number(step),
                "action": _compact_step(step),
                "writes": [
                    {
                        "predicate": change["predicate"],
                        "before": copy.deepcopy(change["before"]),
                        "after": copy.deepcopy(change["after"]),
                    }
                    for change in changes
                ],
            }
        )
        if filter_writers and action["skill"] not in allowed_writers:
            continue
        for change in changes:
            writer_by_predicate[change["key"]] = {
                "step": _step_number(step),
                "action": _compact_step(step),
                "predicate": change["predicate"],
                "before": copy.deepcopy(change["before"]),
                "after": copy.deepcopy(change["after"]),
            }

    failed_predicates = _infer_failed_predicates(
        failed_step=failed_step,
        failure_env=failure_env,
        failure_robot=failure_robot,
        catalog=catalog,
    )
    failed_preconditions = _failed_precondition_contracts(
        failed_predicates=failed_predicates,
        failed_step=failed_step,
        failure_env=failure_env,
        failure_robot=failure_robot,
        catalog=catalog,
    )
    candidates = [
        copy.deepcopy(writer_by_predicate[predicate])
        for predicate in failed_predicates
        if predicate in writer_by_predicate
    ]
    return {
        "version": VCR_DEPENDENCY_SCHEMA_VERSION,
        "skill_closure": list(skill_closure or []),
        "nodes": nodes,
        "failure": {
            "issue_type": issue_type,
            "fix_advice": fix_advice,
            "failed_step": _compact_step(failed_step),
            "failed_predicates": [_predicate_id(predicate) for predicate in failed_predicates],
            "failed_preconditions": failed_preconditions,
        },
        "causal_candidates": candidates,
        "original_todo_list": [_compact_step(step) for step in todo_list or [] if isinstance(step, dict)],
    }


def _select_causal_candidate(
    graph: dict[str, Any],
    failed_step_number: int,
    max_backtrack_depth: int | None,
) -> dict[str, Any] | None:
    candidates = [
        candidate
        for candidate in graph.get("causal_candidates", [])
        if isinstance(candidate, dict)
        and isinstance(candidate.get("step"), int)
        and int(candidate["step"]) < failed_step_number
    ]
    if max_backtrack_depth and max_backtrack_depth > 0:
        candidates = [
            candidate
            for candidate in candidates
            if failed_step_number - int(candidate["step"]) <= max_backtrack_depth
        ]
    if not candidates:
        return None
    return max(candidates, key=lambda candidate: int(candidate["step"]))


def _step_by_number(steps: list, number: int) -> dict:
    for step in steps or []:
        if isinstance(step, dict) and _step_number(step) == number:
            return step
    return {}


def _checkpoint_before_step(
    number: int,
    trajectory_records: list[dict[str, Any]],
    fallback_env: dict,
    fallback_robot: dict,
) -> tuple[dict, dict]:
    for record in trajectory_records or []:
        step = record.get("step", {}) if isinstance(record, dict) else {}
        if _step_number(step) == number:
            return (
                copy.deepcopy(record.get("before_env", {})),
                copy.deepcopy(record.get("before_robot", {})),
            )
    return copy.deepcopy(fallback_env), copy.deepcopy(fallback_robot)


def select_vcr_repair_checkpoint(
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
    max_backtrack_depth: int | None = None,
    skill_profile: str | None = None,
    skill_catalog: SkillPlanningCatalog | None = None,
    skill_closure: list[str] | None = None,
) -> dict[str, Any]:
    failed_number = _step_number(failed_step) or len(validated_steps) + 1
    if skill_catalog is None:
        raise ValueError("VCR requires an evaluation-provided skill catalog")
    catalog = skill_catalog
    graph = build_vcr_dependency_graph(
        todo_list=todo_list,
        trajectory_records=trajectory_records,
        failed_step=failed_step,
        issue_type=issue_type,
        fix_advice=fix_advice,
        failure_env=failure_env,
        failure_robot=failure_robot,
        skill_profile=skill_profile,
        skill_catalog=catalog,
        skill_closure=skill_closure,
    )
    causal_candidate = _select_causal_candidate(graph, failed_number, max_backtrack_depth)
    rollback_number = int(causal_candidate["step"]) if causal_candidate else failed_number
    rollback_step = (
        _step_by_number(todo_list, rollback_number)
        or _step_by_number(validated_steps, rollback_number)
        or (failed_step if rollback_number == failed_number else {})
        or {}
    )
    repair_validated_steps = [
        copy.deepcopy(step)
        for step in validated_steps or []
        if isinstance(step, dict) and (_step_number(step) or 0) < rollback_number
    ]

    if causal_candidate:
        checkpoint_env, checkpoint_robot = _checkpoint_before_step(
            rollback_number,
            trajectory_records,
            sandbox_start_env,
            sandbox_start_robot,
        )
        reason = (
            f"第 {failed_number} 步的失败前置条件由第 {rollback_number} 步改变；"
            f"冲突谓词: {causal_candidate.get('predicate', '')}; "
            f"因果动作: {causal_candidate.get('action')}; "
            f"失败类型: {issue_type}; 修复建议: {fix_advice}"
        )
    else:
        checkpoint_env = copy.deepcopy(failure_env)
        checkpoint_robot = copy.deepcopy(failure_robot)
        reason = "未找到可回溯的因果写入；从失败动作前的真实状态插入前置修复。"

    return {
        "validated_steps": repair_validated_steps,
        "checkpoint_env": checkpoint_env,
        "checkpoint_robot": checkpoint_robot,
        "failed_step": copy.deepcopy(failed_step or {}),
        "rollback_step": copy.deepcopy(rollback_step),
        "rollback_step_num": rollback_number,
        "causal_predicate": causal_candidate.get("predicate", "") if causal_candidate else "",
        "causal_action": copy.deepcopy(causal_candidate.get("action")) if causal_candidate else None,
        "causal_before": copy.deepcopy(causal_candidate.get("before")) if causal_candidate else None,
        "causal_after": copy.deepcopy(causal_candidate.get("after")) if causal_candidate else None,
        "failed_preconditions": copy.deepcopy(
            graph.get("failure", {}).get("failed_preconditions", [])
        ),
        "state_dependency_graph": graph,
        "reason": reason,
    }


__all__ = [
    "VCR_DEPENDENCY_SCHEMA_VERSION",
    "build_vcr_dependency_graph",
    "select_vcr_repair_checkpoint",
]
