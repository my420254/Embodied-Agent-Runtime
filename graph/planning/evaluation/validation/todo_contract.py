from __future__ import annotations

import copy
import re
from dataclasses import dataclass, field
from typing import Any

from graph.state import PlanningState
from skills.planning_catalog import (
    SkillPlanningCatalog,
    SkillPlanningSpec,
    load_planning_catalog,
)


INDEXED_ENTITY_RE = re.compile(r"^(?P<base>.+) \((?P<index>\d+)\)$")


@dataclass
class _RuntimeNames:
    known_names: set[str]
    room_names: set[str]
    generated_names: set[str] = field(default_factory=set)


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    return False


def _string_value(value: Any) -> str:
    return str(value or "").strip()


def _format_catalog(values: set[str], *, limit: int = 14) -> str:
    ordered = sorted(values)
    if len(ordered) <= limit:
        return ", ".join(ordered)
    return ", ".join(ordered[:limit]) + f", ... ({len(ordered)} total)"


def _is_room_entry(info: Any) -> bool:
    if not isinstance(info, dict):
        return False
    entity_type = str(info.get("type") or info.get("category") or "").strip().lower()
    if entity_type in {"room", "location"}:
        return True
    direct_parent = str(info.get("direct_parent") or "").strip().lower()
    full_path = info.get("full_path")
    return direct_parent in {"未知环境", "unknown"} and (
        not isinstance(full_path, list) or not full_path
    )


def _runtime_names(current_env: Any) -> _RuntimeNames:
    if not isinstance(current_env, dict):
        return _RuntimeNames(known_names=set(), room_names=set())
    known_names = {str(name).strip() for name in current_env if str(name).strip()}
    room_names = {
        str(name).strip()
        for name, info in current_env.items()
        if str(name).strip() and _is_room_entry(info)
    }
    return _RuntimeNames(known_names=known_names, room_names=room_names)


def _state_context_value(state: PlanningState, field_name: str) -> str:
    key = str(field_name or "").strip()
    if not key or not isinstance(state, dict):
        return ""
    for section in (
        "task_context",
        "task_input_payload",
        "evaluation_context",
        "structured_task",
    ):
        payload = state.get(section)
        if isinstance(payload, dict):
            value = payload.get(key)
            if value not in (None, ""):
                return _string_value(value)
    return _string_value(state.get(key))


def _max_index(base: str, names: set[str]) -> int:
    max_index = 0
    for name in names:
        match = INDEXED_ENTITY_RE.fullmatch(name)
        if match and match.group("base") == base:
            max_index = max(max_index, int(match.group("index")))
    return max_index


def _indexed_generated_names(target: str, names: set[str], count: int) -> set[str]:
    match = INDEXED_ENTITY_RE.fullmatch(_string_value(target))
    if not match or count <= 0:
        return set()
    base = str(match.group("base") or "").strip()
    first_index = _max_index(base, names) + 1
    return {f"{base} ({index})" for index in range(first_index, first_index + count)}


def _field_parts(value: Any, *, allow_comma_separated: bool) -> list[str]:
    if isinstance(value, list):
        return [_string_value(item) for item in value if _string_value(item)]
    if allow_comma_separated:
        return [
            part.strip() for part in _string_value(value).split(",") if part.strip()
        ]
    text = _string_value(value)
    return [text] if text else []


