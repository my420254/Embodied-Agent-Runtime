from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from skills.loader import load_enabled_skill_specs


def _as_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


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
class SkillRepairSpec:
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

    @classmethod
    def from_contract(cls, name: str, contract: dict[str, str]) -> "SkillRepairSpec":
        return cls(
            name=name,
            target_param=contract.get("planner_target_param", ""),
            item_param=contract.get("planner_item_param", ""),
            destination_param=contract.get("planner_destination_param", ""),
            location_param=contract.get("planner_location_param", ""),
            device_param=contract.get("planner_device_param", ""),
            requires_empty_hand=_as_bool(contract.get("planner_requires_empty_hand", False)),
            state_key=contract.get("planner_state_key", ""),
            state_value=_as_value(contract.get("planner_state_value", "")) if "planner_state_value" in contract else None,
            access_state=_as_bool(contract.get("planner_access_state", False)),
            reversible_state=_as_bool(contract.get("planner_reversible_state", False)),
            container_state_key=contract.get("planner_container_state_key", ""),
            container_state_value=_as_value(contract.get("planner_container_state_value", ""))
            if "planner_container_state_value" in contract
            else None,
            device_state_key=contract.get("planner_device_state_key", ""),
            device_state_value=_as_value(contract.get("planner_device_state_value", ""))
            if "planner_device_state_value" in contract
            else None,
            effect_state_key=contract.get("planner_effect_state_key", ""),
            effect_state_value=_as_value(contract.get("planner_effect_state_value", ""))
            if "planner_effect_state_value" in contract
            else None,
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


class SkillRepairCatalog:
    def __init__(self, specs: list[SkillRepairSpec]):
        self.specs = [spec for spec in specs if spec.has_planning_contract]
        self.by_name = {spec.name: spec for spec in self.specs}

    def get(self, skill_name: str) -> SkillRepairSpec | None:
        return self.by_name.get(skill_name)

    def _first(self, predicate) -> SkillRepairSpec | None:
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
        return {"skill": spec.name, "parameters": {spec.item_param: item, spec.destination_param: destination}}

    def state_action(self, state_key: str, state_value: Any, target: str) -> dict[str, Any] | None:
        spec = self.state_setter(state_key, state_value)
        if not spec or not spec.target_param or not target:
            return None
        return {"skill": spec.name, "parameters": {spec.target_param: target}}

    def state_setter(self, state_key: str, state_value: Any) -> SkillRepairSpec | None:
        for spec in self.specs:
            if not spec.can_set_state:
                continue
            if spec.state_key == state_key and spec.state_value == state_value:
                return spec
        return None

    def access_state_keys(self) -> set[str]:
        return {spec.state_key for spec in self.specs if spec.can_set_state and spec.access_state and spec.state_key}

    def reversible_state_keys(self) -> set[str]:
        return {spec.state_key for spec in self.specs if spec.can_set_state and spec.reversible_state and spec.state_key}


def load_repair_catalog() -> SkillRepairCatalog:
    specs = [
        SkillRepairSpec.from_contract(spec.name, spec.planning_contract)
        for spec in load_enabled_skill_specs()
        if getattr(spec, "planning_contract", None)
    ]
    return SkillRepairCatalog(specs)
