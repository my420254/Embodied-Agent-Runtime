from graph.planning.evaluation.outcomes.continuation import strip_repeated_prefix
from re_trac import (
    build_failed_step_retrac_state,
    build_failure_payload,
    build_state_diff_retrac_state,
    compact_todo_list,
    planning_context,
)


def test_build_failed_step_retrac_state_tracks_wrong_step_and_suffix():
    state = build_failed_step_retrac_state(
        failure_kind="sandbox_failure",
        issue_type="前置位置依赖未满足",
        issue="第 3 步物理拦截: 前置位置依赖未满足",
        fix_advice="先 NavigateTo 砧板_1",
        todo_list=[
            {"step": 1, "execution": {"skill": "NavigateTo", "parameters": {"target_location": "厨房"}}},
            {"step": 2, "execution": {"skill": "Pickup", "parameters": {"target_item": "土豆_1"}}},
            {"step": 3, "execution": {"skill": "Put", "parameters": {"target_item": "土豆_1", "destination": "砧板_1"}}},
            {"step": 4, "execution": {"skill": "Slice", "parameters": {"target_item": "土豆_1", "surface": "砧板_1"}}},
        ],
        validated_steps=[
            {"step": 1, "execution": {"skill": "NavigateTo", "parameters": {"target_location": "厨房"}}},
            {"step": 2, "execution": {"skill": "Pickup", "parameters": {"target_item": "土豆_1"}}},
        ],
        failed_step={"step": 3, "execution": {"skill": "Put", "parameters": {"target_item": "土豆_1", "destination": "砧板_1"}}},
        sim_env={"土豆_1": {"states": {"isClean": True}}},
        sim_robot={"robot_location": "厨房操作台_1", "robot_holding": "土豆_1"},
    )

    assert state["mode"] == "repair_from_failed_step"
    assert state["trajectory"]["validated_step_count"] == 2
    assert state["trajectory"]["wrong_step"]["skill"] == "Put"
    assert state["trajectory"]["discarded_suffix"][0]["step"] == 3
    assert state["frontier"]["next_step_num"] == 3


def test_build_state_diff_retrac_state_marks_recovery_append_mode():
    state = build_state_diff_retrac_state(
        issue_type="状态差异审计拦截",
        issue="多了手持副作用",
        fix_advice="补一个 Put",
        todo_list=[{"step": 1, "execution": {"skill": "Pickup", "parameters": {"target_item": "盘子_1"}}}],
        validated_steps=[{"step": 1, "execution": {"skill": "Pickup", "parameters": {"target_item": "盘子_1"}}}],
        sim_env={"盘子_1": {"states": {"isClean": True}}},
        sim_robot={"robot_location": "水槽_1", "robot_holding": "盘子_1"},
        state_diff={"changed_entity_count": 1, "entities": []},
        audit_result={"unexpected_diffs": [{"path": "robot.robot_holding"}], "accepted_diffs": []},
    )

    assert state["mode"] == "append_recovery_after_valid_plan"
    assert state["trajectory"]["validated_step_count"] == 1
    assert state["current_simulated_state"]["changed_state_diff"]["changed_entity_count"] == 1


def test_strip_repeated_prefix_removes_duplicated_suffix_prefix():
    validated = [
        {"step": 1, "execution": {"skill": "NavigateTo", "parameters": {"target_location": "厨房"}}},
        {"step": 2, "execution": {"skill": "Open", "parameters": {"target_container": "冰箱_1"}}},
    ]
    candidate = [
        {"step": 3, "execution": {"skill": "NavigateTo", "parameters": {"target_location": "厨房"}}},
        {"step": 4, "execution": {"skill": "Open", "parameters": {"target_container": "冰箱_1"}}},
        {"step": 5, "execution": {"skill": "Pickup", "parameters": {"target_item": "冷冻猪肉_1"}}},
    ]

    assert strip_repeated_prefix(validated, candidate) == [
        {"step": 5, "execution": {"skill": "Pickup", "parameters": {"target_item": "冷冻猪肉_1"}}}
    ]


def test_failure_payload_preserves_memory_when_recording_is_disabled():
    memory = {"failed_lessons": ["existing"], "attempt": 2}

    payload = build_failure_payload(
        issue="new issue",
        fix="new fix",
        memory=memory,
        validated_steps=[],
        checkpoint_env={},
        checkpoint_robot={},
        record_retrac_memory=False,
    )

    assert payload["re_trac_memory"] == memory
    assert payload["re_trac_memory"] is not memory
    assert payload["re_trac_memory"]["failed_lessons"] is not memory["failed_lessons"]


def test_compact_todo_list_assigns_missing_step_number_to_execution_step():
    compact = compact_todo_list(
        [{"execution": {"skill": "Open", "parameters": {"target": "fridge_1"}}}]
    )

    assert compact[0]["step"] == 1


def test_planning_context_does_not_expose_mutable_checkpoint_state():
    state = {
        "validated_steps": [{"execution": {"parameters": {"target": "cup_1"}}}],
        "checkpoint_env": {"cup_1": {"states": {"isClean": False}}},
        "checkpoint_robot": {"robot_holding": "cup_1"},
    }

    context = planning_context(state=state, resolved_env={}, fallback_robot={})
    context["validated_steps"][0]["execution"]["parameters"]["target"] = "plate_1"
    context["current_env"]["cup_1"]["states"]["isClean"] = True

    assert state["validated_steps"][0]["execution"]["parameters"]["target"] == "cup_1"
    assert state["checkpoint_env"]["cup_1"]["states"]["isClean"] is False
