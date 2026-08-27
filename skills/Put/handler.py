from skills.base import ValidationResult


class PutSkill:
    name = "Put"

    def validate(self, sim_env: dict, sim_robot: dict, params: dict) -> ValidationResult:
        robot_loc = sim_robot["robot_location"]
        robot_hold = sim_robot["robot_holding"]
        target = params.get("target_item", "")
        dest = params.get("destination", "")
        if not target:
            return False, "参数缺失", "Put 缺少必填参数 target_item（待放置物品唯一ID）"
        if not dest:
            return False, "参数缺失", "Put 缺少必填参数 destination（目标放置节点唯一ID（如 砧板_1、冰箱_1））"
        if target not in sim_env:
            return False, "目标不存在", f"环境中不存在 {target}"
        if dest not in sim_env:
            return False, "目标位置不存在", f"环境中不存在放置节点 {dest}"
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
        dest_states = sim_env.get(dest, {}).get("states", {})
        sim_env[target]["direct_relation"] = "inside" if "isOpen" in dest_states else "on"
        # 同步 full_path：目标新位置 = dest 的路径 + [dest]，避免可达性判断用陈旧路径
        dest_info = sim_env.get(dest, {}) if isinstance(sim_env, dict) else {}
        dest_path = list(dest_info.get("full_path", []) or []) if isinstance(dest_info, dict) else []
        sim_env[target]["full_path"] = dest_path + [dest]
