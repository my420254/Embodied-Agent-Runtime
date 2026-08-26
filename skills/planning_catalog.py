from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from skills.loader import load_enabled_skill_specs


def _as_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _split_items(value: Any) -> tuple[str, ...]:
    text = str(value or "").strip()
    if not text:
        return ()
    return tuple(part.strip() for part in re.split(r"[,\n;]+", text) if part.strip())


def _split_ints(value: Any) -> tuple[int, ...]:
    items: list[int] = []
    for part in _split_items(value):
        try:
            items.append(int(part))
        except ValueError:
            continue
    return tuple(items)


def _split_field_pairs(value: Any) -> tuple[tuple[str, str], ...]:
    text = str(value or "").strip()
    if not text:
        return ()
    pairs: list[tuple[str, str]] = []
    for chunk in re.split(r"[;\n]+", text):
        item = chunk.strip()
        if not item:
            continue
        if "=" not in item:
            continue
        key, raw_value = item.split("=", 1)
        key = key.strip()
        if not key:
            continue
        pairs.append((key, raw_value.strip()))
    return tuple(pairs)


def _as_value(value: Any) -> Any:
    text = str(value).strip()
    lowered = text.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"none", "null"}:
        return None
    return text


@dataclass(frozen=True)
class SkillPlanningSpec:
    name: str
    target_param: str = ""
    item_param: str = ""
    destination_param: str = ""
    location_param: str = ""
    device_param: str = ""
    requires_empty_hand: bool = False
    state_key: str = ""
    state_value: Any = None
    access_state: bool = False
    reversible_state: bool = False
    container_state_key: str = ""
    container_state_value: Any = None
    device_state_key: str = ""
    device_state_value: Any = None
    effect_state_key: str = ""
    effect_state_value: Any = None
    action_name: str = ""
    action_field: str = "action"
    required_fields: tuple[str, ...] = ()
    fixed_fields: tuple[tuple[str, str], ...] = ()
    entity_fields: tuple[str, ...] = ()
    room_fields: tuple[str, ...] = ()
    args_field: str = "args"
    args_arity: int | None = None
    entity_args: tuple[int, ...] = ()
    allow_extra_fields: bool = False
    allow_comma_separated_entities: bool = False
    entity_pattern: str = ""
    dynamic_entity_rule: str = ""
    unchecked_fields: tuple[str, ...] = ()
    context_field: str = ""
    context_values: tuple[str, ...] = ()

    @classmethod
    def from_contract(cls, name: str, contract: dict[str, str]) -> "SkillPlanningSpec":
        has_raw_contract = any(
            key in contract
            for key in (
                "planner_action_name",
                "planner_action_field",
                "planner_required_fields",
                "planner_fixed_fields",
                "planner_entity_fields",
                "planner_room_fields",
                "planner_args_field",
                "planner_args_arity",
                "planner_entity_args",
                "planner_allow_extra_fields",
                "planner_allow_comma_separated_entities",
                "planner_entity_pattern",
                "planner_dynamic_entity_rule",
                "planner_unchecked_fields",
                "planner_context_field",
                "planner_context_values",
            )
        )
        return cls(
            name=name,
            target_param=contract.get("planner_target_param", ""),
            item_param=contract.get("planner_item_param", ""),
            destination_param=contract.get("planner_destination_param", ""),
            location_param=contract.get("planner_location_param", ""),
            device_param=contract.get("planner_device_param", ""),
            requires_empty_hand=_as_bool(contract.get("planner_requires_empty_hand", False)),
            state_key=contract.get("planner_state_key", ""),
            state_value=(
                _as_value(contract.get("planner_state_value", ""))
                if "planner_state_value" in contract
                else None
            ),
            access_state=_as_bool(contract.get("planner_access_state", False)),
            reversible_state=_as_bool(contract.get("planner_reversible_state", False)),
            container_state_key=contract.get("planner_container_state_key", ""),
            container_state_value=(
                _as_value(contract.get("planner_container_state_value", ""))
                if "planner_container_state_value" in contract
                else None
            ),
            device_state_key=contract.get("planner_device_state_key", ""),
            device_state_value=(
                _as_value(contract.get("planner_device_state_value", ""))
                if "planner_device_state_value" in contract
                else None
            ),
            effect_state_key=contract.get("planner_effect_state_key", ""),
            effect_state_value=(
                _as_value(contract.get("planner_effect_state_value", ""))
                if "planner_effect_state_value" in contract
                else None
            ),
            action_name=contract.get("planner_action_name", "") or (name if has_raw_contract else ""),
            action_field=contract.get("planner_action_field", "") or "action",
            required_fields=_split_items(contract.get("planner_required_fields", "")),
            fixed_fields=_split_field_pairs(contract.get("planner_fixed_fields", "")),
            entity_fields=_split_items(contract.get("planner_entity_fields", "")),
            room_fields=_split_items(contract.get("planner_room_fields", "")),
            args_field=contract.get("planner_args_field", "") or "args",
            args_arity=(
                int(str(contract.get("planner_args_arity", "")).strip())
                if "planner_args_arity" in contract and str(contract.get("planner_args_arity", "")).strip()
                else None
            ),
            entity_args=_split_ints(contract.get("planner_entity_args", "")),
            allow_extra_fields=_as_bool(contract.get("planner_allow_extra_fields", False)),
            allow_comma_separated_entities=_as_bool(contract.get("planner_allow_comma_separated_entities", False)),
            entity_pattern=contract.get("planner_entity_pattern", ""),
            dynamic_entity_rule=contract.get("planner_dynamic_entity_rule", ""),
            unchecked_fields=_split_items(contract.get("planner_unchecked_fields", "")),
            context_field=contract.get("planner_context_field", ""),
            context_values=_split_items(contract.get("planner_context_values", "")),
        )

    @property
    def has_planning_contract(self) -> bool:
        return any(
            (
                self.target_param,
                self.item_param,
                self.destination_param,
                self.location_param,
                self.device_param,
                self.state_key,
                self.container_state_key,
                self.device_state_key,
                self.effect_state_key,
                self.action_name,
                self.required_fields,
                self.fixed_fields,
                self.entity_fields,
                self.room_fields,
                self.entity_args,
                self.unchecked_fields,
                self.dynamic_entity_rule,
                self.entity_pattern,
                self.context_field,
                self.context_values,
            )
        )

    @property
    def has_raw_todo_contract(self) -> bool:
        return any(
            (
                self.action_name,
                self.required_fields,
                self.fixed_fields,
                self.entity_fields,
                self.room_fields,
                self.args_arity is not None,
                self.entity_args,
                self.unchecked_fields,
                self.dynamic_entity_rule,
                self.entity_pattern,
                self.context_field,
                self.context_values,
            )
        )

    @property
    def can_move_robot(self) -> bool:
        return bool(self.location_param) and not any(
            (
                self.target_param,
                self.item_param,
                self.destination_param,
                self.device_param,
                self.state_key,
                self.container_state_key,
                self.device_state_key,
                self.effect_state_key,
            )
        )

    @property
    def can_grasp_item(self) -> bool:
        return bool(self.item_param) and not any(
            (
                self.target_param,
                self.destination_param,
                self.location_param,
                self.device_param,
                self.state_key,
                self.container_state_key,
                self.device_state_key,
                self.effect_state_key,
            )
        )

    @property
    def can_place_item(self) -> bool:
        return bool(self.item_param and self.destination_param)

    @property
    def can_set_state(self) -> bool:
        return bool(self.target_param and self.state_key)

    @property
    def can_transform_item(self) -> bool:
        return bool(self.effect_state_key or self.container_state_key or self.device_state_key)

    def param_value(self, action: dict[str, Any], key: str) -> str:
        params = action.get("parameters", {}) if isinstance(action, dict) else {}
        if not isinstance(params, dict) or not key:
            return ""
        return str(params.get(key, "") or "")

    def target_value(self, action: dict[str, Any]) -> str:
        return self.param_value(action, self.target_param)

    def item_value(self, action: dict[str, Any]) -> str:
        return self.param_value(action, self.item_param or self.target_param)

    def destination_value(self, action: dict[str, Any]) -> str:
        return self.param_value(action, self.destination_param)

    def location_value(self, action: dict[str, Any]) -> str:
        return self.param_value(action, self.location_param or self.target_param or self.destination_param)

    def device_value(self, action: dict[str, Any]) -> str:
        return self.param_value(action, self.device_param or self.location_param)


