from skills.base import ValidationResult


class _OpenCloseSkill:
    name = ""
    target_open_state = False

    def validate(self, sim_env: dict, sim_robot: dict, params: dict) -> ValidationResult:
        robot_loc = sim_robot["robot_location"]
        robot_hold = sim_robot["robot_holding"]
        target = params.get("target_container", "")
        if not target:
            return False, "参数缺失", "Open 缺少必填参数 target_container（目标容器唯一ID（如 冰箱_1））"
        if target not in sim_env:
            return False, "目标不存在", f"环境中不存在 {target}"
        states = sim_env[target].get("states", {})
        if "isOpen" not in states:
            return False, "容器属性不符", f"{target} 不具备 isOpen 属性"
        if states.get("isOpen") is self.target_open_state:
            state_name = "打开" if self.target_open_state else "关闭"
            return False, "目标状态重复", f"{target} 已经处于{state_name}状态"
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
