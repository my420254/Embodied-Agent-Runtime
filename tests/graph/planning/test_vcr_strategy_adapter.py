import json
from types import SimpleNamespace

from graph.planning.evaluation import evaluator
from graph.planning.evaluation.repair_strategies.vcr import diagnosis
from graph.planning.evaluation.repair_strategies.contracts import RepairDiagnosis
from skills.planning_catalog import SkillPlanningCatalog, SkillPlanningSpec


def test_vcr_strategy_diagnoses_full_plan_and_reassembles_complete_candidate(
    monkeypatch,
):
    captured = {}
    monkeypatch.setattr(
        diagnosis,
        "analyze_counterfactual_failure_windows",
        lambda **kwargs: {
            "success": True,
            "windows": [
                {
                    "start_index": 0,
                    "anchor_index": 1,
                    "failures": [
                        {
                            "step": kwargs["steps"][1],
                            "issue_type": kwargs["first_issue_type"],
                            "fix_advice": kwargs["first_fix_advice"],
                        }
                    ],
                    "checkpoint": {
                        "rollback_step_num": 1,
                        "reason": "location dependency",
                        "causal_predicate": "robot_location",
                        "causal_action": {
                            "step": 1,
                            "skill": "NavigateTo",
                            "parameters": {"target_location": "错误位置_1"},
                        },
                        "causal_before": "起点_1",
                        "causal_after": "错误位置_1",
                        "failed_preconditions": [
                            {
                                "predicate": "robot.robot.robot_location",
                                "required_value": "橱柜_1",
                            }
                        ],
                        "checkpoint_env": {
                            "厨房_1": {
                                "type": "room",
                                "direct_parent": "未知环境",
                                "states": {},
                            },
                            "卧室_1": {
                                "type": "room",
                                "direct_parent": "未知环境",
                                "states": {},
                            },
                            "起点_1": {
                                "type": "receptacle",
                                "direct_parent": "厨房_1",
                                "states": {},
                            },
                            "错误位置_1": {
                                "type": "receptacle",
                                "direct_parent": "厨房_1",
                                "states": {},
                            },
                            "橱柜_1": {
                                "type": "receptacle",
                                "direct_parent": "厨房_1",
                                "states": {"isOpen": False},
                                "is_container": True,
                            },
                            "工作台_1": {
                                "type": "receptacle",
                                "direct_parent": "厨房_1",
                                "states": {"isClean": True},
                            },
                            "远端工作台_1": {
                                "type": "receptacle",
                                "direct_parent": "卧室_1",
                                "states": {"isClean": True},
                            },
                        },
                        "checkpoint_robot": {
                            "robot_location": "起点_1",
                            "robot_holding": "空",
                        },
                    },
                    "source_windows": [
                        {"start_index": 0, "anchor_index": 1}
                    ],
                    "merge_reasons": [],
                }
            ],
            "states_after": {
                1: {
                    "environment": {
                        "厨房_1": {
                            "type": "room",
                            "direct_parent": "未知环境",
                            "states": {},
                        },
                        "错误位置_1": {
                            "direct_parent": "厨房_1",
                            "states": {},
                        },
                        "橱柜_1": {
                            "direct_parent": "厨房_1",
                            "states": {"isOpen": True},
                        },
                    },
                    "robot": {
                        "robot_location": "橱柜_1",
                        "robot_holding": "空",
                    },
                }
            },
        },
    )
    original_analyzer = diagnosis.analyze_counterfactual_failure_windows

    def capture_analysis(**kwargs):
        captured.update(kwargs)
        return original_analyzer(**kwargs)

    monkeypatch.setattr(diagnosis, "analyze_counterfactual_failure_windows", capture_analysis)
    adapter = diagnosis.VCRRepairStrategy(
        max_segment_actions=7,
        max_backtrack_depth=3,
        merge_gap_actions=2,
    )
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
        {
            "step": 3,
            "execution": {
                "skill": "Pickup",
                "parameters": {"target_object": "杯子_1"},
            },
        },
    ]
    context = SimpleNamespace(
        todo_list=todo_list,
        validated_steps=[todo_list[0]],
        failed_step=todo_list[1],
        issue_type="failure",
        fix_advice="repair",
        failure_env={},
        failure_robot={},
        trajectory_records=[],
        sandbox_start_env={},
        sandbox_start_robot={},
        apply_action=lambda *args: (True, "", ""),
        skill_profile="profile",
        skill_catalog=SkillPlanningCatalog(
            [
                SkillPlanningSpec(
                    name="NavigateTo",
                    location_param="target_location",
                ),
                SkillPlanningSpec(
                    name="Open",
                    target_param="target_container",
                    location_param="target_container",
                    requires_empty_hand=True,
                    state_key="isOpen",
                    state_value=True,
                ),
                SkillPlanningSpec(name="Pickup", item_param="target_item"),
                SkillPlanningSpec(
                    name="Put",
                    item_param="target_item",
                    destination_param="destination",
                ),
            ]
        ),
        skill_closure=["NavigateTo", "Open", "Pickup", "Put"],
        skill_handlers={"Open": object()},
        skill_prompts="NavigateTo(target_location)",
        goal_test=lambda env, robot: True,
        structured_task={
            "intent": "move",
            "required_item_names": {
                "targets": {"primary": ["杯子_1"], "alternatives": []},
                "tools": {"primary": [], "alternatives": []},
                "receptacles": {
                    "primary": ["橱柜_1"],
                    "alternatives": [],
                },
            },
        },
        relevant_item_names=["杯子_1", "橱柜_1", "工作台_1"],
        environment={},
    )

    found = adapter.find_errors(context)
    generated = [
        {
            "execution": {
                "skill": "NavigateTo",
                "parameters": {"target_location": "橱柜_1"},
            }
        },
        {
            "execution": {
                "skill": "Open",
                "parameters": {"target_container": "橱柜_1"},
            }
        }
    ]
    assembled = adapter.reassemble(found, generated)
    payload = json.loads(found.prompt.split("\n\n", 1)[1])
    repair_window = payload["repair_window"]

    assert found.error == ""
    assert "complete_todo_list" not in found.prompt
    assert '"task_goal": "move"' in found.prompt
    assert '"repair_window"' in found.prompt
    assert repair_window["id"] == "window_1"
    assert '"position": {' in found.prompt
    assert '"start_step": 1' in found.prompt
    assert '"end_step": 2' in found.prompt
    assert "动作数量可以不同于原窗口步数" in found.prompt
    assert "每个 action 都必须从当前模拟状态满足对应 requires" in found.prompt
    assert "保持 root_action 并在 failed_action 前补足前置条件" in found.prompt
    assert "替换 root_action" in found.prompt
    assert repair_window["position"] == {"start_step": 1, "end_step": 2}
    assert repair_window["current_state"]["robot"] == {
        "robot_location": "起点_1",
        "robot_holding": "空",
    }
    assert repair_window["current_state"]["entities"] == {
        "橱柜_1": {
            "type": "receptacle",
            "is_container": True,
            "direct_parent": "厨房_1",
            "states": {"isOpen": False},
        },
        "工作台_1": {
            "type": "receptacle",
            "direct_parent": "厨房_1",
            "states": {"isClean": True},
        },
    }
    assert repair_window["target_state"]["robot"] == {
        "robot_location": "橱柜_1",
        "robot_holding": "空",
    }
    assert repair_window["target_state"]["entities"] == {
        "橱柜_1": {
            "direct_parent": "厨房_1",
            "states": {"isOpen": True},
        },
    }
    assert repair_window["failure_obligations"] == [
        {
            "error_id": "window_1_error_1",
            "root_action": {
                "step": 1,
                "skill": "NavigateTo",
                "parameters": {"target_location": "错误位置_1"},
            },
            "failed_action": {
                "step": 2,
                "skill": "Open",
                "parameters": {"target_container": "橱柜_1"},
            },
            "failed_action_preconditions": [
                {
                    "predicate": "robot.robot.robot_location",
                    "required_value": "橱柜_1",
                }
            ],
            "root_state_change": {
                "predicate": "robot_location",
                "before": "起点_1",
                "after": "错误位置_1",
            },
        }
    ]
    assert [item["name"] for item in repair_window["repair_strategies"]] == [
        "preserve_root_action",
        "replace_root_action",
    ]
    assert "工作台_1" in repair_window["current_state"]["entities"]
    assert "远端工作台_1" not in repair_window["current_state"]["entities"]
    assert {
        "predicate": "state.橱柜_1.isOpen",
        "required_value": True,
    } in found.merge_context["window_validation"][0]["exit_contract"]
    contracts = {
        item["skill"]: item for item in repair_window["skill_contracts"]
    }
    assert contracts["NavigateTo"]["effects"] == [
        {"robot_location": "$target_location"}
    ]
    assert {"robot_location": "$target_container"} in contracts["Open"][
        "requires"
    ]
    assert {"robot_holding": "空"} in contracts["Open"]["requires"]
    assert contracts["Put"]["requires"][-1] == {
        "$destination.isOpen": "若存在该状态则不得为 false"
    }
    assert not {
        "replace_interval",
        "original_actions",
        "action_contracts",
        "must_fix",
        "required_exit_state",
        "next_fixed_action",
        "available_entities",
        "max_actions",
    } & repair_window.keys()
    assert "protected_suffix" not in repair_window
    assert "execution_rules" not in payload
    assert "staging_destinations" not in repair_window
    prompt_rules = found.prompt.split("\n\n", 1)[0]
    assert all(
        action_pattern not in prompt_rules
        for action_pattern in (
            "暂存",
            "重新抓取",
            "Pickup 后",
            "Put 前",
            "staging_destination",
        )
    )
    assert "使用 skill_contracts 中的技能" in prompt_rules
    assert "current_state 规划到 target_state" in prompt_rules
    assert "must_fix" not in found.prompt
    assert "original_actions" not in found.prompt
    assert "max_actions" not in found.prompt
    assert '"counterfactual_suffix":' not in found.prompt
    assert "checkpoint_environment" not in found.prompt
    assert "original_interval" not in found.prompt
    assert captured["max_backtrack_depth"] == 3
    assert captured["first_failed_index"] == 1
    assert captured["goal_test"] is context.goal_test
    assert assembled.success is True
    assert [step["execution"]["skill"] for step in assembled.todo_list] == [
        "NavigateTo",
        "Open",
        "Pickup",
    ]
    assert [step["step"] for step in assembled.todo_list] == [1, 2, 3]
    assert [check["segment_id"] for check in assembled.segment_checks] == ["window_1"]
    assert assembled.step_provenance == [
        {
            "source": "generated",
            "repair_window_id": "window_1",
            "window_action_index": 1,
            "generated_action_index": 1,
        },
        {
            "source": "generated",
            "repair_window_id": "window_1",
            "window_action_index": 2,
            "generated_action_index": 2,
        },
        {"source": "original", "original_step": 3},
    ]


