from __future__ import annotations

from skills.loader import load_enabled_skill_names

from .base import FeatureContext, FeatureResult


def filter_skill_selection(
    *,
    proposed_skill_names: list[str],
    available_skill_names: list[str],
) -> list[str]:
    ordered_available = list(dict.fromkeys(str(name) for name in available_skill_names if name))
    available = set(ordered_available)
    selected = []
    seen = set()
    for name in proposed_skill_names:
        text = str(name or "").strip()
        if text and text in available and text not in seen:
            selected.append(text)
            seen.add(text)
    return selected


def run(context: FeatureContext, result: FeatureResult) -> FeatureResult:
    if (
        result.get("stop_pipeline")
        or result.get("is_cancel_all")
        or not result.get("is_complete")
    ):
        return {"skill_closure": []}
    try:
        available = load_enabled_skill_names()
    except Exception:
        return {"skill_closure": []}
    proposed = result.get("skill_closure", [])
    return {
        "skill_closure": filter_skill_selection(
            proposed_skill_names=(
                [str(name) for name in proposed if name]
                if isinstance(proposed, list)
                else []
            ),
            available_skill_names=available,
        )
    }


__all__ = ["filter_skill_selection", "run"]
