import copy 
import re
from typing import Any
try:
    from langchain_core.messages import HumanMessage
except Exception:  # pragma: no cover - fallback for lean test environments
    class HumanMessage:  # type: ignore[no-redef]
        def __init__(self, content: str):
            self.content = content

try:
    from langgraph.graph import END
except Exception:  # pragma: no cover - fallback for lean test environments
    END = "__end__"  # type: ignore[assignment]

from adapters.command_bus import (
    interrupt_bus_supports_prompt,
    normalize_interrupt_command,
    poll_interrupt_command,
    publish_interrupt_command,
)
from config.scene_state import get_runtime_session, set_runtime_session
from graph.state import ExecutionState 
from domain.actions import ACTION_DOMAINS, extract_action
from domain.scene import flat_scene_to_tree_from_base, flatten_scene
from execution import executor as execution_executor
from execution.common import get_item_info_from_house


# =====================================================================
# 1. 中断命令总线适配
# =====================================================================
def _normalize_interrupt_state(interrupt: Any) -> dict[str, Any] | None:
    if interrupt is None:
        return None
    if isinstance(interrupt, dict):
        if not interrupt:
            return None
        return normalize_interrupt_command(interrupt, source=str(interrupt.get("source") or "state"))
    if isinstance(interrupt, str):
        text = interrupt.strip()
        if not text:
            return None
        return normalize_interrupt_command(text, source="state")
    return None


def _consume_interrupt_command(state: dict[str, Any]) -> dict[str, Any] | None:
    interrupt = _normalize_interrupt_state(state.get("interrupt_signal"))
    if interrupt is not None:
        return interrupt
    bus_interrupt = poll_interrupt_command()
    if bus_interrupt is not None:
        return normalize_interrupt_command(bus_interrupt, source=str(bus_interrupt.get("source") or "bus"))
    return None


def _prompt_interrupt_command() -> dict[str, Any] | None:
    if not interrupt_bus_supports_prompt():
        return None
    try:
        print("  [中断窗口] 直接回车继续执行，输入新指令或控制命令则中断当前任务")
        user_in = input("  >>> ").strip()
    except EOFError:
        user_in = ""
    if not user_in:
        return None
    return publish_interrupt_command(user_in)


def _feature_enabled(state: dict, name: str, default: bool = False) -> bool:
    flags = state.get("feature_flags", {})
    if isinstance(flags, dict) and name in flags:
        return bool(flags[name])
    return default


def _compiled_behavior_tree_from_state(state: dict) -> dict | None:
    trace = state.get("cognitive_planning_trace", {})
    if not isinstance(trace, dict):
        return None
    behavior_tree = trace.get("behavior_tree", {})
    if isinstance(behavior_tree, dict) and behavior_tree.get("compiled") is True:
        return dict(behavior_tree)
    return None


def _current_task_has_pending_behavior_tree(state: dict) -> bool:
    stack = state.get("task_stack", [])
    if not stack:
        return False
    task = stack[-1]
    return bool(
        isinstance(task, dict)
        and isinstance(task.get("behavior_tree"), dict)
        and not task.get("behavior_tree_executed")
    )


def _checkpoint_suffix_repair(state: dict) -> dict:
    trace = state.get("cognitive_planning_trace", {})
    if not isinstance(trace, dict):
        return {}
    planning_node = trace.get("planning_node", {})
    if not isinstance(planning_node, dict):
        return {}
    repair = planning_node.get("checkpoint_suffix_repair", {})
    return dict(repair) if isinstance(repair, dict) else {}


def _executable_todo_list_from_state(state: dict, todo_list: list[dict] | None = None) -> list[dict]:
    source_todo = todo_list if todo_list is not None else state.get("todo_list")
    todo_list = [copy.deepcopy(step) for step in (source_todo or []) if isinstance(step, dict)]
    repair = _checkpoint_suffix_repair(state)
    if repair.get("reuse_validated_prefix") is not True:
        return todo_list
    try:
        prefix_len = int(repair.get("validated_step_count") or len(state.get("validated_steps") or []))
    except (TypeError, ValueError):
        prefix_len = 0
    if prefix_len <= 0 or prefix_len > len(todo_list):
        return todo_list
    return todo_list[prefix_len:]


