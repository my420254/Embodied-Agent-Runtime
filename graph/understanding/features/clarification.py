from .base import FeatureContext, FeatureResult


def run(context: FeatureContext, result: FeatureResult) -> FeatureResult:
    task = str(context.get("task", "")).strip()
    allow_clarification = bool(context.get("allow_clarification", True))
    if result.get("is_cancel_all"):
        return {"needs_clarification": False, "clarification_question": ""}

    if not task:
        return {
            "is_complete": False,
            "needs_clarification": True,
            "clarification_question": "请说明您希望机器人执行什么任务。",
        }

    if result.get("is_complete"):
        return {"needs_clarification": False}

    if not allow_clarification:
        return {
            "needs_clarification": False,
            "clarification_question": "",
            "clarification_suppressed": True,
        }

    question = result.get("clarification_question") or "指令参数缺失，请重新指定操作对象。"
    return {
        "is_complete": False,
        "needs_clarification": True,
        "clarification_question": question,
    }