class SkillPlanningCatalog:
    def __init__(self, specs: list[SkillPlanningSpec]):
        self.specs = [spec for spec in specs if spec.has_planning_contract]
        self.by_name = {spec.name: spec for spec in self.specs}
        self.raw_specs = [spec for spec in self.specs if spec.has_raw_todo_contract]
        self.by_action_name: dict[str, SkillPlanningSpec] = {}
        self.by_action_name_casefold: dict[str, SkillPlanningSpec] = {}
        for spec in self.raw_specs:
            action_name = str(spec.action_name or "").strip()
            if not action_name:
                continue
            self.by_action_name.setdefault(action_name, spec)
            self.by_action_name_casefold.setdefault(action_name.casefold(), spec)

    def get(self, skill_name: str) -> SkillPlanningSpec | None:
        return self.by_name.get(skill_name)

    def get_action(self, action_name: str) -> SkillPlanningSpec | None:
        key = str(action_name or "").strip()
        if not key:
            return None
        return self.by_action_name.get(key) or self.by_action_name_casefold.get(key.casefold())

    def _first(self, predicate) -> SkillPlanningSpec | None:
        for spec in self.specs:
            if predicate(spec):
                return spec
        return None

    def requires_empty_hand(self, action: dict[str, Any]) -> bool:
        spec = self.get(str(action.get("skill", "") or ""))
        return bool(spec and spec.requires_empty_hand)

    def location_action(self, target: str) -> dict[str, Any] | None:
        spec = self._first(lambda item: item.can_move_robot)
        if not spec or not spec.location_param or not target:
            return None
        return {"skill": spec.name, "parameters": {spec.location_param: target}}

    def grasp_action(self, item: str) -> dict[str, Any] | None:
        spec = self._first(lambda candidate: candidate.can_grasp_item)
        if not spec or not spec.item_param or not item:
            return None
        return {"skill": spec.name, "parameters": {spec.item_param: item}}

    def place_action(self, item: str, destination: str) -> dict[str, Any] | None:
        spec = self._first(lambda candidate: candidate.can_place_item)
        if not spec or not spec.item_param or not spec.destination_param or not item or not destination:
            return None
        return {
            "skill": spec.name,
            "parameters": {spec.item_param: item, spec.destination_param: destination},
        }

    def state_action(self, state_key: str, state_value: Any, target: str) -> dict[str, Any] | None:
        spec = self.state_setter(state_key, state_value)
        if not spec or not spec.target_param or not target:
            return None
        return {"skill": spec.name, "parameters": {spec.target_param: target}}

    def state_setter(self, state_key: str, state_value: Any) -> SkillPlanningSpec | None:
        for spec in self.specs:
            if spec.can_set_state and spec.state_key == state_key and spec.state_value == state_value:
                return spec
        return None

    def access_state_keys(self) -> set[str]:
        return {
            spec.state_key
            for spec in self.specs
            if spec.can_set_state and spec.access_state and spec.state_key
        }

    def reversible_state_keys(self) -> set[str]:
        return {
            spec.state_key
            for spec in self.specs
            if spec.can_set_state and spec.reversible_state and spec.state_key
        }


def load_planning_catalog(profile: str | None = None) -> SkillPlanningCatalog:
    specs = [
        SkillPlanningSpec.from_contract(spec.name, spec.planning_contract)
        for spec in load_enabled_skill_specs(profile)
        if getattr(spec, "planning_contract", None)
    ]
    return SkillPlanningCatalog(specs)
