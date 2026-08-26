import copy
from pathlib import Path

from graph.planning.evaluation.repair_strategies.vcr.core import (
    analyze_counterfactual_failure_windows as _analyze_counterfactual_failure_windows,
    merge_causal_repair_windows,
    repair_after_counterfactual_failure as _repair_after_counterfactual_failure,
    run_counterfactual_suffix as _run_counterfactual_suffix,
)
from adapters.sandbox import apply_sandbox_action
from skills.planning_catalog import load_planning_catalog
from skills.registry import get_skill_handlers


def run_counterfactual_suffix(**kwargs):
    profile = kwargs.get("skill_profile") or "core_household"
    kwargs.setdefault("skill_handlers", get_skill_handlers(profile))
    return _run_counterfactual_suffix(**kwargs)


def repair_after_counterfactual_failure(**kwargs):
    profile = kwargs.get("skill_profile") or "core_household"
    kwargs.setdefault("skill_catalog", load_planning_catalog(profile))
    kwargs.setdefault("skill_handlers", get_skill_handlers(profile))
    return _repair_after_counterfactual_failure(**kwargs)


def analyze_counterfactual_failure_windows(**kwargs):
    profile = kwargs.get("skill_profile") or "core_household"
    kwargs.setdefault("skill_catalog", load_planning_catalog(profile))
    kwargs.setdefault("skill_handlers", get_skill_handlers(profile))
    return _analyze_counterfactual_failure_windows(**kwargs)


def _step(number, skill, parameters):
    return {"step": number, "execution": {"skill": skill, "parameters": parameters}}


def _location_env():
    return {
        "起点_1": {
            "direct_parent": "厨房_1",
            "type": "receptacle",
            "states": {},
            "is_container": True,
            "full_path": ["厨房_1"],
        },
        "错误位置_1": {
            "direct_parent": "厨房_1",
            "type": "receptacle",
            "states": {},
            "is_container": True,
            "full_path": ["厨房_1"],
        },
        "橱柜_1": {
            "direct_parent": "厨房_1",
            "type": "cabinet",
            "states": {"isOpen": False},
            "is_container": True,
            "full_path": ["厨房_1"],
        },
    }


def _multi_window_env():
    names = [
        "起点_1",
        "前置点_1",
        "错误位置_A",
        "橱柜_A",
        "桥接点_1",
        "桥接点_2",
        "桥接点_3",
        "桥接点_4",
        "错误位置_B",
        "橱柜_B",
        "终点_1",
    ]
    env = {
        name: {
            "direct_parent": "厨房_1",
            "type": "receptacle",
            "states": {},
            "is_container": True,
            "full_path": ["厨房_1"],
        }
        for name in names
    }
    for cabinet in ("橱柜_A", "橱柜_B"):
        env[cabinet]["type"] = "cabinet"
        env[cabinet]["states"] = {"isOpen": False}
    return env


def _first_failure_context(todo, initial_env, initial_robot):
    env = copy.deepcopy(initial_env)
    robot = copy.deepcopy(initial_robot)
    validated = []
    trajectory = []
    for step in todo:
        before_env = copy.deepcopy(env)
        before_robot = copy.deepcopy(robot)
        execution = step["execution"]
        ok, issue, fix = apply_sandbox_action(
            env,
            robot,
            execution["skill"],
            execution["parameters"],
            profile="core_household",
        )
        if not ok:
            return {
                "failed_step": step,
                "issue": issue,
                "fix": fix,
                "failure_env": before_env,
                "failure_robot": before_robot,
                "validated_steps": validated,
                "trajectory_records": trajectory,
            }
        validated.append(copy.deepcopy(step))
        trajectory.append(
            {
                "step": copy.deepcopy(step),
                "before_env": before_env,
                "before_robot": before_robot,
                "after_env": copy.deepcopy(env),
                "after_robot": copy.deepcopy(robot),
            }
        )
    raise AssertionError("todo list did not fail")


