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

class AssembleSkill:
    name = 'assemble'

    def validate(self, sim_env: dict, sim_robot: dict, params: dict):
        workspace = _as_room(params.get('room', ''))
        target_pc = params.get('target_pc', '')
        component_names = ['mainboard', 'cpu', 'ram', 'ssd', 'gpu', 'psu']
        components = [params.get(name, '') for name in component_names]
        if not workspace or not target_pc or any((not component for component in components)):
            return (False, 'missing assemble parameter', 'assemble requires room, mainboard, cpu, ram, ssd, gpu, psu, target_pc')
        if not _room_exists(workspace, sim_env):
            return (False, 'invalid DELTA room', 'assemble.room must be a room from the DELTA scene')
        if workspace and _robot_room(sim_robot) not in {*UNKNOWN_ROOMS, workspace}:
            return (False, 'position precondition failed', repair_feedback(observed=f"robot_location={_robot_room(sim_robot)}", required=f'robot_location={workspace}', repair_actions=['goto']))
        if sim_robot.get('robot_holding') not in {'', '空', None}:
            return (False, '机械臂冲突', repair_feedback(observed=f"robot_holding={sim_robot.get('robot_holding')}", required='robot_holding=空', repair_actions=['drop', 'drop_loadable']))
        if sim_env.get(target_pc, {}).get('states', {}).get('isAssembled') is True:
            return (False, '目标已完成', f'{target_pc} already satisfies pc_assembled')
        missing_entities = [component for component in components if component not in sim_env]
        if missing_entities:
            return (False, 'invalid DELTA component', f"assemble components must exist in the DELTA scene: {', '.join(missing_entities)}")
        expected_predicates = {'mainboard': 'item_is_mainboard', 'cpu': 'item_is_cpu', 'ram': 'item_is_ram', 'ssd': 'item_is_ssd', 'gpu': 'item_is_gpu', 'psu': 'item_is_psu'}
        wrong_components = [f'{param_name}={component}' for (param_name, component) in zip(component_names, components) if not _has_delta_predicate(sim_env, component, expected_predicates[param_name])]
        if wrong_components:
            return (False, 'official DELTA predicate failed', 'assemble component type mismatch: ' + ', '.join(wrong_components))
        blocked_components = [component for component in components if not _has_delta_predicate(sim_env, component, 'item_pickable') or not _has_delta_predicate(sim_env, component, 'item_accessible')]
        if blocked_components:
            return (False, 'official DELTA predicate failed', 'assemble components must be item_pickable and item_accessible: ' + ', '.join(blocked_components))
        missing_components = [component for component in components if _item_room(component, sim_env) != workspace]
        if missing_components:
            return (False, '组件位置不满足', repair_feedback(observed=f"组件不在 {workspace}: {', '.join(missing_components)}", required=f'所有 PC 组件都位于 {workspace}', repair_actions=['pick', 'drop']))
        return (True, '', '')

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        target = params.get('target_pc', '')
        workspace = _as_room(params.get('room', ''))
        sim_env.setdefault(target, {'direct_parent': workspace, 'states': {}, 'is_container': False, 'full_path': []})
        _state(sim_env, target)['isAssembled'] = True
