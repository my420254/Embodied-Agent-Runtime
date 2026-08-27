from __future__ import annotations

from benchmark.delta.framework.code.skills.feedback import repair_feedback
from benchmark.delta.framework.code.skills.delta_state import delta_has_predicate



UNKNOWN_ROOMS = {'', '未知', 'unknown'}

def _set_parent(sim_env: dict, target: str, parent: str) -> None:
    if target in sim_env:
        sim_env[target]['direct_parent'] = parent
        if parent == 'robot_hand':
            sim_env[target]['full_path'] = []
            return
        if parent in sim_env:
            parent_info = sim_env.get(parent, {})
            parent_path = parent_info.get('full_path', []) if isinstance(parent_info, dict) else []
            if parent_info.get('type') == 'room' or (parent_info.get('direct_parent') == '未知环境' and (not parent_path)):
                sim_env[target]['full_path'] = [parent]
            else:
                sim_env[target]['full_path'] = list(parent_path) + [parent]
        elif parent:
            sim_env[target]['full_path'] = [parent]

def _is_loaded_object(info: dict) -> bool:
    states = info.get('states', {}) if isinstance(info, dict) else {}
    return states.get('isLoaded') is True and states.get('isEmpty') is not True

def _is_loadable_object(info: dict) -> bool:
    states = info.get('states', {}) if isinstance(info, dict) else {}
    return 'isLoaded' in states or 'isEmpty' in states or _has_property(info, 'delta_predicate:item_loadable') 

def _is_empty_loadable_object(info: dict) -> bool:
    if not _is_loadable_object(info):
        return False
    states = info.get('states', {}) if isinstance(info, dict) else {}
    if states.get('isEmpty') is True:
        return True
    if states.get('isLoaded') is True:
        return False
    return _has_property(info, 'delta_predicate:item_empty')

def _as_room(value: str | None) -> str:
    text = str(value or '').strip()
    return text[:-7] if text.endswith('_anchor') else text

def _robot_room(sim_robot: dict) -> str:
    return _as_room(str(sim_robot.get('robot_location', '') or ''))

def _room_exists(room: str, sim_env: dict) -> bool:
    value = _as_room(room)
    return value in sim_env or f'{value}_anchor' in sim_env

def _properties(info: dict) -> set[str]:
    raw = info.get('properties', []) if isinstance(info, dict) else []
    if not isinstance(raw, (list, tuple, set)):
        return set()
    return {str(value) for value in raw if str(value)}

def _has_property(info: dict, value: str) -> bool:
    return value in _properties(info)

def _has_delta_predicate(sim_env: dict, item: str, predicate: str) -> bool:
    return delta_has_predicate(sim_env, item, predicate)

class DropLoadableSkill:
    name = 'drop_loadable'

    def validate(self, sim_env: dict, sim_robot: dict, params: dict):
        robot_room = _robot_room(sim_robot)
        robot_hold = sim_robot.get('robot_holding', '')
        target = params.get('item', '')
        room = _as_room(params.get('room', ''))
        if not target or not room:
            return (False, 'missing drop_loadable parameter', 'drop_loadable requires official DELTA parameters: item, room')
        if not _room_exists(room, sim_env):
            return (False, 'invalid DELTA room', 'drop_loadable.room must be a room from the DELTA scene')
        if robot_hold != target:
            return (False, '手持物品不匹配', repair_feedback(observed=f'robot_holding={robot_hold}', required=f'robot_holding={target}', repair_actions=['pick_loadable']))
        if target not in sim_env:
            return (False, 'invalid DELTA item', 'drop_loadable.item must be an item from the DELTA scene')
        if robot_room not in {*UNKNOWN_ROOMS, room}:
            return (False, 'position precondition failed', repair_feedback(observed=f'robot_location={robot_room}', required=f'robot_location={room}', repair_actions=['goto']))
        target_info = sim_env.get(target, {})
        if not _is_loadable_object(target_info) or not _has_delta_predicate(sim_env, target, 'item_loadable'):
            return (False, '目标类型不匹配', f'{target} 不是 loadable 容器')
        if _is_loaded_object(target_info) or not _is_empty_loadable_object(target_info):
            return (False, '容器未清空', repair_feedback(observed=f'{target}.item_empty=false', required=f'{target}.item_empty=true', repair_actions=['unload']))
        return (True, '', '')

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        target = params.get('item', '')
        destination = _as_room(params.get('room', ''))
        sim_robot['robot_holding'] = '空'
        _set_parent(sim_env, target, destination)
