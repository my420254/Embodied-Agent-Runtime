from skills.base import ValidationResult


class SleepSkill:
    name = "Sleep"

    def validate(self, sim_env: dict, sim_robot: dict, params: dict) -> ValidationResult:
        robot_loc = sim_robot["robot_location"]
        target = params.get("target_bed", "")
        if target not in sim_env:
            return False, "目标不存在", f"环境中不存在 {target}"
        direct_parent = sim_env.get(target, {}).get("direct_parent", "")
        if robot_loc not in (target, direct_parent):
            return False, "前置位置依赖未满足", f"必须先导航至 {target} 或其所在交互节点"
        return True, "", ""

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        target = params.get("target_bed", "")
        sim_robot["robot_location"] = target or sim_robot.get("robot_location", "")
        sim_robot["posture"] = "sleeping"
        sim_robot["last_sleep_target"] = target
