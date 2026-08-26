from __future__ import annotations

import copy

from .base import FeatureContext, FeatureResult


def empty_required_item_names() -> dict:
    return {
        "targets": {"primary": [], "alternatives": []},
        "tools": {"primary": [], "alternatives": []},
        "receptacles": {"primary": [], "alternatives": []},
    }


def normalize_name_bucket(bucket) -> dict[str, list[str]]:
    if isinstance(bucket, dict):
        primary = bucket.get("primary", [])
        alternatives = bucket.get("alternatives", [])
    elif isinstance(bucket, list):
        primary = bucket
        alternatives = []
    else:
        primary = []
        alternatives = []
    return {
        "primary": [str(name) for name in primary if name],
        "alternatives": [str(name) for name in alternatives if name],
    }


def normalize_goal_state(goal_state: dict | None) -> dict:
    goal_state = goal_state if isinstance(goal_state, dict) else {}
    entities = {}
    if isinstance(goal_state.get("entities"), dict):
        raw_entities = goal_state.get("entities", {})
    else:
        raw_entities = {
            key: value
            for key, value in goal_state.items()
            if key not in {"robot", "robot_state"}
        }
    if isinstance(raw_entities, dict):
        for entity_name, payload in raw_entities.items():
            name = str(entity_name or "").strip()
            if not name or not isinstance(payload, dict):
                continue
            normalized_payload = {}
            if payload.get("direct_parent") is not None:
                normalized_payload["direct_parent"] = str(payload.get("direct_parent"))
            if payload.get("direct_relation") is not None:
                normalized_payload["direct_relation"] = str(payload.get("direct_relation"))
            states = payload.get("states", {})
            if isinstance(states, dict) and states:
                normalized_payload["states"] = states
            if normalized_payload:
                entities[name] = normalized_payload

    robot = {}
    raw_robot = goal_state.get("robot") or goal_state.get("robot_state") or {}
    if isinstance(raw_robot, dict):
        aliases = {
            "holding": "robot_holding",
            "held": "robot_holding",
            "inventory": "robot_inventory",
            "hands": "robot_hands",
            "location": "robot_location",
            "facing": "robot_facing",
        }
        for key, value in raw_robot.items():
            if value is None or isinstance(value, (str, int, float, bool, dict, list)):
                normalized_key = aliases.get(str(key), str(key))
                robot[normalized_key] = value

    normalized = {}
    if entities:
        normalized["entities"] = entities
    if robot:
        normalized["robot"] = robot
    return normalized


def normalize_structured_task(structured: dict | None) -> dict:
    structured = structured if isinstance(structured, dict) else {}
    names_info = structured.get("required_item_names", {})
    if not isinstance(names_info, dict):
        names_info = {}

    normalized = {
        "intent": str(structured.get("intent", "")),
        "required_item_names": {
            "targets": normalize_name_bucket(names_info.get("targets")),
            "tools": normalize_name_bucket(names_info.get("tools")),
            "receptacles": normalize_name_bucket(names_info.get("receptacles")),
        },
    }
    quantity_constraints = structured.get("quantity_constraints")
    if isinstance(quantity_constraints, (dict, list)) and quantity_constraints:
        normalized["quantity_constraints"] = copy.deepcopy(quantity_constraints)
    for key in ("goal_state", "desired_state", "target_state"):
        value = structured.get(key)
        if isinstance(value, dict) and value:
            goal_state = normalize_goal_state(value)
            normalized["goal_state"] = goal_state if goal_state else copy.deepcopy(value)
            break
        if isinstance(value, list) and value:
            normalized["goal_state"] = copy.deepcopy(value)
            break
    final_state = structured.get("final_state")
    if final_state not in (None, "", {}, []):
        normalized["final_state"] = copy.deepcopy(final_state)
    return normalized


def collect_proposed_entities(names_info: dict) -> list[str]:
    proposed = []
    for category in ("targets", "tools", "receptacles"):
        cat_data = names_info.get(category, {})
        if isinstance(cat_data, dict):
            proposed.extend(cat_data.get("primary", []))
            proposed.extend(cat_data.get("alternatives", []))
        elif isinstance(cat_data, list):
            proposed.extend(cat_data)
    return [name for name in proposed if name]


def run(context: FeatureContext, result: FeatureResult) -> FeatureResult:
    del context
    return {"structured_task": normalize_structured_task(result.get("structured_task", {}))}