def test_counterfactual_effect_comes_from_injected_skill_handler():
    class SyntheticSkill:
        def apply(self, sim_env, sim_robot, params):
            sim_env["signal"]["states"]["ready"] = params["value"]

    def apply_action(sim_env, sim_robot, skill, params):
        if skill == "Follow" and sim_env["signal"]["states"].get("ready") is True:
            sim_robot["finished"] = True
            return True, "", ""
        return False, "missing_effect", "Synthetic must establish ready first"

    result = run_counterfactual_suffix(
        failed_step=_step(1, "Synthetic", {"value": True}),
        failure_env={"signal": {"states": {"ready": False}}},
        failure_robot={},
        suffix_steps=[_step(2, "Follow", {})],
        apply_action=apply_action,
        skill_handlers={"Synthetic": SyntheticSkill()},
    )

    assert result["success"] is True
    assert result["final_env"]["signal"]["states"]["ready"] is True
    assert result["final_robot"]["finished"] is True
    assert result["effect_source"].endswith("SyntheticSkill.apply")


def test_counterfactual_effect_can_use_upstream_semantic_callback():
    class RawSkill:
        @staticmethod
        def apply(sim_env, sim_robot, params):
            raise AssertionError("raw handler must not run when callback is supplied")

    callback_calls = []

    def apply_effect(sim_env, sim_robot, skill, params):
        callback_calls.append((skill, dict(params)))
        sim_env["target"]["states"]["ready"] = True

    result = run_counterfactual_suffix(
        failed_step=_step(1, "Synthetic", {"carrier": "tray_1"}),
        failure_env={"target": {"states": {"ready": False}}},
        failure_robot={},
        suffix_steps=[],
        apply_action=lambda env, robot, skill, params: (True, "", ""),
        skill_handlers={"Synthetic": RawSkill()},
        apply_effect=apply_effect,
        goal_test=lambda env, robot: env["target"]["states"]["ready"] is True,
    )

    assert result["success"] is True
    assert callback_calls == [("Synthetic", {"carrier": "tray_1"})]


def test_vcr_replaces_only_causal_interval_after_shadow_suffix_validation():
    initial_env = _location_env()
    initial_robot = {"robot_location": "起点_1", "robot_holding": "空"}
    todo = [
        _step(1, "NavigateTo", {"target_location": "错误位置_1"}),
        _step(2, "Open", {"target_container": "橱柜_1"}),
        _step(3, "NavigateTo", {"target_location": "起点_1"}),
    ]
    captured_request = {}

    def segment_planner(request):
        captured_request.update(request)
        return {
            "success": True,
            "actions": [{"skill": "NavigateTo", "parameters": {"target_location": "橱柜_1"}}],
            "repair_summary": "先导航到失败动作要求的位置",
            "planner_stats": {"planner": "fake_llm"},
        }

    after_first_env = _location_env()
    after_first_robot = dict(initial_robot)
    ok, issue, fix = apply_sandbox_action(
        after_first_env,
        after_first_robot,
        "NavigateTo",
        {"target_location": "错误位置_1"},
        profile="core_household",
    )
    assert ok, (issue, fix)
    trajectory_records = [
        {
            "step": todo[0],
            "before_env": _location_env(),
            "before_robot": dict(initial_robot),
            "after_env": after_first_env,
            "after_robot": after_first_robot,
        }
    ]

    result = repair_after_counterfactual_failure(
        todo_list=todo,
        validated_steps=[todo[0]],
        failed_step=todo[1],
        issue_type="前置位置依赖未满足",
        fix_advice="必须先导航至 橱柜_1",
        failure_env=after_first_env,
        failure_robot=after_first_robot,
        trajectory_records=trajectory_records,
        sandbox_start_env=_location_env(),
        sandbox_start_robot=initial_robot,
        apply_action=lambda env, robot, skill, params: apply_sandbox_action(
            env,
            robot,
            skill,
            params,
            profile="core_household",
        ),
        goal_test=lambda env, robot: env["橱柜_1"]["states"].get("isOpen") is True,
        skill_profile="core_household",
        max_segment_actions=8,
        task_context={"intent": "打开橱柜后返回起点"},
        segment_planner=segment_planner,
    )

    assert result["success"] is True, result
    repaired = result["todo_list"]
    assert [step["execution"]["skill"] for step in repaired] == ["NavigateTo", "Open", "NavigateTo"]
    assert repaired[0]["execution"]["parameters"] == {"target_location": "橱柜_1"}
    assert repaired[2]["execution"]["parameters"] == {"target_location": "起点_1"}
    assert captured_request["cause_checkpoint"]["robot"] == initial_robot
    assert captured_request["failure_requirement"]["sandbox_fix"] == "必须先导航至 橱柜_1"
    assert captured_request["original_replaced_interval"] == [
        {"step": 1, "execution": {"skill": "NavigateTo", "parameters": {"target_location": "错误位置_1"}}}
    ]
    assert captured_request["protected_continuation"]["suffix_steps"] == [
        {"step": 3, "execution": {"skill": "NavigateTo", "parameters": {"target_location": "起点_1"}}}
    ]
    assert captured_request["protected_continuation"]["possible_conditions"][0]["skill_contract"][
        "resolved_arguments"
    ]["location"] == "起点_1"
    assert result["vcr_state"]["mode"] == "vcr_counterfactual_repair"
    assert result["vcr_state"]["version"] == "vcr_v2"
    assert result["vcr_state"]["causal_rollback"]["selected_step"] == 1
    assert result["vcr_state"]["causal_rollback"]["causal_predicate"] == "robot.robot.robot_location"
    assert result["vcr_state"]["state_dependency_graph"]["version"] == "vcr_dependency_v1"
    assert result["vcr_state"]["state_dependency_graph"]["failure"]["failed_predicates"] == [
        "robot.robot.robot_location"
    ]
    assert "sda_state" not in result["vcr_state"]["causal_rollback"]
    assert result["vcr_state"]["local_task"]["goal"]["type"] == "failed_action_and_continuation_requirements"
    assert result["vcr_state"]["local_task"]["planner_stats"]["planner"] == "fake_llm"
    assert result["checkpoint_env"]["橱柜_1"]["states"]["isOpen"] is True


