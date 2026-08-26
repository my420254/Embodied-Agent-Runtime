from config.settings import get_config

from ace.maintenance import trim_rules
from ace.retrieval import DEFAULT_DUPLICATE_SIMILARITY, is_duplicate_rule
from ace.schema import coerce_rule_metadata, infer_tags, normalize_rule, now_iso, rule_id, safe_section
from ace.storage import load_section_playbook_unlocked, playbook_lock, save_section_playbook_unlocked


def feature_enabled(feature_flags: dict | None, name: str, default: bool = True) -> bool:
    if isinstance(feature_flags, dict) and name in feature_flags:
        return bool(feature_flags[name])
    return default


def apply_delta(section: str, delta: dict) -> bool:
    section = safe_section(section)
    op = delta.get("op")
    now = now_iso()

    with playbook_lock(section):
        data = load_section_playbook_unlocked(section)
        rules = data.setdefault("rules", [])
        by_id = {rule.get("id"): rule for rule in rules if rule.get("id")}

        if op == "add":
            rule_text = normalize_rule(delta.get("rule", ""))
            if not rule_text:
                return False
            existing = [rule.get("rule", "") for rule in rules if not rule.get("deprecated")]
            threshold = float(get_config("ace", "duplicate_similarity", default=DEFAULT_DUPLICATE_SIMILARITY))
            if is_duplicate_rule(rule_text, existing, threshold):
                return False
            rules.append(
                coerce_rule_metadata(
                    section,
                    {
                        "id": delta.get("id") or rule_id(section),
                        "source": delta.get("source", "delta"),
                        "intent_context": delta.get("intent_context", ""),
                        "rule": rule_text,
                        "tags": delta.get("tags") or infer_tags(rule_text, delta.get("intent_context", "")),
                        "status": delta.get("status", "promoted"),
                        "source_split": delta.get("source_split", "unknown"),
                        "source_case_id": delta.get("source_case_id", ""),
                        "counterexamples": delta.get("counterexamples", []),
                        "neutral_count": delta.get("neutral_count", 0),
                        "created_at": now,
                        "updated_at": now,
                    },
                )
            )

        elif op == "update":
            target = by_id.get(delta.get("target_id"))
            if not target:
                return False
            if delta.get("rule"):
                target["rule"] = normalize_rule(delta["rule"])
            if delta.get("tags"):
                target["tags"] = list(dict.fromkeys(delta["tags"]))
            elif delta.get("rule"):
                target["tags"] = infer_tags(target["rule"], target.get("intent_context", ""))
            if "intent_context" in delta:
                target["intent_context"] = delta.get("intent_context", "")
            target["source"] = delta.get("source", target.get("source", "delta"))
            if delta.get("status"):
                target["status"] = delta["status"]
            if "source_split" in delta:
                target["source_split"] = delta.get("source_split", "unknown")
            if "source_case_id" in delta:
                target["source_case_id"] = delta.get("source_case_id", "")
            target["updated_at"] = now

        elif op == "merge":
            target_ids = [rule_id_value for rule_id_value in delta.get("target_ids", []) if rule_id_value in by_id]
            if len(target_ids) < 2:
                return False
            merged_rule = normalize_rule(delta.get("rule", ""))
            if not merged_rule:
                merged_rule = max((by_id[rule_id_value]["rule"] for rule_id_value in target_ids), key=len)
            merged_tags = []
            helpful_count = 0
            harmful_count = 0
            intent_contexts = []
            for rule_id_value in target_ids:
                rule = by_id[rule_id_value]
                merged_tags.extend(rule.get("tags", []))
                helpful_count += int(rule.get("helpful_count", 0) or 0)
                harmful_count += int(rule.get("harmful_count", 0) or 0)
                if rule.get("intent_context"):
                    intent_contexts.append(rule["intent_context"])
                rule["deprecated"] = True
                rule["deprecated_reason"] = f"merged into {delta.get('id') or 'new rule'}"
                rule["updated_at"] = now
            new_id = delta.get("id") or rule_id(section)
            rules.append(
                coerce_rule_metadata(
                    section,
                    {
                        "id": new_id,
                        "source": delta.get("source", "delta_merge"),
                        "intent_context": delta.get("intent_context") or " | ".join(dict.fromkeys(intent_contexts)),
                        "rule": merged_rule,
                        "tags": delta.get("tags") or list(dict.fromkeys(merged_tags)) or infer_tags(merged_rule),
                        "helpful_count": helpful_count,
                        "harmful_count": harmful_count,
                        "status": delta.get("status", "promoted"),
                        "source_split": delta.get("source_split", "unknown"),
                        "source_case_id": delta.get("source_case_id", ""),
                        "created_at": now,
                        "updated_at": now,
                    },
                )
            )

        elif op == "deprecate":
            target = by_id.get(delta.get("target_id"))
            if not target:
                return False
            target["deprecated"] = True
            target["status"] = "deprecated"
            target["deprecated_reason"] = delta.get("reason", "deprecated by delta")
            target["updated_at"] = now

        else:
            raise ValueError(f"unsupported playbook delta op: {op!r}")

        trim_rules(data)
        save_section_playbook_unlocked(section, data)
        return True


def apply_deltas(section: str, deltas: list[dict]) -> int:
    applied = 0
    for delta in deltas:
        if apply_delta(section, delta):
            applied += 1
    return applied


def write_experience(
    section: str,
    source: str,
    rule: str,
    intent_context: str = "",
    *,
    feature_flags: dict | None = None,
) -> bool:
    if not feature_enabled(feature_flags, "playbook_write"):
        return False
    written = apply_delta(
        section,
        {
            "op": "add",
            "source": source,
            "intent_context": intent_context,
            "rule": rule,
        },
    )
    if written:
        print(f"\n[ACE 经验写入] section={section} source={source}: {rule[:60]}...")
    return written


def write_candidate_experience(
    section: str,
    source: str,
    rule: str,
    intent_context: str = "",
    *,
    source_split: str = "train",
    source_case_id: str = "",
    feature_flags: dict | None = None,
) -> bool:
    if not feature_enabled(feature_flags, "playbook_write"):
        return False
    return apply_delta(
        section,
        {
            "op": "add",
            "source": source,
            "intent_context": intent_context,
            "rule": rule,
            "status": "candidate",
            "source_split": source_split,
            "source_case_id": source_case_id,
        },
    )
