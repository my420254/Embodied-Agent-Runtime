from graph.planning.evaluation.repair_strategies.sda.state_dependency import (
    select_repair_checkpoint,
)
from skills.planning_catalog import load_planning_catalog


def _step(num, skill, params):
    return {"step": num, "execution": {"skill": skill, "parameters": params}}


def _record(step, before_robot, after_robot, before_env=None, after_env=None):
    return {
        "step": step,
        "before_env": before_env or {},
        "before_robot": before_robot,
        "after_env": after_env or before_env or {},
        "after_robot": after_robot,
    }


def test_sda_rolls_back_to_causal_hand_occupancy_writer():
    todo = [
        _step(1, "NavigateTo", {"target_location": "冰箱_1"}),
        _step(2, "Open", {"target_container": "冰箱_1"}),
        _step(3, "Pickup", {"target_item": "鸡蛋_1"}),
        _step(4, "NavigateTo", {"target_location": "顶层橱柜_1"}),
        _step(5, "Open", {"target_container": "顶层橱柜_1"}),
    ]
    records = [
        _record(todo[0], {"robot_location": "厨房操作台_1", "robot_holding": "空"}, {"robot_location": "冰箱_1", "robot_holding": "空"}),
        _record(todo[1], {"robot_location": "冰箱_1", "robot_holding": "空"}, {"robot_location": "冰箱_1", "robot_holding": "空"}),
        _record(todo[2], {"robot_location": "冰箱_1", "robot_holding": "空"}, {"robot_location": "冰箱_1", "robot_holding": "鸡蛋_1"}),
        _record(todo[3], {"robot_location": "冰箱_1", "robot_holding": "鸡蛋_1"}, {"robot_location": "顶层橱柜_1", "robot_holding": "鸡蛋_1"}),
    ]

    checkpoint = select_repair_checkpoint(
        todo_list=todo,
        validated_steps=todo[:4],
        failed_step=todo[4],
        issue_type="单臂约束违规",
        fix_advice="开/关容器时必须保持空手",
        failure_env={},
        failure_robot={"robot_location": "顶层橱柜_1", "robot_holding": "鸡蛋_1"},
        trajectory_records=records,
        sandbox_start_env={},
        sandbox_start_robot={"robot_location": "厨房操作台_1", "robot_holding": "空"},
        repair_catalog=load_planning_catalog("core_household"),
    )

    assert checkpoint["rollback_step_num"] == 3
    assert [step["step"] for step in checkpoint["validated_steps"]] == [1, 2]
    assert checkpoint["checkpoint_robot"]["robot_holding"] == "空"
    assert checkpoint["sda_state"]["mode"] == "sda_causal_repair"
    assert checkpoint["sda_state"]["trajectory"]["discarded_suffix"][0]["step"] == 3
    assert checkpoint["sda_state"]["rollback"]["causal_predicate"] == "robot.robot.robot_holding"
    assert checkpoint["causal_action"] == {
        "step": 3,
        "skill": "Pickup",
        "parameters": {"target_item": "鸡蛋_1"},
    }
    assert checkpoint["causal_before"] == "空"
    assert checkpoint["causal_after"] == "鸡蛋_1"


def test_sda_rolls_back_to_location_writer_for_navigation_precondition():
    todo = [
        _step(1, "Pickup", {"target_item": "鸡蛋_1"}),
        _step(2, "NavigateTo", {"target_location": "顶层橱柜_1"}),
        _step(3, "Put", {"target_item": "鸡蛋_1", "destination": "厨房操作台_1"}),
    ]
    records = [
        _record(todo[0], {"robot_location": "冰箱_1", "robot_holding": "空"}, {"robot_location": "冰箱_1", "robot_holding": "鸡蛋_1"}),
        _record(todo[1], {"robot_location": "冰箱_1", "robot_holding": "鸡蛋_1"}, {"robot_location": "顶层橱柜_1", "robot_holding": "鸡蛋_1"}),
    ]

    checkpoint = select_repair_checkpoint(
        todo_list=todo,
        validated_steps=todo[:2],
        failed_step=todo[2],
        issue_type="前置位置依赖未满足",
        fix_advice="放置前必须导航至 厨房操作台_1",
        failure_env={},
        failure_robot={"robot_location": "顶层橱柜_1", "robot_holding": "鸡蛋_1"},
        trajectory_records=records,
        sandbox_start_env={},
        sandbox_start_robot={"robot_location": "冰箱_1", "robot_holding": "空"},
        repair_catalog=load_planning_catalog("core_household"),
    )

    assert checkpoint["rollback_step_num"] == 2
    assert [step["step"] for step in checkpoint["validated_steps"]] == [1]
    assert checkpoint["checkpoint_robot"]["robot_location"] == "冰箱_1"
    assert checkpoint["sda_state"]["trajectory"]["discarded_suffix"][0]["skill"] == "NavigateTo"
    assert checkpoint["causal_before"] == "冰箱_1"
    assert checkpoint["causal_after"] == "顶层橱柜_1"
