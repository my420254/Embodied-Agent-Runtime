from __future__ import annotations

from benchmark.delta.framework.code.skills.feedback import repair_feedback
from benchmark.delta.framework.code.skills.delta_state import delta_has_predicate



UNKNOWN_ROOMS = {'', '未知', 'unknown'}

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

class ChargeSkill:
    name = 'charge'

    def validate(self, sim_env: dict, sim_robot: dict, params: dict):
        station = params.get('station', '')
        room = params.get('room', '')
        if not station or not room:
            return (False, 'missing charge parameter', 'charge requires official DELTA parameters: station, room')
        if station not in sim_env:
            return (False, 'invalid DELTA station', 'charge.station must be an item from the DELTA scene')
        if not _has_delta_predicate(sim_env, station, 'item_is_robot_hub'):
            return (False, 'official DELTA predicate failed', f'{station} is not item_is_robot_hub')
        if not _has_delta_predicate(sim_env, station, 'item_accessible'):
            return (False, 'official DELTA predicate failed', f'{station} is not item_accessible')
        if _item_room(station, sim_env) != room:
            actual_room = _item_room(station, sim_env)
            return (False, 'station room mismatch', repair_feedback(observed=f'{station}.room={actual_room}', required=f'{station}.room={room}', repair_actions=['goto', 'charge'], note=f'charge.room 应使用充电设施所在真实房间 {actual_room}'))
        if sim_robot.get('robot_holding') not in {'', '空', None}:
            return (False, '机械臂冲突', repair_feedback(observed=f"robot_holding={sim_robot.get('robot_holding')}", required='robot_holding=空', repair_actions=['drop', 'drop_loadable']))
        if sim_robot.get('battery_full') is True:
            return (False, '目标已完成', 'battery_full is already true; charge is only valid when the battery is not full')
        if room and _robot_room(sim_robot) not in {*UNKNOWN_ROOMS, room}:
            return (False, 'position precondition failed', repair_feedback(observed=f"robot_location={_robot_room(sim_robot)}", required=f'robot_location={room}', repair_actions=['goto']))
        return (True, '', '')

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        sim_robot['battery_full'] = True