def _executable_behavior_tree_from_state(state: dict, todo_list: list[dict]) -> dict | None:
    if not todo_list:
        return None
    behavior_tree = _compiled_behavior_tree_from_state(state)
    if not behavior_tree:
        return None
    full_todo = [step for step in (state.get("todo_list") or []) if isinstance(step, dict)]
    if len(todo_list) == len(full_todo):
        return behavior_tree
    try:
        from cognitive import compile_legacy_todo_list_to_behavior_tree

        compiled = compile_legacy_todo_list_to_behavior_tree(
            todo_list,
            source_skill_id=behavior_tree.get("source_skill_id"),
            task_graph_id=behavior_tree.get("task_graph_id"),
        )
    except Exception:
        return None
    return {**compiled.as_dict(), "compiled": True}


def _execution_start_env_state(state: dict, fallback_env: dict) -> dict:
    repair = _checkpoint_suffix_repair(state)
    checkpoint_robot = state.get("checkpoint_robot", {})
    if repair.get("reuse_validated_prefix") is True and isinstance(checkpoint_robot, dict) and checkpoint_robot:
        return copy.deepcopy(checkpoint_robot)
    return fallback_env


def _restore_runtime_checkpoint_scene(state: dict, robot_state: dict) -> None:
    repair = _checkpoint_suffix_repair(state)
    checkpoint_env = state.get("checkpoint_env", {})
    if repair.get("reuse_validated_prefix") is not True or not isinstance(checkpoint_env, dict):
        return
    runtime_scene = get_runtime_session()
    flat_env = flatten_scene(runtime_scene)
    for name, info in checkpoint_env.items():
        flat_env[name] = copy.deepcopy(info) if isinstance(info, dict) else info
    held_item = str((robot_state or {}).get("robot_holding") or "空")
    if held_item and held_item != "空" and held_item in flat_env:
        item_info = flat_env.get(held_item, {})
        if isinstance(item_info, dict):
            patched = copy.deepcopy(item_info)
            patched["direct_parent"] = "robot_hand"
            flat_env[held_item] = patched
    set_runtime_session(flat_scene_to_tree_from_base(flat_env, robot_state, runtime_scene))


def _task_payload_from_state(state: dict, todo_list: list[dict]) -> dict:
    executable_todo_list = _executable_todo_list_from_state(state, todo_list)
    task = {
        "instruction": state.get("structured_task", {}).get("intent", state.get("raw_instruction", "主线任务")),
        "todo_list": executable_todo_list,
    }
    if _feature_enabled(state, "cognitive_bt_execute"):
        behavior_tree = _executable_behavior_tree_from_state(state, executable_todo_list)
        if behavior_tree:
            task["behavior_tree"] = behavior_tree
            task["behavior_tree_executed"] = False
    return task


def _interrupt_task_payload(state: dict, interrupt: dict[str, Any]) -> dict:
    task = {
        "instruction": interrupt.get("intent", interrupt.get("text", "新任务")),
        "todo_list": list(interrupt.get("new_todo_list", [])),
    }
    if _feature_enabled(state, "cognitive_bt_execute") and isinstance(interrupt.get("behavior_tree"), dict):
        task["behavior_tree"] = dict(interrupt["behavior_tree"])
        task["behavior_tree_executed"] = False
    return task


def _cancel_all_state(task_stack: list[dict], env: dict, interrupt: dict[str, Any]) -> dict:
    del task_stack
    print(f"\n  [任务管理] 收到终止指令：「{interrupt.get('intent', '取消任务')}」。")
    print("  [系统警报] 任务栈已清空。")
    return {
        "task_stack": [],
        "env_state": env,
        "execution_status": "cancelled",
        "interrupt_signal": None,
    }


def _cancel_current_state(task_stack: list[dict], env: dict, interrupt: dict[str, Any]) -> dict:
    done = task_stack.pop().get("instruction", "") if task_stack else ""
    print(f"\n  [任务管理] 收到取消当前任务指令：「{interrupt.get('intent', '取消当前任务')}」。")
    if task_stack:
        print(f"  [任务管理] 「{done}」已取消，恢复执行底层的「{task_stack[-1].get('instruction', '')}」。")
        status = "running"
    else:
        print("  [任务管理] 当前任务已取消，任务栈为空。")
        status = "cancelled"
    return {
        "task_stack": task_stack,
        "env_state": env,
        "execution_status": status,
        "interrupt_signal": None,
    }


