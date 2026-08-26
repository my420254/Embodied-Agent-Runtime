from __future__ import annotations

from typing import Any, Iterable

RELEVANCE_CATEGORIES = ("directly_related", "indirectly_related", "possibly_related")


def _as_name(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("name", "")).strip()
    return str(value or "").strip()


def _as_score(value: Any, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def unique_names(names: Iterable[str]) -> list[str]:
    seen = set()
    unique = []
    for name in names:
        normalized = str(name or "").strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique.append(normalized)
    return unique


def normalize_entity_relevance(raw: Any) -> dict[str, list[dict[str, Any]]]:
    """Normalize LLM relevance buckets and sort each bucket by score descending."""
    if not isinstance(raw, dict):
        return {category: [] for category in RELEVANCE_CATEGORIES}

    normalized: dict[str, list[dict[str, Any]]] = {}
    used_names = set()
    for category in RELEVANCE_CATEGORIES:
        entries = raw.get(category, [])
        if not isinstance(entries, list):
            entries = []
        bucket = []
        for index, entry in enumerate(entries):
            name = _as_name(entry)
            if not name or name in used_names:
                continue
            fallback_score = max(0.0, 1.0 - index * 0.01)
            if isinstance(entry, dict):
                score = _as_score(entry.get("score"), fallback_score)
                reason = str(entry.get("reason", ""))
                required = bool(entry.get("required", category == "directly_related"))
            else:
                score = fallback_score
                reason = ""
                required = category == "directly_related"
            bucket.append(
                {
                    "name": name,
                    "reason": reason,
                    "required": required,
                    "score": score,
                }
            )
            used_names.add(name)
        normalized[category] = sorted(bucket, key=lambda item: item.get("score", 0.0), reverse=True)
    return normalized


def flatten_entity_relevance(raw: Any) -> list[str]:
    relevance = normalize_entity_relevance(raw)
    names = []
    for category in RELEVANCE_CATEGORIES:
        names.extend(entry["name"] for entry in relevance.get(category, []))
    return unique_names(names)
