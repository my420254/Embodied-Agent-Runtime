from __future__ import annotations

from typing import Any


def _properties(info: dict[str, Any]) -> set[str]:
    raw = info.get("properties", []) if isinstance(info, dict) else []
    if not isinstance(raw, (list, tuple, set)):
        return set()
    return {str(value) for value in raw if str(value)}


def _has_property(info: dict[str, Any], value: str) -> bool:
    return value in _properties(info)


def delta_has_predicate(
    sim_env: dict[str, Any],
    item: str,
    predicate: str,
) -> bool:
    info = sim_env.get(item, {})
    if not isinstance(info, dict):
        return False
    if _has_property(info, f"delta_predicate:{predicate}"):
        return True
    if predicate == "item_empty":
        states = info.get("states", {})
        return isinstance(states, dict) and states.get("isEmpty") is True
    return False


__all__ = ["delta_has_predicate"]
