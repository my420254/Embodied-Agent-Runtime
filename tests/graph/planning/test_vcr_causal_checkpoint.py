from graph.planning.evaluation.repair_strategies.vcr.causal_checkpoint import (
    select_vcr_repair_checkpoint,
)
from skills.planning_catalog import SkillPlanningCatalog, SkillPlanningSpec


def _catalog():
    return SkillPlanningCatalog(
        [
            SkillPlanningSpec(name="NavigateTo", location_param="target_location"),
            SkillPlanningSpec(
                name="Open",
                target_param="target_container",
                location_param="target_container",
                state_key="isOpen",
                state_value=True,
                requires_empty_hand=True,
                access_state=True,
            ),
        ]
    )


def test_vcr_backtracking_uses_frozen_skill_closure_for_root_candidates():
    todo_list = [
        {
            "step": 1,
            "execution": {
                "skill": "NavigateTo",
                "parameters": {"target_location": "错误位置_1"},
            },
        },
        {
            "step": 2,
            "execution": {
                "skill": "Open",
                "parameters": {"target_container": "橱柜_1"},
            },
        },
    ]
    env = {
        "错误位置_1": {"states": {}},
        "橱柜_1": {"states": {"isOpen": False}},
    }
    trajectory_records = [
        {
            "step": todo_list[0],
            "before_env": env,
            "before_robot": {"robot_location": "起点_1", "robot_holding": "空"},
            "after_env": env,
            "after_robot": {"robot_location": "错误位置_1", "robot_holding": "空"},
        }
    ]
    common = {
        "todo_list": todo_list,
        "validated_steps": todo_list[:1],
        "failed_step": todo_list[1],
        "issue_type": "前置位置依赖未满足",
        "fix_advice": "必须先导航至目标容器",
        "failure_env": env,
        "failure_robot": {"robot_location": "错误位置_1", "robot_holding": "空"},
        "trajectory_records": trajectory_records,
        "sandbox_start_env": env,
        "sandbox_start_robot": {"robot_location": "起点_1", "robot_holding": "空"},
        "skill_catalog": _catalog(),
    }

    with_navigation = select_vcr_repair_checkpoint(
        **common,
        skill_closure=["NavigateTo", "Open"],
    )
    without_navigation = select_vcr_repair_checkpoint(
        **common,
        skill_closure=["Open"],
    )

    assert with_navigation["rollback_step_num"] == 1
    assert with_navigation["causal_action"]["skill"] == "NavigateTo"
    assert without_navigation["rollback_step_num"] == 2
    assert without_navigation["causal_action"] is None
