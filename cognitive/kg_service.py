from __future__ import annotations

from typing import Any

from interfaces.contracts import (
    CandidateUpdate,
    EvidenceRecord,
    KGQuery,
    KGQueryResult,
    UpdateStatus,
    is_valid_ttl,
)


TASK_OPERATION_CONTRACTS: dict[tuple[str, str], dict[str, Any]] = {
    ("cut", "beef"): {
        "canonical_target_type": "beef",
        "categories": ("food", "ingredient", "meat", "raw_meat", "cuttable_ingredient"),
        "candidate_skills": ("cooking.cut_ingredient",),
        "facts": (
            {"subject": "beef", "relation": "category", "object": "raw_meat"},
            {"subject": "raw_meat", "relation": "requires_tool", "object": "knife"},
            {"subject": "raw_meat", "relation": "requires_state", "object": "clean_cutting_board"},
            {"subject": "cooking.cut_ingredient", "relation": "uses_primitive", "object": "Slice"},
        ),
        "constraints": (
            {"predicate": "target_not_frozen", "args": ("target",)},
            {"predicate": "surface_clean", "args": ("cutting_surface",)},
            {"predicate": "tool_clean", "args": ("cutting_tool",)},
            {"predicate": "target_on_surface", "args": ("target", "cutting_surface")},
            {"predicate": "avoid_cross_contamination", "args": ("target", "cutting_surface")},
        ),
        "scene_queries_needed": (
            {"query": "resolve_instance", "type": "beef", "role": "target"},
            {"query": "find_instance", "type": "knife", "role": "cutting_tool"},
            {"query": "find_instance", "type": "cutting_board", "role": "cutting_surface"},
            {"query": "find_instance", "type": "water_source", "role": "water_source"},
            {"query": "check_state", "target": "target", "states": ("accessible", "frozen", "packaged")},
            {"query": "check_state", "target": "cutting_surface", "states": ("clean",)},
            {"query": "check_state", "target": "cutting_tool", "states": ("clean",)},
        ),
    },
    ("make", "tea"): {
        "canonical_target_type": "tea",
        "categories": ("drink", "hot_drink", "prepared_beverage"),
        "candidate_skills": ("cooking.make_tea",),
        "facts": (
            {"subject": "tea", "relation": "requires_tool", "object": "cup"},
            {"subject": "tea", "relation": "requires_tool", "object": "water_source"},
            {"subject": "tea", "relation": "requires_tool", "object": "heating_device"},
            {"subject": "cooking.make_tea", "relation": "uses_primitive", "object": "Put"},
            {"subject": "cooking.make_tea", "relation": "uses_primitive", "object": "Close"},
            {"subject": "cooking.make_tea", "relation": "uses_primitive", "object": "ToggleOn"},
            {"subject": "cooking.make_tea", "relation": "uses_primitive", "object": "Heat"},
        ),
        "constraints": (
            {"predicate": "cup_clean", "args": ("cup",)},
            {"predicate": "water_available", "args": ("water_source",)},
            {"predicate": "heat_source_safe", "args": ("heating_device",)},
            {"predicate": "heated_tea_in_cup", "args": ("ingredient", "cup")},
        ),
        "scene_queries_needed": (
            {"query": "find_instance", "type": "cup", "role": "cup"},
            {"query": "find_instance", "type": "tea", "role": "ingredient"},
            {"query": "find_instance", "type": "water_source", "role": "water_source"},
            {"query": "find_instance", "type": "heating_device", "role": "heating_device"},
            {"query": "check_state", "target": "cup", "states": ("clean",)},
        ),
    },
    ("do", "laundry"): {
        "canonical_target_type": "laundry",
        "categories": ("household_task", "cleaning_task", "clothing_care"),
        "candidate_skills": ("laundry.do_laundry",),
        "facts": (
            {"subject": "laundry", "relation": "requires_tool", "object": "washing_machine"},
            {"subject": "laundry", "relation": "requires_tool", "object": "detergent"},
            {"subject": "laundry.do_laundry", "relation": "uses_primitive", "object": "Put"},
            {"subject": "laundry.do_laundry", "relation": "uses_primitive", "object": "ToggleOn"},
        ),
        "constraints": (
            {"predicate": "clothes_sortable", "args": ("dirty_clothes",)},
            {"predicate": "washer_available", "args": ("washing_machine",)},
            {"predicate": "detergent_available", "args": ("detergent",)},
        ),
        "scene_queries_needed": (
            {"query": "find_instance", "type": "dirty_clothes", "role": "load"},
            {"query": "find_instance", "type": "washing_machine", "role": "washer"},
            {"query": "find_instance", "type": "detergent", "role": "detergent"},
            {"query": "check_state", "target": "washing_machine", "states": ("available", "door_open")},
        ),
    },
    ("turn_on", "toggleable_device"): {
        "canonical_target_type": "toggleable_device",
        "categories": ("device", "switchable_object"),
        "candidate_skills": ("device.turn_on",),
        "facts": (
            {"subject": "toggleable_device", "relation": "affords", "object": "ToggleOn"},
            {"subject": "device.turn_on", "relation": "uses_primitive", "object": "NavigateTo"},
            {"subject": "device.turn_on", "relation": "uses_primitive", "object": "ToggleOn"},
        ),
        "constraints": (
            {"predicate": "device_reachable", "args": ("target_device",)},
            {"predicate": "device_has_switch", "args": ("target_device",)},
        ),
        "scene_queries_needed": (
            {"query": "resolve_instance", "type": "toggleable_device", "role": "target_device"},
            {"query": "check_state", "target": "target_device", "states": ("isToggled",)},
        ),
    },
    ("turn_off", "toggleable_device"): {
        "canonical_target_type": "toggleable_device",
        "categories": ("device", "switchable_object"),
        "candidate_skills": ("device.turn_off",),
        "facts": (
            {"subject": "toggleable_device", "relation": "affords", "object": "ToggleOff"},
            {"subject": "device.turn_off", "relation": "uses_primitive", "object": "NavigateTo"},
            {"subject": "device.turn_off", "relation": "uses_primitive", "object": "ToggleOff"},
        ),
        "constraints": (
            {"predicate": "device_reachable", "args": ("target_device",)},
            {"predicate": "device_has_switch", "args": ("target_device",)},
        ),
        "scene_queries_needed": (
            {"query": "resolve_instance", "type": "toggleable_device", "role": "target_device"},
            {"query": "check_state", "target": "target_device", "states": ("isToggled",)},
        ),
    },
    ("open", "openable_container"): {
        "canonical_target_type": "openable_container",
        "categories": ("container", "receptacle", "openable_object"),
        "candidate_skills": ("container.open",),
        "facts": (
            {"subject": "openable_container", "relation": "affords", "object": "Open"},
            {"subject": "container.open", "relation": "uses_primitive", "object": "NavigateTo"},
            {"subject": "container.open", "relation": "uses_primitive", "object": "Open"},
        ),
        "constraints": (
            {"predicate": "container_reachable", "args": ("target_container",)},
            {"predicate": "hand_empty", "args": ("robot",)},
        ),
        "scene_queries_needed": (
            {"query": "resolve_instance", "type": "openable_container", "role": "target_container"},
            {"query": "check_state", "target": "target_container", "states": ("isOpen",)},
        ),
    },
    ("close", "openable_container"): {
        "canonical_target_type": "openable_container",
        "categories": ("container", "receptacle", "openable_object"),
        "candidate_skills": ("container.close",),
        "facts": (
            {"subject": "openable_container", "relation": "affords", "object": "Close"},
            {"subject": "container.close", "relation": "uses_primitive", "object": "NavigateTo"},
            {"subject": "container.close", "relation": "uses_primitive", "object": "Close"},
        ),
        "constraints": (
            {"predicate": "container_reachable", "args": ("target_container",)},
            {"predicate": "hand_empty", "args": ("robot",)},
        ),
        "scene_queries_needed": (
            {"query": "resolve_instance", "type": "openable_container", "role": "target_container"},
            {"query": "check_state", "target": "target_container", "states": ("isOpen",)},
        ),
    },
    ("put", "pickupable_object"): {
        "canonical_target_type": "pickupable_object",
        "categories": ("object", "portable_object"),
        "candidate_skills": ("object.put_into_container",),
        "facts": (
            {"subject": "pickupable_object", "relation": "affords", "object": "Pickup"},
            {"subject": "openable_container", "relation": "affords", "object": "Put"},
            {"subject": "openable_container", "relation": "affords", "object": "Open"},
            {"subject": "openable_container", "relation": "affords", "object": "Close"},
            {"subject": "placement_surface", "relation": "affords", "object": "Put"},
            {"subject": "object.put_into_container", "relation": "uses_primitive", "object": "NavigateTo"},
            {"subject": "object.put_into_container", "relation": "uses_primitive", "object": "Open"},
            {"subject": "object.put_into_container", "relation": "uses_primitive", "object": "Pickup"},
            {"subject": "object.put_into_container", "relation": "uses_primitive", "object": "Put"},
            {"subject": "object.put_into_container", "relation": "uses_primitive", "object": "Close"},
        ),
        "constraints": (
            {"predicate": "object_reachable", "args": ("target_item",)},
            {"predicate": "destination_reachable", "args": ("target_container",)},
            {"predicate": "hand_empty", "args": ("robot",)},
        ),
        "scene_queries_needed": (
            {"query": "resolve_instance", "type": "pickupable_object", "role": "target_item"},
            {"query": "find_instance", "type": "openable_container", "role": "target_container"},
            {"query": "resolve_instance", "type": "receptacle", "role": "target_container"},
            {"query": "resolve_instance", "type": "placement_surface", "role": "target_container"},
            {"query": "check_state", "target": "target_item", "states": ("accessible",)},
            {"query": "check_state", "target": "target_container", "states": ("isOpen", "accessible")},
        ),
    },
    ("clean", "cleanable_object"): {
        "canonical_target_type": "cleanable_object",
        "categories": ("object", "cleanable_object", "washable_object"),
        "candidate_skills": ("object.clean",),
        "facts": (
            {"subject": "cleanable_object", "relation": "affords", "object": "Clean"},
            {"subject": "water_source", "relation": "affords", "object": "Clean"},
            {"subject": "object.clean", "relation": "uses_primitive", "object": "NavigateTo"},
            {"subject": "object.clean", "relation": "uses_primitive", "object": "Pickup"},
            {"subject": "object.clean", "relation": "uses_primitive", "object": "Clean"},
        ),
        "constraints": (
            {"predicate": "object_cleanable", "args": ("target_item",)},
            {"predicate": "water_available", "args": ("water_source",)},
            {"predicate": "object_reachable_or_held", "args": ("target_item",)},
        ),
        "scene_queries_needed": (
            {"query": "resolve_instance", "type": "cleanable_object", "role": "target_item"},
            {"query": "find_instance", "type": "water_source", "role": "water_source"},
            {"query": "check_state", "target": "target_item", "states": ("isClean", "cleanable")},
            {"query": "check_state", "target": "water_source", "states": ("available", "isFilledWithLiquid")},
        ),
    },
    ("pickup", "pickupable_object"): {
        "canonical_target_type": "pickupable_object",
        "categories": ("object", "portable_object"),
        "candidate_skills": ("object.pickup",),
        "facts": (
            {"subject": "pickupable_object", "relation": "affords", "object": "Pickup"},
            {"subject": "object.pickup", "relation": "uses_primitive", "object": "NavigateTo"},
            {"subject": "object.pickup", "relation": "uses_primitive", "object": "Pickup"},
        ),
        "constraints": (
            {"predicate": "object_reachable", "args": ("target_item",)},
            {"predicate": "hand_empty", "args": ("robot",)},
        ),
        "scene_queries_needed": (
            {"query": "resolve_instance", "type": "pickupable_object", "role": "target_item"},
            {"query": "check_state", "target": "target_item", "states": ("accessible",)},
        ),
    },
    ("read", "readable_object"): {
        "canonical_target_type": "readable_object",
        "categories": ("object", "document", "readable_object"),
        "candidate_skills": ("object.read",),
        "facts": (
            {"subject": "readable_object", "relation": "affords", "object": "Read"},
            {"subject": "object.read", "relation": "uses_primitive", "object": "NavigateTo"},
            {"subject": "object.read", "relation": "uses_primitive", "object": "Pickup"},
            {"subject": "object.read", "relation": "uses_primitive", "object": "Read"},
        ),
        "constraints": (
            {"predicate": "object_visible_or_held", "args": ("target_item",)},
            {"predicate": "object_readable", "args": ("target_item",)},
        ),
        "scene_queries_needed": (
            {"query": "resolve_instance", "type": "readable_object", "role": "target_item"},
            {"query": "check_state", "target": "target_item", "states": ("accessible", "readable")},
        ),
    },
    ("observe", "observable_object"): {
        "canonical_target_type": "observable_object",
        "categories": ("object", "observable_object"),
        "candidate_skills": ("object.observe",),
        "facts": (
            {"subject": "observable_object", "relation": "affords", "object": "Observe"},
            {"subject": "object.observe", "relation": "uses_primitive", "object": "NavigateTo"},
            {"subject": "object.observe", "relation": "uses_primitive", "object": "Observe"},
        ),
        "constraints": (
            {"predicate": "object_visible", "args": ("target_object",)},
            {"predicate": "object_reachable", "args": ("target_object",)},
        ),
        "scene_queries_needed": (
            {"query": "resolve_instance", "type": "observable_object", "role": "target_object"},
            {"query": "check_state", "target": "target_object", "states": ("accessible", "observable")},
        ),
    },
    ("touch", "touchable_object"): {
        "canonical_target_type": "touchable_object",
        "categories": ("object", "touchable_object"),
        "candidate_skills": ("object.touch",),
        "facts": (
            {"subject": "touchable_object", "relation": "affords", "object": "Touch"},
            {"subject": "object.touch", "relation": "uses_primitive", "object": "NavigateTo"},
            {"subject": "object.touch", "relation": "uses_primitive", "object": "Touch"},
        ),
        "constraints": (
            {"predicate": "object_reachable", "args": ("target_object",)},
            {"predicate": "object_touchable", "args": ("target_object",)},
        ),
        "scene_queries_needed": (
            {"query": "resolve_instance", "type": "touchable_object", "role": "target_object"},
            {"query": "check_state", "target": "target_object", "states": ("accessible", "touchable")},
        ),
    },
    ("type", "typeable_device"): {
        "canonical_target_type": "typeable_device",
        "categories": ("device", "computer", "keyboard", "typeable_device"),
        "candidate_skills": ("device.type_on",),
        "facts": (
            {"subject": "typeable_device", "relation": "affords", "object": "Type"},
            {"subject": "device.type_on", "relation": "uses_primitive", "object": "NavigateTo"},
            {"subject": "device.type_on", "relation": "uses_primitive", "object": "Type"},
        ),
        "constraints": (
            {"predicate": "device_reachable", "args": ("target_device",)},
            {"predicate": "device_typeable", "args": ("target_device",)},
        ),
        "scene_queries_needed": (
            {"query": "resolve_instance", "type": "typeable_device", "role": "target_device"},
            {"query": "check_state", "target": "target_device", "states": ("accessible", "typeable")},
        ),
    },
    ("sleep", "sleepable_object"): {
        "canonical_target_type": "sleepable_object",
        "categories": ("object", "bed", "sleepable_object"),
        "candidate_skills": ("object.sleep_on",),
        "facts": (
            {"subject": "sleepable_object", "relation": "affords", "object": "Sleep"},
            {"subject": "object.sleep_on", "relation": "uses_primitive", "object": "NavigateTo"},
            {"subject": "object.sleep_on", "relation": "uses_primitive", "object": "Sleep"},
        ),
        "constraints": (
            {"predicate": "bed_reachable", "args": ("target_bed",)},
            {"predicate": "bed_available", "args": ("target_bed",)},
        ),
        "scene_queries_needed": (
            {"query": "resolve_instance", "type": "sleepable_object", "role": "target_bed"},
            {"query": "check_state", "target": "target_bed", "states": ("accessible", "sleepable")},
        ),
    },
    ("drink", "drinkable_object"): {
        "canonical_target_type": "drinkable_object",
        "categories": ("object", "drink", "beverage", "drinkable_object"),
        "candidate_skills": ("object.drink",),
        "facts": (
            {"subject": "drinkable_object", "relation": "affords", "object": "Drink"},
            {"subject": "object.drink", "relation": "uses_primitive", "object": "NavigateTo"},
            {"subject": "object.drink", "relation": "uses_primitive", "object": "Pickup"},
            {"subject": "object.drink", "relation": "uses_primitive", "object": "Drink"},
        ),
        "constraints": (
            {"predicate": "object_drinkable", "args": ("target_item",)},
            {"predicate": "object_reachable_or_held", "args": ("target_item",)},
        ),
        "scene_queries_needed": (
            {"query": "resolve_instance", "type": "drinkable_object", "role": "target_item"},
            {"query": "check_state", "target": "target_item", "states": ("accessible", "drinkable", "isConsumed")},
        ),
    },
    ("sit", "seat_object"): {
        "canonical_target_type": "seat_object",
        "categories": ("object", "seat", "seat_object"),
        "candidate_skills": ("object.sit_on",),
        "facts": (
            {"subject": "seat_object", "relation": "affords", "object": "Sit"},
            {"subject": "object.sit_on", "relation": "uses_primitive", "object": "NavigateTo"},
            {"subject": "object.sit_on", "relation": "uses_primitive", "object": "Sit"},
        ),
        "constraints": (
            {"predicate": "seat_reachable", "args": ("target_seat",)},
            {"predicate": "seat_available", "args": ("target_seat",)},
        ),
        "scene_queries_needed": (
            {"query": "resolve_instance", "type": "seat_object", "role": "target_seat"},
            {"query": "check_state", "target": "target_seat", "states": ("accessible", "seatable")},
        ),
    },
}


