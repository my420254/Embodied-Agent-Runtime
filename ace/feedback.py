import copy

from ace.schema import now_iso, safe_section
from ace.storage import load_section_playbook_unlocked, playbook_lock, save_section_playbook_unlocked


def _feature_enabled(feature_flags: dict | None, name: str, default: bool = True) -> bool:
    if isinstance(feature_flags, dict) and name in feature_flags:
        return bool(feature_flags[name])
    return default


def record_rule_feedback(
    section: str,
    rule_ids: list[str] | None,
    *,
    outcome: str,
    feature_flags: dict | None = None,
) -> int:
    if not _feature_enabled(feature_flags, "playbook_write"):
        return 0
    if not rule_ids:
        return 0
    if outcome not in {"helpful", "harmful"}:
        raise ValueError(f"invalid rule feedback outcome: {outcome!r}")

    section = safe_section(section)
    rule_id_set = set(rule_ids)
    count_key = "helpful_count" if outcome == "helpful" else "harmful_count"

    with playbook_lock(section):
        data = load_section_playbook_unlocked(section)
        updated = 0
        for rule in data.get("rules", []):
            if rule.get("id") in rule_id_set:
                rule[count_key] = int(rule.get(count_key, 0) or 0) + 1
                rule["updated_at"] = now_iso()
                updated += 1
        if updated:
            save_section_playbook_unlocked(section, data)
        return updated


def promote_rule(section: str, rule_id: str, *, feature_flags: dict | None = None) -> bool:
    if not _feature_enabled(feature_flags, "playbook_write"):
        return False
    section = safe_section(section)
    with playbook_lock(section):
        data = load_section_playbook_unlocked(section)
        for rule in data.get("rules", []):
            if rule.get("id") == rule_id and not rule.get("deprecated"):
                rule["status"] = "promoted"
                rule["updated_at"] = now_iso()
                save_section_playbook_unlocked(section, data)
                return True
        return False


def record_rule_counterexample(
    section: str,
    rule_id: str,
    counterexample: dict,
    *,
    deprecate: bool = False,
    feature_flags: dict | None = None,
) -> bool:
    if not _feature_enabled(feature_flags, "playbook_write"):
        return False
    section = safe_section(section)
    with playbook_lock(section):
        data = load_section_playbook_unlocked(section)
        for rule in data.get("rules", []):
            if rule.get("id") != rule_id:
                continue

            examples = rule.setdefault("counterexamples", [])
            examples.append(copy.deepcopy(counterexample))
            rule["harmful_count"] = int(rule.get("harmful_count", 0) or 0) + 1
            if deprecate:
                rule["deprecated"] = True
                rule["status"] = "deprecated"
                rule["deprecated_reason"] = counterexample.get("reason", "counterexample screening failed")
            rule["updated_at"] = now_iso()
            save_section_playbook_unlocked(section, data)
            return True
        return False
