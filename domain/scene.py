from __future__ import annotations

import copy
from typing import Any

from config.scene_state import load_scene

# 定义一个常量 IGNORED_SCENE_KEYS，包含在场景树中需要忽略的键。这些键通常用于描述场景节点的状态、类型、位置等信息，而不是实体名称，因此在收集实体名称时需要跳过它们。
IGNORED_SCENE_KEYS = {
    "states",
    "type",
    "direct_relation",
    "robot_location",
    "scene_name",
    "robot_inventory",
}

# 这个函数 walk_entity_names 用于递归地收集场景树中的所有实体名称，以供理解层进行名称白名单校验。函数接受一个字典类型的场景数据作为输入，并返回一个包含所有实体名称的集合。
def walk_entity_names(scene_data: dict) -> set:
    names = set()

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "robot_holding_items" and isinstance(value, dict):
                    walk(value)
                    continue
                if key not in ("environment", "contains", *IGNORED_SCENE_KEYS):
                    names.add(key)
                if key in IGNORED_SCENE_KEYS:
                    continue
                if isinstance(value, dict):
                    walk(value)

    walk(scene_data)
    return names


def _require_scene_file(scene_file: str | None) -> str:
    if not scene_file:
        raise ValueError("scene_file is required; pass request-level scene data for benchmark runs")
    return scene_file


def get_all_entity_names(scene_file: str | None = None) -> set:
    """从指定场景文件加载所有实体名称。"""
    return walk_entity_names(load_scene(_require_scene_file(scene_file), fallback={}))


def get_all_entity_names_from_scene_data(scene_data: dict | None) -> set:
    """直接从内存中的场景数据收集实体名称。"""
    if not isinstance(scene_data, dict):
        return set()
    return walk_entity_names(scene_data)


def flatten_scene(scene_data: dict) -> dict[str, dict[str, Any]]:
    """把嵌套场景树压平成 {实体名 -> 实体信息} 的扁平索引。"""
    flat_house = {}

    def build_flat(node, path=None, *, in_environment=False):
        if path is None:
            path = []
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "robot_holding_items" and isinstance(value, dict):
                    for held_name, held_value in value.items():
                        if not isinstance(held_value, dict):
                            continue
                        flat_house[held_name] = {
                            "direct_parent": "robot_hand",
                            "direct_relation": held_value.get("direct_relation"),
                            "type": held_value.get("type"),
                            "states": copy.deepcopy(held_value.get("states", {})),
                            "properties": copy.deepcopy(held_value.get("properties", [])),
                            "is_container": "contains" in held_value or held_value.get("type") == "receptacle",
                            "full_path": [],
                        }
                        if "contains" in held_value:
                            build_flat(held_value["contains"], [held_name])
                    continue
                if key in IGNORED_SCENE_KEYS:
                    continue
                if key == "environment" and isinstance(value, dict):
                    build_flat(value, path, in_environment=True)
                    continue
                if key == "contains" and isinstance(value, dict):
                    build_flat(value, path)
                    continue
                if isinstance(value, dict):
                    direct_parent = path[-1] if len(path) > 0 else "未知环境"
                    direct_relation = value.get("direct_relation")
                    if direct_relation in {None, ""} and path:
                        direct_relation = "inside"
                    is_room_root = in_environment and not path
                    flat_house[key] = {
                        "direct_parent": direct_parent,
                        "direct_relation": direct_relation,
                        "type": "room" if is_room_root else value.get("type"),
                        "states": copy.deepcopy(value.get("states", {})),
                        "properties": copy.deepcopy(value.get("properties", [])),
                        "is_container": False if is_room_root else ("contains" in value or value.get("type") == "receptacle"),
                        "full_path": list(path),
                    }
                    if "contains" in value:
                        build_flat(value["contains"], path + [key])

    build_flat(scene_data)
    return flat_house


def get_full_flat_scene(scene_file: str | None = None) -> dict:
    """直接返回场景文件对应的扁平场景索引。"""
    return flatten_scene(load_scene(_require_scene_file(scene_file), fallback={}))


def _resolve_items_from_flat_scene(flat_house: dict, item_name_keywords: list) -> dict:
    resolved = {}
    parents_to_add = set()

    for keyword in item_name_keywords:
        for entity_name, entity_info in flat_house.items():
            if keyword in entity_name or entity_name in keyword:
                resolved[entity_name] = entity_info
                parents_to_add.update(entity_info["full_path"])

    for parent in parents_to_add:
        if parent in flat_house and parent not in resolved:
            resolved[parent] = flat_house[parent]

    return resolved


