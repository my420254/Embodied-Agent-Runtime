from __future__ import annotations

from typing import Any


def append_debug_event(state: dict, event: dict) -> list[dict]:
    events = list(state.get("planning_debug_events") or [])
    events.append(event)
    return events


def sync_debug_event_aliases(payload: dict[str, Any]) -> dict[str, Any]:
    events = payload.get("planning_debug_events")
    if isinstance(events, list):
        payload["planning_debug_events"] = list(events)
    return payload