def test_vcr_inserts_missing_prerequisite_from_real_prefailure_state():
    initial_env = _location_env()
    initial_robot = {"robot_location": "起点_1", "robot_holding": "空"}
    failed_step = _step(1, "Open", {"target_container": "橱柜_1"})

    result = repair_after_counterfactual_failure(
        todo_list=[failed_step],
        validated_steps=[],
        failed_step=failed_step,
        issue_type="前置位置依赖未满足",
        fix_advice="必须先导航至 橱柜_1",
        failure_env=initial_env,
        failure_robot=initial_robot,
        trajectory_records=[],
        sandbox_start_env=_location_env(),
        sandbox_start_robot=initial_robot,
        apply_action=lambda env, robot, skill, params: apply_sandbox_action(
            env,
            robot,
            skill,
            params,
            profile="core_household",
        ),
        goal_test=lambda env, robot: env["橱柜_1"]["states"].get("isOpen") is True,
        skill_profile="core_household",
        max_segment_actions=8,
        segment_planner=lambda request: {
            "success": True,
            "actions": [{"skill": "NavigateTo", "parameters": {"target_location": "橱柜_1"}}],
            "planner_stats": {"planner": "fake_llm"},
        },
    )

    assert result["success"] is True, result
    assert [step["execution"]["skill"] for step in result["todo_list"]] == ["NavigateTo", "Open"]
    assert result["vcr_state"]["causal_rollback"]["selected_step"] == 1
    assert "失败动作前的真实状态" in result["vcr_state"]["causal_rollback"]["reason"]


def test_vcr_retries_single_window_with_replay_feedback():
    initial_env = _location_env()
    initial_robot = {"robot_location": "起点_1", "robot_holding": "空"}
    failed_step = _step(1, "Open", {"target_container": "橱柜_1"})
    requests = []

    def planner(request):
        requests.append(copy.deepcopy(request))
        target = "错误位置_1" if len(requests) == 1 else "橱柜_1"
        return {
            "success": True,
            "actions": [{"skill": "NavigateTo", "parameters": {"target_location": target}}],
            "planner_stats": {"planner": "fake_retry_llm"},
        }

    result = repair_after_counterfactual_failure(
        todo_list=[failed_step],
        validated_steps=[],
        failed_step=failed_step,
        issue_type="前置位置依赖未满足",
        fix_advice="必须先导航至 橱柜_1",
        failure_env=initial_env,
        failure_robot=initial_robot,
        trajectory_records=[],
        sandbox_start_env=_location_env(),
        sandbox_start_robot=initial_robot,
        apply_action=lambda env, robot, skill, params: apply_sandbox_action(
            env,
            robot,
            skill,
            params,
            profile="core_household",
        ),
        goal_test=lambda env, robot: env["橱柜_1"]["states"].get("isOpen") is True,
        skill_profile="core_household",
        max_retries=1,
        segment_planner=planner,
    )

    assert result["success"] is True, result
    assert len(requests) == 2
    assert requests[0]["retry_context"] == {
        "attempt_number": 1,
        "max_attempts": 2,
        "is_retry": False,
        "previous_failures": [],
    }
    assert requests[1]["retry_context"]["is_retry"] is True
    assert requests[1]["retry_context"]["previous_failures"][0]["reason"] == (
        "real_candidate_replay_failed"
    )
    planner_stats = result["vcr_state"]["local_task"]["planner_stats"]
    assert planner_stats["attempt_count"] == 2
    assert planner_stats["retry_count"] == 1
    assert planner_stats["max_retries"] == 1


