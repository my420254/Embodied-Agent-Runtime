from __future__ import annotations

import copy
import json
from typing import Any


# Model-facing fields follow DELTA's official PDDL parameter signatures.
# Handler-facing semantic names are derived only after strict parsing.
DELTA_ACTION_FIELDS: dict[str, tuple[str, ...]] = {
    "goto": ("agent", "room_1", "room_2"),
    "pick": ("agent", "item", "room"),
    "drop": ("agent", "item", "room"),
    "place_on": ("agent", "item_1", "item_2", "room"),
    "pick_loadable": ("agent", "item", "room"),
    "drop_loadable": ("agent", "item", "room"),
    "load": ("agent", "item_1", "item_2", "room"),
    "unload": ("agent", "item_1", "item_2", "room"),
    "dispose": ("agent", "item_1", "item_2", "room"),
    "mop_floor": ("agent", "item", "room"),
    "clean_mop": ("agent", "item_1", "item_2", "room"),
    "charge": ("agent", "item", "room"),
    "assemble": ("agent", "room", "item_1", "item_2", "item_3", "item_4", "item_5", "item_6", "pc"),
}

DELTA_DOMAIN_ACTIONS: dict[str, tuple[str, ...]] = {
    "clean": ("goto", "pick", "drop", "dispose", "mop_floor", "clean_mop", "charge"),
    "dining": ("goto", "pick", "drop", "place_on"),
    "office": ("goto", "pick", "drop", "pick_loadable", "drop_loadable", "load", "unload"),
    "pc": ("goto", "pick", "drop", "assemble"),
}

DELTA_ROOM_FIELDS = {"room", "room_1", "room_2"}
DELTA_AGENT_FIELDS = {"agent"}
DELTA_TARGET_ONLY_FIELDS = {"pc"}

DELTA_HANDLER_FIELD_MAP: dict[str, dict[str, str]] = {
    "goto": {"room_1": "from", "room_2": "to"},
    "pick": {"item": "item", "room": "room"},
    "drop": {"item": "item", "room": "room"},
    "place_on": {"item_1": "item", "item_2": "surface", "room": "room"},
    "pick_loadable": {"item": "item", "room": "room"},
    "drop_loadable": {"item": "item", "room": "room"},
    "load": {"item_1": "loadable", "item_2": "item", "room": "room"},
    "unload": {"item_1": "loadable", "item_2": "item", "room": "room"},
    "dispose": {"item_1": "item", "item_2": "disposal", "room": "room"},
    "mop_floor": {"item": "tool", "room": "room"},
    "clean_mop": {"item_1": "tool", "item_2": "water_source", "room": "room"},
    "charge": {"item": "station", "room": "room"},
    "assemble": {
        "room": "room",
        "item_1": "mainboard",
        "item_2": "cpu",
        "item_3": "ram",
        "item_4": "ssd",
        "item_5": "gpu",
        "item_6": "psu",
        "pc": "target_pc",
    },
}


def _delta_domain_from_state(state: Any) -> str:
    if not isinstance(state, dict):
        return ""
    task_context = state.get("task_context")
    if isinstance(task_context, dict):
        domain = str(task_context.get("domain") or "").strip().lower()
        if domain:
            return domain
    payload = state.get("task_input_payload")
    if isinstance(payload, dict):
        domain = str(payload.get("domain") or "").strip().lower()
        if domain:
            return domain
    return str(state.get("domain") or "").strip().lower()


def allowed_delta_actions_for_domain(domain: str | None) -> tuple[str, ...]:
    normalized = str(domain or "").strip().lower()
    return DELTA_DOMAIN_ACTIONS.get(normalized, tuple(DELTA_ACTION_FIELDS))


def allowed_delta_actions_from_state(state: Any) -> tuple[str, ...]:
    return allowed_delta_actions_for_domain(_delta_domain_from_state(state))


