from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


DELTA_REPO_ROOT = Path("/data/zmy/DELTA")
DEFAULT_VALIDATE_CANDIDATES = (
    Path("/data/zmy/VAL/build/linux64/Release/install/bin/Validate"),
    Path("/usr/local/bin/Validate"),
)


# 本模块是严格的 DELTA 评估适配器。
# 模型侧输出的是 DELTA 官方动作对象；runner 会把这些官方动作临时接成
# evaluator 使用的 execution 形态后传入本文件。本文件只负责写 VAL 需要的
# PDDL plan，不修复规划、不补任何动作、不注入 oracle subgoals。每一条
# native action 必须已是可直接提交给 DELTA PDDL/VAL 的动作。

def delta_domain_file(case_input: dict[str, Any], repo_root: str | Path = DELTA_REPO_ROOT) -> Path:
    return Path(repo_root) / "data" / "pddl" / "domain" / f"{case_input['domain']}_domain.pddl"


def delta_problem_file(case_input: dict[str, Any], repo_root: str | Path = DELTA_REPO_ROOT) -> Path:
    return Path(repo_root) / "data" / "pddl" / "problem" / f"{case_input['scene_name']}_{case_input['domain']}_problem.pddl"


def load_delta_problem_init_predicates(
    case_input: dict[str, Any],
    repo_root: str | Path = DELTA_REPO_ROOT,
) -> list[tuple[str, ...]]:
    """Extract only the initial-state atoms from DELTA's source problem PDDL.

    The goal block is not parsed and this function never feeds goal atoms into
    understanding, planning, or sandbox handlers.
    """
    text = Path(delta_problem_file(case_input, repo_root)).read_text(encoding="utf-8")
    start = text.find("(:init")
    if start < 0:
        return []
    goal_pos = text.find("(:goal", start)
    block = text[start:goal_pos] if goal_pos >= 0 else text[start:]
    predicates: list[tuple[str, ...]] = []
    for match in re.finditer(r"\(([A-Za-z_][\w-]*)\s+([^()]+?)\)", block):
        args = tuple(part for part in match.group(2).replace("\n", " ").split() if part)
        if args:
            predicates.append((match.group(1), *args))
    return predicates


def _official_name(name: str | None) -> str:
    return str(name or "").strip()


def _official_room(name: str | None) -> str:
    return _official_name(name)


def _walk_delta_items(
    scene_graph: dict[str, Any],
) -> tuple[dict[str, str], dict[str, str | None], dict[str, set[str]]]:
    item_room: dict[str, str] = {}
    item_parent: dict[str, str | None] = {}
    item_affordances: dict[str, set[str]] = {}

    def walk(room_name: str, items: dict[str, Any], parent: str | None = None) -> None:
        for item_name, item in items.items():
            item_room[item_name] = room_name
            item_parent[item_name] = parent
            item_affordances[item_name] = {str(affordance) for affordance in item.get("affordance", [])}
            content = item.get("content", {})
            if isinstance(content, dict):
                walk(room_name, content, item_name)

    for room_name, room in scene_graph.get("rooms", {}).items():
        walk(room_name, room.get("items", {}))
    return item_room, item_parent, item_affordances


def _room_for_name(name: str, scene_graph: dict[str, Any], item_room: dict[str, str]) -> str | None:
    value = _official_room(name)
    if value in scene_graph.get("rooms", {}):
        return value
    return item_room.get(value)


def _initial_room(problem_file: str | Path) -> str:
    text = Path(problem_file).read_text(encoding="utf-8")
    match = re.search(r"\(agent_at\s+robot\s+([^\s)]+)\)", text)
    return match.group(1) if match else "living_room"


def _official_loadable_names(case_input: dict[str, Any], repo_root: str | Path = DELTA_REPO_ROOT) -> set[str]:
    """Loadable containers are defined by the official item_loadable init atoms."""
    return {
        str(args[0])
        for predicate, *args in load_delta_problem_init_predicates(case_input, repo_root)
        if predicate == "item_loadable" and args
    }