def test_vcr_rejects_llm_segment_when_full_candidate_fails_sandbox():
    initial_env = _location_env()
    initial_robot = {"robot_location": "起点_1", "robot_holding": "空"}
    failed_step = _step(1, "Open", {"target_container": "橱柜_1"})
    requests = []

    def planner(request):
        requests.append(copy.deepcopy(request))
        return {
            "success": True,
            "actions": [{"skill": "NavigateTo", "parameters": {"target_location": "错误位置_1"}}],
            "planner_stats": {"planner": "fake_llm"},
        }

    result = repair_after_counterfactual_failure(
        todo_list=[failed_step],
        validated_steps=[],
        failed_step=failed_step,
        issue_type="前置位置依赖未满足",
        fix_advice="必须先导航至 橱柜_1",
        failure_env=initial_env,
        failure_robot=initial_robot,
        trajectory_records=[],
        sandbox_start_env=_location_env(),
        sandbox_start_robot=initial_robot,
        apply_action=lambda env, robot, skill, params: apply_sandbox_action(
            env,
            robot,
            skill,
            params,
            profile="core_household",
        ),
        goal_test=lambda env, robot: env["橱柜_1"]["states"].get("isOpen") is True,
        skill_profile="core_household",
        max_retries=2,
        segment_planner=planner,
    )

    assert result["success"] is False
    assert result["failure_reason"] == "real_candidate_replay_failed"
    assert result["failure_details"]["replay"]["reason"] == "candidate_step_failed"
    assert result["failure_details"]["replay"]["step"]["execution"]["skill"] == "Open"
    assert result["failure_details"]["attempt_count"] == 3
    assert result["failure_details"]["max_retries"] == 2
    assert len(result["failure_details"]["retry_history"]) == 3
    assert len(requests) == 3


def test_counterfactual_suffix_rejects_when_explicit_goal_is_not_reached():
    class SyntheticSkill:
        def apply(self, sim_env, sim_robot, params):
            sim_env["signal"]["states"]["ready"] = True

    result = run_counterfactual_suffix(
        failed_step=_step(1, "Synthetic", {}),
        failure_env={"signal": {"states": {"ready": False}}},
        failure_robot={},
        suffix_steps=[],
        apply_action=lambda env, robot, skill, params: (True, "", ""),
        skill_handlers={"Synthetic": SyntheticSkill()},
        goal_test=lambda env, robot: False,
    )

    assert result == {
        "success": False,
        "reason": "counterfactual_task_not_completed",
        "details": {
            "executed_steps": [_step(1, "Synthetic", {})],
            "task_completion": {
                "status": "not_completed",
                "evidence_source": "explicit_goal",
            },
        },
    }


def test_vcr_analysis_rejects_when_counterfactual_plan_misses_explicit_goal():
    initial_env = _location_env()
    initial_robot = {"robot_location": "起点_1", "robot_holding": "空"}
    todo = [
        _step(1, "NavigateTo", {"target_location": "错误位置_1"}),
        _step(2, "Open", {"target_container": "橱柜_1"}),
    ]
    context = _first_failure_context(todo, initial_env, initial_robot)

    analysis = analyze_counterfactual_failure_windows(
        steps=todo,
        first_failed_index=1,
        first_issue_type=context["issue"],
        first_fix_advice=context["fix"],
        failure_env=context["failure_env"],
        failure_robot=context["failure_robot"],
        trajectory_records=context["trajectory_records"],
        sandbox_start_env=initial_env,
        sandbox_start_robot=initial_robot,
        apply_action=lambda env, robot, skill, params: apply_sandbox_action(
            env,
            robot,
            skill,
            params,
            profile="core_household",
        ),
        max_backtrack_depth=0,
        skill_profile="core_household",
        goal_test=lambda env, robot: False,
    )

    assert analysis["success"] is False
    assert analysis["reason"] == "counterfactual_task_not_completed"


