from __future__ import annotations

from benchmark.delta.framework.code.skills.feedback import repair_feedback



def _as_room(value: str | None) -> str:
    text = str(value or '').strip()
    return text[:-7] if text.endswith('_anchor') else text

def _robot_room(sim_robot: dict) -> str:
    return _as_room(str(sim_robot.get('robot_location', '') or ''))

def _room_exists(room: str, sim_env: dict) -> bool:
    value = _as_room(room)
    return value in sim_env or f'{value}_anchor' in sim_env


def _room_neighbors(sim_robot: dict) -> dict[str, set[str]]:
    raw = sim_robot.get('delta_room_neighbors', {})
    if not isinstance(raw, dict):
        return {}
    return {
        str(room).strip(): {
            str(neighbor).strip()
            for neighbor in (values if isinstance(values, (list, tuple, set)) else [])
            if str(neighbor).strip()
        }
        for room, values in raw.items()
        if str(room).strip()
    }


def _has_navigation_path(
    source: str,
    target: str,
    neighbors: dict[str, set[str]],
) -> bool:
    """Room-level goto is valid if a path exists in the public neighbor graph.

    The concrete neighbor-by-neighbor expansion is performed by the PDDL
    exporter, mirroring the DELTA paper pipeline where a classical planner
    expands abstract navigation into executable hops.
    """
    if source == target:
        return True
    if source not in neighbors or target not in neighbors:
        return False
    frontier = [source]
    visited = {source}
    while frontier:
        room = frontier.pop(0)
        for neighbor in neighbors.get(room, set()):
            if neighbor == target:
                return True
            if neighbor not in visited:
                visited.add(neighbor)
                frontier.append(neighbor)
    return False


class GotoSkill:
    name = 'goto'

    def validate(self, sim_env: dict, sim_robot: dict, params: dict):
        source = _as_room(params.get('from', ''))
        target = _as_room(params.get('to', ''))
        if not source or not target:
            return (False, 'missing goto parameter', 'goto requires official DELTA parameters: from, to')
        if source == target:
            return (False, 'invalid DELTA room transition', 'goto.from and goto.to must be different rooms')
        if not _room_exists(source, sim_env) or not _room_exists(target, sim_env):
            return (False, 'invalid DELTA room', 'goto.from and goto.to must be rooms from the DELTA scene')
        neighbors = _room_neighbors(sim_robot)
        if not neighbors:
            return (False, 'missing DELTA navigation graph', 'DELTA sandbox is missing source scene_graph room-neighbor data')
        if not _has_navigation_path(source, target, neighbors):
            available = ', '.join(sorted(neighbors.get(source, set()))) or 'none'
            return (
                False,
                'invalid DELTA room transition',
                repair_feedback(
                    observed=f'goto.from={source}, goto.to={target}',
                    required=f'{source} 与 {target} 之间必须在场景图邻接表中存在可达路径；{source} 的直接邻居: {available}',
                    repair_actions=['goto'],
                ),
            )
        current = _robot_room(sim_robot)
        if current not in {'', '未知', 'unknown', source}:
            return (False, 'position precondition failed', repair_feedback(observed=f'robot_location={current}, goto.from={source}', required='goto.from 必须等于机器人当前房间', repair_actions=['goto'], note='修正当前 goto 的 from 字段，或从当前真实房间重新规划后续 goto'))
        return (True, '', '')

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        sim_robot['robot_location'] = _as_room(params.get('to', ''))
