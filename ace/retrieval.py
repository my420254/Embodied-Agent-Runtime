import re
from difflib import SequenceMatcher

from config.settings import get_config

from ace.schema import infer_tags, normalize_rule
from ace.storage import iter_section_rules


DEFAULT_DUPLICATE_SIMILARITY = 0.92
DEFAULT_RELEVANT_RULE_LIMIT = 8
OBSOLETE_PLANNING_RULE_KEYWORDS = ("FinishTask", "复原", "恢复", "归还", "归位", "收尾")


def normalize_query_text(value) -> str:
    if isinstance(value, dict):
        return " ".join(normalize_query_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(normalize_query_text(item) for item in value)
    return str(value or "")


def _is_rule_compatible(section: str, rule: dict) -> bool:
    rule_text = str(rule.get("rule", "") or "")
    if section == "planning":
        return not any(keyword in rule_text for keyword in OBSOLETE_PLANNING_RULE_KEYWORDS)
    return True


def score_rule(rule: dict, query: str, tags: set[str]) -> float:
    rule_text = f"{rule.get('rule', '')} {rule.get('intent_context', '')}".lower()
    query_tokens = set(re.findall(r"[\w\u4e00-\u9fff]+", query.lower()))
    overlap = sum(1 for token in query_tokens if token and token in rule_text)
    tag_overlap = len(tags.intersection(set(rule.get("tags", []))))
    helpful = int(rule.get("helpful_count", 0) or 0)
    harmful = int(rule.get("harmful_count", 0) or 0)
    return overlap + (tag_overlap * 3) + (helpful * 0.5) - harmful


def is_duplicate_rule(rule: str, existing_rules: list[str], threshold: float) -> bool:
    normalized = normalize_rule(rule)
    if not normalized:
        return True
    for existing in existing_rules:
        existing_normalized = normalize_rule(existing)
        if normalized == existing_normalized:
            return True
        if SequenceMatcher(None, normalized, existing_normalized).ratio() >= threshold:
            return True
    return False


def load_section_rules(section: str, empty_message: str | None = None) -> str:
    rules = [
        f"[{rule.get('source', '未知')}] {rule['rule']}"
        for rule in iter_section_rules(section)
        if rule.get("rule") and _is_rule_compatible(section, rule)
    ]
    if rules:
        return "\n".join([f"- {rule}" for rule in rules])
    return empty_message or f"暂无 {section} 层历史经验。"


def format_rules(rules: list[dict], empty_message: str | None = None, section: str = "planning") -> str:
    lines = [
        f"- [{rule.get('source', '未知')}|{rule.get('id', 'no-id')}] {rule['rule']}"
        for rule in rules
        if rule.get("rule") and _is_rule_compatible(section, rule)
    ]
    if lines:
        return "\n".join(lines)
    return empty_message or f"暂无 {section} 层历史经验。"


def load_relevant_rules(
    section: str,
    *,
    intent: str = "",
    context: dict | None = None,
    tags: list[str] | None = None,
    limit: int | None = None,
) -> list[dict]:
    rules = [rule for rule in iter_section_rules(section) if _is_rule_compatible(section, rule)]
    if limit is None:
        limit = get_config("ace", "relevant_rule_limit", default=DEFAULT_RELEVANT_RULE_LIMIT)
    if not isinstance(limit, int) or limit <= 0:
        limit = DEFAULT_RELEVANT_RULE_LIMIT

    query = normalize_query_text({"intent": intent, "context": context or {}})
    requested_tags = set(tags or infer_tags(query))
    ranked = sorted(
        rules,
        key=lambda rule: (score_rule(rule, query, requested_tags), int(rule.get("helpful_count", 0) or 0), rule.get("updated_at", "")),
        reverse=True,
    )
    return ranked[:limit]


def load_relevant_section_rules(
    section: str,
    *,
    intent: str = "",
    context: dict | None = None,
    tags: list[str] | None = None,
    limit: int | None = None,
    empty_message: str | None = None,
) -> tuple[str, list[str]]:
    rules = load_relevant_rules(section, intent=intent, context=context, tags=tags, limit=limit)
    return format_rules(rules, empty_message=empty_message, section=section), [rule["id"] for rule in rules if rule.get("id")]
