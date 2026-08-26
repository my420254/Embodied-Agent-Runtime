from .base import FeatureContext, FeatureResult
from .normalize import empty_required_item_names

CANCEL_KEYWORDS = ("取消", "终止", "停止", "结束", "cancel", "stop", "terminate", "abort")


def run(context: FeatureContext, result: FeatureResult) -> FeatureResult:
    del result
    task = str(context.get("task", ""))
    if not any(keyword in task.lower() for keyword in CANCEL_KEYWORDS):
        return {}

    return {
        "is_complete": True,
        "is_cancel_all": True,
        "needs_clarification": False,
        "execution_status": "fully_completed",
        "feedback": "任务已取消，无需执行动作。",
        "clarification_question": "",
        "relevant_item_names": [],
        "structured_task": {
            "intent": "取消当前任务",
            "required_item_names": empty_required_item_names(),
        },
        "stop_pipeline": True,
    }
