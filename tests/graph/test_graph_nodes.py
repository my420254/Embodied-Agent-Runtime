from graph.nodes import retry_execution_node, retry_planning_node
from graph.reflection import node as reflection_node
from graph import routes


def test_retry_planning_preserves_checkpoint_for_suffix_repair():
    state = {
        "structured_task": {"intent": "把苹果放到盘子", "constraints": []},
        "new_constraints": ["先打开容器"],
        "task_stack": [{"todo_list": [{"execution": {"skill": "Pickup", "parameters": {"target_item": "苹果"}}}]}],
        "validated_steps": [{"step": 1, "execution": {"skill": "NavigateTo", "parameters": {"target_location": "桌子"}}}],
        "checkpoint_env": {"苹果": {"direct_parent": "桌子"}},
        "checkpoint_robot": {"robot_location": "桌子", "robot_holding": "空"},
        "planning_continuation": {
            "validated_step_count": 1,
            "reuse_validated_prefix": True,
        },
        "corrected_plan_hint": "只续写失败动作之后的步骤",
    }

    result = retry_planning_node(state)

    assert result["validated_steps"] == state["validated_steps"]
    assert result["checkpoint_env"] == state["checkpoint_env"]
    assert result["checkpoint_robot"] == state["checkpoint_robot"]
    assert result["planning_continuation"] == state["planning_continuation"]
    assert result["feedback"] == "只续写失败动作之后的步骤"
    assert result["task_stack"] == []


def test_understanding_router_continues_when_explicit_goal_is_satisfied():
    assert routes.global_understanding_router(
        {
            "is_complete": True,
            "is_cancel_all": False,
            "task_already_satisfied": True,
        }
    ) == "Planning_Module"


def test_retry_execution_replaces_current_action_and_drops_stale_behavior_tree():
    state = {
        "task_stack": [
            {
                "instruction": "拿杯子",
                "todo_list": [{"execution": {"skill": "Pickup", "parameters": {"target_item": "杯子_1"}}}],
                "behavior_tree": {"compiled": True, "root": {}},
                "behavior_tree_executed": True,
            }
        ],
        "corrected_execution": {"skill": "Pickup", "parameters": {"target_item": "备用杯子_1"}},
        "failed_action": "Pickup",
        "error_feedback": "gripper jammed",
    }

    result = retry_execution_node(state)

    assert result["execution_status"] == "running"
    assert result["task_stack"][-1]["todo_list"][0] == {
        "execution": {"skill": "Pickup", "parameters": {"target_item": "备用杯子_1"}}
    }
    assert "behavior_tree" not in result["task_stack"][-1]
    assert result["task_stack"][-1]["behavior_tree_executed"] is True
    assert result["failed_action"] == ""
    assert result["error_feedback"] == ""


def test_retry_execution_escalates_when_reflection_omits_corrected_action():
    state = {
        "task_stack": [
            {"todo_list": [{"execution": {"skill": "Pickup", "parameters": {"target_item": "杯子_1"}}}]}
        ],
        "corrected_execution": {},
        "failed_action": "Pickup",
        "error_feedback": "gripper jammed",
    }

    result = retry_execution_node(state)

    assert result["execution_status"] == "failed"
    assert result["failure_layer"] == "planning"
    assert result["failed_action"] == "Pickup"
    assert "gripper jammed" in result["error_feedback"]
    assert result["next_routing"] == "retry_planning"
    assert result["failure_reason"] == "invalid_corrected_execution"
    assert result["task_stack"] == state["task_stack"]


def test_retry_execution_invalid_bt_reflection_routes_directly_to_retry_planning():
    state = {
        "task_stack": [
            {
                "todo_list": [
                    {"step": 2, "execution": {"skill": "Pickup", "parameters": {"target_item": "杯子_1"}}}
                ]
            }
        ],
        "corrected_execution": {},
        "failed_action": "Pickup",
        "error_feedback": "gripper jammed",
        "behavior_tree_execution": {"succeeded": False, "events": [{"node_id": "step_2_action", "status": "failure"}]},
    }

    result = retry_execution_node(state)

    assert "failed step 2" in result["corrected_plan_hint"]
    assert routes.global_task_management_router(
        {**state, **result, "feature_flags": {"reflection": True}}
    ) == "Retry_Planning"