def _handle_interrupt_command(state: dict, task_stack: list[dict], env: dict, interrupt: dict[str, Any]) -> dict:
    kind = interrupt.get("kind")
    if kind == "resume":
        return {
            "task_stack": task_stack,
            "env_state": env,
            "execution_status": "running",
            "interrupt_signal": None,
        }
    if kind == "cancel_all" or interrupt.get("is_cancel_all"):
        return _cancel_all_state(task_stack, env, interrupt)
    if kind == "cancel_current":
        return _cancel_current_state(task_stack, env, interrupt)
    if kind == "pause":
        print(f"\n  [任务管理] 收到暂停指令：「{interrupt.get('intent', '暂停当前任务')}」。")
        return {
            "task_stack": task_stack,
            "env_state": env,
            "execution_status": "paused",
            "interrupt_signal": None,
        }

    if interrupt.get("new_todo_list"):
        new_task = _interrupt_task_payload(state, interrupt)
        task_stack.append(new_task)
        print(f"\n  [任务管理] 新任务已压栈：「{new_task['instruction']}」")
        return {
            "task_stack": task_stack,
            "env_state": env,
            "execution_status": "running",
            "interrupt_signal": None,
        }

    text = str(interrupt.get("text") or interrupt.get("intent") or "").strip()
    if text:
        print("\n  [任务管理] 收到外部中断命令。原任务就地挂起，系统状态封存！")
        return {
            "task_stack": task_stack,
            "env_state": env,
            "execution_status": "interrupted",
            "interrupt_signal": interrupt,
            "messages": [HumanMessage(content=text)],
        }

    return {
        "task_stack": task_stack,
        "env_state": env,
        "execution_status": "running",
        "interrupt_signal": None,
    }


# =====================================================================
# 3. 节点 1：任务管理
# =====================================================================
def task_manager_node(state: ExecutionState) -> ExecutionState: 
    task_stack = copy.deepcopy(state.get("task_stack", [])) 
    env        = _execution_start_env_state(state, copy.deepcopy(state.get("env_state", {}))) 

    # 首次进入：将规划层 todo_list 压入任务栈。
    if not task_stack: 
        todo_list = state.get("todo_list", []) 
        if todo_list: 
            _restore_runtime_checkpoint_scene(state, env)
            task_stack = [_task_payload_from_state(state, list(todo_list))]

    # 硬件失败透传：保留给未来真实硬件桥接使用。
    if state.get("execution_status") == "failed": 
        return state 

    # 中断检测：只消费 CommandBus 的结构化命令，不关心命令来自控制台、API 还是 ROS。
    interrupt = _consume_interrupt_command(state)
    if interrupt:
        return _handle_interrupt_command(state, task_stack, env, interrupt)

    # 当前任务完成后弹栈，并恢复下层任务。
    if task_stack and len(task_stack[-1].get("todo_list", [])) == 0: 
        done = task_stack[-1].get("instruction", "") 
        task_stack.pop() 
        
        if not task_stack: 
            print("\n  [任务管理] 栈内指令全部执行完毕！") 
            return {"task_stack": task_stack, "env_state": env, "execution_status": "success"} 
        else: 
            print(f"\n  [任务管理] 「{done}」完成，弹出栈顶。恢复执行底层的「{task_stack[-1].get('instruction','')}」") 
            return {"task_stack": task_stack, "env_state": env, "execution_status": "running"} 

    return {"task_stack": task_stack, "env_state": env, "execution_status": "running"} 


# =====================================================================
# 4. 节点 2：动作分类
# =====================================================================
def task_classification_node(state: ExecutionState) -> ExecutionState: 
    task_stack = copy.deepcopy(state.get("task_stack", [])) 
    if not task_stack or not task_stack[-1].get("todo_list"): 
        return state 

    item       = task_stack[-1]["todo_list"][0] 
    act_name, _, _ = extract_action(item)
    act_name = act_name or "未知动作"

    category = ACTION_DOMAINS.get(act_name, "通用控制") 
    return {"current_action_category": category} 


