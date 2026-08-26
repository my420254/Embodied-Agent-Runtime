from skills.base import ValidationResult


class _ToggleSkill:
    name = ""
    target_toggle_state = False

    def validate(self, sim_env: dict, sim_robot: dict, params: dict) -> ValidationResult:
        robot_loc = sim_robot["robot_location"]
        robot_hold = sim_robot["robot_holding"]
        target = params.get("target_device", "")
        if robot_loc != target:
            return False, "前置位置依赖未满足", f"必须导航至 {target}"
        if robot_hold != "空":
            return False, "单臂约束违规", "拨动开关需保持空手操作"
        return True, "", ""

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        target = params.get("target_device", "")
        sim_env[target].setdefault("states", {})["isToggled"] = self.target_toggle_state


class ToggleOnSkill(_ToggleSkill):
    name = "ToggleOn"
    target_toggle_state = True
