from __future__ import annotations

from benchmark.delta.framework.code.skills.feedback import repair_feedback
from benchmark.delta.framework.code.skills.delta_state import delta_has_predicate



class DropSkill:
    name = 'drop'

    def validate(self, sim_env: dict, sim_robot: dict, params: dict):
        action_name = self.name
        robot_room = _robot_room(sim_robot)
        robot_hold = sim_robot.get('robot_holding', '')
        target = params.get('item', '') or robot_hold
        room = _as_room(params.get('room', ''))
        if not room:
            return (False, f'missing {action_name} parameter', f'{action_name} requires official DELTA parameter: room')
        if not _room_exists(room, sim_env):
            return (False, 'invalid DELTA room', f'{action_name}.room must be a room from the DELTA scene')
        if robot_hold in {'', '空', None}:
            return (False, '手持物品不匹配', repair_feedback(observed=f"robot_holding={robot_hold}", required='robot_holding=某个可放下物品', repair_actions=['pick']))
        if target not in sim_env:
            return (False, 'invalid DELTA item', f'{action_name}.item must be an item from the DELTA scene')
        if robot_room not in {*UNKNOWN_ROOMS, room}:
            return (False, 'position precondition failed', repair_feedback(observed=f'robot_location={robot_room}', required=f'robot_location={room}', repair_actions=['goto']))
        if robot_hold != target:
            return (False, '手持物品不匹配', repair_feedback(observed=f'robot_holding={robot_hold}', required=f'robot_holding={target}', repair_actions=['pick']))
        if not _has_delta_predicate(sim_env, target, 'item_pickable'):
            return (False, 'official DELTA predicate failed', f'{target} is not item_pickable; {action_name} only supports pickable items')
        if _is_loadable_object(sim_env.get(target, {})):
            return (False, '目标类型不匹配', repair_feedback(observed=f'{target}=loadable', required=f'{action_name} 只处理普通手持物', repair_actions=['drop_loadable']))
        if _is_loaded_object(sim_env.get(target, {})):
            return (False, '容器未清空', repair_feedback(observed=f'{target}.isEmpty=false', required=f'{target}.isEmpty=true', repair_actions=['unload']))
        return (True, '', '')

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        target = params.get('item', '') or sim_robot.get('robot_holding', '')
        destination = _as_room(params.get('room', ''))
        sim_robot['robot_holding'] = '空'
        _set_parent(sim_env, target, destination)

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

class PlaceOnSkill(DropSkill):
    name = 'place_on'

    def validate(self, sim_env: dict, sim_robot: dict, params: dict):
        (ok, issue, fix) = super().validate(sim_env, sim_robot, params)
        if not ok:
            return (ok, issue, fix)
        destination = params.get('surface', '')
        if not destination:
            return (False, 'missing place_on parameter', 'place_on requires official DELTA parameter: surface')
        if destination not in sim_env:
            return (False, 'invalid DELTA surface', 'place_on.surface must be an item from the DELTA scene')
        room = params.get('room', '')
        if _item_room(destination, sim_env) != room:
            actual_room = _item_room(destination, sim_env)
            return (False, 'surface room mismatch', repair_feedback(observed=f'{destination}.room={actual_room}', required=f'{destination}.room={room}', repair_actions=['goto', 'place_on'], note=f'place_on.room 应使用目标表面所在真实房间 {actual_room}'))
        if not _has_delta_predicate(sim_env, destination, 'item_is_dining_table'):
            return (False, 'official DELTA predicate failed', f'{destination} is not item_is_dining_table')
        if sim_env.get(destination, {}).get('is_container') is True and destination.endswith('_anchor'):
            return (False, '目标位置不合法', repair_feedback(observed=f'surface={destination}', required='surface 必须是具体表面节点', repair_actions=['place_on'], note='把 surface 改为当前环境中的真实表面实体，不要使用 room anchor'))
        return (True, '', '')

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        target = params.get('item', '') or sim_robot.get('robot_holding', '')
        sim_robot['robot_holding'] = '空'
        _set_parent(sim_env, target, params.get('surface', ''))