# =====================================================================
# 5. 节点 3：模拟执行
# 任务管理层只负责取当前动作、调用 simulation、消费返回结果。
# =====================================================================
def simulate_action_node(state: ExecutionState) -> ExecutionState: 
    task_stack = copy.deepcopy(state.get("task_stack", [])) 
    env        = copy.deepcopy(state.get("env_state", {})) 

    if not task_stack or not task_stack[-1].get("todo_list"): 
        return state 

    cur_task   = task_stack[-1] 
    item       = copy.deepcopy(cur_task["todo_list"][0])
    act_name, _, action_str = extract_action(item)
    if not act_name:
        cur_task["todo_list"].pop(0) 
        return {"task_stack": task_stack, "env_state": env, "execution_status": "running"} 

    remaining_after_action = len(cur_task["todo_list"]) - 1
    total_remaining_after_action = sum(len(t.get("todo_list", [])) for t in task_stack) - 1
    result = execution_executor.execute_action(
        item,
        env,
        state.get("current_action_category", ""),
        remaining_after_action,
        total_remaining_after_action,
    )
    if not result.ok:
        return {
            "task_stack": task_stack,
            "env_state": result.env_state,
            "execution_status": "failed",
            "failed_action": result.action_str or action_str,
            "error_feedback": result.error_feedback,
            "failure_layer": result.failure_layer,
        }

    cur_task["todo_list"].pop(0) 
    remaining = len(cur_task["todo_list"]) 

    if remaining > 0 and state.get("allow_interrupt_input", False): 
        interrupt = _prompt_interrupt_command()
        if interrupt: 
            label = interrupt.get("text") or interrupt.get("intent") or interrupt.get("kind")
            print(f"  [中断已记录] \"{label}\" 将在下一调度周期触发\n") 

    return {"task_stack": task_stack, "env_state": result.env_state, "execution_status": "running"} 


def execute_behavior_tree_node(state: ExecutionState) -> ExecutionState:
    task_stack = copy.deepcopy(state.get("task_stack", []))
    env = copy.deepcopy(state.get("env_state", {}))

    if not task_stack or not task_stack[-1].get("behavior_tree"):
        return state

    cur_task = task_stack[-1]
    original_todo = copy.deepcopy(cur_task.get("todo_list", []))
    behavior_tree_payload = cur_task.get("behavior_tree", {})
    try:
        from cognitive import behavior_tree_from_dict, execute_behavior_tree

        behavior_tree = behavior_tree_from_dict(behavior_tree_payload)
    except Exception as exc:
        return _bt_failure_state(task_stack, env, "BehaviorTree", f"BT 载入失败: {exc}")

    context = {
        "env_state": env,
        "total_actions": _count_executable_actions(behavior_tree_payload),
        "action_index": 0,
    }
    result = execute_behavior_tree(
        behavior_tree,
        action_runner=_bt_action_runner,
        condition_checker=_bt_condition_checker,
        context=context,
    )
    execution_trace = result.as_dict()
    cognitive_trace = _merge_behavior_tree_execution_trace(state, execution_trace)
    cur_task["behavior_tree_executed"] = True
    if not result.succeeded:
        execution_failure = _bt_primitive_execution_failure(execution_trace)
        replan_request = {} if execution_failure else _bt_replan_request(execution_trace)
        failed_step = _bt_failed_step(execution_failure, replan_request, result.node_id)
        runtime_checkpoint = _bt_runtime_checkpoint(state, original_todo, failed_step, context.get("env_state", env))
        cur_task["todo_list"] = _bt_remaining_todo_suffix(cur_task.get("todo_list", []), failed_step)
        failure_state = {
            "failure_layer": "planning" if replan_request else "execution",
            "error_feedback": _bt_failure_feedback(result, execution_trace, execution_failure),
        }
        if replan_request:
            budget_exhausted = _bt_direct_replan_budget_exhausted(state)
            cognitive_trace = _record_bt_recovery_budget_event(
                cognitive_trace,
                state,
                exhausted=budget_exhausted,
            )
            failure_state.update(
                {
                    "next_routing": "retry_planning",
                    "corrected_plan_hint": replan_request.get("hint", ""),
                    "failure_reason": "behavior_tree_replan_requested",
                    "bt_recovery_retry_budget_exhausted": budget_exhausted,
                }
            )
        return {
            "task_stack": task_stack,
            "env_state": context.get("env_state", env),
            "execution_status": "failed",
            "failed_action": _bt_failed_action_name(cur_task.get("todo_list", []), failed_step, execution_failure, result.node_id),
            "behavior_tree_execution": execution_trace,
            "cognitive_planning_trace": cognitive_trace,
            **runtime_checkpoint,
            **failure_state,
        }

    cur_task["todo_list"] = []
    return {
        "task_stack": task_stack,
        "env_state": context.get("env_state", env),
        "execution_status": "running",
        "behavior_tree_execution": execution_trace,
        "cognitive_planning_trace": cognitive_trace,
    }


