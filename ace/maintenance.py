from config.settings import get_config

from ace.schema import rule_value


DEFAULT_MAX_RULES_PER_SECTION = 40


def trim_rules(data: dict) -> None:
    max_rules = get_config("ace", "max_rules_per_section", default=DEFAULT_MAX_RULES_PER_SECTION)
    if not isinstance(max_rules, int) or max_rules <= 0:
        max_rules = DEFAULT_MAX_RULES_PER_SECTION

    rules = data.get("rules", [])
    if len(rules) > max_rules:
        data["rules"] = sorted(
            rules,
            key=lambda rule: (bool(rule.get("deprecated")), rule_value(rule), rule.get("updated_at", "")),
            reverse=True,
        )[:max_rules]
