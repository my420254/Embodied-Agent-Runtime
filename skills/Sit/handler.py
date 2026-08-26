from skills.base import ValidationResult


class SitSkill:
    name = "Sit"

    def validate(self, sim_env: dict, sim_robot: dict, params: dict) -> ValidationResult:
        robot_loc = sim_robot["robot_location"]
        target = params.get("target_seat", "")
        if target not in sim_env:
            return False, "目标不存在", f"环境中不存在 {target}"
        target_info = sim_env.get(target, {})
        allowed_locations = {
            str(target),
            str(target_info.get("direct_parent") or ""),
        }
        allowed_locations.discard("")
        if robot_loc not in allowed_locations:
            return False, "前置位置依赖未满足", f"必须先导航至 {target} 或其可交互位置"
        if target_info.get("states", {}).get("seatable") is False:
            return False, "目标不可坐", f"{target} 当前不可坐"
        return True, "", ""

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        target = params.get("target_seat", "")
        sim_robot["robot_location"] = target or sim_robot.get("robot_location", "")
        sim_robot["posture"] = "sitting"
        sim_robot["last_seat"] = target