def test_vcr_finds_each_failure_root_cause_before_building_repair_window():
    initial_env = _multi_window_env()
    initial_robot = {"robot_location": "起点_1", "robot_holding": "空"}
    todo = [
        _step(1, "NavigateTo", {"target_location": "前置点_1"}),
        _step(2, "NavigateTo", {"target_location": "错误位置_A"}),
        _step(3, "Open", {"target_container": "橱柜_A"}),
        _step(4, "NavigateTo", {"target_location": "桥接点_1"}),
        _step(5, "NavigateTo", {"target_location": "桥接点_2"}),
        _step(6, "NavigateTo", {"target_location": "桥接点_3"}),
        _step(7, "NavigateTo", {"target_location": "桥接点_4"}),
        _step(8, "NavigateTo", {"target_location": "错误位置_B"}),
        _step(9, "Open", {"target_container": "橱柜_B"}),
        _step(10, "NavigateTo", {"target_location": "终点_1"}),
    ]
    context = _first_failure_context(todo, initial_env, initial_robot)

    analysis = analyze_counterfactual_failure_windows(
        steps=todo,
        first_failed_index=2,
        first_issue_type=context["issue"],
        first_fix_advice=context["fix"],
        failure_env=context["failure_env"],
        failure_robot=context["failure_robot"],
        trajectory_records=context["trajectory_records"],
        sandbox_start_env=initial_env,
        sandbox_start_robot=initial_robot,
        apply_action=lambda env, robot, skill, params: apply_sandbox_action(
            env,
            robot,
            skill,
            params,
            profile="core_household",
        ),
        max_backtrack_depth=0,
        skill_profile="core_household",
    )

    assert analysis["success"] is True, analysis
    assert [item["step"]["step"] for item in analysis["failures"]] == [3, 9]
    assert [item["checkpoint"]["rollback_step_num"] for item in analysis["windows"]] == [2, 8]
    assert [item["checkpoint"]["causal_before"] for item in analysis["windows"]] == [
        "前置点_1",
        "桥接点_4",
    ]
    assert [item["checkpoint"]["causal_after"] for item in analysis["windows"]] == [
        "错误位置_A",
        "错误位置_B",
    ]
    assert [
        item["checkpoint"]["failed_preconditions"]
        for item in analysis["windows"]
    ] == [
        [
            {
                "predicate": "robot.robot.robot_location",
                "required_value": "橱柜_A",
                "actual_value": "错误位置_A",
            }
        ],
        [
            {
                "predicate": "robot.robot.robot_location",
                "required_value": "橱柜_B",
                "actual_value": "错误位置_B",
            }
        ],
    ]
    assert [item["anchor_index"] for item in analysis["windows"]] == [2, 8]
    assert all(len(item["failures"]) == 1 for item in analysis["windows"])