def test_reflection_triage_stops_at_retry_limit(monkeypatch):
    monkeypatch.setattr(reflection_node, "get_config", lambda *args, **kwargs: 2)

    result = reflection_node.failure_triage_node(
        {
            "failure_layer": "execution",
            "reflection_retry_count": 2,
            "error_feedback": "still failing",
        }
    )

    assert result["determined_reflection_layer"] == "end"
    assert result["reflection_retry_count"] == 2
    assert result["execution_status"] == "failed"
    assert result["next_routing"] == "end"
    assert "反思重试已达到上限(2)" in result["error_feedback"]


def test_failed_task_routes_to_end_when_reflection_disabled():
    state = {"execution_status": "failed", "feature_flags": {"reflection": False}}

    assert routes.global_task_management_router(state) == routes.END
    assert routes.global_planning_router(state) == routes.END


def test_bt_recovery_can_route_directly_to_retry_planning_when_enabled():
    state = {
        "execution_status": "failed",
        "failure_reason": "behavior_tree_replan_requested",
        "next_routing": "retry_planning",
        "feature_flags": {
            "reflection": False,
            "cognitive_bt_recovery_direct_replan": True,
        },
    }

    assert routes.global_task_management_router(state) == "Retry_Planning"


def test_bt_recovery_direct_replan_respects_runtime_budget():
    state = {
        "execution_status": "failed",
        "failure_reason": "behavior_tree_replan_requested",
        "next_routing": "retry_planning",
        "bt_recovery_direct_replan_count": 1,
        "feature_flags": {
            "reflection": True,
            "cognitive_bt_recovery_direct_replan": True,
            "cognitive_bt_direct_replan_budget": 1,
        },
    }

    assert routes.global_task_management_router(state) == "Reflection_Module"


def test_retry_planning_consumes_bt_recovery_plan_hint():
    state = {
        "feature_flags": {"cognitive_bt_recovery_direct_replan": True, "cognitive_bt_direct_replan_budget": 1},
        "structured_task": {"intent": "拿杯子", "constraints": []},
        "task_stack": [{"todo_list": [{"execution": {"skill": "Pickup", "parameters": {"target_item": "杯子_1"}}}]}],
        "cognitive_planning_trace": {"trace_id": "trace-bt-retry"},
        "corrected_plan_hint": "BehaviorTree recovery requested repair_plan; replan from failed step 1.",
        "failure_reason": "behavior_tree_replan_requested",
        "next_routing": "retry_planning",
    }

    result = retry_planning_node(state)

    assert result["feedback"] == "BehaviorTree recovery requested repair_plan; replan from failed step 1."
    assert result["task_stack"] == []
    assert result["bt_recovery_direct_replan_count"] == 1
    assert result["cognitive_planning_trace"]["bt_recovery_retry_budget"] == [
        {
            "budget": 1,
            "used": 1,
            "exhausted": True,
            "route": "Retry_Planning",
            "stage": "retry_planning",
        }
    ]


def test_retry_planning_clears_stale_recovery_routing_state():
    state = {
        "structured_task": {"intent": "读书", "constraints": []},
        "task_stack": [{"todo_list": [{"execution": {"skill": "Read", "parameters": {"target_item": "book"}}}]}],
        "corrected_plan_hint": "BehaviorTree recovery requested repair_plan; replan from failed step 3.",
        "failure_reason": "invalid_corrected_execution",
        "next_routing": "retry_planning",
        "corrected_execution": {"skill": "Read", "parameters": {"target_item": "backup_book"}},
        "correction_strategy": "stale reflection",
        "evaluation_repair_request": {"prompt": "stale repair"},
        "repair_todo_list": [{"execution": {"skill": "Read", "parameters": {}}}],
        "evaluation_recheck": True,
        "evaluation_revision_context": {
            "source": "state_diff_recovery",
            "artifacts": {},
        },
        "repair_history": [{"stage": "sandbox", "assembled": True}],
    }

    result = retry_planning_node(state)

    assert result["next_routing"] == ""
    assert result["failure_reason"] == ""
    assert result["corrected_execution"] == {}
    assert result["correction_strategy"] == ""
    assert result["evaluation_repair_request"] == {}
    assert result["repair_todo_list"] == []
    assert result["evaluation_recheck"] is False
    assert result["evaluation_revision_context"] == {}
    assert result["repair_history"] == []


def test_cancelled_understanding_routes_to_end():
    state = {"is_complete": True, "is_cancel_all": True}

    assert routes.global_understanding_router(state) == routes.END


def test_fully_completed_planning_state_routes_directly_to_end():
    state = {"execution_status": "fully_completed"}

    assert routes.global_planning_router(state) == routes.END
