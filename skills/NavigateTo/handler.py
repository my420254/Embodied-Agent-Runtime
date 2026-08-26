from domain.scene import is_room_level_node
from skills.base import ValidationResult


class NavigateToSkill:
    name = "NavigateTo"

    def validate(self, sim_env: dict, sim_robot: dict, params: dict) -> ValidationResult:
        target = params.get("target_location", "")
        if target not in sim_env:
            return False, f"无效的导航节点 '{target}'", "导航目标必须属于合法的环境节点"
        if is_room_level_node(target, sim_env):
            return False, f"无效的泛区域导航 '{target}'", "NavigateTo 目标必须是具体交互节点，不能是房间级泛区域"
        return True, "", ""

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        sim_robot["robot_location"] = params.get("target_location", "")
