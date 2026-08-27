from skills.base import ValidationResult


class _ToggleSkill:
    name = ""
    target_toggle_state = False

    def validate(self, sim_env: dict, sim_robot: dict, params: dict) -> ValidationResult:
        robot_loc = sim_robot["robot_location"]
        robot_hold = sim_robot["robot_holding"]
        target = params.get("target_device", "")
        if not target:
            return False, "参数缺失", "ToggleOff 缺少必填参数 target_device（目标设备唯一ID（如 微波炉_1））"
        if target not in sim_env:
            return False, "目标不存在", f"环境中不存在 {target}"
        states = sim_env[target].get("states", {})
        if "isToggled" not in states:
            return False, "设备属性不符", f"{target} 不具备 isToggled 属性"
        if states.get("isToggled") is self.target_toggle_state:
            state_name = "开启" if self.target_toggle_state else "关闭"
            return False, "目标状态重复", f"{target} 已经处于{state_name}状态"
        if robot_loc != target:
            return False, "前置位置依赖未满足", f"必须导航至 {target}"
        if robot_hold != "空":
            return False, "单臂约束违规", "拨动开关需保持空手操作"
        return True, "", ""

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        target = params.get("target_device", "")
        sim_env[target].setdefault("states", {})["isToggled"] = self.target_toggle_state


class ToggleOffSkill(_ToggleSkill):
    name = "ToggleOff"
    target_toggle_state = False
