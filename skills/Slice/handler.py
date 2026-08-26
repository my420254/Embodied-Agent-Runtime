from skills.base import ValidationResult


class SliceSkill:
    name = "Slice"

    def validate(self, sim_env: dict, sim_robot: dict, params: dict) -> ValidationResult:
        robot_loc = sim_robot["robot_location"]
        robot_hold = sim_robot["robot_holding"]
        target = params.get("target_item", "")
        surface = params.get("surface", "")
        if robot_loc != surface:
            return False, "前置位置依赖未满足", f"必须先导航至表面节点 {surface}"
        if robot_hold == "空":
            return False, "工具依赖未满足", "需持有对应切割工具"

        tool_states = sim_env.get(robot_hold, {}).get("states", {})
        if tool_states.get("isBroken", False):
            return False, "工具状态受限", "当前工具已损坏，请请求备用工具"
        if not tool_states.get("isSharp", True):
            return False, "工具状态受限", "当前工具不具备锋利属性"
        if sim_env.get(target, {}).get("direct_parent") != surface:
            return False, "空间干涉", f"食材必须被安置在 {surface} 表面才能切割"
        if sim_env.get(target, {}).get("states", {}).get("isClean") is not True:
            return False, "卫生前置约束未满足", f"{target} 在切割前必须先执行 Clean"
        return True, "", ""

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        robot_hold = sim_robot["robot_holding"]
        target = params.get("target_item", "")
        sim_env[target].setdefault("states", {})["isSliced"] = True
        sim_env[robot_hold].setdefault("states", {})["isDirty"] = True
        sim_env[robot_hold].setdefault("states", {})["isClean"] = False

