from __future__ import annotations
from typing import Any


_EXACT_CODES = {
    "position precondition failed": "wrong_room",
    "room precondition failed": "wrong_room_parameter",
    "loadable room mismatch": "wrong_room_parameter",
    "surface room mismatch": "wrong_room_parameter",
    "station room mismatch": "wrong_room_parameter",
    "water source room mismatch": "wrong_room_parameter",
    "disposal room mismatch": "wrong_room_parameter",
    "机械臂冲突": "hand_occupied",
    "手持物品不匹配": "wrong_held_item",
    "容器未清空": "container_not_empty",
    "容器为空": "container_empty",
    "物理可达性受限": "inaccessible_entity",
    "工具状态不满足": "tool_state_missing",
    "组件位置不满足": "component_location_mismatch",
    "目标位置不合法": "invalid_destination",
    "目标类型不匹配": "wrong_target_type",
    "目标已处理": "already_disposed",
    "目标已完成": "already_completed",
    "official DELTA predicate failed": "predicate_failed",
    "item_in precondition failed": "containment_precondition",
    "invalid DELTA room transition": "invalid_navigation_transition",
    "missing DELTA navigation graph": "missing_navigation_graph",
    "invalid DELTA loadable": "invalid_loadable",
    "invalid DELTA surface": "invalid_surface",
    "invalid DELTA station": "invalid_station",
    "invalid DELTA tool": "invalid_tool",
    "invalid DELTA water source": "invalid_water_source",
    "invalid DELTA disposal": "invalid_disposal",
    "invalid DELTA component": "invalid_component",
}


def _code(issue: str) -> str:
    if issue in _EXACT_CODES:
        return _EXACT_CODES[issue]
    lowered = issue.lower()
    if lowered.startswith("missing "):
        return "missing_parameter"
    if lowered.startswith("invalid delta ") or issue in {"无效来源容器", "无效的目标房间"}:
        return "invalid_entity_or_room"
    return "handler_rejection"


def _robot_evidence(robot: dict[str, Any] | None) -> dict[str, Any]:
    state = robot if isinstance(robot, dict) else {}
    return {key: state[key] for key in ("robot_location", "robot_holding", "battery", "battery_full") if key in state}


def classify_failure(issue_type: str, fix_advice: str, *, skill: str = "", parameters: dict[str, Any] | None = None, environment: dict[str, Any] | None = None, robot: dict[str, Any] | None = None) -> dict[str, Any]:
    issue = str(issue_type or "").strip()
    return {"dataset": "delta", "error_code": _code(issue), "issue_type": issue, "issue": issue, "fix_advice": str(fix_advice or ""), "evidence": {"skill": str(skill or ""), "parameters": parameters if isinstance(parameters, dict) else {}, "robot": _robot_evidence(robot)}, "source": "handler.validate"}


__all__ = ["classify_failure"]
