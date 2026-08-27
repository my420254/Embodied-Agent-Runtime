from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from benchmark.task_environment_bridge import (
    PreparedTaskEnvironment,
    build_task_environment_closure,
    scene_entity_catalog,
)
from benchmark.delta.framework.code.pddl_plan_exporter import load_delta_problem_init_predicates

FAIR_SCENE_MODE = "full"
FULL_TASK_ENVIRONMENT_MODE = "full"
UNDERSTANDING_PRUNED_TASK_ENVIRONMENT_MODE = "understanding_pruned"


# DELTA 原仓库里有两个不同层级的环境信息：
#
# 1. scene_graph.py 里的完整 3D scene graph
#    这是论文任务真正发生的环境，应作为公平比较的默认输入。
# planning 阶段默认不是把完整 scene 全量塞回去，而是使用 understanding
# 输出的 required_item_names 从完整 scene 中精确取回相关实体的状态和位置。


def _delta_states(state: str | None) -> dict[str, Any]:
    state = (state or "").lower()
    states: dict[str, Any] = {}
    if "closed" in state:
        states["isOpen"] = False
    if "open" in state:
        states["isOpen"] = True
    if "off" in state:
        states["isToggled"] = False
    if "on" in state:
        states["isToggled"] = True
    if "clean" in state:
        states["isClean"] = True
        states["isDirty"] = False
    if "assembled" in state:
        states["isAssembled"] = True
    if "disposed" in state:
        states["isDisposed"] = True
    if "loaded" in state:
        states["isLoaded"] = True
    if "empty" in state:
        states["isEmpty"] = True
    return states


def _delta_node(name: str, item: dict[str, Any]) -> dict[str, Any]:
    """把 DELTA 物体节点转换成 OurAgent scene 节点。

    这里只翻译公开环境事实：状态、容器关系、可交互能力。
    不读取 subgoal / subgoal_pddl / gt_cost。
    """
    affordance = list(item.get("affordance", []))
    properties = {
        f"delta_accessible:{str(item.get('accessible', True) is not False).lower()}",
        *(f"delta_affordance:{str(value)}" for value in affordance),
    }
    node = {
        "properties": sorted(properties),
        "states": _delta_states(item.get("state")),
    }
    receptacle_affordances = {
        "open",
        "close",
        "dispose",
        "load",
        "unload",
        "charge",
    }
    if any(token in affordance for token in receptacle_affordances):
        node["type"] = "receptacle"
    content = item.get("content", {})
    if isinstance(content, dict) and content:
        node["type"] = "receptacle"
        node["contains"] = {
            child_name: _delta_node(child_name, child_item)
            for child_name, child_item in content.items()
        }
    return node


def _delta_agent_position(scene_graph: dict[str, Any], environment: dict[str, Any]) -> str:
    agent = scene_graph.get("agent", {})
    position = str((agent if isinstance(agent, dict) else {}).get("position") or "").strip()
    if position in environment:
        return position
    if "living_room" in environment:
        return "living_room"
    return next(iter(environment.keys()), "unknown_room")


def _delta_agent_state(scene_graph: dict[str, Any]) -> dict[str, Any]:
    agent = scene_graph.get("agent", {})
    state_text = str((agent if isinstance(agent, dict) else {}).get("state") or "").strip().lower()
    robot_state: dict[str, Any] = {}
    if state_text in {"battery-full", "battery_full", "battery full"}:
        robot_state["battery_full"] = True
        robot_state["battery"] = "full"
    elif state_text in {"battery-not-full", "battery_not_full", "battery-low", "battery_low", "battery empty"}:
        robot_state["battery_full"] = False
        robot_state["battery"] = "not_full"
    return robot_state


def _delta_room_neighbors(scene_graph: dict[str, Any]) -> dict[str, list[str]]:
    rooms = scene_graph.get("rooms", {})
    if not isinstance(rooms, dict):
        return {}
    return {
        str(room_name): [
            str(neighbor)
            for neighbor in (room.get("neighbor", []) or [])
            if str(neighbor).strip()
        ]
        for room_name, room in rooms.items()
        if str(room_name).strip() and isinstance(room, dict)
    }


