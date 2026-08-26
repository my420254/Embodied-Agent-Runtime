from __future__ import annotations

from .base import FeatureContext, FeatureResult
from .entity_relevance import flatten_entity_relevance, unique_names
from .normalize import collect_proposed_entities


def run(context: FeatureContext, result: FeatureResult) -> FeatureResult:
    if result.get("stop_pipeline") or result.get("is_cancel_all"):
        return {}

    scene_entities = list(context.get("scene_entities", []))
    scene_entity_set = set(scene_entities)

    candidates = flatten_entity_relevance(result.get("entity_relevance", {}))

    llm_relevant_names = result.get("relevant_item_names", [])
    if isinstance(llm_relevant_names, list) and llm_relevant_names:
        candidates.extend(str(name) for name in llm_relevant_names if name)

    structured = result.get("structured_task", {})
    names_info = structured.get("required_item_names", {}) if isinstance(structured, dict) else {}
    candidates.extend(collect_proposed_entities(names_info if isinstance(names_info, dict) else {}))
    candidates = unique_names(candidates)

    return {
        "relevant_item_names": unique_names(
            [candidate for candidate in candidates if candidate in scene_entity_set]
        )
    }
