from skills.base import ValidationResult


def _is_inside(target: str, container: str, sim_env: dict) -> bool:
    current = target
    seen = set()
    while current in sim_env and current not in seen:
        seen.add(current)
        parent = sim_env[current].get("direct_parent", "")
        if parent == container:
            return True
        if parent in ("", "robot_hand", "未知环境"):
            return False
        current = parent
    return False


class _HeatCoolSkill:
    name = ""
    device_param = ""

    def validate(self, sim_env: dict, sim_robot: dict, params: dict) -> ValidationResult:
        robot_loc = sim_robot["robot_location"]
        robot_hold = sim_robot["robot_holding"]
        target = params.get("target_item", "")
        device = params.get(self.device_param, "")

        if not target:
            return False, "参数缺失", "Cool 缺少必填参数 target_item（待冷却物品唯一ID）"
        if not device:
            return False, "参数缺失", "Cool 缺少必填参数 cooling_device（制冷设备唯一ID（如 冰箱_1））"
        if target not in sim_env:
            return False, "目标不存在", f"环境中不存在 {target}"
        if device not in sim_env:
            return False, "设备不存在", f"环境中不存在制冷设备 {device}"
        if robot_loc != device:
            return False, "前置位置依赖未满足", f"必须先导航至设施 {device}"
        if robot_hold != "空":
            return False, "单臂约束违规", "按键操作须保持空手"
        if not _is_inside(target, device, sim_env):
            return False, "容器依赖未满足", f"物品需存放于 {device} 内部"
        if sim_env.get(device, {}).get("states", {}).get("isOpen", True) is True:
            return False, "安全约束违规", "该设备舱门必须处于关闭状态"
        if sim_env.get(device, {}).get("states", {}).get("isToggled", False) is False:
            return False, "电源依赖未满足", "需调用 ToggleOn 开启该设备"
        if sim_env[target].get("states", {}).get("isCold") is not False:
            return False, "目标状态重复", f"{target} 必须处于 isCold: False 状态"
        return True, "", ""


class CoolSkill(_HeatCoolSkill):
    name = "Cool"
    device_param = "cooling_device"

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        target = params.get("target_item", "")
        sim_env[target].setdefault("states", {})["isCold"] = True
        sim_env[target].setdefault("states", {})["isCooked"] = False
