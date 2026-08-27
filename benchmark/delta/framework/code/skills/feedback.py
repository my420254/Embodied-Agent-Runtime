from __future__ import annotations

from typing import Iterable


def repair_feedback(
    *,
    observed: str,
    required: str,
    repair_actions: Iterable[str] | None = None,
    note: str = "",
) -> str:
    parts = [
        f"当前状态: {observed}",
        f"缺失条件: {required}",
    ]
    actions = [str(action).strip() for action in (repair_actions or []) if str(action).strip()]
    if actions:
        parts.append("可用修复动作类型: " + ", ".join(actions))
    if note:
        parts.append(f"说明: {note}")
    return "；".join(parts)

