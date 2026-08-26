from difflib import SequenceMatcher

from config.settings import get_config

from ace.maintenance import trim_rules
from ace.retrieval import DEFAULT_DUPLICATE_SIMILARITY
from ace.schema import normalize_rule, now_iso, rule_value, safe_section
from ace.storage import load_section_playbook_unlocked, playbook_lock, save_section_playbook_unlocked


DEFAULT_REFINE_DUPLICATE_SIMILARITY = DEFAULT_DUPLICATE_SIMILARITY


def refine_playbook(section: str, *, duplicate_similarity: float | None = None, prune_harmful: bool = True) -> dict:
    section = safe_section(section)
    if duplicate_similarity is None:
        duplicate_similarity = get_config("ace", "refine_duplicate_similarity", default=DEFAULT_REFINE_DUPLICATE_SIMILARITY)
    if not isinstance(duplicate_similarity, (int, float)) or duplicate_similarity <= 0 or duplicate_similarity > 1:
        duplicate_similarity = DEFAULT_REFINE_DUPLICATE_SIMILARITY

    with playbook_lock(section):
        data = load_section_playbook_unlocked(section)
        rules = data.get("rules", [])
        changed = False
        deprecated_count = 0
        merged_count = 0

        if prune_harmful:
            for rule in rules:
                helpful = int(rule.get("helpful_count", 0) or 0)
                harmful = int(rule.get("harmful_count", 0) or 0)
                if not rule.get("deprecated") and harmful >= 3 and harmful > helpful:
                    rule["deprecated"] = True
                    rule["deprecated_reason"] = "harmful feedback exceeded helpful feedback"
                    rule["updated_at"] = now_iso()
                    deprecated_count += 1
                    changed = True

        active = [rule for rule in rules if not rule.get("deprecated")]
        used_ids: set[str] = set()
        for index, rule in enumerate(active):
            if rule["id"] in used_ids:
                continue
            group = [rule]
            for other in active[index + 1:]:
                if other["id"] in used_ids:
                    continue
                similarity = SequenceMatcher(None, normalize_rule(rule["rule"]), normalize_rule(other["rule"])).ratio()
                if similarity >= float(duplicate_similarity):
                    group.append(other)
            if len(group) < 2:
                continue
            keeper = max(group, key=lambda item: (rule_value(item), len(item.get("rule", ""))))
            for item in group:
                if item is keeper:
                    continue
                keeper["helpful_count"] += int(item.get("helpful_count", 0) or 0)
                keeper["harmful_count"] += int(item.get("harmful_count", 0) or 0)
                keeper["tags"] = list(dict.fromkeys(keeper.get("tags", []) + item.get("tags", [])))
                item["deprecated"] = True
                item["deprecated_reason"] = f"merged into {keeper['id']}"
                item["updated_at"] = now_iso()
                used_ids.add(item["id"])
                merged_count += 1
                changed = True
            keeper["updated_at"] = now_iso()

        trim_rules(data)
        if changed:
            save_section_playbook_unlocked(section, data)

        return {
            "section": section,
            "changed": changed,
            "merged": merged_count,
            "deprecated": deprecated_count,
            "active_rules": len([rule for rule in data.get("rules", []) if not rule.get("deprecated")]),
            "total_rules": len(data.get("rules", [])),
        }
