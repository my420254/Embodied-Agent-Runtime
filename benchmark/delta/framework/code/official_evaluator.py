from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


# 轻量 DELTA goal evaluator。
#
# 输入：
# - scene_graph：DELTA 原始 scene graph 或显式 oracle-pruned graph。
# - execution_calls：由 DELTA 官方动作临时接成的 evaluator execution calls。
# - goal_pddls：/data/zmy/DELTA/data/example.py 中的 goal/subgoal PDDL。
#
# 公平性边界：
# - goal_pddls 是答案，只能在规划结束后用于评测。
# - 本文件不参与 understanding/planning prompt 构造。
#
# 方法边界：
# - 这里是 Python replay + goal atom checker，不是 DELTA 原仓库的 Fast Downward/VAL 完整验证。
# - 它覆盖当前 DELTA 官方动作到 DELTA goal predicate 的主要映射，用于快速得到成功率。
# - 如果要写论文主表，最好再补一条官方 PDDL/VAL 对齐验证，或在实验说明中明确这是 local symbolic evaluator。


@dataclass
class DeltaSymbolicState:
    rooms: set[str] = field(default_factory=set)
    item_location: dict[str, str | None] = field(default_factory=dict)
    item_relation: dict[str, str] = field(default_factory=dict)
    agent_location: str = ""
    holding: str | None = None
    predicates: set[tuple[str, ...]] = field(default_factory=set)


def _official_name(name: str | None) -> str:
    return str(name or "").strip()


def _official_room(name: str | None) -> str:
    value = _official_name(name)
    return value[:-7] if value.endswith("_anchor") else value


def _walk_scene_items(state: DeltaSymbolicState, room_name: str, items: dict[str, Any], parent: str | None = None) -> None:
    for item_name, item in items.items():
        state.item_location[item_name] = parent or room_name
        state.item_relation[item_name] = "in" if parent else "at"
        item_state = str(item.get("state", "")).lower()
        if "disposed" in item_state:
            state.predicates.add(("item_disposed", item_name))
        if "clean" in item_state:
            state.predicates.add(("mop_clean", item_name))
        content = item.get("content", {})
        if isinstance(content, dict):
            _walk_scene_items(state, room_name, content, item_name)


def build_symbolic_state(scene_graph: dict[str, Any]) -> DeltaSymbolicState:
    """从 DELTA scene graph 建初始符号状态。

    只读取环境初始事实，不读取 subgoal、gt_cost 或模型输出之外的 plan。
    """
    state = DeltaSymbolicState()
    for room_name, room in scene_graph.get("rooms", {}).items():
        state.rooms.add(room_name)
        _walk_scene_items(state, room_name, room.get("items", {}))
    agent = scene_graph.get("agent", {})
    agent_position = str((agent if isinstance(agent, dict) else {}).get("position") or "").strip()
    if agent_position in state.rooms:
        state.agent_location = agent_position
    else:
        state.agent_location = "living_room" if "living_room" in state.rooms else next(iter(state.rooms), "")
    agent_state = str((agent if isinstance(agent, dict) else {}).get("state") or "").strip().lower()
    if agent_state in {"battery-full", "battery_full", "battery full"}:
        state.predicates.add(("battery_full", "robot"))
    return state


def _root_room(state: DeltaSymbolicState, item_name: str) -> str | None:
    location = state.item_location.get(item_name)
    visited = set()
    while location and location not in state.rooms and location not in visited:
        visited.add(location)
        location = state.item_location.get(location)
    return location if location in state.rooms else None