def test_vcr_publishes_only_earliest_window_and_preserves_later_plan(monkeypatch):
    todo_list = [
        {
            "step": index,
            "execution": {
                "skill": "Original",
                "parameters": {"label": f"original_{index}"},
            },
        }
        for index in range(1, 9)
    ]
    windows = [
        _causal_window(todo_list, start_index=0, anchor_index=1),
        _causal_window(todo_list, start_index=6, anchor_index=7),
    ]
    monkeypatch.setattr(
        diagnosis,
        "analyze_counterfactual_failure_windows",
        lambda **kwargs: {"success": True, "windows": windows},
    )
    adapter = diagnosis.VCRRepairStrategy(merge_gap_actions=1)

    found = adapter.find_errors(_context(todo_list))
    payload = json.loads(found.prompt.split("\n\n", 1)[1])
    assembled = adapter.reassemble(
        found,
        [
            {
                "execution": {
                    "skill": "RepairFirst",
                    "parameters": {},
                },
            },
        ],
    )

    assert payload["repair_window"]["id"] == "window_1"
    assert "window_2" not in found.prompt
    assert found.merge_context["repair_windows"] == [
        {"window_id": "window_1", "start_index": 0, "end_index": 1},
    ]
    assert assembled.success is True
    assert [step["execution"]["skill"] for step in assembled.todo_list] == [
        "RepairFirst",
        "Original",
        "Original",
        "Original",
        "Original",
        "Original",
        "Original",
    ]
    assert [
        step["execution"]["parameters"]["label"]
        for step in assembled.todo_list[1:]
    ] == [
        "original_3",
        "original_4",
        "original_5",
        "original_6",
        "original_7",
        "original_8",
    ]
    assert all(
        "repair_window_id" not in step for step in assembled.todo_list
    )
    assert [check["segment_id"] for check in assembled.segment_checks] == ["window_1"]


