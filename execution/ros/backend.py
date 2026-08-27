from adapters.ros_bridge import get_ros_bridge
from domain.runtime import commit_runtime_scene, preview_runtime_scene
from execution.common import apply_env_delta, print_execution_trace, resolve_action_target
from execution.result import ExecutionResult


def execute_ros_action(item, env: dict, action_category: str, remaining: int, total_remaining: int) -> ExecutionResult:
    """Execute one action through ROS, then mirror accepted effects into runtime state."""
    env.setdefault("robot_location", "初始位置")
    env.setdefault("robot_holding", "空")
    env["changed_objects"] = {}

    act_name, params, action_str, target, location = resolve_action_target(item)
    if not act_name:
        return ExecutionResult(ok=True, action_str=action_str, env_state=env)

    updated_scene, scene_ok, scene_error = preview_runtime_scene(act_name, target, location, params)
    if not scene_ok:
        return ExecutionResult(
            ok=False,
            action_str=action_str,
            env_state=env,
            error_feedback=scene_error or "运行态场景校验失败",
        )

    payload = {"action": act_name, "target": target, "location": location, "parameters": params}
    hardware_ok, hardware_error = get_ros_bridge().send_to_hardware(act_name, action_category, payload)
    if not hardware_ok:
        return ExecutionResult(
            ok=False,
            action_str=action_str,
            env_state=env,
            error_feedback=hardware_error or "硬件桥接执行失败",
        )

    commit_runtime_scene(updated_scene)
    apply_env_delta(env, act_name, target, location, action_str)

    print_execution_trace(action_str, env, remaining, total_remaining)
    return ExecutionResult(ok=True, action_str=action_str, env_state=env)