def delta_action_contract_lines(domain: str | None = None, *, allowed_actions: tuple[str, ...] | list[str] | set[str] | None = None) -> list[str]:
    allowed = allowed_delta_actions_for_domain(domain)
    if allowed_actions is not None:
        allowed_set = {str(action).strip().lower() for action in allowed_actions if str(action).strip()}
        allowed = tuple(action for action in allowed if action in allowed_set)
    examples = {
        "goto": '{"action":"goto","agent":"robot","room_1":"<current_room>","room_2":"<destination_room>"}',
        "pick": '{"action":"pick","agent":"robot","item":"<item_entity>","room":"<item_room>"}',
        "drop": '{"action":"drop","agent":"robot","item":"<held_item_entity>","room":"<drop_room>"}',
        "place_on": '{"action":"place_on","agent":"robot","item_1":"<held_item_entity>","item_2":"<dining_table_entity>","room":"<table_room>"}',
        "pick_loadable": '{"action":"pick_loadable","agent":"robot","item":"<empty_loadable_entity>","room":"<loadable_room>"}',
        "drop_loadable": '{"action":"drop_loadable","agent":"robot","item":"<held_loadable_entity>","room":"<drop_room>"}',
        "load": '{"action":"load","agent":"robot","item_1":"<loadable_entity>","item_2":"<held_item_entity>","room":"<loadable_room>"}',
        "unload": '{"action":"unload","agent":"robot","item_1":"<loadable_entity>","item_2":"<contained_item_entity>","room":"<loadable_room>"}',
        "dispose": '{"action":"dispose","agent":"robot","item_1":"<held_disposable_entity>","item_2":"<rubbish_bin_entity>","room":"<disposal_room>"}',
        "mop_floor": '{"action":"mop_floor","agent":"robot","item":"<held_clean_mop_entity>","room":"<floor_room>"}',
        "clean_mop": '{"action":"clean_mop","agent":"robot","item_1":"<held_mop_entity>","item_2":"<sink_entity>","room":"<sink_room>"}',
        "charge": '{"action":"charge","agent":"robot","item":"<charging_station_entity>","room":"<charging_station_room>"}',
        "assemble": '{"action":"assemble","agent":"robot","room":"<workspace_room>","item_1":"<mainboard_entity>","item_2":"<cpu_entity>","item_3":"<ram_entity>","item_4":"<ssd_entity>","item_5":"<gpu_entity>","item_6":"<psu_entity>","pc":"<target_pc_entity>"}',
    }
    return [
        f"{index}. {action}: {examples[action]}"
        for index, action in enumerate(allowed, start=1)
    ]


def _strip_model_wrappers(text: str) -> str:
    raw = str(text or "").strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    elif raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    return raw.strip()


def _native_step(action: str, params: dict[str, Any], step: int) -> dict[str, Any]:
    return {"step": step, "action": action, **copy.deepcopy(params)}


def _is_delta_room_entry(info: Any) -> bool:
    if not isinstance(info, dict):
        return False
    if str(info.get("type") or "").strip().lower() == "room":
        return True
    direct_parent = str(info.get("direct_parent") or "").strip().lower()
    full_path = info.get("full_path")
    return direct_parent in {"未知环境", "unknown"} and (not isinstance(full_path, list) or not full_path)


def _delta_env_catalog(current_env: Any) -> tuple[set[str], set[str]]:
    if not isinstance(current_env, dict):
        return set(), set()
    names = {str(name).strip() for name in current_env if str(name).strip()}
    rooms = {
        str(name).strip()
        for name, info in current_env.items()
        if str(name).strip() and _is_delta_room_entry(info)
    }
    return names, rooms


def _format_catalog(values: set[str], *, limit: int = 12) -> str:
    ordered = sorted(values)
    if len(ordered) <= limit:
        return ", ".join(ordered)
    return ", ".join(ordered[:limit]) + f", ... ({len(ordered)} total)"