def _find_scene_node(environment: dict[str, Any], name: str) -> dict[str, Any] | None:
    for node_name, node in environment.items():
        if node_name == name and isinstance(node, dict):
            return node
        contains = node.get("contains") if isinstance(node, dict) else None
        if isinstance(contains, dict):
            found = _find_scene_node(contains, name)
            if found is not None:
                return found
    return None


def _delta_initial_attribute_predicates(
    predicates: list[tuple[str, ...]],
) -> list[tuple[str, ...]]:
    allowed_prefixes = (
        "item_accessible",
        "item_pickable",
        "item_loadable",
        "item_empty",
        "item_disposed",
        "item_is_",
        "mop_clean",
        "floor_clean",
        "battery_full",
    )
    return [
        predicate
        for predicate in predicates
        if len(predicate) == 2 and predicate[0].startswith(allowed_prefixes)
    ]


def _merge_delta_initial_predicates(
    scene: dict[str, Any],
    predicates: list[tuple[str, ...]],
) -> None:
    environment = scene.get("environment", {})
    if not isinstance(environment, dict):
        return
    for predicate, *args in _delta_initial_attribute_predicates(predicates):
        if predicate == "battery_full":
            continue
        if not args:
            continue
        target = str(args[0])
        node = _find_scene_node(environment, target)
        if node is None:
            continue
        properties = node.setdefault("properties", [])
        if isinstance(properties, list) and f"delta_predicate:{predicate}" not in properties:
            properties.append(f"delta_predicate:{predicate}")
        if predicate in {"item_is_sink", "item_is_dining_table"}:
            node["type"] = "receptacle"
        states = node.setdefault("states", {})
        if predicate == "mop_clean":
            states["isClean"] = True
            states["isDirty"] = False
        elif predicate == "floor_clean":
            states["floor_clean"] = True
            states["isClean"] = True
        elif predicate == "item_disposed":
            states["isDisposed"] = True
        elif predicate == "item_empty":
            states["isEmpty"] = True
            states["isLoaded"] = False


def _apply_delta_robot_initial_state(
    scene: dict[str, Any],
    env_state: dict[str, Any],
    predicates: list[tuple[str, ...]],
) -> None:
    for predicate, *args in predicates:
        if not args:
            continue
        if predicate == "battery_full" and str(args[0]) == "robot":
            scene["robot_state"] = {**scene.get("robot_state", {}), "battery_full": True, "battery": "full"}
            env_state["battery_full"] = True
        elif predicate == "agent_at" and len(args) >= 2 and str(args[0]) == "robot":
            env_state["robot_location"] = str(args[1])


