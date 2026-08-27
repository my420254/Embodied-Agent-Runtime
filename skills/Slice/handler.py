from skills.base import ValidationResult


class SliceSkill:
    name = "Slice"

    def validate(self, sim_env: dict, sim_robot: dict, params: dict) -> ValidationResult:
        robot_loc = sim_robot["robot_location"]
        robot_hold = sim_robot["robot_holding"]
        target = params.get("target_item", "")
        surface = params.get("surface", "")
        if not target:
            return False, "参数缺失", "Slice 缺少必填参数 target_item（待切割食材唯一ID）"
        if not surface:
            return False, "参数缺失", "Slice 缺少必填参数 surface（切割表面节点唯一ID（如 厨房操作台_1））"
        if target not in sim_env:
            return False, "目标不存在", f"环境中不存在 {target}"
        if surface not in sim_env:
            return False, "切割表面不存在", f"环境中不存在切割表面 {surface}"
        if robot_loc != surface:
            return False, "前置位置依赖未满足", f"必须先导航至表面节点 {surface}"
        if robot_hold == "空":
            return False, "工具依赖未满足", "需持有对应切割工具"
        if robot_hold not in sim_env:
            return False, "工具不存在", f"环境中不存在当前手持工具 {robot_hold}"

        tool_states = sim_env.get(robot_hold, {}).get("states", {})
        if tool_states.get("isBroken") is not False:
            return False, "工具状态受限", "当前工具已损坏，请请求备用工具"
        if tool_states.get("isSharp") is not True:
            return False, "工具状态受限", "当前工具不具备锋利属性"
        if sim_env.get(target, {}).get("direct_parent") != surface:
            return False, "空间干涉", f"食材必须被安置在 {surface} 表面才能切割"
        if sim_env.get(target, {}).get("states", {}).get("isClean") is not True:
            return False, "卫生前置约束未满足", f"{target} 在切割前必须先执行 Clean"
        if sim_env[target].get("states", {}).get("isSliced") is not False:
            return False, "目标状态重复", f"{target} 必须处于 isSliced: False 状态"
        return True, "", ""

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        robot_hold = sim_robot["robot_holding"]
        target = params.get("target_item", "")
        sim_env[target].setdefault("states", {})["isSliced"] = True
        sim_env[robot_hold].setdefault("states", {})["isDirty"] = True
        sim_env[robot_hold].setdefault("states", {})["isClean"] = False