def test_vcr_default_does_not_merge_overlaps_and_selects_earliest_failure(monkeypatch):
    todo_list = [
        {
            "step": index,
            "execution": {
                "skill": "Original",
                "parameters": {"label": f"original_{index}"},
            },
        }
        for index in range(1, 7)
    ]
    windows = [
        _causal_window(todo_list, start_index=0, anchor_index=3),
        _causal_window(todo_list, start_index=1, anchor_index=1),
        _causal_window(todo_list, start_index=1, anchor_index=2),
    ]
    monkeypatch.setattr(
        diagnosis,
        "analyze_counterfactual_failure_windows",
        lambda **kwargs: {"success": True, "windows": windows},
    )

    found = diagnosis.VCRRepairStrategy().find_errors(_context(todo_list))
    payload = json.loads(found.prompt.split("\n\n", 1)[1])

    assert found.error == ""
    assert found.merge_context["repair_windows"] == [
        {"window_id": "window_1", "start_index": 1, "end_index": 1},
    ]
    assert payload["repair_window"]["position"] == {
        "start_step": 2,
        "end_step": 2,
    }


def test_vcr_merges_nearby_windows_without_exposing_causal_details(monkeypatch):
    todo_list = [
        {
            "step": index,
            "execution": {
                "skill": "Original",
                "parameters": {"label": f"original_{index}"},
            },
        }
        for index in range(1, 6)
    ]
    windows = [
        _causal_window(todo_list, start_index=0, anchor_index=1),
        _causal_window(todo_list, start_index=3, anchor_index=4),
    ]
    monkeypatch.setattr(
        diagnosis,
        "analyze_counterfactual_failure_windows",
        lambda **kwargs: {"success": True, "windows": windows},
    )
    adapter = diagnosis.VCRRepairStrategy(merge_gap_actions=1)

    found = adapter.find_errors(_context(todo_list))
    payload = json.loads(found.prompt.split("\n\n", 1)[1])

    assert found.merge_context["repair_windows"] == [
        {"window_id": "window_1", "start_index": 0, "end_index": 4}
    ]
    assert payload["repair_window"]["id"] == "window_1"
    assert payload["repair_window"]["position"] == {
        "start_step": 1,
        "end_step": 5,
    }
    assert not {"must_fix", "causal_groups"} & payload["repair_window"].keys()