def build_delta_scene(
    scene_graph: dict[str, Any],
    instruction: str,
    *,
    case_input: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """把 DELTA scene_graph.py 的房间/物体结构转成 OurAgent scene。

    输入是 DELTA 原仓库发布的完整 scene graph。该函数不做任务分解，
    也不根据 goal 删除或新增物体。
    """
    environment = {}
    rooms = scene_graph.get("rooms", {})
    for room_name, room in rooms.items():
        contains = {}
        for item_name, item in room.get("items", {}).items():
            contains[item_name] = _delta_node(item_name, item)
        environment[room_name] = {"contains": contains}

    start_room = _delta_agent_position(scene_graph, environment)
    robot_state = _delta_agent_state(scene_graph)
    scene = {
        "environment": environment,
        "robot_location": start_room,
        "robot_inventory": None,
        "robot_holding_items": {},
        "scene_name": instruction,
    }
    if robot_state:
        scene["robot_state"] = robot_state
    return scene


def load_delta_scene_graph(case_input: dict[str, Any]) -> dict[str, Any]:
    scene_graph = case_input.get("scene_graph")
    if isinstance(scene_graph, dict) and "rooms" in scene_graph:
        return scene_graph
    cache_path = str(case_input.get("scene_graph_cache_path", "") or "").strip()
    if not cache_path:
        raise ValueError("DELTA framework case is missing scene_graph_cache_path")
    payload = json.loads(Path(cache_path).read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("scene_graph"), dict):
        return payload["scene_graph"]
    if isinstance(payload, dict) and isinstance(payload.get("rooms"), dict):
        return payload
    raise ValueError(f"DELTA scene graph cache must contain scene_graph: {cache_path}")


def delta_task_environment_mode(case_input: dict[str, Any]) -> str:
    mode = str(case_input.get("delta_task_environment_mode") or UNDERSTANDING_PRUNED_TASK_ENVIRONMENT_MODE)
    if mode not in {FULL_TASK_ENVIRONMENT_MODE, UNDERSTANDING_PRUNED_TASK_ENVIRONMENT_MODE}:
        raise ValueError(f"unsupported DELTA task environment mode: {mode}")
    return mode


def prepare_environment(
    case_input: dict[str, Any],
    *,
    scene: dict[str, Any] | None = None,
    env_state: dict[str, Any] | None = None,
) -> PreparedTaskEnvironment:
    instruction = str(case_input.get("instruction", ""))
    selected_graph = load_delta_scene_graph(case_input)
    resolved_scene = scene if isinstance(scene, dict) else build_delta_scene(
        selected_graph,
        instruction,
        case_input=case_input,
    )
    initial_predicates = load_delta_problem_init_predicates(case_input)
    _merge_delta_initial_predicates(resolved_scene, initial_predicates)
    if isinstance((env := env_state), dict):
        resolved_env_state = copy.deepcopy(env)
        resolved_env_state.setdefault("delta_room_neighbors", _delta_room_neighbors(selected_graph))
    else:
        resolved_env_state = {
            "robot_location": resolved_scene.get("robot_location", "未知"),
            "robot_holding": resolved_scene.get("robot_inventory") or "空",
            "delta_room_neighbors": _delta_room_neighbors(selected_graph),
        }
        robot_state = resolved_scene.get("robot_state")
        if isinstance(robot_state, dict):
            resolved_env_state.update(robot_state)
    resolved_env_state.setdefault("domain", str(case_input.get("domain") or "").strip().lower())
    resolved_env_state["delta_initial_predicates"] = [
        " ".join(predicate)
        for predicate in _delta_initial_attribute_predicates(initial_predicates)
    ]
    _apply_delta_robot_initial_state(resolved_scene, resolved_env_state, initial_predicates)
    return PreparedTaskEnvironment(
        instruction=instruction,
        scene=resolved_scene,
        env_state=resolved_env_state,
        entity_catalog=scene_entity_catalog(resolved_scene),
        context={
            "selected_graph": selected_graph,
            "task_context": {
                "dataset": "delta",
                "task_name": str(case_input.get("task_id", "")),
                "domain": str(case_input.get("domain", "")),
                "instruction": instruction,
                "task_source": str(case_input.get("task_source", "") or "delta_data_example_py"),
                "environment_source": str(case_input.get("environment_source", "") or "delta_data_scene_graph_py"),
                "scene_graph_cache_path": str(case_input.get("scene_graph_cache_path", "") or ""),
                "delta_add_obj_types": [str(value) for value in (case_input.get("add_obj") or []) if value],
                "delta_env_state_predicates": [str(value) for value in case_input.get("delta_env_state", []) if value],
                "delta_initial_predicates": [
                    " ".join(predicate)
                    for predicate in _delta_initial_attribute_predicates(initial_predicates)
                ],
                "delta_room_neighbors": _delta_room_neighbors(selected_graph),
                "delta_accessible_items": _delta_accessible_item_names(selected_graph),
                "loadable_containers": _loadable_container_summary(selected_graph),
                "task_environment_mode": delta_task_environment_mode(case_input),
            },
        },
        task_environment_module=__name__,
    )


def _filter_name_bucket(bucket: Any, valid_names: set[str]) -> dict[str, list[str]]:
    if isinstance(bucket, dict):
        primary = bucket.get("primary", [])
        alternatives = bucket.get("alternatives", [])
    elif isinstance(bucket, list):
        primary = bucket
        alternatives = []
    else:
        primary = []
        alternatives = []
    return {
        "primary": [str(name) for name in primary if str(name) in valid_names],
        "alternatives": [str(name) for name in alternatives if str(name) in valid_names],
    }


def _filter_required_item_names(required_item_names: Any, valid_names: set[str]) -> dict[str, Any]:
    names = required_item_names if isinstance(required_item_names, dict) else {}
    return {
        "targets": _filter_name_bucket(names.get("targets"), valid_names),
        "tools": _filter_name_bucket(names.get("tools"), valid_names),
        "receptacles": _filter_name_bucket(names.get("receptacles"), valid_names),
    }


def _is_room_entry(info: Any) -> bool:
    if not isinstance(info, dict):
        return False
    if str(info.get("type") or "").strip().lower() == "room":
        return True
    return str(info.get("direct_parent") or "").strip() == "未知环境" and not info.get("full_path")


def _mentioned_room_names(structured_task: dict[str, Any], room_names: set[str]) -> list[str]:
    text_parts = [
        str(structured_task.get("intent") or ""),
    ]
    goal_state = structured_task.get("goal_state")
    if isinstance(goal_state, dict):
        text_parts.append(json.dumps(goal_state, ensure_ascii=False))
    text = " ".join(text_parts).lower()

    mentioned: list[str] = []
    for name in sorted(room_names):
        lowered = name.lower()
        spaced = lowered.replace("_", " ")
        if lowered in text:
            mentioned.append(name)
            continue
        if spaced != lowered and re.search(rf"(?<![a-z0-9]){re.escape(spaced)}(?![a-z0-9])", text):
            mentioned.append(name)
    return mentioned


def _preserve_mentioned_rooms(structured_task: dict[str, Any], room_names: set[str]) -> None:
    mentioned = _mentioned_room_names(structured_task, room_names)
    if not mentioned:
        return
    required = structured_task.get("required_item_names")
    if not isinstance(required, dict):
        required = {}
        structured_task["required_item_names"] = required
    receptacles = required.get("receptacles")
    if not isinstance(receptacles, dict):
        receptacles = {"primary": [], "alternatives": []}
        required["receptacles"] = receptacles
    primary = receptacles.get("primary")
    if not isinstance(primary, list):
        primary = []
    for room_name in mentioned:
        if room_name not in primary:
            primary.append(room_name)
    receptacles["primary"] = primary


def _iter_delta_scene_items(scene_graph: dict[str, Any]):
    for room_name, room in scene_graph.get("rooms", {}).items():
        items = room.get("items", {})
        if not isinstance(items, dict):
            continue
        stack = list(items.items())
        while stack:
            item_name, item = stack.pop(0)
            if isinstance(item, dict):
                yield str(room_name), str(item_name), item
                content = item.get("content", {})
                if isinstance(content, dict):
                    stack.extend(content.items())


def _delta_accessible_item_names(scene_graph: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for _, item_name, item in _iter_delta_scene_items(scene_graph):
        if item.get("accessible", True) is False:
            continue
        if item_name not in names:
            names.append(item_name)
    return names


def _all_delta_room_nodes(flat_scene: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    rooms: dict[str, dict[str, Any]] = {}
    for name, info in flat_scene.items():
        if isinstance(info, dict) and str(info.get("type") or "").strip().lower() == "room":
            rooms[name] = copy.deepcopy(info)
    return rooms


def build_task_environment(
    case_input: dict[str, Any],
    structured_task: dict[str, Any],
    prepared: PreparedTaskEnvironment,
) -> dict[str, Any]:
    """Build DELTA task facts from the public scene graph.

    Default mode uses OurAgent understanding output as the scene-filtering
    signal: understanding selects exact entity names, then this adapter reads
    each entity's state and location from the full DELTA scene. It does not use
    DELTA paper-side intermediate fields or subgoal answers.
    """
    if not isinstance(prepared.scene, dict):
        return {}
    from domain.scene import flatten_scene

    flat_scene = flatten_scene(prepared.scene)
    if delta_task_environment_mode(case_input) == FULL_TASK_ENVIRONMENT_MODE:
        return flat_scene

    closure = build_task_environment_closure(
        prepared.scene,
        structured_task,
        prepared.env_state,
    )
    # 房间连通结构是公开导航数据，goto 官方动作依赖完整房间图。
    # understanding 裁剪只裁实体，不能裁掉走廊等中间导航房间，
    # 否则模型无法生成可验证的 goto 序列。
    closure.update(_all_delta_room_nodes(flat_scene))
    return closure


def _loadable_container_summary(scene_graph: dict[str, Any]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for room_name, room in scene_graph.get("rooms", {}).items():
        for item_name, item in room.get("items", {}).items():
            affordances = {str(affordance) for affordance in item.get("affordance", [])}
            if not ({"load", "unload"} & affordances):
                continue
            content = item.get("content", {})
            contents = list(content.keys()) if isinstance(content, dict) else []
            summary.append(
                {
                    "name": item_name,
                    "room": room_name,
                    "is_loaded": bool(contents),
                    "contents": contents,
                    "affordances": sorted(affordances),
                }
            )
    return summary


def _goal_state_has_entity_goals(goal_state: Any) -> bool:
    if not isinstance(goal_state, dict):
        return False
    entities = goal_state.get("entities")
    if isinstance(entities, dict) and any(isinstance(payload, dict) and payload for payload in entities.values()):
        return True
    if isinstance(entities, list) and any(isinstance(payload, dict) and payload for payload in entities):
        return True
    return False


def _goal_state_has_only_robot_location(goal_state: Any) -> bool:
    if not isinstance(goal_state, dict):
        return False
    if _goal_state_has_entity_goals(goal_state):
        return False
    robot = goal_state.get("robot") or goal_state.get("robot_state") or {}
    if not isinstance(robot, dict) or not robot:
        return False
    return set(robot.keys()) <= {"location", "robot_location"}


def _pc_goal_state_lacks_assembled_goal(goal_state: Any) -> bool:
    if not isinstance(goal_state, dict):
        return False
    entities = goal_state.get("entities")
    if not isinstance(entities, dict):
        return True
    pc_goal = entities.get("my_pc") or entities.get("pc")
    if not isinstance(pc_goal, dict):
        return True
    states = pc_goal.get("states")
    return not (isinstance(states, dict) and states.get("isAssembled") is True)


def _drop_insufficient_goal_state_for_delta(
    case_input: dict[str, Any],
    structured_task: dict[str, Any],
) -> None:
    domain = str(case_input.get("domain") or "").strip().lower()
    if domain not in {"pc", "dining", "office"}:
        return
    goal_state = structured_task.get("goal_state")
    if _goal_state_has_only_robot_location(goal_state):
        structured_task.pop("goal_state", None)
        return
    if domain == "pc" and _pc_goal_state_lacks_assembled_goal(goal_state):
        structured_task.pop("goal_state", None)


def align_structured_task(
    case_input: dict[str, Any],
    structured_task: dict[str, Any],
    prepared: PreparedTaskEnvironment,
) -> dict[str, Any]:
    if not isinstance(structured_task, dict) or not isinstance(prepared.scene, dict):
        return structured_task
    from domain.scene import flatten_scene

    flat_scene = flatten_scene(prepared.scene)
    valid_names = set(flat_scene.keys())
    room_names = {name for name, info in flat_scene.items() if _is_room_entry(info)}
    aligned = copy.deepcopy(structured_task)
    aligned["required_item_names"] = _filter_required_item_names(aligned.get("required_item_names", {}), valid_names)
    _preserve_mentioned_rooms(aligned, room_names)
    _drop_insufficient_goal_state_for_delta(case_input, aligned)
    return aligned
