from skills.base import ValidationResult


class DrinkSkill:
    name = "Drink"

    def validate(self, sim_env: dict, sim_robot: dict, params: dict) -> ValidationResult:
        robot_loc = sim_robot["robot_location"]
        robot_hold = sim_robot["robot_holding"]
        target = params.get("target_item", "")
        if target not in sim_env:
            return False, "目标不存在", f"环境中不存在 {target}"
        direct_parent = sim_env.get(target, {}).get("direct_parent", "")
        if robot_hold != target and robot_loc not in (target, direct_parent):
            return False, "前置状态未满足", f"必须先持有或靠近 {target}"
        return True, "", ""

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        target = params.get("target_item", "")
        sim_env[target].setdefault("states", {})["isConsumed"] = True
        sim_robot["last_drunk"] = target
