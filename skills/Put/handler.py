from skills.base import ValidationResult


class PutSkill:
    name = "Put"

    def validate(self, sim_env: dict, sim_robot: dict, params: dict) -> ValidationResult:
        robot_loc = sim_robot["robot_location"]
        robot_hold = sim_robot["robot_holding"]
        target = params.get("target_item", "")
        dest = params.get("destination", "")
        if robot_loc != dest:
            return False, "前置位置依赖未满足", f"放置前必须导航至 {dest}"
        if robot_hold != target:
            return False, "手持物品不匹配", f"当前持有的是 {robot_hold}，无 {target} 可用"
        if sim_env.get(dest, {}).get("is_container") and sim_env[dest].get("states", {}).get("isOpen") is False:
            return False, "容器干涉拦截", "目标容器关闭，须先执行 Open"
        return True, "", ""

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        target = params.get("target_item", "")
        dest = params.get("destination", "")
        sim_robot["robot_holding"] = "空"
        sim_env[target]["direct_parent"] = dest