def resolve_items_from_scene(item_name_keywords: list, scene_file: str | None = None) -> dict:
    """按关键词从场景中解析相关实体，并补齐它们的父级上下文节点。"""
    flat_house = get_full_flat_scene(_require_scene_file(scene_file))
    return _resolve_items_from_flat_scene(flat_house, item_name_keywords)


def resolve_items_from_scene_data(item_name_keywords: list, scene_data: dict | None) -> dict:
    """按关键词从内存场景中解析相关实体，并补齐父级上下文。"""
    if not isinstance(scene_data, dict):
        return {}
    flat_house = flatten_scene(scene_data)
    return _resolve_items_from_flat_scene(flat_house, item_name_keywords)


def flat_scene_to_tree(flat_house: dict, robot_state: dict, base_scene_file: str | None = None) -> dict:
    """把扁平场景索引重新组装回嵌套场景树，并写入机器人当前状态。"""
    scene = load_scene(_require_scene_file(base_scene_file), fallback={})
    return flat_scene_to_tree_from_base(flat_house, robot_state, scene)


def flat_scene_to_tree_from_base(flat_house: dict, robot_state: dict, scene: dict) -> dict:
    """基于给定 scene 副本重建场景树，避免回写时误切到其他 session。"""
    scene = copy.deepcopy(scene)
    scene["robot_location"] = robot_state.get("robot_location", scene.get("robot_location"))
    if isinstance(robot_state.get("robot_hands"), dict):
        held_items = [value for value in robot_state["robot_hands"].values() if value not in {"", "空", None}]
        scene["robot_inventory"] = held_items[0] if len(held_items) == 1 else None
    else:
        scene["robot_inventory"] = None if robot_state.get("robot_holding") == "空" else robot_state.get("robot_holding")
    scene["robot_holding_items"] = {}

    env_root = scene.get("environment", {})
    for room in env_root.values():
        if isinstance(room, dict):
            room["contains"] = {}

    nodes = {
        name: {
            "type": info.get("type"),
            "direct_relation": info.get("direct_relation"),
            "states": copy.deepcopy(info.get("states", {})),
            "properties": copy.deepcopy(info.get("properties", [])),
            "contains": {},
        }
        for name, info in flat_house.items()
    }

    for name, info in flat_house.items():
        if info.get("direct_parent") == "未知环境" and not info.get("full_path"):
            continue
        node = nodes[name]
        if not node.get("type"):
            node.pop("type", None)
        if not node.get("direct_relation"):
            node.pop("direct_relation", None)
        parent = info.get("direct_parent", "")
        if parent == "robot_hand":
            scene["robot_holding_items"][name] = node
        elif parent in nodes and not is_room_level_node(parent, flat_house):
            nodes[parent].setdefault("contains", {})[name] = node
        else:
            full_path = info.get("full_path", [])
            room_name = parent if parent in env_root else (full_path[0] if full_path else parent)
            room = env_root.get(room_name)
            if isinstance(room, dict):
                room.setdefault("contains", {})[name] = node

    return scene


def is_room_level_node(node_name: str, flat_house: dict) -> bool:
    """判断一个节点是否只是房间级泛区域，而不是可直接交互的目标点。"""
    info = flat_house.get(node_name, {})
    return info.get("direct_parent") == "未知环境" and not info.get("full_path")


def is_item_accessible(item_name: str, sim_env: dict) -> bool:
    """沿父节点向上检查容器开闭状态，判断目标物体当前是否物理可达。"""
    current = item_name
    while current in sim_env:
        parent = sim_env[current].get("direct_parent", "")
        if parent in ("robot_hand", "未知环境", ""):
            break

        parent_states = sim_env.get(parent, {}).get("states", {})
        if parent_states.get("isOpen") is False:
            return False
        current = parent
    return True


def can_reach_item_from_location(item_name: str, robot_location: str, sim_env: dict) -> bool:
    """判断机器人当前位置是否能直接交互该目标或其直接交互父级。"""
    if item_name not in sim_env:
        return False
    if robot_location == item_name:
        return True

    info = sim_env.get(item_name, {})
    parent = str(info.get("direct_parent", "") or "")
    if robot_location == parent:
        return True

    full_path = [str(part) for part in (info.get("full_path", []) or []) if str(part)]
    if robot_location in full_path:
        return True

    # 允许在目标的直接交互父级锚点处交互
    if full_path and robot_location == full_path[-1]:
        return True
    return False
