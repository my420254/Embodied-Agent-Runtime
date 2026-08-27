from skills.base import ValidationResult


class CleanSkill:
    name = "Clean"

    def validate(self, sim_env: dict, sim_robot: dict, params: dict) -> ValidationResult:
        robot_loc = sim_robot["robot_location"]
        target = params.get("target_item", "")
        water_source = params.get("water_source", "")
        if not target:
            return False, "参数缺失", "Clean 缺少必填参数 target_item（待清洗物品唯一ID）"
        if not water_source:
            return False, "参数缺失", "Clean 缺少必填参数 water_source（水源设施唯一ID（如 水槽_1））"
        if target not in sim_env:
            return False, "目标不存在", f"环境中不存在 {target}"
        if water_source not in sim_env:
            return False, "水源不存在", f"环境中不存在水源设施 {water_source}"
        if robot_loc != water_source:
            return False, "前置位置依赖未满足", f"必须导航至相关水设施 {water_source}"

        water_source_states = sim_env.get(water_source, {}).get("states", {})
        if "isFilledWithLiquid" not in water_source_states and "水槽" not in water_source:
            return False, "设施属性不符", "该节点无清洗或液源相关属性"

        item_parent = sim_env.get(target, {}).get("direct_parent", "")
        if item_parent != "robot_hand" and item_parent != water_source:
            return False, "距离干涉", "目标物品必须处于手持或置入水池状态"
        target_states = sim_env[target].get("states", {})
        if target_states.get("isClean") is True and not target_states.get("isDirty", False):
            return False, "目标状态重复", f"{target} 已经处于清洁状态"
        return True, "", ""

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        target = params.get("target_item", "")
        sim_env[target].setdefault("states", {})["isClean"] = True
        sim_env[target].setdefault("states", {})["isDirty"] = False