def _validate_names_against_current_env(action: str, params: dict[str, str], current_env: Any) -> None:
    names, rooms = _delta_env_catalog(current_env)
    if not names:
        return
    for field, value in params.items():
        if field in DELTA_AGENT_FIELDS:
            if value != "robot":
                raise ValueError(
                    f"DELTA action {action} field agent must be 'robot', got {value!r}"
                )
            continue
        if field in DELTA_ROOM_FIELDS:
            valid_rooms = rooms or names
            if value not in valid_rooms:
                raise ValueError(
                    f"DELTA action {action} field {field} references unknown room {value!r}; "
                    f"available rooms: {_format_catalog(valid_rooms)}"
                )
            continue
        if field in DELTA_TARGET_ONLY_FIELDS:
            continue
        if value not in names:
            raise ValueError(
                f"DELTA action {action} field {field} references unknown entity {value!r}; "
                f"available entities: {_format_catalog(names)}"
            )


def _handler_params(action: str, paper_params: dict[str, str]) -> dict[str, str]:
    mapping = DELTA_HANDLER_FIELD_MAP.get(action)
    if mapping is None:
        raise ValueError(f"unsupported DELTA official action: {action or '<empty>'}")
    return {
        handler_field: paper_params.get(paper_field, "")
        for paper_field, handler_field in mapping.items()
    }


def parse_delta_native_actions(
    text: str,
    *,
    state: Any = None,
    env_state: Any = None,
    current_env: Any = None,
    **_: Any,
) -> tuple[str, list[dict[str, Any]]]:
    normalized = _strip_model_wrappers(text)
    parsed = json.loads(normalized)
    if not isinstance(parsed, list):
        raise ValueError("DELTA native output must be a JSON list of official action objects")

    validation_env = current_env if isinstance(current_env, dict) else env_state
    allowed_actions = set(allowed_delta_actions_from_state(state))
    domain = _delta_domain_from_state(state)
    native_plan: list[dict[str, Any]] = []
    for index, item in enumerate(parsed, start=1):
        if not isinstance(item, dict):
            raise ValueError("DELTA native action must be a JSON object")
        action = str(item.get("action", "") or "").strip().lower()
        if action not in DELTA_ACTION_FIELDS:
            raise ValueError(f"unsupported DELTA official action: {action or '<empty>'}")
        if action not in allowed_actions:
            domain_label = domain or "unknown"
            raise ValueError(
                f"DELTA action {action} is not available in domain {domain_label}; "
                f"allowed actions: {', '.join(sorted(allowed_actions))}"
            )
        allowed = {"action", "step", *DELTA_ACTION_FIELDS[action]}
        extra = {str(key) for key in item.keys()} - allowed
        if extra:
            raise ValueError(f"DELTA action {action} contains unsupported fields: {sorted(extra)}")
        params = {name: str(item.get(name, "") or "").strip() for name in DELTA_ACTION_FIELDS[action]}
        missing = [name for name, value in params.items() if not value]
        if missing:
            raise ValueError(f"DELTA action {action} missing required fields: {missing}")
        _validate_names_against_current_env(action, params, validation_env)
        native_plan.append(_native_step(action, params, index))
    return json.dumps(parsed, ensure_ascii=False, indent=2), native_plan


def delta_native_step_to_skill_call(step: dict[str, Any], sim_robot: dict | None = None) -> tuple[str, dict[str, Any]]:
    del sim_robot
    action = str(step.get("action", "") or "").strip().lower()
    if action not in DELTA_ACTION_FIELDS:
        raise ValueError(f"unsupported DELTA official action: {action or '<empty>'}")
    paper_params = {
        field: str(step.get(field, "") or "").strip()
        for field in DELTA_ACTION_FIELDS[action]
    }
    return action, _handler_params(action, paper_params)


def delta_native_plan_to_execution_calls(native_plan: list[dict[str, Any]]) -> list[dict[str, Any]]:
    converted: list[dict[str, Any]] = []
    for index, native_step in enumerate(native_plan or [], start=1):
        action, params = delta_native_step_to_skill_call(native_step, None)
        converted.append(
            {
                "step": index,
                "execution": {
                    "skill": action,
                    "parameters": params,
                },
            }
        )
    return converted
