from __future__ import annotations



from typing import Any

from benchmark.delta.framework.code.skills.feedback import repair_feedback
from benchmark.delta.framework.code.skills.delta_state import delta_has_predicate



UNKNOWN_ROOMS = {'', '未知', 'unknown'}

def _state(sim_env: dict, target: str) -> dict[str, Any]:
    return sim_env.setdefault(target, {}).setdefault('states', {})

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

def _update_parent_load_state(sim_env: dict, parent: str, removed_child: str) -> None:
    if parent not in sim_env:
        return
    parent_states = _state(sim_env, parent)
    if 'isLoaded' not in parent_states and 'isEmpty' not in parent_states:
        return
    still_contains_items = any((name != removed_child and isinstance(info, dict) and (info.get('direct_parent') == parent) for (name, info) in sim_env.items()))
    parent_states['isLoaded'] = still_contains_items
    parent_states['isEmpty'] = not still_contains_items

def _as_room(value: str | None) -> str:
    text = str(value or '').strip()
    return text[:-7] if text.endswith('_anchor') else text

def _robot_room(sim_robot: dict) -> str:
    return _as_room(str(sim_robot.get('robot_location', '') or ''))

def _item_room(item_name: str, sim_env: dict) -> str:
    info = sim_env.get(item_name, {})
    direct_parent = str(info.get('direct_parent', '') or '') if isinstance(info, dict) else ''
    if direct_parent == 'robot_hand':
        return 'robot_hand'
    if direct_parent.endswith('_anchor'):
        return _as_room(direct_parent)
    if direct_parent and direct_parent in sim_env and (direct_parent != item_name):
        parent_info = sim_env.get(direct_parent, {})
        if isinstance(parent_info, dict) and (parent_info.get('type') == 'room' or (parent_info.get('direct_parent') == '未知环境' and (not parent_info.get('full_path')))):
            return _as_room(direct_parent)
        return _item_room(direct_parent, sim_env)
    full_path = info.get('full_path', []) if isinstance(info, dict) else []
    if isinstance(full_path, list) and full_path:
        return _as_room(str(full_path[0]))
    return _as_room(direct_parent)

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

class UnloadSkill:
    name = 'unload'

    def validate(self, sim_env: dict, sim_robot: dict, params: dict):
        robot_room = _robot_room(sim_robot)
        robot_hold = sim_robot.get('robot_holding', '')
        target = params.get('item', '')
        parent = params.get('loadable', '')
        room = _as_room(params.get('room', '')) or _item_room(parent, sim_env)
        target_info = sim_env.get(target, {})
        if not target or not parent or (not room):
            return (False, 'missing unload parameter', 'unload requires official DELTA parameters: loadable, item, room')
        if target not in sim_env:
            return (False, 'invalid DELTA item', 'unload.item must be an item from the DELTA scene')
        if robot_hold not in {'', '空', None}:
            return (False, '机械臂冲突', repair_feedback(observed=f'robot_holding={robot_hold}', required='robot_holding=空', repair_actions=['drop', 'drop_loadable']))
        if not parent or parent not in sim_env:
            return (False, '无效来源容器', f'{target} 当前不在可卸载容器内')
        if not _room_exists(room, sim_env):
            return (False, 'invalid DELTA room', 'unload.room must be a room from the DELTA scene')
        if _item_room(parent, sim_env) != room:
            actual_room = _item_room(parent, sim_env)
            return (False, 'loadable room mismatch', repair_feedback(observed=f'{parent}.room={actual_room}', required=f'{parent}.room={room}', repair_actions=['goto', 'unload'], note=f'unload.room 应使用 loadable 容器所在真实房间 {actual_room}'))
        if room and robot_room not in {*UNKNOWN_ROOMS, room}:
            return (False, 'position precondition failed', repair_feedback(observed=f'robot_location={robot_room}', required=f'robot_location={room}', repair_actions=['goto']))
        parent_info = sim_env.get(parent, {})
        if not _is_loadable_object(parent_info) or not _has_delta_predicate(sim_env, parent, 'item_loadable'):
            return (False, '无效来源容器', f'{parent} 不是 loadable 容器')
        if not _has_delta_predicate(sim_env, target, 'item_pickable'):
            return (False, 'official DELTA predicate failed', f'{target} is not item_pickable; unload only supports pickable items')
        if target_info.get('direct_parent') != parent:
            actual_parent = target_info.get('direct_parent', '')
            return (False, 'item_in precondition failed', repair_feedback(observed=f'{target}.direct_parent={actual_parent}', required=f'{target}.direct_parent={parent}', repair_actions=['load', 'unload'], note='只能 unload 当前真实位于该 loadable 容器内的物体'))
        if _is_empty_loadable_object(parent_info):
            return (False, '容器为空', f'{parent} 当前是 item_empty，没有可卸载的 {target}')
        return (True, '', '')

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        target = params.get('item', '')
        parent = params.get('loadable', '') or sim_env.get(target, {}).get('direct_parent', '')
        destination = _as_room(params.get('room', '')) or _item_room(parent, sim_env)
        _set_parent(sim_env, target, destination)
        _update_parent_load_state(sim_env, parent, target)
