# validation/checkpoint.py - step, checkpoint, and goal-predicate helpers.
# 这些函数不读取可被测试 monkeypatch 的全局符号（apply_sandbox_action / get_config 等），
# 仅依赖 copy 与 entities 的纯辅助，可安全下沉到子包。
import copy
import re
from typing import Any


def _reindex_todo_steps(steps: list) -> list[dict[str, Any]]:
    """把一串 step 重新按 1 起步连续编号，常用于拼接“已验证前缀 + 补丁后缀”后恢复正确步号。"""
    reindexed = []
    for index, step in enumerate(steps or [], start=1):
        if not isinstance(step, dict):
            continue
        item = copy.deepcopy(step)
        item["step"] = index
        reindexed.append(item)
    return reindexed


def _step_number(step: dict | None) -> int | None:
    if not isinstance(step, dict):
        return None
    try:
        return int(step.get("step"))
    except (TypeError, ValueError):
        return None


def _step_by_number(steps: list, step_num: int | None) -> dict:
    if step_num is None:
        return {}
    for step in steps or []:
        if _step_number(step) == step_num:
            return step if isinstance(step, dict) else {}
    return {}


def _infer_failed_step_num(*texts: str, fallback: int | None = None) -> int | None:
    for text in texts:
        if not text:
            continue
        for pattern in (
            r"\b[Ss]tep\s*#?\s*(\d+)",
            r"第\s*(\d+)\s*步",
            r"步骤\s*(\d+)",
        ):
            match = re.search(pattern, str(text))
            if match:
                return int(match.group(1))
    return fallback


def _apply_checkpoint_env(flat_env: dict[str, Any], checkpoint_env: dict[str, Any], robot_state: dict[str, Any]) -> dict[str, Any]:
    """把上一轮保存的 checkpoint 环境叠到当前沙盒基线上：
    1) 用 checkpoint 中的实体覆盖同名基线实体；
    2) 若机器人此时正抓着某物，把该物的 direct_parent 标成 robot_hand，确保后续放置语义自洽。"""
    merged = copy.deepcopy(flat_env)
    for name, info in (checkpoint_env or {}).items():
        merged[name] = copy.deepcopy(info) if isinstance(info, dict) else info
    held_item = str((robot_state or {}).get("robot_holding") or "空")
    if held_item and held_item != "空" and held_item in merged:
        item_info = merged.get(held_item, {})
        if isinstance(item_info, dict):
            patched = copy.deepcopy(item_info)
            patched["direct_parent"] = "robot_hand"
            merged[held_item] = patched
    return merged


def _semantic_repair_checkpoint(
    *,
    failed_step_num: int | None,
    todo_steps: list,
    prefix_steps: list,
    validated_steps: list,
    trajectory_records: list[dict[str, Any]],
    sandbox_start_env: dict[str, Any],
    sandbox_start_robot: dict[str, Any],
    repair_base_env: dict[str, Any],
    repair_base_robot: dict[str, Any],
) -> tuple[list, dict, dict, dict]:
    """语义审计失败后，挑选一个“回退到哪一步”的修复 checkpoint。
    优先级：失败步之前已验证前缀 -> 回退到上轮 base -> 回退到 trajectory 中对应记录 -> 回退到沙盒起点。"""
    if failed_step_num is None:
        return [], sandbox_start_env, sandbox_start_robot, {}

    prefix_count = max(0, min(failed_step_num - 1, len(validated_steps)))
    repair_validated_steps = copy.deepcopy(validated_steps[:prefix_count])
    failed_step = _step_by_number(todo_steps, failed_step_num)

    if prefix_count == 0:
        return repair_validated_steps, sandbox_start_env, sandbox_start_robot, failed_step

    base_prefix_count = len(prefix_steps)
    if prefix_count <= base_prefix_count:
        return repair_validated_steps, repair_base_env, repair_base_robot, failed_step

    record_index = prefix_count - base_prefix_count - 1
    if 0 <= record_index < len(trajectory_records):
        record = trajectory_records[record_index]
        return (
            repair_validated_steps,
            copy.deepcopy(record.get("after_env", {})),
            copy.deepcopy(record.get("after_robot", {})),
            failed_step,
        )

    return repair_validated_steps, repair_base_env, repair_base_robot, failed_step


def _explicit_goal_test(structured_task: dict | None):
    """只在任务显式声明了 goal_state/desired_state/target_state 时，构造一个
    “env+robot 是否满足目标”的谓词，交给选中的修复策略用于成功判定。"""
    if not isinstance(structured_task, dict):
        return None
    if not any(structured_task.get(key) for key in ("goal_state", "desired_state", "target_state")):
        return None

    from domain.goal import goal_state_satisfied

    def goal_test(env, robot):
        return goal_state_satisfied(structured_task, env, robot) is True

    goal_test.completion_source = "explicit_goal"
    return goal_test


def _state_path_parts(path: Any) -> tuple[str, str] | None:
    """解析形如 "<entity>.states.<state_key>.xxx" 的状态路径，
    返回 (entity, state_key) 供可逆状态修复定位使用。"""
    text = str(path or "")
    marker = ".states."
    if marker not in text:
        return None
    entity, state_key = text.split(marker, 1)
    entity = entity.strip()
    state_key = state_key.strip().split(".", 1)[0]
    if not entity or not state_key:
        return None
    return entity, state_key


__all__ = [
    "_reindex_todo_steps",
    "_step_number",
    "_step_by_number",
    "_apply_checkpoint_env",
    "_semantic_repair_checkpoint",
    "_explicit_goal_test",
    "_state_path_parts",
]
