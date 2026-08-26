from config.scene_state import get_runtime_session
from domain.actions import extract_action, summarize_action_targets
from domain.scene import flatten_scene


def get_item_info_from_house(target_item: str) -> dict:
    try:
        flat_scene = flatten_scene(get_runtime_session())
        info = flat_scene.get(target_item)
        if not info:
            return {"found": False}
        return {
            "found": True,
            "exact_name": target_item,
            "direct_parent": info.get("direct_parent", ""),
            "states": info.get("states", {}),
        }
    except Exception as e:
        return {"found": False, "error": str(e)}


def resolve_action_target(item) -> tuple[str, dict, str, str, str]:
    act_name, params, action_str = extract_action(item)
    target, location = summarize_action_targets(params)
    if target:
        info = get_item_info_from_house(target)
        if info.get("found"):
            target = info["exact_name"]
    return act_name, params, action_str, target, location


def apply_env_delta(env: dict, act_name: str, target: str, location: str, action_str: str) -> None:
    if act_name == "NavigateTo":
        env["robot_location"] = target
    elif act_name == "Pickup":
        if env.get("robot_holding") != "空":
            print(f" [系统警告] 单手容量冲突！原持有: [{env['robot_holding']}]，强制覆盖为: [{target}]")
        env["robot_holding"] = target
    elif act_name == "Put":
        env["robot_holding"] = "空"
        env["changed_objects"][target] = f"已放入 [{location}]"
    elif act_name == "Open":
        env["changed_objects"][target] = "isOpen: True"
    elif act_name == "Close":
        env["changed_objects"][target] = "isOpen: False"
    elif act_name == "ToggleOn":
        env["changed_objects"][target] = "isToggled: True"
    elif act_name == "ToggleOff":
        env["changed_objects"][target] = "isToggled: False"
    elif act_name == "Slice":
        env["changed_objects"][target] = "isSliced: True"
    elif act_name == "Heat":
        env["changed_objects"][target] = "isCooked: True"
    elif act_name == "Cool":
        env["changed_objects"][target] = "isCold: True"
    elif act_name == "Clean":
        env["changed_objects"][target] = "isClean: True"
    elif act_name == "Read":
        env["last_read"] = target
    elif act_name == "Observe":
        env["last_observed"] = target
    elif act_name == "Type":
        env["last_typed_on"] = target
    elif act_name == "Touch":
        env["last_touched"] = target
    elif act_name == "Drink":
        env["last_drunk"] = target
        env["changed_objects"][target] = "isConsumed: True"
    elif act_name == "Sit":
        env["posture"] = "sitting"
        env["last_seat"] = target
    elif act_name == "Sleep":
        env["posture"] = "sleeping"
        env["last_sleep_target"] = target

    env["last_action"] = action_str


def print_execution_trace(action_str: str, env: dict, remaining: int, total_remaining: int) -> None:
    print(f"\n[物理执行] {action_str}")
    print(f"[环境状态] 位置: {env['robot_location']}  |  手持: {env['robot_holding']}")
    if env["changed_objects"]:
        changes = " | ".join(f"{key} -> {value}" for key, value in env["changed_objects"].items())
        print(f"[状态突变] {changes}")
    if total_remaining > 0:
        print(f"[进度]     当前任务剩余 {remaining} 步 | 全局剩余 {total_remaining} 步")
    print("-" * 60)
