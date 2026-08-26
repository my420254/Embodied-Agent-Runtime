import re
import uuid
from datetime import datetime, timezone


SECTION_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
RULE_STATUSES = {"candidate", "promoted", "deprecated"}

TAG_KEYWORDS = {
    "navigation": ("navigate", "navigation", "位置", "导航", "所在位置", "target_location"),
    "precondition": ("前置", "必须先", "约束", "校验", "满足"),
    "output_format": ("输出", "非空", "格式", "序列", "todo_list"),
    "restoration": ("复原", "归还", "关闭", "还原", "收尾"),
    "termination": ("finishtask", "终结", "闭环", "结束"),
    "food_cleaning": ("clean", "清洗", "清洁", "卫生", "食材"),
    "skill_validity": ("动作", "技能", "有效性", "未定义", "支持集合"),
    "tool_use": ("工具", "刀", "锋利", "损坏", "手持"),
    "container_access": ("容器", "打开", "关闭", "open", "close"),
}


def safe_section(section: str) -> str:
    normalized = (section or "").strip()
    if not SECTION_PATTERN.fullmatch(normalized):
        raise ValueError(f"invalid playbook section: {section!r}")
    return normalized


def empty_playbook() -> dict:
    return {"rules": []}


def coerce_playbook(data: dict) -> dict:
    if not isinstance(data, dict):
        return empty_playbook()
    rules = data.get("rules", [])
    if not isinstance(rules, list):
        rules = []
    data["rules"] = [rule for rule in rules if isinstance(rule, dict)]
    return data


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def rule_id(section: str) -> str:
    return f"{section}-{uuid.uuid4().hex[:12]}"


def normalize_rule(rule: str) -> str:
    return re.sub(r"\s+", " ", rule or "").strip()


def infer_tags(rule: str, intent_context: str = "") -> list[str]:
    text = f"{rule} {intent_context}".lower()
    tags = [
        tag
        for tag, keywords in TAG_KEYWORDS.items()
        if any(keyword.lower() in text for keyword in keywords)
    ]
    return tags or ["general"]


def strip_section(rule: dict) -> dict:
    clean_rule = dict(rule)
    clean_rule.pop("section", None)
    return clean_rule


def with_section(section: str, rule: dict) -> dict:
    if "section" in rule:
        return dict(rule)
    return {"section": section, **rule}


def coerce_rule_metadata(section: str, rule: dict) -> dict:
    clean_rule = strip_section(rule)
    rule_text = normalize_rule(clean_rule.get("rule", ""))
    now = now_iso()
    clean_rule["id"] = clean_rule.get("id") or rule_id(section)
    clean_rule["source"] = clean_rule.get("source", "未知")
    clean_rule["intent_context"] = clean_rule.get("intent_context", "")
    clean_rule["rule"] = rule_text
    clean_rule["tags"] = clean_rule.get("tags") or infer_tags(rule_text, clean_rule.get("intent_context", ""))
    clean_rule["helpful_count"] = int(clean_rule.get("helpful_count", 0) or 0)
    clean_rule["harmful_count"] = int(clean_rule.get("harmful_count", 0) or 0)
    clean_rule["neutral_count"] = int(clean_rule.get("neutral_count", 0) or 0)
    status = clean_rule.get("status") or "promoted"
    clean_rule["status"] = status if status in RULE_STATUSES else "promoted"
    clean_rule["source_split"] = clean_rule.get("source_split", "unknown")
    clean_rule["source_case_id"] = clean_rule.get("source_case_id", "")
    counterexamples = clean_rule.get("counterexamples", [])
    clean_rule["counterexamples"] = counterexamples if isinstance(counterexamples, list) else []
    clean_rule["created_at"] = clean_rule.get("created_at") or now
    clean_rule["updated_at"] = clean_rule.get("updated_at") or clean_rule["created_at"]
    clean_rule["deprecated"] = bool(clean_rule.get("deprecated", False))
    if clean_rule["deprecated"]:
        clean_rule["status"] = "deprecated"
    if clean_rule.get("deprecated_reason") is None:
        clean_rule.pop("deprecated_reason", None)
    return clean_rule


def rule_value(rule: dict) -> float:
    helpful = int(rule.get("helpful_count", 0) or 0)
    harmful = int(rule.get("harmful_count", 0) or 0)
    return helpful - (harmful * 2)
