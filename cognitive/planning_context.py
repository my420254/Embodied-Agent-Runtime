from __future__ import annotations

from dataclasses import replace

from domain.action_contracts import OPENABLE_CONTAINER_TYPES
from interfaces.contracts import PlanStep, TaskGraph, TodoList
from interfaces.services import BrainTask


def _scene_instances(graph: TaskGraph) -> list[dict]:
    return [
        node.data
        for node in graph.nodes
        if node.node_type == "scene_instance" and isinstance(node.data, dict)
    ]


def _first_instance(graph: TaskGraph, semantic_type: str) -> dict | None:
    return next((item for item in _scene_instances(graph) if item.get("type") == semantic_type), None)


def _instance_by_id(graph: TaskGraph, instance_id: str) -> dict | None:
    return next((item for item in _scene_instances(graph) if str(item.get("id") or "") == instance_id), None)


def _first_instance_any(graph: TaskGraph, semantic_types: tuple[str, ...]) -> dict | None:
    return next((item for item in _scene_instances(graph) if item.get("type") in semantic_types), None)


def _first_instance_excluding(graph: TaskGraph, semantic_type: str, excluded_ids: set[str]) -> dict | None:
    return next(
        (
            item
            for item in _scene_instances(graph)
            if item.get("type") == semantic_type and str(item.get("id") or "") not in excluded_ids
        ),
        None,
    )


def _preferred_instance(graph: TaskGraph, semantic_type: str, preferred_id: str = "") -> dict | None:
    preferred_id = preferred_id.strip()
    if preferred_id:
        preferred = next(
            (
                item
                for item in _scene_instances(graph)
                if item.get("type") == semantic_type and str(item.get("id") or "") == preferred_id
            ),
            None,
        )
        if preferred is not None:
            return preferred
    return _first_instance(graph, semantic_type)


def _preferred_instance_any(graph: TaskGraph, semantic_types: tuple[str, ...], preferred_id: str = "") -> dict | None:
    preferred_id = preferred_id.strip()
    if preferred_id:
        preferred = next(
            (
                item
                for item in _scene_instances(graph)
                if item.get("type") in semantic_types and str(item.get("id") or "") == preferred_id
            ),
            None,
        )
        if preferred is not None:
            return preferred
    return _first_instance_any(graph, semantic_types)


def _location(instance: dict | None) -> str:
    if not instance:
        return ""
    return str(instance.get("location") or instance.get("direct_parent") or instance.get("id") or "")


def _states(instance: dict | None) -> dict:
    if not instance or not isinstance(instance.get("states"), dict):
        return {}
    return instance["states"]


def _is_clean(instance: dict | None) -> bool:
    states = _states(instance)
    return states.get("isClean") is True or states.get("clean") is True


def _is_openable_container(instance: dict | None) -> bool:
    if not instance:
        return False
    instance_type = str(instance.get("type") or "")
    states = _states(instance)
    return "isOpen" in states or instance_type in OPENABLE_CONTAINER_TYPES


def _parent_openable_container(graph: TaskGraph, instance: dict | None) -> dict | None:
    if not instance:
        return None
    parent_id = str(instance.get("direct_parent") or "")
    if not parent_id:
        return None
    parent = _instance_by_id(graph, parent_id)
    if not _is_openable_container(parent):
        return None
    return parent


def _has_prior_open_step(steps: list[PlanStep], container_id: str) -> bool:
    return any(step.skill == "Open" and step.parameters.get("target_container") == container_id for step in steps)


def _append_navigation_step(steps: list[PlanStep], target_location: str) -> None:
    if not target_location:
        return
    if steps and steps[-1].skill == "NavigateTo" and steps[-1].parameters.get("target_location") == target_location:
        return
    steps.append(PlanStep(step=len(steps) + 1, skill="NavigateTo", parameters={"target_location": target_location}))


