from __future__ import annotations

from copy import deepcopy

from config.scene_state import get_runtime_session, set_runtime_session
from domain.scene import flatten_scene, flat_scene_to_tree_from_base
from skills.registry import get_skill_handlers


def _robot_from_scene(scene_data: dict) -> dict:
    holding = scene_data.get("robot_inventory")
    return {
        "robot_location": scene_data.get("robot_location", "未知"),
        "robot_holding": holding if holding else "空",
    }


def apply_execution_to_scene(scene_data: dict, execution: dict) -> tuple[dict, bool, str]:
    act_name = str(execution.get("skill", ""))
    params = execution.get("parameters", {}) or {}
    if not act_name:
        return deepcopy(scene_data), False, "缺少 execution.skill"

    flat_env = flatten_scene(scene_data)
    sim_env = deepcopy(flat_env)
    sim_robot = _robot_from_scene(scene_data)

    handler = get_skill_handlers().get(act_name)
    if handler is None:
        return deepcopy(scene_data), False, f"技能 {act_name} 当前未启用或未定义"

    ok, issue, fix = handler.validate(sim_env, sim_robot, params)
    if not ok:
        detail = fix or issue or f"{act_name} 校验失败"
        return deepcopy(scene_data), False, detail

    handler.apply(sim_env, sim_robot, params)
    updated_scene = flat_scene_to_tree_from_base(sim_env, sim_robot, scene_data)
    return updated_scene, True, ""


def update_runtime_execution(execution: dict) -> tuple[bool, str]:
    updated_scene, ok, error = preview_runtime_execution(execution)
    if not ok:
        return False, error
    commit_runtime_scene(updated_scene)
    return True, ""


def preview_runtime_execution(execution: dict) -> tuple[dict, bool, str]:
    """Validate an action and compute its next scene without committing it."""
    return apply_execution_to_scene(get_runtime_session(), execution)


def commit_runtime_scene(scene_data: dict) -> None:
    """Commit a previewed scene only after the external action succeeds."""
    set_runtime_session(scene_data)


def update_runtime_scene(
    action_name: str,
    target: str = "",
    location: str = "",
    params: dict | None = None,
) -> tuple[bool, str]:
    """把一次执行动作同步进运行态场景。

    params 提供时优先透传完整原始参数（如 Slice 的 surface、Clean 的
    water_source、Heat 的 heat_source），避免重建参数时丢失；否则按
    action_name/target/location 重建最小参数集。
    """
    resolved_params = _merged_or_rebuilt_params(action_name, target, location, params)
    return update_runtime_execution({"skill": action_name, "parameters": resolved_params})


def preview_runtime_scene(
    action_name: str,
    target: str = "",
    location: str = "",
    params: dict | None = None,
) -> tuple[dict, bool, str]:
    resolved_params = _merged_or_rebuilt_params(action_name, target, location, params)
    return preview_runtime_execution({"skill": action_name, "parameters": resolved_params})


def _merged_or_rebuilt_params(
    action_name: str,
    target: str,
    location: str,
    params: dict | None,
) -> dict:
    if isinstance(params, dict) and params:
        merged = {
            str(key): value
            for key, value in params.items()
            if value not in (None, "", [])
        }
        if not any(k in merged for k in ("target_item", "target_object", "target_device", "target_container", "target_location", "target_bed", "target_seat")) and target:
            merged["target_item"] = target
        if not any(k in merged for k in ("destination", "target_location", "target_container", "target_bed", "target_seat")) and location:
            merged["destination"] = location
        return merged
    return _rebuilt_params(action_name, target, location)


def _rebuilt_params(action_name: str, target: str = "", location: str = "") -> dict[str, str]:
    params: dict[str, str] = {}
    if action_name == "NavigateTo":
        params["target_location"] = target or location
    elif action_name == "Pickup":
        params["target_item"] = target
    elif action_name == "Put":
        params["target_item"] = target
        if location:
            params["destination"] = location
    elif action_name in {"Open", "Close"}:
        params["target_container"] = target
    elif action_name in {"ToggleOn", "ToggleOff", "Type"}:
        params["target_device"] = target
    elif action_name in {"Slice", "Heat", "Clean", "Read", "Drink"}:
        params["target_item"] = target
    elif action_name in {"Observe", "Touch"}:
        params["target_object"] = target
    elif action_name == "Sit":
        params["target_seat"] = target or location
    elif action_name == "Sleep":
        params["target_bed"] = target or location
    else:
        if target:
            params["target_item"] = target
        if location:
            params.setdefault("destination", location)
    return params


def runtime_env_state() -> dict:
    return _robot_from_scene(get_runtime_session())
