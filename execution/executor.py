from config.settings import get_config
from execution.result import ExecutionResult

# 这个函数 execution_backend 用于获取当前配置的执行后端。
# 函数从配置中读取 "execution" 模块下的 "backend" 键的值，如果没有设置则默认为 "simulation"。函数返回一个字符串，表示当前使用的执行后端。
def execution_backend() -> str:
    backend = get_config("execution", "backend", default="simulation")
    return str(backend or "simulation").strip().lower()

# 这个函数 execute_action 用于将已经规划好的动作分发到配置的执行后端进行执行。
# 函数接受以下参数：
# - item: 表示要执行的动作项，通常是一个包含动作信息的数据
# - env: 一个字典，表示当前的环境状态
# - action_category: 一个字符串，表示动作的类别
# - remaining: 一个整数，表示当前任务剩余的步骤数
# - total_remaining: 一个整数，表示全局剩余的步骤数
# 函数首先调用 execution_backend() 来获取当前配置的执行后端，然后根据后端类型调用相应的执行函数来执行动作。
# 如果后端是 "simulation"，则调用 execute_simulated_action；
# 如果后端是 "ros"，则调用 execute_ros_action。如果后端类型未知，则返回一个 ExecutionResult 对象，表示执行失败，并包含错误反馈信息。
def execute_action(item, env: dict, action_category: str, remaining: int, total_remaining: int):
    """Dispatch an already-planned action to the configured execution backend."""
    backend = execution_backend()
    if backend == "simulation":
        from execution.simulation import execute_simulated_action

        return execute_simulated_action(item, env, action_category, remaining, total_remaining)
    if backend == "ros":
        from execution.ros import execute_ros_action

        return execute_ros_action(item, env, action_category, remaining, total_remaining)

    return ExecutionResult(
        ok=False,
        env_state=env,
        error_feedback=f"未知执行后端: {backend}",
    )