def test_vcr_repairs_two_distant_failure_windows_and_preserves_middle_segment():
    initial_env = _multi_window_env()
    initial_robot = {"robot_location": "起点_1", "robot_holding": "空"}
    todo = [
        _step(1, "NavigateTo", {"target_location": "前置点_1"}),
        _step(2, "NavigateTo", {"target_location": "错误位置_A"}),
        _step(3, "Open", {"target_container": "橱柜_A"}),
        _step(4, "NavigateTo", {"target_location": "桥接点_1"}),
        _step(5, "NavigateTo", {"target_location": "桥接点_2"}),
        _step(6, "NavigateTo", {"target_location": "桥接点_3"}),
        _step(7, "NavigateTo", {"target_location": "桥接点_4"}),
        _step(8, "NavigateTo", {"target_location": "错误位置_B"}),
        _step(9, "Open", {"target_container": "橱柜_B"}),
        _step(10, "NavigateTo", {"target_location": "终点_1"}),
    ]
    context = _first_failure_context(todo, initial_env, initial_robot)
    requests = []

    def planner(request):
        requests.append(copy.deepcopy(request))
        target = request["failure_requirement"]["failed_step"]["execution"]["parameters"][
            "target_container"
        ]
        return {
            "success": True,
            "actions": [
                {"skill": "NavigateTo", "parameters": {"target_location": target}},
                {"skill": "Open", "parameters": {"target_container": target}},
            ],
            "planner_stats": {"planner": "fake_multi_window"},
        }

    result = repair_after_counterfactual_failure(
        todo_list=todo,
        validated_steps=context["validated_steps"],
        failed_step=context["failed_step"],
        issue_type=context["issue"],
        fix_advice=context["fix"],
        failure_env=context["failure_env"],
        failure_robot=context["failure_robot"],
        trajectory_records=context["trajectory_records"],
        sandbox_start_env=initial_env,
        sandbox_start_robot=initial_robot,
        apply_action=lambda env, robot, skill, params: apply_sandbox_action(
            env,
            robot,
            skill,
            params,
            profile="core_household",
        ),
        goal_test=lambda env, robot: (
            env["橱柜_A"]["states"].get("isOpen") is True
            and env["橱柜_B"]["states"].get("isOpen") is True
            and robot.get("robot_location") == "终点_1"
        ),
        skill_profile="core_household",
        max_segment_actions=8,
        merge_gap_actions=3,
        segment_planner=planner,
    )

    assert result["success"] is True, result
    assert len(requests) == 2
    assert [len(request["failure_requirements"]) for request in requests] == [1, 1]
    assert result["vcr_state"]["counterfactual"]["failure_count"] == 2
    assert result["vcr_state"]["planner_stats"]["window_count"] == 2
    assert [
        item["repair_window"]["merged"] for item in result["vcr_state"]["repair_windows"]
    ] == [False, False]
    assert result["vcr_state"]["protected_segments"] == [
        {"start_step": 1, "end_step": 1},
        {"start_step": 4, "end_step": 7},
        {"start_step": 10, "end_step": 10},
    ]
    assert result["todo_list"][1]["execution"]["parameters"] == {"target_location": "橱柜_A"}
    assert result["todo_list"][7]["execution"]["parameters"] == {"target_location": "橱柜_B"}
    assert result["checkpoint_robot"]["robot_location"] == "终点_1"


def test_vcr_default_merge_keeps_all_windows_separate():
    def window(start_index, anchor_index):
        return {
            "start_index": start_index,
            "anchor_index": anchor_index,
            "failures": [],
            "source_windows": [
                {"start_index": start_index, "anchor_index": anchor_index}
            ],
            "merge_reasons": [],
        }

    separated = merge_causal_repair_windows(
        [window(0, 1), window(3, 4)]
    )
    overlapping = merge_causal_repair_windows(
        [window(0, 2), window(2, 4)]
    )
    explicitly_merged = merge_causal_repair_windows(
        [window(0, 2), window(2, 4)],
        merge_gap_actions=1,
    )

    assert [(item["start_index"], item["anchor_index"]) for item in separated] == [
        (0, 1),
        (3, 4),
    ]
    assert [(item["start_index"], item["anchor_index"]) for item in overlapping] == [
        (0, 2),
        (2, 4),
    ]
    assert len(explicitly_merged) == 1
    assert explicitly_merged[0]["merge_reasons"] == ["overlapping_causal_windows"]