def _append_pickup_from_scene(
    graph: TaskGraph,
    steps: list[PlanStep],
    target: dict | None,
    *,
    robot_holding: str = "",
) -> None:
    if not target:
        return
    target_id = str(target.get("id") or "")
    if not target_id:
        return
    target_parent = str(target.get("direct_parent") or "")
    if robot_holding == target_id or target_parent == "robot_hand":
        return

    parent_container = _parent_openable_container(graph, target)
    parent_container_id = str(parent_container.get("id")) if parent_container else ""
    parent_container_states = _states(parent_container)

    if (
        parent_container_id
        and parent_container_states.get("isOpen") is not True
        and not _has_prior_open_step(steps, parent_container_id)
    ):
        _append_navigation_step(steps, parent_container_id)
        steps.append(
            PlanStep(
                step=len(steps) + 1,
                skill="Open",
                parameters={"target_container": parent_container_id},
                expected_effects=(f"{parent_container_id}.isOpen == true",),
            )
        )

    target_location = _location(target)
    if target_location and target_location != parent_container_id:
        _append_navigation_step(steps, target_location)

    pickup_preconditions = ["robot_holding == 空"]
    if parent_container_id:
        pickup_preconditions.append(f"{parent_container_id}.isOpen == true")
    steps.append(
        PlanStep(
            step=len(steps) + 1,
            skill="Pickup",
            parameters={"target_item": target_id},
            preconditions=tuple(pickup_preconditions),
            expected_effects=(f"robot_holding == {target_id}",),
        )
    )


def _robot_holding(task: BrainTask) -> str:
    current_robot = task.context.get("current_robot", {})
    if not isinstance(current_robot, dict):
        return ""
    return str(current_robot.get("robot_holding") or "")


def _robot_location(task: BrainTask) -> str:
    current_robot = task.context.get("current_robot", {})
    if not isinstance(current_robot, dict):
        return ""
    return str(current_robot.get("robot_location") or "")


def _task_contract(task: BrainTask) -> dict:
    contract_task = task.context.get("task", {})
    return contract_task if isinstance(contract_task, dict) else {}


def _validated_steps(task: BrainTask) -> list[dict]:
    steps = task.context.get("validated_steps", [])
    return [step for step in steps if isinstance(step, dict)]


def _task_target_name(task: BrainTask) -> str:
    return str(_task_contract(task).get("target_name") or "").strip()


def _task_container_name(task: BrainTask) -> str:
    return str(_task_contract(task).get("container_name") or "").strip()


def _task_water_source_name(task: BrainTask) -> str:
    return str(_task_contract(task).get("water_source_name") or "").strip()


def _task_named_value(task: BrainTask, key: str) -> str:
    return str(_task_contract(task).get(key) or "").strip()


def _type_plan_requires_turn_off(task: BrainTask) -> bool:
    contract_task = task.context.get("task", {})
    if not isinstance(contract_task, dict):
        return False
    desired_result = contract_task.get("desired_result", {})
    if isinstance(desired_result, dict) and str(desired_result.get("device_state") or "").strip().lower() == "off":
        return True
    post_actions = contract_task.get("post_actions", ())
    if isinstance(post_actions, (list, tuple, set)):
        return any(str(action).strip().lower() == "turn_off" for action in post_actions)
    return False


def _put_plan_requires_close(task: BrainTask) -> bool:
    contract_task = task.context.get("task", {})
    if not isinstance(contract_task, dict):
        return False
    desired_result = contract_task.get("desired_result", {})
    if isinstance(desired_result, dict) and str(desired_result.get("container_state") or "").strip().lower() == "closed":
        return True
    post_actions = contract_task.get("post_actions", ())
    if isinstance(post_actions, (list, tuple, set)):
        return any(str(action).strip().lower() in {"close", "close_container"} for action in post_actions)
    return False


def _apply_bt_recovery_suffix(task: BrainTask, todo: TodoList) -> TodoList:
    if _validated_steps(task):
        return todo
    recovery = task.context.get("bt_recovery", {})
    if not isinstance(recovery, dict):
        return todo
    failed_step = recovery.get("failed_step")
    try:
        failed_step_num = int(failed_step)
    except (TypeError, ValueError):
        return todo
    if failed_step_num <= 1 or failed_step_num > len(todo.steps):
        return todo
    suffix = todo.steps[failed_step_num - 1 :]
    return TodoList(
        steps=tuple(replace(step, step=index) for index, step in enumerate(suffix, start=1)),
        source_skill_id=todo.source_skill_id,
        task_graph_id=todo.task_graph_id,
    )