class _TodoContractChecker:
    def __init__(
        self,
        *,
        state: PlanningState,
        skill_catalog: SkillPlanningCatalog,
        current_env: dict[str, Any],
    ) -> None:
        self.state = state
        self.catalog = skill_catalog
        self.names = _runtime_names(current_env)

    def validate(self, todo_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for index, raw_step in enumerate(todo_list or [], start=1):
            normalized.append(self._validate_step(raw_step, index))
        return normalized

    def _resolve_spec(self, step: dict[str, Any], index: int) -> SkillPlanningSpec:
        action_fields = tuple(
            dict.fromkeys(
                spec.action_field
                for spec in self.catalog.raw_specs
                if spec.action_field
            )
        )
        for field_name in action_fields:
            if field_name not in step:
                continue
            action_name = _string_value(step.get(field_name))
            if not action_name:
                continue
            spec = self.catalog.get_action(action_name)
            if spec is not None and spec.action_field == field_name:
                return spec
            available = _format_catalog(
                {
                    spec.action_name
                    for spec in self.catalog.raw_specs
                    if spec.action_name
                }
            )
            raise ValueError(
                f"todo_list step {index} uses unsupported action {action_name!r}; "
                f"available actions: {available}"
            )
        expected = ", ".join(action_fields) or "action"
        raise ValueError(
            f"todo_list step {index} missing configured action field: {expected}"
        )

    def _validate_context(
        self, spec: SkillPlanningSpec, step: dict[str, Any], index: int
    ) -> None:
        if not spec.context_field or not spec.context_values:
            return
        current_value = _state_context_value(self.state, spec.context_field)
        if not current_value:
            return
        allowed = {value.casefold() for value in spec.context_values}
        if current_value.casefold() in allowed:
            return
        action_name = _string_value(step.get(spec.action_field))
        raise ValueError(
            f"todo_list step {index} action {action_name!r} is not valid when "
            f"{spec.context_field}={current_value!r}; allowed values: {', '.join(spec.context_values)}"
        )

    def _allowed_fields(self, spec: SkillPlanningSpec) -> set[str]:
        allowed = {"step", spec.action_field}
        allowed.update(spec.required_fields)
        allowed.update(field for field, _value in spec.fixed_fields)
        allowed.update(spec.entity_fields)
        allowed.update(spec.room_fields)
        allowed.update(spec.unchecked_fields)
        if spec.args_arity is not None:
            allowed.add(spec.args_field)
        return {field for field in allowed if field}

    def _validate_required_fields(
        self, spec: SkillPlanningSpec, step: dict[str, Any], index: int
    ) -> None:
        missing = [
            field
            for field in spec.required_fields
            if field not in step or _is_missing(step.get(field))
        ]
        if missing:
            action_name = _string_value(step.get(spec.action_field))
            raise ValueError(
                f"todo_list step {index} action {action_name!r} missing required fields: {missing}"
            )

    def _validate_extra_fields(
        self, spec: SkillPlanningSpec, step: dict[str, Any], index: int
    ) -> None:
        if spec.allow_extra_fields:
            return
        allowed = self._allowed_fields(spec)
        extra = {str(key) for key in step.keys()} - allowed
        if extra:
            action_name = _string_value(step.get(spec.action_field))
            raise ValueError(
                f"todo_list step {index} action {action_name!r} contains unsupported fields: {sorted(extra)}"
            )

    def _validate_fixed_fields(
        self, spec: SkillPlanningSpec, step: dict[str, Any], index: int
    ) -> None:
        action_name = _string_value(step.get(spec.action_field))
        for field_name, expected in spec.fixed_fields:
            actual = _string_value(step.get(field_name))
            if actual != expected:
                raise ValueError(
                    f"todo_list step {index} action {action_name!r} field {field_name} "
                    f"must be {expected!r}, got {actual!r}"
                )

    def _validate_args(
        self, spec: SkillPlanningSpec, step: dict[str, Any], index: int
    ) -> list[str]:
        if spec.args_arity is None:
            return []
        action_name = _string_value(step.get(spec.action_field))
        args = step.get(spec.args_field)
        if not isinstance(args, list):
            raise ValueError(
                f"todo_list step {index} action {action_name!r} field {spec.args_field} must be a list"
            )
        normalized = [_string_value(item) for item in args]
        if len(normalized) != spec.args_arity:
            raise ValueError(
                f"todo_list step {index} action {action_name!r} expects {spec.args_arity} args, "
                f"got {len(normalized)}"
            )
        for arg_index in spec.entity_args:
            if arg_index < 0 or arg_index >= len(normalized):
                raise ValueError(
                    f"todo_list step {index} action {action_name!r} declares invalid entity arg index {arg_index}"
                )
            self._validate_entity_value(
                spec, normalized[arg_index], index, f"{spec.args_field}[{arg_index}]"
            )
        return normalized

    def _validate_entity_value(
        self, spec: SkillPlanningSpec, value: str, index: int, field_name: str
    ) -> None:
        action_label = spec.action_name or spec.name
        if spec.entity_pattern:
            try:
                matches_pattern = re.fullmatch(spec.entity_pattern, value) is not None
            except re.error as exc:
                raise ValueError(
                    f"skill {spec.name!r} has invalid planner_entity_pattern: {exc}"
                ) from exc
            if not matches_pattern:
                raise ValueError(
                    f"todo_list step {index} action {action_label!r} field {field_name} "
                    f"does not match required entity pattern {spec.entity_pattern!r}: {value!r}"
                )
        if not self.names.known_names:
            return
        available = self.names.known_names | self.names.generated_names
        if value in available:
            return
        raise ValueError(
            f"todo_list step {index} action {action_label!r} field {field_name} references unknown entity "
            f"{value!r}; available entities: {_format_catalog(available)}"
        )

    def _validate_room_value(
        self, spec: SkillPlanningSpec, value: str, index: int, field_name: str
    ) -> None:
        if not self.names.known_names:
            return
        available_rooms = self.names.room_names or self.names.known_names
        if value in available_rooms:
            return
        action_label = spec.action_name or spec.name
        raise ValueError(
            f"todo_list step {index} action {action_label!r} field {field_name} references unknown room "
            f"{value!r}; available rooms: {_format_catalog(available_rooms)}"
        )

    def _validate_named_fields(
        self, spec: SkillPlanningSpec, step: dict[str, Any], index: int
    ) -> None:
        for field_name in spec.entity_fields:
            for value in _field_parts(
                step.get(field_name),
                allow_comma_separated=spec.allow_comma_separated_entities,
            ):
                self._validate_entity_value(spec, value, index, field_name)
        for field_name in spec.room_fields:
            for value in _field_parts(
                step.get(field_name), allow_comma_separated=False
            ):
                self._validate_room_value(spec, value, index, field_name)

    def _first_dynamic_source(
        self, spec: SkillPlanningSpec, step: dict[str, Any], args: list[str]
    ) -> str:
        for field_name in spec.entity_fields:
            parts = _field_parts(
                step.get(field_name),
                allow_comma_separated=spec.allow_comma_separated_entities,
            )
            if len(parts) == 1:
                return parts[0]
        if args:
            return args[0]
        return ""

    def _apply_dynamic_entities(
        self, spec: SkillPlanningSpec, step: dict[str, Any], args: list[str]
    ) -> None:
        rule = str(spec.dynamic_entity_rule or "").strip()
        if not rule:
            return
        source = self._first_dynamic_source(spec, step, args)
        if not source:
            return
        if rule == "slice_parts_from_target":
            self.names.generated_names.update(
                {f"{source}_part_{index}" for index in range(2)}
            )
            return
        prefix = "indexed_same_base_copies:"
        if rule.startswith(prefix):
            try:
                count = int(rule.removeprefix(prefix))
            except ValueError as exc:
                raise ValueError(
                    f"skill {spec.name!r} has invalid dynamic entity rule {rule!r}"
                ) from exc
            self.names.generated_names.update(
                _indexed_generated_names(
                    source,
                    self.names.known_names | self.names.generated_names,
                    count,
                )
            )

    def _validate_step(self, raw_step: Any, index: int) -> dict[str, Any]:
        if not isinstance(raw_step, dict):
            raise ValueError(f"todo_list step {index} must be an object")
        step = copy.deepcopy(raw_step)
        spec = self._resolve_spec(step, index)
        self._validate_context(spec, step, index)
        self._validate_required_fields(spec, step, index)
        self._validate_extra_fields(spec, step, index)
        self._validate_fixed_fields(spec, step, index)
        args = self._validate_args(spec, step, index)
        self._validate_named_fields(spec, step, index)
        self._apply_dynamic_entities(spec, step, args)

        normalized = {
            key: copy.deepcopy(value) for key, value in step.items() if key != "step"
        }
        return {"step": index, **normalized}


def validate_todo_contract(
    *,
    state: PlanningState,
    todo_list: list[dict[str, Any]],
    current_env: dict[str, Any],
    skill_catalog: SkillPlanningCatalog | None = None,
) -> list[dict[str, Any]]:
    """Validate todo_list steps against the raw action contract of configured skills."""

    catalog = skill_catalog or load_planning_catalog()
    if not catalog.raw_specs:
        return copy.deepcopy(todo_list or [])
    checker = _TodoContractChecker(
        state=state, skill_catalog=catalog, current_env=current_env
    )
    return checker.validate(todo_list or [])


__all__ = ["validate_todo_contract"]