def test_vcr_merges_nearby_failure_windows_into_one_long_repair():
    initial_env = _multi_window_env()
    initial_robot = {"robot_location": "起点_1", "robot_holding": "空"}
    todo = [
        _step(1, "NavigateTo", {"target_location": "错误位置_A"}),
        _step(2, "Open", {"target_container": "橱柜_A"}),
        _step(3, "NavigateTo", {"target_location": "桥接点_1"}),
        _step(4, "NavigateTo", {"target_location": "错误位置_B"}),
        _step(5, "Open", {"target_container": "橱柜_B"}),
        _step(6, "NavigateTo", {"target_location": "终点_1"}),
    ]
    context = _first_failure_context(todo, initial_env, initial_robot)
    requests = []

    def planner(request):
        requests.append(copy.deepcopy(request))
        assert len(request["failure_requirements"]) == 2
        return {
            "success": True,
            "actions": [
                {"skill": "NavigateTo", "parameters": {"target_location": "橱柜_A"}},
                {"skill": "Open", "parameters": {"target_container": "橱柜_A"}},
                {"skill": "NavigateTo", "parameters": {"target_location": "橱柜_B"}},
                {"skill": "Open", "parameters": {"target_container": "橱柜_B"}},
            ],
            "planner_stats": {"planner": "fake_merged_window"},
        }

    result = repair_after_counterfactual_failure(
        todo_list=todo,
        validated_steps=context["validated_steps"],
        failed_step=context["failed_step"],
        issue_type=context["issue"],
        fix_advice=context["fix"],
        failure_env=context["failure_env"],
        failure_robot=context["failure_robot"],
        trajectory_records=context["trajectory_records"],
        sandbox_start_env=initial_env,
        sandbox_start_robot=initial_robot,
        apply_action=lambda env, robot, skill, params: apply_sandbox_action(
            env,
            robot,
            skill,
            params,
            profile="core_household",
        ),
        goal_test=lambda env, robot: (
            env["橱柜_A"]["states"].get("isOpen") is True
            and env["橱柜_B"]["states"].get("isOpen") is True
            and robot.get("robot_location") == "终点_1"
        ),
        skill_profile="core_household",
        max_segment_actions=8,
        merge_gap_actions=3,
        segment_planner=planner,
    )

    assert result["success"] is True, result
    assert len(requests) == 1
    window = result["vcr_state"]["repair_windows"][0]
    assert window["repair_window"]["merged"] is True
    assert window["repair_window"]["failure_count"] == 2
    assert window["repair_window"]["merge_reasons"] == ["nearby_gap_1"]
    assert [step["execution"]["skill"] for step in result["todo_list"]] == [
        "NavigateTo",
        "Open",
        "NavigateTo",
        "Open",
        "NavigateTo",
    ]


def test_vcr_merge_gap_threshold_can_keep_nearby_windows_separate():
    initial_env = _multi_window_env()
    initial_robot = {"robot_location": "起点_1", "robot_holding": "空"}
    todo = [
        _step(1, "NavigateTo", {"target_location": "错误位置_A"}),
        _step(2, "Open", {"target_container": "橱柜_A"}),
        _step(3, "NavigateTo", {"target_location": "桥接点_1"}),
        _step(4, "NavigateTo", {"target_location": "错误位置_B"}),
        _step(5, "Open", {"target_container": "橱柜_B"}),
        _step(6, "NavigateTo", {"target_location": "终点_1"}),
    ]
    context = _first_failure_context(todo, initial_env, initial_robot)
    requests = []

    def planner(request):
        requests.append(copy.deepcopy(request))
        target = request["failure_requirement"]["failed_step"]["execution"]["parameters"][
            "target_container"
        ]
        return {
            "success": True,
            "actions": [
                {"skill": "NavigateTo", "parameters": {"target_location": target}},
                {"skill": "Open", "parameters": {"target_container": target}},
            ],
        }

    result = repair_after_counterfactual_failure(
        todo_list=todo,
        validated_steps=context["validated_steps"],
        failed_step=context["failed_step"],
        issue_type=context["issue"],
        fix_advice=context["fix"],
        failure_env=context["failure_env"],
        failure_robot=context["failure_robot"],
        trajectory_records=context["trajectory_records"],
        sandbox_start_env=initial_env,
        sandbox_start_robot=initial_robot,
        apply_action=lambda env, robot, skill, params: apply_sandbox_action(
            env,
            robot,
            skill,
            params,
            profile="core_household",
        ),
        goal_test=lambda env, robot: (
            env["橱柜_A"]["states"].get("isOpen") is True
            and env["橱柜_B"]["states"].get("isOpen") is True
            and robot.get("robot_location") == "终点_1"
        ),
        skill_profile="core_household",
        max_segment_actions=8,
        merge_gap_actions=0,
        segment_planner=planner,
    )

    assert result["success"] is True, result
    assert len(requests) == 2
    assert result["vcr_state"]["planner_stats"]["window_count"] == 2