def test_vcr_rejects_exit_contract_entities_not_recalled_by_understanding():
    assert diagnosis._missing_exit_entities(
        [
            {
                "predicate": "state.冰箱_1.isOpen",
                "required_value": False,
            },
            {
                "predicate": "entity.鸡蛋_1.direct_parent",
                "required_value": "陶瓷盘_1",
            },
        ],
        ["鸡蛋_1", "陶瓷盘_1"],
    ) == ["冰箱_1"]


def test_vcr_checks_entity_values_referenced_by_exit_contract():
    snapshot = {
        "environment": {
            "鸡蛋_1": {"direct_parent": "冷藏室_1"},
            "陶瓷盘_1": {"direct_parent": "顶层橱柜_1"},
        }
    }

    assert diagnosis._missing_exit_entities(
        [
            {
                "predicate": "entity.鸡蛋_1.direct_parent",
                "required_value": "陶瓷盘_1",
            }
        ],
        ["鸡蛋_1"],
        snapshot,
    ) == ["陶瓷盘_1"]


def test_vcr_exit_contract_keeps_all_counterfactual_entity_deltas():
    entry_snapshot = {
        "environment": {
            "鸡蛋_1": {
                "direct_parent": "盘_1",
                "states": {"isCooked": False, "isCold": True},
            },
            "设备_1": {
                "direct_parent": "台面_1",
                "phase": "idle",
                "states": {"isToggled": False},
            },
        },
        "robot": {"robot_location": "台面_1", "robot_holding": "空"},
    }
    exit_snapshot = {
        "environment": {
            "鸡蛋_1": {
                "direct_parent": "盘_2",
                "states": {"isCooked": True, "isCold": False},
            },
            "设备_1": {
                "direct_parent": "台面_1",
                "phase": "ready",
                "states": {"isToggled": True},
            },
        },
        "robot": {"robot_location": "台面_1", "robot_holding": "空"},
    }

    contract = diagnosis._counterfactual_exit_contract(
        entry_snapshot=entry_snapshot,
        exit_snapshot=exit_snapshot,
        causal_groups=[],
        entities=["鸡蛋_1", "设备_1"],
    )

    assert contract == [
        {"predicate": "robot.robot.robot_holding", "required_value": "空"},
        {"predicate": "robot.robot.robot_location", "required_value": "台面_1"},
        {
            "predicate": "entity.鸡蛋_1.direct_parent",
            "required_value": "盘_2",
        },
        {"predicate": "state.鸡蛋_1.isCold", "required_value": False},
        {"predicate": "state.鸡蛋_1.isCooked", "required_value": True},
        {"predicate": "entity.设备_1.phase", "required_value": "ready"},
        {"predicate": "state.设备_1.isToggled", "required_value": True},
    ]