def _bt_action_runner(action: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    skill = str(action.get("skill") or "")
    parameters = action.get("parameters") or {}
    if skill == "RepairOrReplan":
        failed_step = parameters.get("failed_step")
        failure_policy = parameters.get("failure_policy", {})
        return {
            "ok": False,
            "status": "failure",
            "error": "BehaviorTree recovery requested repair_or_replan",
            "replan_requested": True,
            "failed_step": failed_step,
            "failure_policy": failure_policy,
            "hint": _bt_replan_hint(failed_step, failure_policy),
        }
    if not skill or not isinstance(parameters, dict):
        return {"ok": False, "status": "failure", "error": "invalid BehaviorTree action payload"}

    item = {"execution": {"skill": skill, "parameters": dict(parameters)}}
    action_index = int(context.get("action_index", 0) or 0)
    total_actions = int(context.get("total_actions", 1) or 1)
    remaining = max(total_actions - action_index - 1, 0)
    result = execution_executor.execute_action(
        item,
        context.setdefault("env_state", {}),
        ACTION_DOMAINS.get(skill, "通用控制"),
        remaining,
        remaining,
    )
    context["action_index"] = action_index + 1
    context["env_state"] = result.env_state
    return {
        "ok": bool(result.ok),
        "status": "success" if result.ok else "failure",
        "message": result.action_str,
        "error": result.error_feedback,
        "failure_layer": result.failure_layer,
    }


def _bt_condition_checker(condition: str, context: dict[str, Any]) -> bool:
    if "==" not in condition:
        return False
    left, right = (part.strip() for part in condition.split("==", 1))
    expected = _parse_condition_value(right)
    env = context.get("env_state", {})
    if left == "robot_holding":
        return env.get("robot_holding", "空") == expected
    if "." not in left:
        return False
    object_id, attr = left.split(".", 1)
    info = get_item_info_from_house(object_id)
    if not info.get("found"):
        return False
    if attr == "direct_parent":
        return info.get("direct_parent") == expected
    states = info.get("states", {})
    if isinstance(states, dict) and attr in states:
        return states.get(attr) == expected
    return False


def _bt_replan_request(execution_trace: dict) -> dict[str, Any]:
    events = execution_trace.get("events", [])
    if not isinstance(events, list):
        return {}
    for event in events:
        action_result = event.get("action_result", {}) if isinstance(event, dict) else {}
        if isinstance(action_result, dict) and action_result.get("replan_requested") is True:
            return dict(action_result)
    return {}


def _bt_primitive_execution_failure(execution_trace: dict) -> dict[str, Any]:
    events = execution_trace.get("events", [])
    if not isinstance(events, list):
        return {}
    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("node_type") != "Action" or event.get("name") == "repair_or_replan":
            continue
        action_result = event.get("action_result", {})
        if (
            event.get("status") == "failure"
            and isinstance(action_result, dict)
            and action_result.get("failure_layer", "execution") == "execution"
        ):
            return event
    return {}


def _bt_failure_feedback(result, execution_trace: dict, execution_failure: dict[str, Any] | None = None) -> str:
    if execution_failure:
        action_result = execution_failure.get("action_result", {})
        if isinstance(action_result, dict):
            return str(action_result.get("error") or action_result.get("message") or result.message)
    replan_request = _bt_replan_request(execution_trace)
    if replan_request:
        return replan_request.get("hint") or replan_request.get("error") or "BehaviorTree 请求重规划"
    events = execution_trace.get("events", [])
    if isinstance(events, list):
        for event in events:
            action_result = event.get("action_result", {}) if isinstance(event, dict) else {}
            if isinstance(action_result, dict) and action_result.get("error"):
                return str(action_result["error"])
    return result.message or "BehaviorTree 执行失败"


def _bt_failed_step(
    execution_failure: dict[str, Any] | None,
    replan_request: dict[str, Any] | None,
    fallback_node_id: str = "",
) -> int | None:
    if isinstance(replan_request, dict):
        failed_step = _coerce_step_number(replan_request.get("failed_step"))
        if failed_step is not None:
            return failed_step
    if isinstance(execution_failure, dict):
        failed_step = _step_from_node_id(execution_failure.get("node_id"))
        if failed_step is not None:
            return failed_step
    return _step_from_node_id(fallback_node_id)


def _bt_remaining_todo_suffix(todo_list: list[dict], failed_step: int | None) -> list[dict]:
    if failed_step is None:
        return list(todo_list)
    for index, item in enumerate(todo_list):
        step = _coerce_step_number(item.get("step") if isinstance(item, dict) else None)
        if step == failed_step:
            return list(todo_list[index:])
    return list(todo_list)


def _bt_failed_action_name(
    remaining_todo: list[dict],
    failed_step: int | None,
    execution_failure: dict[str, Any] | None,
    fallback_name: str,
) -> str:
    if isinstance(execution_failure, dict) and execution_failure.get("name"):
        return str(execution_failure["name"])
    if failed_step is not None:
        for item in remaining_todo:
            if not isinstance(item, dict):
                continue
            step = _coerce_step_number(item.get("step"))
            execution = item.get("execution", {})
            if step == failed_step and isinstance(execution, dict) and execution.get("skill"):
                return str(execution["skill"])
    return fallback_name


def _bt_runtime_checkpoint(
    state: dict,
    original_todo: list[dict],
    failed_step: int | None,
    env_state: dict,
) -> dict[str, Any]:
    if failed_step is None:
        return {}
    prefix = _bt_validated_prefix(original_todo, failed_step)
    if not prefix:
        return {}
    existing = [copy.deepcopy(step) for step in (state.get("validated_steps") or []) if isinstance(step, dict)]
    merged = _merge_runtime_validated_steps(existing, prefix)
    runtime_scene = get_runtime_session()
    checkpoint_env = (
        copy.deepcopy(flatten_scene(runtime_scene))
        if isinstance(runtime_scene, dict)
        else copy.deepcopy(state.get("checkpoint_env", {}))
    )
    checkpoint_robot = copy.deepcopy(env_state) if isinstance(env_state, dict) else {}
    return {
        "validated_steps": merged,
        "checkpoint_env": checkpoint_env,
        "checkpoint_robot": checkpoint_robot,
    }


def _bt_validated_prefix(todo_list: list[dict], failed_step: int) -> list[dict]:
    prefix: list[dict] = []
    for item in todo_list:
        if not isinstance(item, dict):
            continue
        step = _coerce_step_number(item.get("step"))
        if step is None or step >= failed_step:
            break
        prefix.append(copy.deepcopy(item))
    return prefix


def _merge_runtime_validated_steps(existing: list[dict], runtime_prefix: list[dict]) -> list[dict]:
    if not existing:
        return runtime_prefix
    prefix_start = 0
    if len(runtime_prefix) >= len(existing):
        existing_slice = runtime_prefix[: len(existing)]
        if existing_slice == existing:
            prefix_start = len(existing)
    return existing + runtime_prefix[prefix_start:]


def _bt_replan_hint(failed_step: Any, failure_policy: Any) -> str:
    policy = failure_policy if isinstance(failure_policy, dict) else {}
    policy_hint = policy.get("on_failed") or policy.get("strategy") or "repair_plan"
    if failed_step is None:
        return f"BehaviorTree recovery requested {policy_hint}; replan from the failed BT node."
    return f"BehaviorTree recovery requested {policy_hint}; replan from failed step {failed_step}."


def _step_from_node_id(node_id: Any) -> int | None:
    if not isinstance(node_id, str):
        return None
    match = re.match(r"step_(\d+)_", node_id)
    if not match:
        return None
    return _coerce_step_number(match.group(1))


def _coerce_step_number(value: Any) -> int | None:
    try:
        step = int(value)
    except (TypeError, ValueError):
        return None
    return step if step > 0 else None


def _bt_direct_replan_budget(state: dict) -> int:
    flags = state.get("feature_flags", {})
    raw_budget = flags.get("cognitive_bt_direct_replan_budget", 1) if isinstance(flags, dict) else 1
    try:
        budget = int(raw_budget)
    except (TypeError, ValueError):
        budget = 1
    return max(budget, 0)


def _bt_direct_replan_count(state: dict) -> int:
    try:
        return int(state.get("bt_recovery_direct_replan_count") or state.get("direct_replan_count") or 0)
    except (TypeError, ValueError):
        return 0


def _bt_direct_replan_budget_exhausted(state: dict) -> bool:
    return (
        _feature_enabled(state, "cognitive_bt_recovery_direct_replan")
        and _bt_direct_replan_count(state) >= _bt_direct_replan_budget(state)
    )


def _record_bt_recovery_budget_event(trace: dict, state: dict, *, exhausted: bool) -> dict:
    enriched = dict(trace) if isinstance(trace, dict) else {}
    events = enriched.get("bt_recovery_retry_budget", [])
    if not isinstance(events, list):
        events = []
    events.append(
        {
            "budget": _bt_direct_replan_budget(state),
            "used": _bt_direct_replan_count(state),
            "exhausted": bool(exhausted),
            "route": "Retry_Planning",
            "stage": "behavior_tree_execution",
        }
    )
    enriched["bt_recovery_retry_budget"] = events
    return enriched


def _merge_behavior_tree_execution_trace(state: dict, execution_trace: dict) -> dict:
    trace = state.get("cognitive_planning_trace", {})
    if not isinstance(trace, dict):
        trace = {}
    enriched = {**trace, "behavior_tree_execution": dict(execution_trace)}
    if _feature_enabled(state, "cognitive_trace_write"):
        try:
            from cognitive.trace_store import JsonlTraceRecorder

            trace_id = JsonlTraceRecorder().record(enriched)
            enriched["trace_storage"] = {
                "written": True,
                "trace_id": trace_id,
                "format": "jsonl",
                "stage": "behavior_tree_execution",
            }
        except Exception as exc:
            enriched["trace_storage"] = {
                "written": False,
                "error": str(exc),
                "format": "jsonl",
                "stage": "behavior_tree_execution",
            }
    return enriched


def _parse_condition_value(value: str) -> Any:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return value


def _count_executable_actions(payload: dict) -> int:
    def walk(node: dict) -> int:
        action = node.get("action", {}) if isinstance(node, dict) else {}
        count = 0
        if isinstance(action, dict) and action.get("skill") and action.get("skill") != "RepairOrReplan":
            count += 1
        children = node.get("children", []) if isinstance(node, dict) else []
        if isinstance(children, list):
            count += sum(walk(child) for child in children)
        return count

    root = payload.get("root", {}) if isinstance(payload, dict) else {}
    return max(walk(root), 1)


def _bt_failure_state(task_stack: list[dict], env: dict, failed_action: str, error: str) -> dict:
    return {
        "task_stack": task_stack,
        "env_state": env,
        "execution_status": "failed",
        "failed_action": failed_action,
        "error_feedback": error,
        "failure_layer": "execution",
    }


# =====================================================================
# 6. 图结构定义与路由
# =====================================================================
def route_after_manager(state: ExecutionState) -> str: 
    status = state.get("execution_status") 
    if not state.get("task_stack") or status in ("success", "failed", "interrupted", "paused", "cancelled"): 
        return END 
    if _feature_enabled(state, "cognitive_bt_execute") and _current_task_has_pending_behavior_tree(state):
        return "behavior_tree_execute"
    return "task_classification" 

def route_after_simulation(state: ExecutionState) -> str: 
    if state.get("execution_status") == "failed": 
        return END 
    return "task_manager" 

def build_task_management_graph(): 
    try:
        from langgraph.graph import StateGraph
    except Exception as exc:  # pragma: no cover - fail-soft import boundary
        raise RuntimeError("langgraph is required to build the task management graph") from exc

    workflow = StateGraph(ExecutionState) 
    workflow.add_node("task_manager",        task_manager_node) 
    workflow.add_node("behavior_tree_execute", execute_behavior_tree_node)
    workflow.add_node("task_classification", task_classification_node) 
    workflow.add_node("simulate_action",     simulate_action_node) 
    workflow.set_entry_point("task_manager") 
    workflow.add_conditional_edges("task_manager",        route_after_manager) 
    workflow.add_edge("behavior_tree_execute", "task_manager")
    workflow.add_edge("task_classification", "simulate_action") 
    workflow.add_conditional_edges("simulate_action",     route_after_simulation) 
    return workflow.compile()
