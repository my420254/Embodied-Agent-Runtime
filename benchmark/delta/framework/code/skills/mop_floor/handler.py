from __future__ import annotations



from typing import Any

from benchmark.delta.framework.code.skills.feedback import repair_feedback
from benchmark.delta.framework.code.skills.delta_state import delta_has_predicate



UNKNOWN_ROOMS = {'', '未知', 'unknown'}

def _state(sim_env: dict, target: str) -> dict[str, Any]:
    return sim_env.setdefault(target, {}).setdefault('states', {})

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

def _properties(info: dict) -> set[str]:
    raw = info.get('properties', []) if isinstance(info, dict) else []
    if not isinstance(raw, (list, tuple, set)):
        return set()
    return {str(value) for value in raw if str(value)}

def _has_property(info: dict, value: str) -> bool:
    return value in _properties(info)

def _has_delta_predicate(sim_env: dict, item: str, predicate: str) -> bool:
    return delta_has_predicate(sim_env, item, predicate)

class MopFloorSkill:
    name = 'mop_floor'

    def validate(self, sim_env: dict, sim_robot: dict, params: dict):
        target_room = _as_room(params.get('room', ''))
        if not target_room:
            return (False, 'missing mop_floor parameter', 'mop_floor requires official DELTA parameter: room')
        if target_room not in sim_env:
            return (False, '无效的目标房间', f'目标房间 {target_room} 不在环境中')
        if _robot_room(sim_robot) not in {*UNKNOWN_ROOMS, target_room}:
            return (False, 'position precondition failed', repair_feedback(observed=f"robot_location={_robot_room(sim_robot)}", required=f'robot_location={target_room}', repair_actions=['goto']))
        tool = params.get('tool', '')
        if not tool:
            return (False, 'missing mop_floor parameter', 'mop_floor requires official DELTA parameter: tool')
        if tool not in sim_env:
            return (False, 'invalid DELTA tool', 'mop_floor.tool must be an item from the DELTA scene')
        if not _has_delta_predicate(sim_env, tool, 'item_is_mop'):
            return (False, 'official DELTA predicate failed', f'{tool} is not item_is_mop')
        if not _has_delta_predicate(sim_env, tool, 'item_pickable'):
            return (False, 'official DELTA predicate failed', f'{tool} is not item_pickable')
        if not _has_delta_predicate(sim_env, tool, 'item_accessible'):
            return (False, 'official DELTA predicate failed', f'{tool} is not item_accessible')
        if sim_robot.get('robot_holding') != tool:
            return (False, '手持物品不匹配', repair_feedback(observed=f"robot_holding={sim_robot.get('robot_holding')}", required=f'robot_holding={tool}', repair_actions=['pick']))
        tool_states = sim_env.get(tool, {}).get('states', {})
        if tool_states.get('isDirty') is True or tool_states.get('isClean') is False:
            return (False, '工具状态不满足', repair_feedback(observed=f'{tool}.isClean=false', required=f'{tool}.isClean=true', repair_actions=['clean_mop']))
        if sim_env.get(target_room, {}).get('states', {}).get('floor_clean') is True:
            return (False, '目标已完成', f'{target_room} 地面已清洁，无需重复 mop_floor')
        return (True, '', '')

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        target_room = _as_room(params.get('room', ''))
        tool = params.get('tool', '')
        room = target_room
        _state(sim_env, room)['floor_clean'] = True
        _state(sim_env, room)['isClean'] = True
        if tool in sim_env:
            _state(sim_env, tool)['isClean'] = False
            _state(sim_env, tool)['isDirty'] = True
        sim_robot['battery_full'] = False
