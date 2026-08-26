from __future__ import annotations

from typing import Any

from interfaces.contracts import BehaviorTree, BehaviorTreeNode, PlanStep, TodoList


def compile_todo_list_to_behavior_tree(todo_list: TodoList) -> BehaviorTree:
    """Compile an audited primitive TodoList into a minimal BehaviorTree schema."""

    if not todo_list.steps:
        raise ValueError("cannot compile empty todo_list to behavior tree")

    root = BehaviorTreeNode(
        node_id="bt_root",
        node_type="Sequence",
        name="todo_list_sequence",
        children=tuple(_compile_step(step) for step in todo_list.steps),
        metadata={"step_count": len(todo_list.steps)},
    )
    return BehaviorTree(
        root=root,
        source="todo_list",
        source_skill_id=todo_list.source_skill_id,
        task_graph_id=todo_list.task_graph_id,
    )


def compile_legacy_todo_list_to_behavior_tree(
    todo_steps: list[dict[str, Any]],
    *,
    source_skill_id: str | None = None,
    task_graph_id: str | None = None,
) -> BehaviorTree:
    return compile_todo_list_to_behavior_tree(
        TodoList(
            steps=tuple(_legacy_step_to_plan_step(index, raw_step) for index, raw_step in enumerate(todo_steps, start=1)),
            source_skill_id=source_skill_id,
            task_graph_id=task_graph_id,
        )
    )


def behavior_tree_from_dict(payload: dict[str, Any]) -> BehaviorTree:
    if not isinstance(payload, dict):
        raise ValueError("behavior tree payload must be a dictionary")
    root_payload = payload.get("root")
    if not isinstance(root_payload, dict):
        raise ValueError("behavior tree payload must include a root node")
    return BehaviorTree(
        root=_node_from_dict(root_payload),
        source=str(payload.get("source") or "todo_list"),
        source_skill_id=payload.get("source_skill_id"),
        task_graph_id=payload.get("task_graph_id"),
        schema_version=str(payload.get("schema_version") or "behavior_tree.v1"),
    )


def _compile_step(step: PlanStep) -> BehaviorTreeNode:
    guarded_children: list[BehaviorTreeNode] = []
    already_satisfied_conditions = step.success_check or step.expected_effects
    if already_satisfied_conditions:
        guarded_children.append(
            BehaviorTreeNode(
                node_id=f"step_{step.step}_already_satisfied",
                node_type="Condition",
                name="already_satisfied",
                conditions=already_satisfied_conditions,
                metadata={"step": step.step},
            )
        )

    execute_children: list[BehaviorTreeNode] = []
    if step.preconditions:
        execute_children.append(
            BehaviorTreeNode(
                node_id=f"step_{step.step}_preconditions_met",
                node_type="Condition",
                name="preconditions_met",
                conditions=step.preconditions,
                metadata={"step": step.step},
            )
        )
    execute_children.append(
        BehaviorTreeNode(
            node_id=f"step_{step.step}_action",
            node_type="Action",
            name=step.skill,
            action={"skill": step.skill, "parameters": _json_safe(step.parameters)},
            metadata={"step": step.step},
        )
    )
    guarded_children.append(
        BehaviorTreeNode(
            node_id=f"step_{step.step}_execute",
            node_type="Sequence",
            name="execute_step",
            children=tuple(execute_children),
            metadata={"step": step.step},
        )
    )

    guarded_action = BehaviorTreeNode(
        node_id=f"step_{step.step}_guard",
        node_type="Fallback",
        name="already_satisfied_or_execute",
        children=tuple(guarded_children),
        metadata={"step": step.step},
    )
    recovery_action = BehaviorTreeNode(
        node_id=f"step_{step.step}_repair_or_replan",
        node_type="Action",
        name="repair_or_replan",
        action={
            "skill": "RepairOrReplan",
            "parameters": {
                "failed_step": step.step,
                "failure_policy": _json_safe(step.failure_policy),
                "retry_policy": _json_safe(step.retry_policy),
            },
        },
        metadata={"step": step.step},
    )
    return BehaviorTreeNode(
        node_id=f"step_{step.step}_recovery",
        node_type="Recovery",
        name="execute_with_recovery",
        children=(guarded_action, recovery_action),
        metadata={"step": step.step},
    )


def _legacy_step_to_plan_step(index: int, raw_step: dict[str, Any]) -> PlanStep:
    if not isinstance(raw_step, dict):
        raise ValueError(f"todo_list step {index} must be a dictionary")

    execution = raw_step.get("execution", {})
    if not isinstance(execution, dict):
        raise ValueError(f"todo_list step {index} execution must be a dictionary")

    skill = execution.get("skill")
    if not skill:
        raise ValueError(f"todo_list step {index} execution.skill is required")

    parameters = execution.get("parameters", {})
    if parameters is None:
        parameters = {}
    if not isinstance(parameters, dict):
        raise ValueError(f"todo_list step {index} execution.parameters must be a dictionary")

    return PlanStep(
        step=int(raw_step.get("step") or index),
        skill=str(skill),
        parameters=dict(parameters),
        preconditions=_string_tuple(raw_step.get("preconditions")),
        expected_effects=_string_tuple(raw_step.get("expected_effects")),
        success_check=_string_tuple(raw_step.get("success_check")),
        failure_policy=_dict_field(raw_step.get("failure_policy")),
        retry_policy=_dict_field(raw_step.get("retry_policy")),
    )


def _node_from_dict(payload: dict[str, Any]) -> BehaviorTreeNode:
    children = payload.get("children", [])
    if children is None:
        children = []
    if not isinstance(children, list):
        raise ValueError("behavior tree node children must be a list")
    node_id = payload.get("id") or payload.get("node_id")
    node_type = payload.get("type") or payload.get("node_type")
    name = payload.get("name")
    if not node_id or not node_type or not name:
        raise ValueError("behavior tree node requires id, type, and name")
    action = payload.get("action") or {}
    conditions = payload.get("conditions") or ()
    metadata = payload.get("metadata") or {}
    if not isinstance(action, dict):
        raise ValueError("behavior tree node action must be a dictionary")
    if not isinstance(metadata, dict):
        raise ValueError("behavior tree node metadata must be a dictionary")
    return BehaviorTreeNode(
        node_id=str(node_id),
        node_type=str(node_type),
        name=str(name),
        children=tuple(_node_from_dict(child) for child in children),
        action=dict(action),
        conditions=_string_tuple(conditions),
        metadata=dict(metadata),
    )


def _string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value)
    return (str(value),)


def _dict_field(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    raise ValueError("todo_list policy fields must be dictionaries")


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(child) for child in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
