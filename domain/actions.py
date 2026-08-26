# 这个模块定义了与动作相关的函数，用于从输入数据中提取动作信息，并确保动作数据具有正确的结构。
ACTION_DOMAINS = {
    "NavigateTo": "底盘控制",
    "Pickup": "机械臂控制",
    "Put": "机械臂控制",
    "Open": "机械臂控制",
    "Close": "机械臂控制",
    "Clean": "机械臂控制",
    "Slice": "机械臂控制",
    "ToggleOn": "机械臂控制",
    "ToggleOff": "机械臂控制",
    "Heat": "机械臂控制",
    "Cool": "机械臂控制",
    "Observe": "感知/信息交互",
    "Read": "感知/信息交互",
    "Type": "感知/信息交互",
    "Drink": "机械臂控制",
    "Sit": "底盘控制",
    "Sleep": "底盘控制",
    "Touch": "感知/信息交互",
}


def summarize_action_targets(params: dict) -> tuple[str, str]:
    target = ""
    location = ""
    for key in ("target_item", "target_object", "target_device", "target_container", "target_location", "target_bed", "target_seat"):
        if params.get(key):
            target = str(params[key])
            break
    for key in ("destination", "target_location", "target_container", "target_bed", "target_seat"):
        if params.get(key):
            location = str(params[key])
            break
    return target, location
def format_action_call(act_name: str, params: dict) -> str:
    if not params:
        return f"{act_name}()"
    args = ", ".join(f"{k}={v}" for k, v in params.items())
    return f"{act_name}({args})"

# 从输入数据中提取动作名称、参数和格式化的动作调用字符串。
def extract_action(item) -> tuple[str, dict, str]:
    if isinstance(item, dict) and isinstance(item.get("execution"), dict):
        execution = item["execution"]
        act_name = execution.get("skill", "")
        params = execution.get("parameters", {}) or {}
        return act_name, params, format_action_call(act_name, params)
    if isinstance(item, dict) and item.get("skill"):
        act_name = item.get("skill", "")
        params = item.get("parameters", {}) or {}
        return act_name, params, format_action_call(act_name, params)
    return "", {}, str(item)

# 确保输入的动作数据具有正确的结构，如果缺少 "execution" 字段，则根据提取的动作名称和参数构造一个新的 "execution" 字段。
def ensure_execution_shape(step: dict) -> dict:
    if not isinstance(step, dict):
        return {}
    act, params, _ = extract_action(step)
    if act and not step.get("execution"):
        step["execution"] = {"skill": act, "parameters": params}
    return step