def test_vcr_expands_invalid_hand_exit_to_proven_containment_handoff():
    steps = [
        {
            "step": 1,
            "execution": {"skill": "Pickup", "parameters": {"target_item": "鸡蛋_1"}},
        },
        {
            "step": 2,
            "execution": {"skill": "Pickup", "parameters": {"target_item": "陶瓷盘_1"}},
        },
        {
            "step": 3,
            "execution": {
                "skill": "Put",
                "parameters": {
                    "target_item": "鸡蛋_1",
                    "destination": "陶瓷盘_1",
                },
            },
        },
    ]
    raw_exit = {
        "environment": {
            "鸡蛋_1": {"direct_parent": "robot_hand"},
            "陶瓷盘_1": {"direct_parent": "robot_hand"},
        },
        "robot": {"robot_location": "顶层橱柜_1", "robot_holding": "陶瓷盘_1"},
    }
    handoff_exit = {
        "environment": {
            "鸡蛋_1": {"direct_parent": "陶瓷盘_1"},
            "陶瓷盘_1": {"direct_parent": "robot_hand"},
        },
        "robot": {"robot_location": "顶层橱柜_1", "robot_holding": "空"},
    }

    windows, error = diagnosis._resolve_containment_handoff_windows(
        repair_windows=[{"start_index": 0, "anchor_index": 1}],
        steps=steps,
        analysis={"states_after": {1: raw_exit, 2: handoff_exit}},
        skill_catalog=SkillPlanningCatalog(
            [
                SkillPlanningSpec(name="Pickup", item_param="target_item"),
                SkillPlanningSpec(
                    name="Put",
                    item_param="target_item",
                    destination_param="destination",
                ),
            ]
        ),
    )

    assert error == ""
    assert windows[0]["anchor_index"] == 2
    assert windows[0]["target_snapshot"] == {
        "environment": {
            "鸡蛋_1": {"direct_parent": "陶瓷盘_1"},
            "陶瓷盘_1": {"direct_parent": "robot_hand"},
        },
        "robot": {
            "robot_location": "顶层橱柜_1",
            "robot_holding": "陶瓷盘_1",
        },
    }
    assert diagnosis._hand_ownership(windows[0]["target_snapshot"])["valid"] is True


