from skills.base import ValidationResult


class _OpenCloseSkill:
    name = ""
    target_open_state = False

    def validate(self, sim_env: dict, sim_robot: dict, params: dict) -> ValidationResult:
        robot_loc = sim_robot["robot_location"]
        robot_hold = sim_robot["robot_holding"]
        target = params.get("target_container", "")
        if robot_loc != target:
            return False, "前置位置依赖未满足", f"必须先导航至 {target}"
        if robot_hold != "空":
            return False, "单臂约束违规", "开/关容器时必须保持空手"
        return True, "", ""

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        target = params.get("target_container", "")
        sim_env[target].setdefault("states", {})["isOpen"] = self.target_open_state


class OpenSkill(_OpenCloseSkill):
    name = "Open"
    target_open_state = True