def _scene_neighbors(scene_graph: dict[str, Any]) -> dict[str, list[str]]:
    rooms = scene_graph.get("rooms", {})
    if not isinstance(rooms, dict):
        return {}
    return {
        str(room_name): [str(neighbor) for neighbor in room.get("neighbor", []) if str(neighbor).strip()]
        for room_name, room in rooms.items()
        if str(room_name).strip() and isinstance(room, dict)
    }


def _expand_navigation_path(source: str, target: str, neighbors: dict[str, list[str]]) -> list[str]:
    """Expand an abstract room-level goto into concrete neighbor hops (BFS)."""
    if source == target:
        return []
    if source not in neighbors or target not in neighbors:
        return []
    frontier: list[list[str]] = [[source]]
    visited = {source}
    while frontier:
        path = frontier.pop(0)
        tail = path[-1]
        for neighbor in neighbors.get(tail, []):
            if neighbor == target:
                return path[1:] + [target]
            if neighbor not in visited:
                visited.add(neighbor)
                frontier.append(path + [neighbor])
    return []


def _execution(step: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    execution = step.get("execution", {})
    if not isinstance(execution, dict):
        return "", {}
    skill = str(execution.get("skill", ""))
    params = execution.get("parameters", {})
    return skill, params if isinstance(params, dict) else {}


def _held_item(dynamic_parent: dict[str, str | None]) -> str:
    for item, parent in dynamic_parent.items():
        if parent == "robot_hand":
            return item
    return ""


def _destination_room(
    destination: str,
    *,
    scene_graph: dict[str, Any],
    item_room: dict[str, str],
    current_room_for_name,
) -> str | None:
    return (
        current_room_for_name(destination)
        or _room_for_name(destination, scene_graph, item_room)
        or destination
    )


def export_delta_pddl_plan(
    *,
    case_input: dict[str, Any],
    scene_graph: dict[str, Any],
    execution_calls: list[dict[str, Any]],
    output_path: str | Path,
    repo_root: str | Path = DELTA_REPO_ROOT,
) -> dict[str, Any]:
    """Export DELTA official action calls as a PDDL plan file.

    The exporter is intentionally conservative: it maps explicit official
    actions only. Missing navigation, missing pickups, and illegal ordering are
    left for VAL to reject.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    problem_file = delta_problem_file(case_input, repo_root)
    item_room, item_parent, _item_affordances = _walk_delta_items(scene_graph)
    dynamic_parent = dict(item_parent)
    official_loadable = _official_loadable_names(case_input, repo_root)
    current_room = _initial_room(problem_file)
    plan_lines: list[str] = []
    errors: list[str] = []
    def current_room_for_name(name: str) -> str | None:
        value = _official_room(name)
        if value in scene_graph.get("rooms", {}):
            return value
        if value not in item_room:
            return None
        parent = dynamic_parent.get(value)
        if parent == "robot_hand":
            return current_room
        if parent in scene_graph.get("rooms", {}):
            return parent
        if parent in item_room:
            return current_room_for_name(parent)
        return item_room.get(value)

    for index, step in enumerate(execution_calls, start=1):
        skill, params = _execution(step)
        source_step = f"step {step.get('step', index)} {skill or '<missing-skill>'}"

        if skill == "goto":
            source = _official_room(params.get("from"))
            target = _official_room(params.get("to"))
            if not source or not target:
                errors.append(f"{source_step}: missing from or to")
                continue
            if source != current_room:
                errors.append(f"{source_step}: goto.from must match current room {current_room}")
                continue
            neighbors = _scene_neighbors(scene_graph)
            hops = _expand_navigation_path(source, target, neighbors)
            if not hops:
                errors.append(
                    f"{source_step}: no scene_graph navigation path from {source} to {target}"
                )
                continue
            for hop in hops:
                plan_lines.append(f"(goto robot {current_room} {hop})")
                current_room = hop
            continue

        if skill == "pick":
            target = _official_name(params.get("item"))
            room = _official_room(params.get("room"))
            if not target or not room:
                errors.append(f"{source_step}: missing item or room")
                continue
            held = _held_item(dynamic_parent)
            if held:
                errors.append(f"{source_step}: robot already holds {held}")
            if room != current_room:
                errors.append(f"{source_step}: pick room must match current room {current_room}")
            if target in official_loadable:
                errors.append(f"{source_step}: loadable containers must use pick_loadable")
                continue
            plan_lines.append(f"(pick robot {target} {current_room})")
            dynamic_parent[target] = "robot_hand"
            continue

        if skill == "pick_loadable":
            target = _official_name(params.get("item"))
            room = _official_room(params.get("room"))
            if not target or not room:
                errors.append(f"{source_step}: missing item or room")
                continue
            held = _held_item(dynamic_parent)
            if held:
                errors.append(f"{source_step}: robot already holds {held}")
            if room != current_room:
                errors.append(f"{source_step}: pick_loadable room must match current room {current_room}")
                continue
            plan_lines.append(f"(pick_loadable robot {target} {current_room})")
            dynamic_parent[target] = "robot_hand"
            continue

        if skill == "drop":
            target = _official_name(params.get("item")) or _held_item(dynamic_parent)
            room = _official_room(params.get("room"))
            if not target or not room:
                errors.append(f"{source_step}: missing item or room")
                continue
            if target in official_loadable:
                errors.append(f"{source_step}: loadable containers must use drop_loadable")
                continue
            if room != current_room:
                errors.append(f"{source_step}: drop room must match current room {current_room}")
            plan_lines.append(f"(drop robot {target} {current_room})")
            dynamic_parent[target] = current_room
            continue

        if skill == "drop_loadable":
            target = _official_name(params.get("item")) or _held_item(dynamic_parent)
            room = _official_room(params.get("room"))
            if not target or not room:
                errors.append(f"{source_step}: missing item or room")
                continue
            if room != current_room:
                errors.append(f"{source_step}: drop_loadable room must match current room {current_room}")
            plan_lines.append(f"(drop_loadable robot {target} {current_room})")
            dynamic_parent[target] = current_room
            continue

        if skill == "place_on":
            target = _official_name(params.get("item")) or _held_item(dynamic_parent)
            destination = _official_name(params.get("surface"))
            room = _official_room(params.get("room"))
            if not target or not destination or not room:
                errors.append(f"{source_step}: missing item, surface, or room")
                continue
            if room != current_room:
                errors.append(f"{source_step}: place_on room must match current room {current_room}")
            if destination != "dining_table" and destination != current_room:
                destination_room = _destination_room(
                    destination,
                    scene_graph=scene_graph,
                    item_room=item_room,
                    current_room_for_name=current_room_for_name,
                )
                if destination_room != current_room:
                    errors.append(f"{source_step}: place_on destination must be in current room {current_room}")
            plan_lines.append(f"(place_on robot {target} {destination} {current_room})")
            dynamic_parent[target] = destination
            continue

        if skill == "load":
            destination = _official_name(params.get("loadable"))
            target = _official_name(params.get("item")) or _held_item(dynamic_parent)
            room = _official_room(params.get("room"))
            if not target or not destination or not room:
                errors.append(f"{source_step}: missing loadable, item, or room")
                continue
            if room != current_room:
                errors.append(f"{source_step}: load room must match current room {current_room}")
            plan_lines.append(f"(load robot {destination} {target} {current_room})")
            dynamic_parent[target] = destination
            continue

        if skill == "unload":
            parent = _official_name(params.get("loadable"))
            target = _official_name(params.get("item"))
            room = _official_room(params.get("room"))
            if not parent or not target or not room:
                errors.append(f"{source_step}: missing loadable, item, or room")
                continue
            if dynamic_parent.get(target) != parent:
                errors.append(f"{source_step}: {target} is not currently in {parent}")
            if room != current_room:
                errors.append(f"{source_step}: unload room must match current room {current_room}")
            plan_lines.append(f"(unload robot {parent} {target} {current_room})")
            dynamic_parent[target] = current_room
            continue

        if skill == "dispose":
            target = _official_name(params.get("item"))
            disposal_target = _official_name(params.get("disposal"))
            room = _official_room(params.get("room"))
            if not target or not disposal_target or not room:
                errors.append(f"{source_step}: missing item, disposal, or room")
                continue
            if room != current_room:
                errors.append(f"{source_step}: dispose room must match current room {current_room}")
            plan_lines.append(f"(dispose robot {target} {disposal_target} {current_room})")
            dynamic_parent[target] = disposal_target
            continue

        if skill == "mop_floor":
            target_room = _official_room(params.get("room"))
            tool = _official_name(params.get("tool"))
            if not target_room or not tool:
                errors.append(f"{source_step}: missing tool or room")
                continue
            if target_room != current_room:
                errors.append(f"{source_step}: robot is in {current_room}, cannot mop_floor {target_room} without goto")
            if dynamic_parent.get(tool) != "robot_hand":
                errors.append(f"{source_step}: robot must pick {tool} before mop_floor")
            plan_lines.append(f"(mop_floor robot {tool} {current_room})")
            continue

        if skill == "clean_mop":
            target = _official_name(params.get("tool"))
            water_source = _official_name(params.get("water_source"))
            room = _official_room(params.get("room"))
            if not target or not water_source or not room:
                errors.append(f"{source_step}: missing tool, water_source, or room")
                continue
            if room != current_room:
                errors.append(f"{source_step}: clean_mop room must match current room {current_room}")
            if dynamic_parent.get(target) != "robot_hand":
                errors.append(f"{source_step}: robot must hold {target} before clean_mop")
            plan_lines.append(f"(clean_mop robot {target} {water_source} {current_room})")
            dynamic_parent[target] = current_room
            continue

        if skill == "charge":
            station = _official_name(params.get("station"))
            room = _official_room(params.get("room"))
            if not station or not room:
                errors.append(f"{source_step}: missing station or room")
                continue
            if room != current_room:
                errors.append(f"{source_step}: charge room must match current room {current_room}")
            plan_lines.append(f"(charge robot {station} {current_room})")
            continue

        if skill == "assemble":
            room = _official_room(params.get("room"))
            component_names = ["mainboard", "cpu", "ram", "ssd", "gpu", "psu"]
            components = [_official_name(params.get(name)) for name in component_names]
            target_pc = _official_name(params.get("target_pc"))
            if not room or not target_pc or any(not component for component in components):
                errors.append(f"{source_step}: missing room, pc components, or target_pc")
                continue
            if room != current_room:
                errors.append(f"{source_step}: assemble room must match current room {current_room}")
            plan_lines.append(
                f"(assemble robot {current_room} {' '.join(components)} {target_pc})"
            )
            continue

        errors.append(f"{source_step}: unsupported DELTA PDDL mapping")

    output_path.write_text("\n".join(plan_lines) + ("\n" if plan_lines else ""), encoding="utf-8")
    return {
        "plan_path": str(output_path),
        "plan_lines": plan_lines,
        "export_errors": errors,
        "domain_file": str(delta_domain_file(case_input, repo_root)),
        "problem_file": str(problem_file),
    }


def find_validate_binary(explicit_path: str | Path | None = None) -> Path | None:
    candidates: list[Path] = []
    if explicit_path:
        candidates.append(Path(explicit_path))
    env_path = os.getenv("OURAGENT_DELTA_VALIDATE")
    if env_path:
        candidates.append(Path(env_path))
    which_path = shutil.which("Validate")
    if which_path:
        candidates.append(Path(which_path))
    candidates.extend(DEFAULT_VALIDATE_CANDIDATES)

    for candidate in candidates:
        if candidate.exists() and os.access(candidate, os.X_OK):
            return candidate
    return None


def validate_delta_pddl_plan(
    *,
    domain_file: str | Path,
    problem_file: str | Path,
    plan_file: str | Path,
    validate_binary: str | Path | None = None,
) -> dict[str, Any]:
    validate_path = find_validate_binary(validate_binary)
    if validate_path is None:
        return {
            "available": False,
            "success": False,
            "validator": "",
            "stdout": "",
            "stderr": "",
            "error": "VAL Validate binary not found. Set OURAGENT_DELTA_VALIDATE or install Validate in PATH.",
        }

    command = [str(validate_path), "-v", str(domain_file), str(problem_file), str(plan_file)]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    return {
        "available": True,
        "success": "Plan valid" in stdout,
        "validator": str(validate_path),
        "returncode": completed.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "error": "" if "Plan valid" in stdout else (stderr or stdout),
    }