def test_vcr_rejects_first_window_when_it_changes_a_protected_boundary():
    initial_env = _multi_window_env()
    initial_env["额外橱柜"] = {
        "direct_parent": "厨房_1",
        "type": "cabinet",
        "states": {"isOpen": False},
        "is_container": True,
        "full_path": ["厨房_1"],
    }
    initial_robot = {"robot_location": "起点_1", "robot_holding": "空"}
    todo = [
        _step(1, "NavigateTo", {"target_location": "错误位置_A"}),
        _step(2, "Open", {"target_container": "橱柜_A"}),
        _step(3, "NavigateTo", {"target_location": "桥接点_1"}),
        _step(4, "NavigateTo", {"target_location": "桥接点_2"}),
        _step(5, "NavigateTo", {"target_location": "桥接点_3"}),
        _step(6, "NavigateTo", {"target_location": "桥接点_4"}),
        _step(7, "NavigateTo", {"target_location": "错误位置_B"}),
        _step(8, "Open", {"target_container": "橱柜_B"}),
        _step(9, "NavigateTo", {"target_location": "终点_1"}),
    ]
    context = _first_failure_context(todo, initial_env, initial_robot)

    def run(planner, max_retries):
        return repair_after_counterfactual_failure(
            todo_list=todo,
            validated_steps=context["validated_steps"],
            failed_step=context["failed_step"],
            issue_type=context["issue"],
            fix_advice=context["fix"],
            failure_env=context["failure_env"],
            failure_robot=context["failure_robot"],
            trajectory_records=context["trajectory_records"],
            sandbox_start_env=initial_env,
            sandbox_start_robot=initial_robot,
            apply_action=lambda env, robot, skill, params: apply_sandbox_action(
                env,
                robot,
                skill,
                params,
                profile="core_household",
            ),
            goal_test=lambda env, robot: (
                env["橱柜_A"]["states"].get("isOpen") is True
                and env["橱柜_B"]["states"].get("isOpen") is True
                and robot.get("robot_location") == "终点_1"
            ),
            skill_profile="core_household",
            max_segment_actions=8,
            merge_gap_actions=3,
            max_retries=max_retries,
            segment_planner=planner,
        )

    def boundary_polluting_plan(request):
        return {
            "success": True,
            "actions": [
                {"skill": "NavigateTo", "parameters": {"target_location": "橱柜_A"}},
                {"skill": "Open", "parameters": {"target_container": "橱柜_A"}},
                {"skill": "NavigateTo", "parameters": {"target_location": "额外橱柜"}},
                {"skill": "Open", "parameters": {"target_container": "额外橱柜"}},
            ],
        }

    rejected = run(boundary_polluting_plan, max_retries=0)

    assert rejected["success"] is False
    assert rejected["failure_reason"] == "protected_boundary_not_preserved"
    assert rejected["failure_details"]["environment_matches"] is False
    assert rejected["failure_details"]["expected_robot"] == rejected["failure_details"]["actual_robot"]

    requests = []

    def recovering_planner(request):
        requests.append(copy.deepcopy(request))
        window_index = request["repair_window"]["window_index"]
        attempt_number = request["retry_context"]["attempt_number"]
        if window_index == 1 and attempt_number == 1:
            return boundary_polluting_plan(request)
        target = request["failure_requirement"]["failed_step"]["execution"]["parameters"][
            "target_container"
        ]
        return {
            "success": True,
            "actions": [
                {"skill": "NavigateTo", "parameters": {"target_location": target}},
                {"skill": "Open", "parameters": {"target_container": target}},
            ],
        }

    repaired = run(recovering_planner, max_retries=1)

    assert repaired["success"] is True, repaired
    assert [
        (request["repair_window"]["window_index"], request["retry_context"]["attempt_number"])
        for request in requests
    ] == [(1, 1), (1, 2), (2, 1)]
    assert requests[1]["retry_context"]["previous_failures"][0]["reason"] == (
        "protected_boundary_not_preserved"
    )
    assert repaired["vcr_state"]["planner_stats"]["attempt_count"] == 3
    assert repaired["vcr_state"]["planner_stats"]["retry_count"] == 1


def test_vcr_python_package_has_no_sda_dependency():
    package_root = (
        Path(__file__).resolve().parents[2]
        / "graph"
        / "planning"
        / "evaluation"
        / "repair_strategies"
        / "vcr"
    )
    source = "\n".join(path.read_text(encoding="utf-8") for path in package_root.glob("*.py"))

    assert "repair_strategies.sda" not in source
    assert "repair_strategies.retrac" not in source
    assert "sda_state" not in source
    assert "from collections import deque" not in source
    assert "max_expansions" not in source
    assert "_candidate_actions" not in source
