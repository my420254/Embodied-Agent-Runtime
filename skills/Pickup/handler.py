from domain.scene import can_reach_item_from_location, is_item_accessible
from skills.base import ValidationResult


class PickupSkill:
    name = "Pickup"

    def validate(self, sim_env: dict, sim_robot: dict, params: dict) -> ValidationResult:
        robot_loc = sim_robot["robot_location"]
        robot_hold = sim_robot["robot_holding"]
        target = params.get("target_item", "")
        direct_parent = sim_env.get(target, {}).get("direct_parent", "")
        if not can_reach_item_from_location(target, robot_loc, sim_env):
            return False, "前置位置依赖未满足", f"目标在 {direct_parent}，需先导航至直接位置或其可交互父级节点"
        if robot_hold != "空":
            return False, "机械臂冲突", "当前机械臂处于占用状态，需先执行 Put"
        if not is_item_accessible(target, sim_env):
            return False, "物理可达性受限", f"容器 {direct_parent} 未打开，需先执行 Open"
        return True, "", ""

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        target = params.get("target_item", "")
        sim_robot["robot_holding"] = target
        sim_env[target]["direct_parent"] = "robot_hand"
