from skills.base import ValidationResult


class ReadSkill:
    name = "Read"

    def validate(self, sim_env: dict, sim_robot: dict, params: dict) -> ValidationResult:
        robot_loc = sim_robot["robot_location"]
        robot_hold = sim_robot["robot_holding"]
        target = params.get("target_item", "")
        if target not in sim_env:
            return False, "目标不存在", f"环境中不存在 {target}"
        direct_parent = sim_env.get(target, {}).get("direct_parent", "")
        if robot_hold != target and robot_loc not in (target, direct_parent):
            return False, "前置位置依赖未满足", f"必须先靠近或持有 {target}"
        return True, "", ""

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        sim_robot["last_read"] = params.get("target_item", "")