class StaticKGService:
    """Deterministic KG facade for task contracts and gated updates.

    This prototype intentionally returns stable semantic contracts instead of
    doing LLM-driven graph reasoning. Scene instances and live states are owned
    by the scene graph service.
    """

    def __init__(self) -> None:
        self.evidence: dict[str, EvidenceRecord] = {}
        self.committed_updates: dict[str, CandidateUpdate] = {}

    def query(self, query: KGQuery) -> KGQueryResult:
        if query.query_type != "task_operation_contract":
            return KGQueryResult(query_type=query.query_type, unknowns=(f"unsupported query_type={query.query_type}",))

        task = query.payload.get("task", {})
        operation = str(task.get("operation", "")).strip().lower()
        target_type = str(task.get("target_type_hint") or task.get("target_type") or task.get("target_name") or "").strip().lower()
        contract = TASK_OPERATION_CONTRACTS.get((operation, target_type))
        if contract is None:
            return KGQueryResult(
                query_type=query.query_type,
                unknowns=(f"no task contract for operation={operation!r}, target_type={target_type!r}",),
            )
        scene_queries_needed = tuple(_bind_scene_query_name_hints(item, task) for item in contract["scene_queries_needed"])
        return KGQueryResult(
            query_type=query.query_type,
            facts=tuple(contract["facts"]),
            constraints=tuple(contract["constraints"]),
            candidate_skills=tuple(contract["candidate_skills"]),
            scene_queries_needed=scene_queries_needed,
        )

    def record_observation(self, evidence: EvidenceRecord) -> str:
        self.evidence[evidence.evidence_id] = evidence
        return evidence.evidence_id

    def propose_update(self, update: CandidateUpdate) -> CandidateUpdate:
        if update.status is not UpdateStatus.CANDIDATE:
            raise ValueError(f"only candidate updates can be proposed, got {update.status.value}")
        self._ensure_known_evidence(update)
        self._ensure_governance_metadata(update)
        return update

    def commit_validated_update(self, update: CandidateUpdate) -> CandidateUpdate:
        self._ensure_known_evidence(update)
        committed = update.commit()
        self._ensure_governance_metadata(committed)
        self.committed_updates[committed.candidate_id] = committed
        return committed

    def _ensure_known_evidence(self, update: CandidateUpdate) -> None:
        if not update.evidence_ids:
            raise ValueError("candidate updates require evidence_ids")
        missing = tuple(evidence_id for evidence_id in update.evidence_ids if evidence_id not in self.evidence)
        if missing:
            raise ValueError(f"candidate update references unknown evidence_ids: {missing}")

    def _ensure_governance_metadata(self, update: CandidateUpdate) -> None:
        if not str(update.proposed_by or "").strip():
            raise ValueError("candidate updates require provenance")
        if not is_valid_ttl(update.ttl):
            raise ValueError("candidate updates require ISO-8601 TTL")
        if not 0.0 <= float(update.confidence) <= 1.0:
            raise ValueError("candidate update confidence must be between 0 and 1")


def _bind_scene_query_name_hints(scene_query: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    bound = dict(scene_query)
    if bound.get("name_hint"):
        return bound

    role = str(bound.get("role") or "")
    name_hint = ""
    if role in {"target", "target_item", "target_device", "target_object", "target_bed", "target_seat"}:
        name_hint = str(task.get("target_name") or "")
    elif role == "ingredient":
        name_hint = str(task.get("ingredient_name") or "")
    elif role == "cup":
        name_hint = str(task.get("cup_name") or "")
    elif role == "heating_device":
        name_hint = str(task.get("heating_device_name") or "")
    elif role == "load":
        name_hint = str(task.get("load_name") or "")
    elif role == "washer":
        name_hint = str(task.get("washer_name") or "")
    elif role == "detergent":
        name_hint = str(task.get("detergent_name") or "")
    elif role == "target_container":
        name_hint = str(task.get("container_name") or task.get("target_name") or "")
    elif role == "water_source":
        name_hint = str(task.get("water_source_name") or "")

    if name_hint:
        bound["name_hint"] = name_hint
    return bound
