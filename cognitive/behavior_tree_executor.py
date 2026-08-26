from __future__ import annotations

from collections.abc import Callable
from typing import Any

from interfaces.contracts import (
    BehaviorTree,
    BehaviorTreeExecutionEvent,
    BehaviorTreeExecutionResult,
    BehaviorTreeNode,
)

ActionRunner = Callable[[dict[str, Any], dict[str, Any]], bool | dict[str, Any] | BehaviorTreeExecutionResult]
ConditionChecker = Callable[[str, dict[str, Any]], bool]


class RecordingBehaviorTreeMonitor:
    """Minimal runtime monitor that records node outcomes for trace/debug use."""

    def __init__(self) -> None:
        self._events: list[BehaviorTreeExecutionEvent] = []

    @property
    def events(self) -> tuple[BehaviorTreeExecutionEvent, ...]:
        return tuple(self._events)

    def reset(self) -> None:
        self._events.clear()

    def record(self, node: BehaviorTreeNode, result: BehaviorTreeExecutionResult) -> None:
        self._events.append(
            BehaviorTreeExecutionEvent(
                node_id=node.node_id,
                node_type=node.node_type,
                name=node.name,
                status=result.status,
                message=result.message,
                action_result=result.action_result,
            )
        )


class PrototypeBehaviorTreeExecutor:
    """Deterministic interpreter for the minimal BehaviorTree schema.

    Action execution and condition checks are injected so this scaffold can be
    tested without binding cognitive planning to a simulator, ROS, or benchmark.
    """

    def __init__(
        self,
        *,
        action_runner: ActionRunner | None = None,
        condition_checker: ConditionChecker | None = None,
        monitor: RecordingBehaviorTreeMonitor | None = None,
    ) -> None:
        self.action_runner = action_runner
        self.condition_checker = condition_checker or _condition_unknown
        self.monitor = monitor or RecordingBehaviorTreeMonitor()

    def execute(self, behavior_tree: BehaviorTree, context: dict[str, Any] | None = None) -> BehaviorTreeExecutionResult:
        self.monitor.reset()
        runtime_context = context if isinstance(context, dict) else {}
        result = self._execute_node(behavior_tree.root, runtime_context)
        return _with_events(result, self.monitor.events)

    def _execute_node(self, node: BehaviorTreeNode, context: dict[str, Any]) -> BehaviorTreeExecutionResult:
        node_type = node.node_type
        if node_type == "Sequence":
            result = self._execute_sequence(node, context)
        elif node_type == "Fallback":
            result = self._execute_fallback(node, context)
        elif node_type == "Recovery":
            result = self._execute_recovery(node, context)
        elif node_type == "Condition":
            result = self._execute_condition(node, context)
        elif node_type == "Action":
            result = self._execute_action(node, context)
        else:
            result = _result(node, "failure", f"unsupported behavior tree node type: {node_type}")
        self.monitor.record(node, result)
        return result

    def _execute_sequence(self, node: BehaviorTreeNode, context: dict[str, Any]) -> BehaviorTreeExecutionResult:
        for child in node.children:
            child_result = self._execute_node(child, context)
            if not child_result.succeeded:
                return _result(node, "failure", f"sequence child failed: {child.node_id}")
        return _result(node, "success")

    def _execute_fallback(self, node: BehaviorTreeNode, context: dict[str, Any]) -> BehaviorTreeExecutionResult:
        last_failure = ""
        for child in node.children:
            child_result = self._execute_node(child, context)
            if child_result.succeeded:
                return _result(node, "success")
            last_failure = child_result.message
        return _result(node, "failure", last_failure or "all fallback children failed")

    def _execute_recovery(self, node: BehaviorTreeNode, context: dict[str, Any]) -> BehaviorTreeExecutionResult:
        if not node.children:
            return _result(node, "failure", "recovery node has no primary child")
        primary = self._execute_node(node.children[0], context)
        if primary.succeeded:
            return _result(node, "success")
        if len(node.children) < 2:
            return _result(node, "failure", primary.message)
        recovery = self._execute_node(node.children[1], context)
        if recovery.succeeded:
            return _result(node, "success", f"recovered from: {primary.message}")
        return _result(node, "failure", recovery.message or primary.message)

    def _execute_condition(self, node: BehaviorTreeNode, context: dict[str, Any]) -> BehaviorTreeExecutionResult:
        failed = [condition for condition in node.conditions if not self.condition_checker(condition, context)]
        if failed:
            return _result(node, "failure", f"condition failed: {failed[0]}")
        return _result(node, "success")

    def _execute_action(self, node: BehaviorTreeNode, context: dict[str, Any]) -> BehaviorTreeExecutionResult:
        if not node.action:
            return _result(node, "failure", "action node has no action payload")
        if self.action_runner is None:
            return _result(node, "failure", "no action runner configured")
        raw_result = self.action_runner(dict(node.action), context)
        result = _coerce_action_result(node, raw_result)
        return result


def execute_behavior_tree(
    behavior_tree: BehaviorTree,
    *,
    action_runner: ActionRunner | None = None,
    condition_checker: ConditionChecker | None = None,
    context: dict[str, Any] | None = None,
    monitor: RecordingBehaviorTreeMonitor | None = None,
) -> BehaviorTreeExecutionResult:
    executor = PrototypeBehaviorTreeExecutor(
        action_runner=action_runner,
        condition_checker=condition_checker,
        monitor=monitor,
    )
    return executor.execute(behavior_tree, context=context)


def _coerce_action_result(
    node: BehaviorTreeNode,
    raw_result: bool | dict[str, Any] | BehaviorTreeExecutionResult,
) -> BehaviorTreeExecutionResult:
    if isinstance(raw_result, BehaviorTreeExecutionResult):
        return raw_result
    if isinstance(raw_result, bool):
        return _result(node, "success" if raw_result else "failure")
    status = str(raw_result.get("status") or ("success" if raw_result.get("ok") is True else "failure"))
    message = str(raw_result.get("message") or raw_result.get("error") or "")
    return _result(node, status, message, action_result=dict(raw_result))


def _with_events(
    result: BehaviorTreeExecutionResult,
    events: tuple[BehaviorTreeExecutionEvent, ...],
) -> BehaviorTreeExecutionResult:
    return BehaviorTreeExecutionResult(
        status=result.status,
        node_id=result.node_id,
        node_type=result.node_type,
        message=result.message,
        action_result=result.action_result,
        events=events,
    )


def _result(
    node: BehaviorTreeNode,
    status: str,
    message: str = "",
    *,
    action_result: dict[str, Any] | None = None,
) -> BehaviorTreeExecutionResult:
    return BehaviorTreeExecutionResult(
        status=status,
        node_id=node.node_id,
        node_type=node.node_type,
        message=message,
        action_result=dict(action_result or {}),
    )


def _condition_unknown(_condition: str, _context: dict[str, Any]) -> bool:
    return False
