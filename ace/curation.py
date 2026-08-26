from config.prompts import render_prompt

from ace.delta import write_experience
from ace.storage import iter_section_rules


def build_evaluator_curator_prompt(raw_issue: str, raw_fix: str, step_detail: str) -> str:
    planning_rules = [rule.get("rule", "") for rule in iter_section_rules("planning")]
    existing_str = "\n".join([f"- {rule}" for rule in planning_rules]) if planning_rules else "为空"

    return render_prompt(
        "ace.evaluator_curator",
        raw_issue=raw_issue,
        raw_fix=raw_fix,
        existing_rules=existing_str,
        step_detail=step_detail,
    )


def summarize_success_trajectory(intent: str, todo_list: list[dict]) -> str:
    skills = [
        step.get("execution", {}).get("skill", "")
        for step in todo_list
        if isinstance(step, dict) and step.get("execution", {}).get("skill")
    ]
    if not skills:
        return ""

    unique_skills = list(dict.fromkeys(skills))
    if any("Slice" in skill for skill in unique_skills) and any("Clean" in skill for skill in unique_skills):
        return "成功轨迹经验：涉及食材切割的任务可按“清洗食材 -> 放置到操作表面 -> 持有锋利工具 -> Slice”的顺序规划。"
    if any("Pickup" in skill for skill in unique_skills) and any("Put" in skill for skill in unique_skills):
        return "成功轨迹经验：搬运类任务通常需要按“NavigateTo 源位置 -> Pickup -> NavigateTo 目标位置 -> Put”的顺序规划。"
    if any("Open" in skill for skill in unique_skills) and any("Close" in skill for skill in unique_skills):
        return "成功轨迹经验：涉及容器访问的任务应在访问前 Open；只有当任务目标明确要求关闭容器时才追加 Close。"
    return ""


def learn_from_success(
    section: str,
    intent: str,
    todo_list: list[dict],
    *,
    feature_flags: dict | None = None,
) -> bool:
    rule = summarize_success_trajectory(intent, todo_list)
    if not rule:
        return False
    return write_experience(
        section=section,
        source="成功轨迹总结",
        rule=rule,
        intent_context=intent,
        feature_flags=feature_flags,
    )


def curate_evaluator_finding(
    raw_issue: str,
    raw_fix: str,
    intent: str,
    step_detail: str,
    invoke_curator,
    *,
    feature_flags: dict | None = None,
) -> bool:
    """Generalize a sandbox evaluator finding and write it into the playbook."""
    curator_prompt = build_evaluator_curator_prompt(raw_issue, raw_fix, step_detail)

    try:
        result = invoke_curator(curator_prompt)
        if result.get("is_duplicate", False):
            return False
        generalized_rule = result.get("generalized_rule", "")
        if not generalized_rule:
            return False
        return write_experience(
            section="planning",
            source="动态验证拦截",
            rule=generalized_rule,
            intent_context=intent,
            feature_flags=feature_flags,
        )
    except Exception as e:
        print(f"[ACE 警报] evaluator 经验策展失败: {e}")
        return False