def apply_delta_execution_calls(state: DeltaSymbolicState, execution_calls: list[dict]) -> DeltaSymbolicState:
    """把 DELTA 官方动作 execution calls 回放到轻量 DELTA 符号状态上。

    这里的动作效果应与 DELTA benchmark 官方动作保持一致。
    它用于评测，不会把修复后的状态或提示反馈给 planner。
    """
    for step in execution_calls:
        execution = step.get("execution", {})
        skill = execution.get("skill", "")
        params = execution.get("parameters", {}) or {}

        if skill == "goto":
            target = _official_room(params.get("to"))
            if target in state.rooms:
                state.agent_location = target
            elif target in state.item_location:
                parent_room = _root_room(state, target)
                if parent_room:
                    state.agent_location = parent_room
        elif skill == "pick":
            target = _official_name(params.get("item"))
            if target:
                state.holding = target
                state.item_location[target] = None
        elif skill == "pick_loadable":
            target = _official_name(params.get("item"))
            if target:
                state.holding = target
                state.item_location[target] = None
        elif skill == "drop":
            target = _official_name(params.get("item")) or str(state.holding or "")
            destination = _official_room(params.get("room"))
            if target and destination:
                state.holding = None if state.holding == target else state.holding
                state.item_location[target] = destination
                state.item_relation[target] = "at"
        elif skill == "drop_loadable":
            target = _official_name(params.get("item")) or str(state.holding or "")
            destination = _official_room(params.get("room"))
            if target and destination:
                state.holding = None if state.holding == target else state.holding
                state.item_location[target] = destination
                state.item_relation[target] = "at"
        elif skill == "place_on":
            target = _official_name(params.get("item")) or str(state.holding or "")
            destination = _official_name(params.get("surface"))
            if target and destination:
                state.holding = None if state.holding == target else state.holding
                state.item_location[target] = destination
                state.item_relation[target] = "on"
        elif skill == "load":
            target = _official_name(params.get("item")) or str(state.holding or "")
            destination = _official_name(params.get("loadable"))
            if target and destination:
                state.holding = None if state.holding == target else state.holding
                state.item_location[target] = destination
                state.item_relation[target] = "in"
        elif skill == "unload":
            target = _official_name(params.get("item"))
            destination = _official_room(params.get("room"))
            if target and destination:
                state.item_location[target] = destination
                state.item_relation[target] = "at"
        elif skill == "dispose":
            target = _official_name(params.get("item"))
            disposal = _official_name(params.get("disposal"))
            room = _official_room(params.get("room"))
            if target and disposal and room:
                state.predicates.add(("item_disposed", target))
        elif skill == "mop_floor":
            room = _official_room(params.get("room"))
            tool = _official_name(params.get("tool"))
            if room and tool:
                state.predicates.add(("floor_clean", room))
        elif skill == "clean_mop":
            mop = _official_name(params.get("tool"))
            if mop:
                state.predicates.add(("mop_clean", mop))
        elif skill == "charge":
            station = _official_name(params.get("station"))
            room = _official_room(params.get("room"))
            if station and room:
                state.predicates.add(("battery_full", "robot"))
        elif skill == "assemble":
            target = _official_name(params.get("target_pc"))
            if target:
                state.predicates.add(("pc_assembled", target))
    return state


def parse_delta_goal_atoms(goal_pddl: str) -> list[tuple[str, ...]]:
    """从 DELTA goal PDDL 里抽取正向原子目标。"""
    atoms = []
    for predicate, raw_args in re.findall(r"\(([A-Za-z_][\w-]*)\s+([^()]+?)\)", goal_pddl):
        args = tuple(arg for arg in raw_args.replace("\n", " ").split() if arg)
        if args:
            atoms.append((predicate, *args))
    return atoms


def _goal_satisfied(state: DeltaSymbolicState, atom: tuple[str, ...]) -> bool:
    predicate = atom[0]
    if predicate == "item_at" and len(atom) == 3:
        return _root_room(state, atom[1]) == atom[2]
    if predicate in {"item_on", "item_in"} and len(atom) == 3:
        item, destination = atom[1], atom[2]
        expected_relation = "on" if predicate == "item_on" else "in"
        return state.item_location.get(item) == destination and state.item_relation.get(item) in {expected_relation, "put"}
    return atom in state.predicates


def evaluate_delta_goals(scene_graph: dict[str, Any], execution_calls: list[dict], goal_pddls: list[str]) -> dict[str, Any]:
    """评测 DELTA 官方动作序列是否满足 DELTA goal atoms。

    goal_pddls 在此处才被读取；如果调用链把它传进 planning，就是不公平用法。
    """
    state = apply_delta_execution_calls(build_symbolic_state(scene_graph), execution_calls)
    atoms = [atom for goal_pddl in goal_pddls for atom in parse_delta_goal_atoms(goal_pddl)]
    satisfied = [atom for atom in atoms if _goal_satisfied(state, atom)]
    total = len(atoms)
    return {
        "evaluation_mode": "delta_symbolic_goal_verifier",
        "success": total > 0 and len(satisfied) == total,
        "goal_success_rate": (len(satisfied) / total) if total else 0.0,
        "satisfied_goals": ["(" + " ".join(atom) + ")" for atom in satisfied],
        "unsatisfied_goals": ["(" + " ".join(atom) + ")" for atom in atoms if atom not in satisfied],
    }
