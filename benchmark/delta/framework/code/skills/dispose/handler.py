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

def _properties(info: dict) -> set[str]:
    raw = info.get('properties', []) if isinstance(info, dict) else []
    if not isinstance(raw, (list, tuple, set)):
        return set()
    return {str(value) for value in raw if str(value)}

def _has_property(info: dict, value: str) -> bool:
    return value in _properties(info)

def _has_delta_predicate(sim_env: dict, item: str, predicate: str) -> bool:
    return delta_has_predicate(sim_env, item, predicate)

class DisposeSkill:
    name = 'dispose'

    def validate(self, sim_env: dict, sim_robot: dict, params: dict):
        target = params.get('item', '')
        disposal_target = params.get('disposal', '')
        room = params.get('room', '')
        if not target or not disposal_target or (not room):
            return (False, 'missing dispose parameter', 'dispose requires official DELTA parameters: item, disposal, room')
        if target not in sim_env:
            return (False, 'invalid DELTA item', 'dispose.item must be an item from the DELTA scene')
        if disposal_target not in sim_env:
            return (False, 'invalid DELTA disposal', 'dispose.disposal must be an item from the DELTA scene')
        if not _has_delta_predicate(sim_env, target, 'item_pickable'):
            return (False, 'official DELTA predicate failed', f'{target} is not item_pickable; dispose.item must be pickable')
        if not _has_delta_predicate(sim_env, target, 'item_accessible'):
            return (False, 'official DELTA predicate failed', f'{target} is not item_accessible; make it accessible before dispose')
        if not _has_delta_predicate(sim_env, disposal_target, 'item_is_rubbish_bin'):
            return (False, 'official DELTA predicate failed', f'{disposal_target} is not item_is_rubbish_bin')
        if _item_room(disposal_target, sim_env) != room:
            actual_room = _item_room(disposal_target, sim_env)
            return (False, 'disposal room mismatch', repair_feedback(observed=f'{disposal_target}.room={actual_room}', required=f'{disposal_target}.room={room}', repair_actions=['goto', 'dispose'], note=f'dispose.room 应使用垃圾桶所在真实房间 {actual_room}'))
        if sim_env.get(target, {}).get('states', {}).get('isDisposed') is True:
            return (False, '目标已处理', f'{target} 已被处理/丢弃，无需重复 dispose')
        if sim_robot.get('robot_holding') != target:
            return (False, '手持物品不匹配', repair_feedback(observed=f"robot_holding={sim_robot.get('robot_holding')}", required=f'robot_holding={target}', repair_actions=['pick']))
        if room and _robot_room(sim_robot) not in {*UNKNOWN_ROOMS, room}:
            return (False, 'position precondition failed', repair_feedback(observed=f"robot_location={_robot_room(sim_robot)}", required=f'robot_location={room}', repair_actions=['goto']))
        return (True, '', '')

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        target = params.get('item', '')
        disposal_target = params.get('disposal', '')
        _state(sim_env, target)['isDisposed'] = True
        _set_parent(sim_env, target, disposal_target)
        if sim_robot.get('robot_holding') == target:
            sim_robot['robot_holding'] = '空'
        sim_robot['battery_full'] = False