def test_vcr_rejects_invalid_hand_exit_without_proven_containment_handoff():
    raw_exit = {
        "environment": {
            "鸡蛋_1": {"direct_parent": "robot_hand"},
            "陶瓷盘_1": {"direct_parent": "robot_hand"},
        },
        "robot": {"robot_holding": "陶瓷盘_1"},
    }

    windows, error = diagnosis._resolve_containment_handoff_windows(
        repair_windows=[{"start_index": 0, "anchor_index": 0}],
        steps=[
            {
                "step": 1,
                "execution": {
                    "skill": "Pickup",
                    "parameters": {"target_item": "陶瓷盘_1"},
                },
            }
        ],
        analysis={"states_after": {0: raw_exit}},
        skill_catalog=SkillPlanningCatalog(
            [SkillPlanningSpec(name="Pickup", item_param="target_item")]
        ),
    )

    assert windows == []
    assert "后续没有明确将 鸡蛋_1 放入 陶瓷盘_1" in error


def test_vcr_segment_validation_reads_generic_entity_fields():
    assert evaluator._segment_contract_mismatches(
        {"设备_1": {"phase": "ready"}},
        {},
        [{"predicate": "entity.设备_1.phase", "required_value": "ready"}],
    ) == []


def test_vcr_compact_contracts_do_not_expand_understanding_skill_closure():
    catalog = SkillPlanningCatalog(
        [
            SkillPlanningSpec(name="NavigateTo", location_param="target_location"),
            SkillPlanningSpec(
                name="Open",
                target_param="target_container",
                location_param="target_container",
                state_key="isOpen",
                state_value=True,
            ),
            SkillPlanningSpec(
                name="Put",
                item_param="target_item",
                destination_param="destination",
            ),
        ]
    )

    contracts = diagnosis._compact_skill_contracts(catalog, ["Open"])

    assert [contract["skill"] for contract in contracts] == ["Open"]


def _causal_window(todo_list, *, start_index, anchor_index):
    return {
        "start_index": start_index,
        "anchor_index": anchor_index,
        "failures": [
            {
                "index": anchor_index,
                "step": todo_list[anchor_index],
                "issue_type": f"failure_{anchor_index + 1}",
                "fix_advice": f"repair_{anchor_index + 1}",
            }
        ],
        "checkpoint": {
            "rollback_step_num": start_index + 1,
            "reason": f"cause_{start_index + 1}",
            "causal_predicate": "robot_location",
            "causal_action": todo_list[start_index],
            "causal_before": f"before_{start_index + 1}",
            "causal_after": f"after_{start_index + 1}",
            "failed_preconditions": [
                {
                    "predicate": "robot.robot.robot_location",
                    "required_value": f"target_{anchor_index + 1}",
                }
            ],
        },
        "source_windows": [
            {"start_index": start_index, "anchor_index": anchor_index}
        ],
        "merge_reasons": [],
    }


def _context(todo_list):
    catalog = SkillPlanningCatalog(
        [SkillPlanningSpec(name="Original", target_param="label")]
    )
    return SimpleNamespace(
        todo_list=todo_list,
        validated_steps=[],
        failed_step=todo_list[1],
        issue_type="failure",
        fix_advice="repair",
        failure_env={},
        failure_robot={},
        trajectory_records=[],
        sandbox_start_env={},
        sandbox_start_robot={},
        apply_action=lambda *args: (True, "", ""),
        skill_profile="profile",
        skill_catalog=catalog,
        skill_closure=["Original"],
        skill_handlers={"Original": object()},
        skill_prompts="Original(label)",
        goal_test=None,
        structured_task={"intent": "repair all windows"},
        relevant_item_names=[],
        environment={},
    )
