import json
from types import SimpleNamespace

import pytest

from graph.planning import node as planning_node
from graph import routes as graph_routes
from graph.planning.evaluation import evaluator, flags as evaluation_flags
from graph.planning.evaluation.models import (
    EvaluationFailure,
    EvaluationFailureCode,
)
from graph.planning.evaluation.composition import (
    resolve_repair_strategy,
)
from graph.planning.repair import (
    PlanningRegenerationError,
    regenerate_todo_list,
)
from graph.planning.config import merge_planning_feature_flags
from skills.planning_catalog import SkillPlanningCatalog, SkillPlanningSpec


class _Response:
    def __init__(self, content):
        self.content = content


class _SequenceLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.prompts = []

    def invoke(self, messages):
        self.prompts.append(messages[0].content)
        return _Response(self.responses.pop(0))


def test_regeneration_preserves_model_invocation_failures():
    def fail_factory():
        raise OSError("model transport unavailable")

    with pytest.raises(PlanningRegenerationError) as captured:
        regenerate_todo_list(
            "repair",
            None,
            "skills",
            planning_llm_factory=fail_factory,
            parse_json=lambda *_args, **_kwargs: {},
            ensure_shape=lambda step: step,
            message_factory=lambda content: _Response(content),
        )

    assert captured.value.category == "model_invocation"
    assert "model transport unavailable" in str(captured.value)


def test_regeneration_rejects_malformed_model_output_explicitly():
    with pytest.raises(PlanningRegenerationError) as captured:
        regenerate_todo_list(
            "repair",
            None,
            "skills",
            planning_llm_factory=lambda: _SequenceLLM(["not-json"]),
            parse_json=lambda *_args, **_kwargs: {},
            ensure_shape=lambda step: step,
            message_factory=lambda content: _Response(content),
        )

    assert captured.value.category == "model_output"
    assert "动作数组" in str(captured.value)


def test_regeneration_appends_skill_contracts_once():
    llm = _SequenceLLM(
        ['{"todo_list": [{"execution": {"skill": "NavigateTo", "parameters": {}}}]}']
    )

    generated = regenerate_todo_list(
        "vcr repair payload",
        "core_household",
        "NavigateTo(target_location)",
        planning_llm_factory=lambda: llm,
        parse_json=lambda *_args, **_kwargs: {
            "todo_list": [
                {
                    "execution": {
                        "skill": "NavigateTo",
                        "parameters": {},
                    }
                }
            ]
        },
        ensure_shape=lambda step: step,
        message_factory=lambda content: _Response(content),
    )

    assert len(generated) == 1
    assert llm.prompts[0].count("vcr repair payload") == 1
    assert llm.prompts[0].count("NavigateTo(target_location)") == 1


def test_vcr_compact_contract_mode_skips_full_skill_markdown(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        planning_node,
        "load_enabled_skill_prompts",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("VCR compact mode must not load full skill markdown")
        ),
    )
    monkeypatch.setattr(
        planning_node,
        "regenerate_todo_list",
        lambda prompt, profile, skills_markdown, **_kwargs: captured.update(
            {
                "prompt": prompt,
                "profile": profile,
                "skills_markdown": skills_markdown,
            }
        )
        or [{"execution": {"skill": "NavigateTo", "parameters": {}}}],
    )

    generated = planning_node._regenerate_evaluation_repair(
        {
            "prompt": "compact VCR prompt",
            "skill_contract_mode": "compact",
        },
        "core_household",
    )

    assert generated
    assert captured == {
        "prompt": "compact VCR prompt",
        "profile": "core_household",
        "skills_markdown": "",
    }


def test_regeneration_accepts_single_window_actions_output():
    actions = [
        {
            "execution": {
                "skill": "NavigateTo",
                "parameters": {"target_location": "工作台_1"},
            }
        }
    ]
    generated = regenerate_todo_list(
        "vcr repair payload",
        "core_household",
        "NavigateTo(target_location)",
        planning_llm_factory=lambda: _SequenceLLM(["{}"]),
        parse_json=lambda *_args, **_kwargs: {
            "repair_window_id": "window_1",
            "actions": actions,
        },
        ensure_shape=lambda step: step,
        message_factory=lambda content: _Response(content),
    )

    assert generated == actions


def test_vcr_retry_prompt_uses_only_compact_validation_errors():
    failures = evaluator._candidate_failures_for_retry(
        {
            "strategy_name": "vcr",
            "candidate_failures": [{"validation_scope": "stale_failure"}],
        },
        {"validation_scope": "independent_repair_windows"},
    )
    prompt = evaluator._candidate_retry_prompt(
        "base prompt",
        failures,
        strategy_name="vcr",
    )
    payload = json.loads(prompt.rsplit("\n\n", 1)[1])

    assert failures == [{"validation_scope": "independent_repair_windows"}]
    assert payload["candidate_feedback"]["status"] == (
        "rejected_during_repair_window_validation"
    )
    assert "repair_window.repair_strategies" in payload["candidate_feedback"]["instruction"]
    assert "保持 root_action" in payload["candidate_feedback"]["instruction"]
    assert "替换 root_action" in payload["candidate_feedback"]["instruction"]
    assert "rejected_sequences" in payload["candidate_feedback"]["instruction"]
    assert payload["candidate_feedback"]["validation_errors"] == []
    assert "latest_failure" not in payload["candidate_feedback"]
    assert "failures" not in payload["candidate_feedback"]


def test_vcr_retry_remembers_unique_compact_failure_constraints():
    fridge_constraint = {
        "repair_window_id": "window_1",
        "failed_action": {
            "skill": "Close",
            "parameters": {"target_container": "冰箱_1"},
        },
        "causal_errors": [
            {
                "root_action": {
                    "action_index": 0,
                    "skill": "NavigateTo",
                    "parameters": {"target_location": "厨房操作台_1"},
                },
                "state_mismatches": [
                    {
                        "state": "robot_location",
                        "actual": "厨房操作台_1",
                        "expected": "冰箱_1",
                    }
                ],
            }
        ],
    }
    request = {
        "strategy_name": "vcr",
        "candidate_failure_memory": [fridge_constraint],
    }
    feedback = {
        "validation_scope": "independent_repair_windows",
        "failed_windows": [
            {
                "repair_window_id": "window_1",
                "failed_action": {
                    "skill": "Close",
                    "parameters": {"target_container": "冰箱_1"},
                },
                "failed_preconditions": [
                    {
                        "predicate": "robot.robot_holding",
                        "required_value": "空",
                        "actual_value": "鸡蛋_1",
                    }
                ],
                "observed_root_actions": [
                    {
                        "predicate": "robot.robot_holding",
                        "root_action": {
                            "action_index": 1,
                            "skill": "Pickup",
                            "parameters": {"target_item": "鸡蛋_1"},
                        },
                    }
                ],
                "local_segment_path": [
                    {
                        "segment_action_index": 1,
                        "skill": "Pickup",
                        "parameters": {"target_item": "鸡蛋_1"},
                    },
                    {
                        "skill": "Close",
                        "parameters": {"target_container": "冰箱_1"},
                        "is_failed_action": True,
                    },
                ],
            }
        ],
    }

    memory = evaluator._candidate_failure_memory(request, feedback)
    duplicate_memory = evaluator._candidate_failure_memory(
        {**request, "candidate_failure_memory": memory},
        feedback,
    )
    prompt = evaluator._candidate_retry_prompt(
        "base prompt",
        [feedback],
        strategy_name="vcr",
        failure_memory=memory,
    )
    payload = json.loads(prompt.rsplit("\n\n", 1)[1])

    assert len(memory) == 1
    assert memory[0]["failed_action"] == {
        **fridge_constraint["failed_action"],
        "action_index": None,
    }
    assert memory[0]["causal_errors"] == [
        fridge_constraint["causal_errors"][0],
        {
            "root_action": {
                "action_index": 1,
                "skill": "Pickup",
                "parameters": {"target_item": "鸡蛋_1"},
            },
            "state_mismatches": [
                {
                    "state": "robot_holding",
                    "actual": "鸡蛋_1",
                    "expected": "空",
                }
            ],
        },
    ]
    assert memory[0]["rejected_sequences"] == [
        {
            "actions": [
                {
                    "action_index": 1,
                    "skill": "Pickup",
                    "parameters": {"target_item": "鸡蛋_1"},
                },
                {
                    "action_index": 2,
                    "skill": "Close",
                    "parameters": {"target_container": "冰箱_1"},
                    "is_failed_action": True,
                },
            ],
            "failed_action_index": 2,
        }
    ]
    assert duplicate_memory == memory
    assert payload["candidate_feedback"]["validation_errors"] == memory
    assert "rejected_sequences" in prompt
    assert "placeholder_bindings" not in payload["candidate_feedback"]
    assert "observed_tail" not in payload["candidate_feedback"]
    assert "violations" not in payload["candidate_feedback"]


def test_vcr_failure_facts_keep_concrete_container_and_device_values():
    catalog = SkillPlanningCatalog(
        [
            SkillPlanningSpec(
                name="Heat",
                item_param="target_item",
                device_param="heating_device",
                container_state_key="isOpen",
                container_state_value=False,
                device_state_key="isToggled",
                device_state_value=True,
                effect_state_key="isCooked",
                effect_state_value=True,
            )
        ]
    )
    session = SimpleNamespace(skill_catalog=catalog)
    step = {
        "execution": {
            "skill": "Heat",
            "parameters": {
                "target_item": "鸡蛋_1",
                "heating_device": "微波炉_1",
            },
        }
    }
    checkpoint_env = {
        "微波炉_1": {
            "states": {"isOpen": True, "isToggled": False},
        }
    }

    container = evaluator._candidate_failed_preconditions(
        session,
        EvaluationFailure(
            code=EvaluationFailureCode.CONTAINER_STATE,
            issue_type="容器状态不满足",
            fix_advice="设备舱门必须关闭",
            step=step,
            checkpoint_env=checkpoint_env,
        ),
    )
    device = evaluator._candidate_failed_preconditions(
        session,
        EvaluationFailure(
            code=EvaluationFailureCode.DEVICE_STATE,
            issue_type="设备状态不满足",
            fix_advice="设备必须开启",
            step=step,
            checkpoint_env=checkpoint_env,
        ),
    )

    assert container[0] == {
        "code": "container_state",
        "required_condition": "设备舱门必须关闭",
        "predicate": "state.微波炉_1.isOpen",
        "required_value": False,
        "actual_value": True,
    }
    assert device[0] == {
        "code": "device_state",
        "required_condition": "设备必须开启",
        "predicate": "state.微波炉_1.isToggled",
        "required_value": True,
        "actual_value": False,
    }


def test_vcr_generic_failure_is_kept_as_error_without_blank_state_fact():
    constraints = evaluator._compact_vcr_failure_constraints(
        {
            "failed_windows": [
                {
                    "repair_window_id": "window_1",
                    "segment_action_index": 2,
                    "failed_action": {
                        "skill": "UnknownAction",
                        "parameters": {},
                    },
                    "issue_type": "调用无效动作",
                    "failed_preconditions": [
                        {
                            "code": "invalid_action",
                            "required_condition": "不支持该动作",
                        }
                    ],
                }
            ]
        }
    )

    assert constraints == [
        {
            "repair_window_id": "window_1",
            "failed_action": {
                "action_index": 2,
                "skill": "UnknownAction",
                "parameters": {},
            },
            "causal_errors": [],
            "error": {
                "code": "invalid_action",
                "issue_type": "调用无效动作",
            },
        }
    ]


def test_vcr_root_action_comes_only_from_observed_state_writes():
    writes = evaluator._segment_state_writes(
        {},
        {"robot_location": "起点_1", "robot_holding": "空"},
        {},
        {"robot_location": "错误位置_1", "robot_holding": "空"},
    )
    observed = [
        {
            "action_index": 1,
            "action": {
                "skill": "RelocateWithCustomPolicy",
                "parameters": {"destination": "错误位置_1"},
            },
            "writes": writes,
        }
    ]

    roots = evaluator._observed_root_actions(
        observed,
        [
            {
                "predicate": "robot.robot_location",
                "required_value": "目标_1",
                "actual_value": "错误位置_1",
            },
            {
                "predicate": "robot.robot_holding",
                "required_value": "杯子_1",
                "actual_value": "空",
            },
        ],
    )

    assert roots == [
        {
            "predicate": "robot.robot_location",
            "root_action": {
                "action_index": 1,
                "skill": "RelocateWithCustomPolicy",
                "parameters": {"destination": "错误位置_1"},
            },
        },
        {
            "predicate": "robot.robot_holding",
            "root_action": {},
        },
    ]


def test_repair_strategy_is_read_from_evaluation_config_only():
    raw_flags = {"repair_strategy": "ReTrac", "evaluation_repair_attempts": "10"}
    flags = merge_planning_feature_flags(raw_flags)

    assert resolve_repair_strategy(lambda *args, **kwargs: "VCR") == "vcr"
    assert flags["evaluation_repair_attempts"] == 10
    assert not {
        "repair_strategy",
        "sda_repair",
        "vcr_repair",
        "re_trac_repair",
    } & flags.keys()


def test_repair_assembly_output_retries_missing_vcr_windows():
    original = [
        {
            "step": 1,
            "execution": {"skill": "NavigateTo", "parameters": {}},
        }
    ]
    request = {
        "version": "evaluation_repair_v1",
        "round": 2,
        "stage": "sandbox",
        "assembly_mode": "strategy",
        "strategy_name": "vcr",
        "prompt": "base prompt",
        "merge_context": {
            "repair_windows": [
                {"window_id": "window_1"},
                {"window_id": "window_2"},
            ]
        },
        "original_todo_list": original,
    }
    state = {
        "todo_list": original,
        "feature_flags": {"evaluation_repair_attempts": 10},
        "repair_history": [
            {
                "round": 1,
                "stage": "sandbox",
                "status": "rejected",
                "assembled": True,
            },
            {
                "round": 2,
                "stage": "sandbox",
                "status": "diagnosed",
                "assembled": False,
            },
        ],
    }

    retried = evaluator._retry_repair_assembly_output(
        state,
        request,
        "VCR 未生成窗口 window_2 的替换动作",
        generated_count=3,
    )

    assert "execution_status" not in retried
    assert retried["evaluation_repair_request"]["round"] == 3
    assert retried["evaluation_repair_request"]["merge_context"][
        "active_window_ids"
    ] == ["window_1", "window_2"]
    assert "active_repair_window_ids" in retried["evaluation_repair_request"][
        "prompt"
    ]
    assert [entry["status"] for entry in retried["repair_history"]] == [
        "rejected",
        "rejected",
        "diagnosed",
    ]
    rejected = retried["repair_history"][1]
    assert rejected["generated_count"] == 3
    assert rejected["candidate_failure"]["assembly_error"] == (
        "VCR 未生成窗口 window_2 的替换动作"
    )


def test_legacy_repair_flags_are_discarded_without_selecting_strategy():
    raw_flags = {"checkpoint_repair": True, "vcr_repair": True, "sda_repair": False}
    flags = merge_planning_feature_flags(raw_flags)

    assert resolve_repair_strategy(lambda *args, **kwargs: "sda") == "sda"
    assert not {"sda_repair", "vcr_repair", "re_trac_repair"} & flags.keys()


def _configure(monkeypatch, env, llm, apply_action=None, repair_strategy="sda"):
    monkeypatch.setattr(evaluation_flags, "ENABLE_SANDBOX_EVALUATOR", True)
    monkeypatch.setattr(evaluator, "get_full_flat_house", lambda _environment: env)
    monkeypatch.setattr(
        evaluator,
        "apply_sandbox_action",
        apply_action or (lambda *args, **kwargs: (True, "", "")),
    )
    monkeypatch.setattr(evaluator, "get_planning_llm", lambda: llm)
    monkeypatch.setattr(planning_node, "get_planning_llm", lambda: llm)
    monkeypatch.setattr(
        evaluator,
        "get_config",
        lambda *keys, default=None: (
            repair_strategy
            if keys == ("planning", "evaluation", "repair_strategy")
            else default
        ),
    )
    monkeypatch.setattr(
        evaluator,
        "load_enabled_skill_prompts",
        lambda profile=None: "NavigateTo(target_location)",
    )
    monkeypatch.setattr(
        planning_node,
        "load_enabled_skill_prompts",
        lambda profile=None: "NavigateTo(target_location)",
    )
    monkeypatch.setattr(
        evaluator,
        "save_evaluator_finding_to_playbook",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        evaluator,
        "record_rule_feedback",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        evaluator,
        "learn_from_success",
        lambda *args, **kwargs: None,
    )


def _run_planning_evaluation_cycle(state):
    current = dict(state)
    for _ in range(8):
        evaluated = evaluator.evaluate_feasibility(current)
        current.update(evaluated)
        if evaluated.get("is_feasible") or evaluated.get("execution_status") == "failed":
            return current
        if evaluated.get("evaluation_recheck"):
            continue
        if not evaluated.get("evaluation_repair_request"):
            return current
        planned = planning_node.decompose_task(current)
        current.update(planned)
        if planned.get("execution_status") == "failed":
            return current
        current.update(evaluator.assemble_repair_candidate(current))
    raise AssertionError("planning/evaluation repair cycle did not terminate")


def _state(todo_list, feature_flags=None, environment=None):
    return {
        "todo_list": todo_list,
        "env_state": {"robot_location": "起点_1", "robot_holding": "空"},
        "structured_task": {"intent": "移动到桌子"},
        "relevant_item_names": ["起点_1", "错误位置_1", "橱柜_1", "桌子_1"],
        "skill_closure": [
            "NavigateTo",
            "Pickup",
            "Put",
            "Open",
            "Close",
            "Clean",
            "Slice",
            "ToggleOn",
            "ToggleOff",
            "Heat",
            "Cool",
        ],
        "iteration_count": 1,
        "environment": environment or {"__request_environment__": {"states": {}}},
        "validated_steps": [],
        "injected_playbook_rule_ids": [],
        "feature_flags": {
            "sandbox_evaluator": True,
            "semantic_audit": False,
            "state_diff_audit": False,
            **(feature_flags or {}),
        },
    }


def test_legality_stage_reports_all_violations_in_one_replan_prompt(monkeypatch):
    env = {
        "起点_1": {"type": "receptacle", "states": {}},
        "桌子_1": {"type": "receptacle", "states": {}},
    }
    llm = _SequenceLLM(
        [
            '{"todo_list": [{"execution": {"skill": "NavigateTo", '
            '"parameters": {"target_location": "桌子_1"}}}]}'
        ]
    )
    _configure(monkeypatch, env, llm)
    state = _state(
        [
            {
                "step": 1,
                "execution": {
                    "skill": "InventedSkill",
                    "parameters": {"target": "不存在_1"},
                },
            },
            {
                "step": 2,
                "execution": {
                    "skill": "Pickup",
                    "parameters": {"extra": "桌子_1"},
                },
            },
        ]
    )

    result = _run_planning_evaluation_cycle(state)

    assert result["is_feasible"] is True, result
    assert len(llm.prompts) == 1
    assert "unknown_skill" in llm.prompts[0]
    assert "missing_parameter" in llm.prompts[0]
    assert "unexpected_parameter" in llm.prompts[0]
    assert result["repair_history"][0]["stage"] == "legality"
    assert len(result["repair_history"][0]["violations"]) == 3


def test_llm_replan_is_checked_again_before_sandbox(monkeypatch):
    env = {
        "起点_1": {"type": "receptacle", "states": {}},
        "桌子_1": {"type": "receptacle", "states": {}},
    }
    llm = _SequenceLLM(
        [
            '{"todo_list": [{"execution": {"skill": "Pickup", "parameters": {}}}]}',
            '{"todo_list": [{"execution": {"skill": "NavigateTo", '
            '"parameters": {"target_location": "桌子_1"}}}]}',
        ]
    )
    _configure(monkeypatch, env, llm)
    state = _state(
        [
            {
                "step": 1,
                "execution": {"skill": "InventedSkill", "parameters": {}},
            }
        ]
    )

    result = _run_planning_evaluation_cycle(state)

    assert result["is_feasible"] is True
    assert len(llm.prompts) == 2
    assert "unknown_skill" in llm.prompts[0]
    assert "missing_parameter" in llm.prompts[1]
    assert [item["stage"] for item in result["repair_history"]] == [
        "legality",
        "legality",
    ]


def test_empty_plan_is_regenerated_before_sandbox(monkeypatch):
    env = {
        "起点_1": {"type": "receptacle", "states": {}},
        "桌子_1": {"type": "receptacle", "states": {}},
    }
    llm = _SequenceLLM(
        [
            '{"todo_list": [{"execution": {"skill": "NavigateTo", '
            '"parameters": {"target_location": "桌子_1"}}}]}'
        ]
    )
    _configure(monkeypatch, env, llm)

    result = _run_planning_evaluation_cycle(_state([]))

    assert result["is_feasible"] is True
    assert "empty_plan" in llm.prompts[0]
    assert result["repair_history"][0]["stage"] == "legality"


def test_retrac_diagnoses_failure_and_reassembles_generated_suffix(monkeypatch):
    env = {
        "起点_1": {"type": "receptacle", "states": {}},
        "错误位置_1": {"type": "receptacle", "states": {}},
        "橱柜_1": {
            "type": "cabinet",
            "states": {"isOpen": False},
            "is_container": True,
        },
    }
    llm = _SequenceLLM(
        [
            '{"todo_list": ['
            '{"execution": {"skill": "NavigateTo", '
            '"parameters": {"target_location": "橱柜_1"}}},'
            '{"execution": {"skill": "Open", '
            '"parameters": {"target_container": "橱柜_1"}}}'
            ']}'
        ]
    )

    def apply_action(sim_env, sim_robot, skill, parameters, profile=None):
        if skill == "NavigateTo":
            sim_robot["robot_location"] = parameters["target_location"]
            return True, "", ""
        if skill == "Open" and sim_robot["robot_location"] != parameters["target_container"]:
            return False, "前置位置依赖未满足", "必须先导航到目标容器"
        sim_env[parameters["target_container"]]["states"]["isOpen"] = True
        return True, "", ""

    _configure(monkeypatch, env, llm, apply_action, repair_strategy="retrac")
    state = _state(
        [
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
        ],
    )
    result = _run_planning_evaluation_cycle(state)

    assert result["is_feasible"] is True, result
    assert [step["execution"]["skill"] for step in result["todo_list"]] == [
        "NavigateTo",
        "NavigateTo",
        "Open",
    ]
    assert result["todo_list"][0]["execution"]["parameters"] == {
        "target_location": "错误位置_1"
    }
    assert result["todo_list"][1]["execution"]["parameters"] == {
        "target_location": "橱柜_1"
    }
    assert result["repair_history"][0]["assembled"] is True
    assert not {"sda_state", "vcr_state", "retrac_state"} & result.keys()
    assert "repair_strategy" not in result["feature_flags"]
    prompt = llm.prompts[0]
    assert "ReTrac" in prompt
    assert '"plan_intent": "移动到桌子"' in prompt
    assert prompt.count('"complete_todo_list"') == 1
    assert '"preserved_prefix_end_step": 1' in prompt
    assert '"regenerate_start_step": 2' in prompt
    assert '"regenerate_end_step": 2' in prompt
    assert '"error_reason"' in prompt
    assert "NavigateTo(target_location)" not in prompt
    assert '"retrac_state"' not in prompt
    assert '"current_simulated_state"' not in prompt
    assert '"original_todo_list"' not in prompt
    assert '"discarded_suffix"' not in prompt


def test_vcr_loads_one_skill_snapshot_per_evaluation_pass(monkeypatch):
    env = {
        "起点_1": {"type": "receptacle", "states": {}},
        "错误位置_1": {"type": "receptacle", "states": {}},
        "橱柜_1": {
            "type": "cabinet",
            "states": {"isOpen": False},
            "is_container": True,
        },
    }
    llm = _SequenceLLM(
        [
            '{"todo_list": ['
            '{"execution": {"skill": "NavigateTo", '
            '"parameters": {"target_location": "橱柜_1"}}},'
            '{"execution": {"skill": "Open", '
            '"parameters": {"target_container": "橱柜_1"}}}'
            ']}'
        ]
    )
    handler_loads = []
    prompt_loads = []
    handler_applies = []

    class OpenHandler:
        def apply(self, sim_env, sim_robot, parameters):
            handler_applies.append(parameters["target_container"])
            sim_env[parameters["target_container"]]["states"]["isOpen"] = True

    class NavigateHandler:
        def apply(self, sim_env, sim_robot, parameters):
            sim_robot["robot_location"] = parameters["target_location"]

    def apply_action(sim_env, sim_robot, skill, parameters, profile=None):
        if skill == "NavigateTo":
            sim_robot["robot_location"] = parameters["target_location"]
            return True, "", ""
        if sim_robot["robot_location"] != parameters["target_container"]:
            return False, "前置位置依赖未满足", "必须先导航到目标容器"
        sim_env[parameters["target_container"]]["states"]["isOpen"] = True
        return True, "", ""

    _configure(monkeypatch, env, llm, apply_action, repair_strategy="vcr")
    monkeypatch.setattr(
        evaluator,
        "load_enabled_skill_prompts",
        lambda profile=None: prompt_loads.append(profile)
        or "NavigateTo(target_location)\nOpen(target_container)",
    )
    monkeypatch.setattr(
        evaluator,
        "get_skill_handlers",
        lambda profile=None: handler_loads.append(profile)
        or {"NavigateTo": NavigateHandler(), "Open": OpenHandler()},
    )
    state = _state(
        [
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
        ],
    )
    state["structured_task"] = {
        "intent": "打开橱柜",
        "goal_state": {"橱柜_1": {"states": {"isOpen": True}}},
    }

    result = _run_planning_evaluation_cycle(state)

    assert result["is_feasible"] is True, result
    assert handler_loads == [None, None]
    assert prompt_loads == [None, None]
    assert handler_applies
    assert set(handler_applies) == {"橱柜_1"}
    assert result["repair_history"][0]["assembled"] is True
    assert not {"sda_state", "vcr_state", "retrac_state"} & result.keys()


def test_vcr_refines_plan_when_llm_says_counterfactual_task_completed(monkeypatch):
    env = {
        "起点_1": {"type": "receptacle", "states": {}},
        "错误位置_1": {"type": "receptacle", "states": {}},
        "橱柜_1": {
            "type": "cabinet",
            "states": {"isOpen": False},
            "is_container": True,
        },
    }
    llm = _SequenceLLM(
        [
            '{"task_completed": true, "evidence": "橱柜最终已打开"}',
            '{"todo_list": ['
            '{"execution": {"skill": "NavigateTo", '
            '"parameters": {"target_location": "橱柜_1"}}},'
            '{"execution": {"skill": "Open", '
            '"parameters": {"target_container": "橱柜_1"}}}'
            ']}',
        ]
    )

    def apply_action(sim_env, sim_robot, skill, parameters, profile=None):
        if skill == "NavigateTo":
            sim_robot["robot_location"] = parameters["target_location"]
            return True, "", ""
        if sim_robot["robot_location"] != parameters["target_container"]:
            return False, "前置位置依赖未满足", "必须先导航到目标容器"
        sim_env[parameters["target_container"]]["states"]["isOpen"] = True
        return True, "", ""

    _configure(monkeypatch, env, llm, apply_action, repair_strategy="vcr")
    state = _state(
        [
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
        ],
    )
    state["structured_task"] = {"intent": "打开橱柜"}

    result = _run_planning_evaluation_cycle(state)

    assert result["is_feasible"] is True, result
    assert [step["execution"]["skill"] for step in result["todo_list"]] == [
        "NavigateTo",
        "Open",
    ]
    assert len(llm.prompts) == 2
    assert "只判断反事实模拟的最终状态是否已经完成任务" in llm.prompts[0]
    assert '"task_completed": true 或 false' in llm.prompts[0]


def test_vcr_defers_counterfactual_task_not_completed_without_replanning(monkeypatch):
    env = {
        "起点_1": {"type": "receptacle", "states": {}},
        "错误位置_1": {"type": "receptacle", "states": {}},
        "橱柜_1": {
            "type": "cabinet",
            "states": {"isOpen": False},
            "is_container": True,
        },
    }
    llm = _SequenceLLM(
        ['{"task_completed": false, "evidence": "任务所需目标状态未出现"}']
    )

    def apply_action(sim_env, sim_robot, skill, parameters, profile=None):
        if skill == "NavigateTo":
            sim_robot["robot_location"] = parameters["target_location"]
            return True, "", ""
        if sim_robot["robot_location"] != parameters["target_container"]:
            return False, "前置位置依赖未满足", "必须先导航到目标容器"
        sim_env[parameters["target_container"]]["states"]["isOpen"] = True
        return True, "", ""

    _configure(monkeypatch, env, llm, apply_action, repair_strategy="vcr")
    state = _state(
        [
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
        ],
    )
    state["structured_task"] = {"intent": "把苹果放进冰箱"}

    result = evaluator.evaluate_feasibility(state)

    assert result["is_feasible"] is False
    assert result["evaluation_repair_request"] == {}
    assert result["counterfactual_task_completion"] == {
        "status": "not_completed",
        "evidence_source": "llm_state_diff",
        "evidence": "任务所需目标状态未出现",
        "handled": False,
    }
    assert planning_node._counterfactual_completion_deferred(result) is True
    assert graph_routes.global_planning_router(result) == graph_routes.END
    assert len(llm.prompts) == 1


def test_rejected_vcr_window_retries_original_plan_transactionally(monkeypatch):
    env = {
        "起点_1": {"type": "receptacle", "states": {}},
        "错误位置_1": {"type": "receptacle", "states": {}},
        "橱柜_1": {
            "type": "cabinet",
            "states": {"isOpen": False},
            "is_container": True,
        },
    }
    llm = _SequenceLLM(
        [
            '{"todo_list": ['
            '{"execution": {"skill": "NavigateTo", '
            '"parameters": {"target_location": "错误位置_1"}}},'
            '{"execution": {"skill": "Open", '
            '"parameters": {"target_container": "橱柜_1"}}}'
            ']}'
        ]
    )

    def apply_action(sim_env, sim_robot, skill, parameters, profile=None):
        if skill == "NavigateTo":
            sim_robot["robot_location"] = parameters["target_location"]
            return True, "", ""
        if sim_robot["robot_location"] != parameters["target_container"]:
            return False, "前置位置依赖未满足", "必须先导航到目标容器"
        sim_env[parameters["target_container"]]["states"]["isOpen"] = True
        return True, "", ""

    _configure(monkeypatch, env, llm, apply_action, repair_strategy="vcr")
    original = [
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
    current = _state(
        original,
        {"evaluation_repair_attempts": 2},
    )
    current["structured_task"] = {
        "intent": "打开橱柜",
        "goal_state": {"橱柜_1": {"states": {"isOpen": True}}},
    }

    diagnosed = evaluator.evaluate_feasibility(current)
    current.update(diagnosed)
    original_request = diagnosed["evaluation_repair_request"]
    planned = planning_node.decompose_task(current)
    current.update(planned)
    assembled = evaluator.assemble_repair_candidate(current)
    current.update(assembled)

    assert assembled["evaluation_revision_context"]["source"] == (
        "evaluation_repair_candidate"
    )
    assert assembled["evaluation_revision_context"]["base_todo_list"] == original

    retried = evaluator.evaluate_feasibility(current)

    assert retried["todo_list"] == original
    retry_request = retried["evaluation_repair_request"]
    assert retry_request["merge_context"] == {
        **original_request["merge_context"],
        "active_window_ids": ["window_1"],
        "accepted_window_steps": {},
    }
    assert retry_request["original_todo_list"] == original
    candidate_failure = retry_request["candidate_failures"][0]
    assert candidate_failure["validation_scope"] == "independent_repair_windows"
    assert candidate_failure["accepted_window_ids"] == []
    window_failure = candidate_failure["failed_windows"][0]
    assert window_failure["repair_window_id"] == "window_1"
    assert window_failure["validation_stage"] == "segment_action"
    assert window_failure["failed_action"]["skill"] == "Open"
    assert window_failure["state_before_failure"]["robot"] == {
        "robot_location": "错误位置_1",
        "robot_holding": "空",
    }
    assert window_failure["failed_preconditions"] == [
        {
            "code": "navigation_precondition",
            "required_condition": "必须先导航到目标容器",
            "predicate": "robot.robot_location",
            "required_value": "橱柜_1",
            "actual_value": "错误位置_1",
        }
    ]
    assert len(window_failure["local_segment_path"]) == 2
    assert window_failure["local_segment_path"][-1]["is_failed_action"] is True
    assert "rejected_during_repair_window_validation" in retry_request["prompt"]
    assert "causal_errors" in retry_request["prompt"]
    assert "rejected_sequences" in retry_request["prompt"]
    assert "local_segment_path" not in retry_request["prompt"]
    retry_payload = json.loads(retry_request["prompt"].rsplit("\n\n", 1)[1])
    assert "validation_errors" in retry_payload["candidate_feedback"]
    assert "observed_tail" not in retry_payload["candidate_feedback"]
    assert "latest_failure" not in retry_payload["candidate_feedback"]
    assert "failures" not in retry_payload["candidate_feedback"]
    assert [entry["status"] for entry in retried["repair_history"]] == [
        "rejected",
        "diagnosed",
    ]


def test_vcr_candidate_later_original_failure_accepts_prior_window():
    todo_list = [
        {"step": 1, "execution": {"skill": "Generated", "parameters": {}}},
        {"step": 2, "execution": {"skill": "Original", "parameters": {}}},
        {"step": 3, "execution": {"skill": "Original", "parameters": {}}},
    ]
    transaction = {
        "step_provenance": [
            {"source": "generated", "repair_window_id": "window_1"},
            {"source": "original", "original_step": 3},
            {"source": "original", "original_step": 4},
        ]
    }
    session = SimpleNamespace(todo_list=todo_list)

    assert evaluator._candidate_failure_after_repair_window(
        session,
        EvaluationFailure(
            code=EvaluationFailureCode.INVALID_ACTION,
            issue_type="later failure",
            fix_advice="repair next window",
            step=todo_list[1],
        ),
        transaction,
    ) is True
    assert evaluator._candidate_failure_after_repair_window(
        session,
        EvaluationFailure(
            code=EvaluationFailureCode.INVALID_ACTION,
            issue_type="segment failure",
            fix_advice="retry same window",
            step=todo_list[0],
        ),
        transaction,
    ) is False


def test_vcr_multi_window_validation_accepts_independent_segments():
    def apply_action(environment, robot, skill, parameters):
        if skill == "NavigateTo":
            robot["robot_location"] = parameters["target_location"]
            return True, "", ""
        return False, "调用无效动作", "不支持该动作"

    session = SimpleNamespace(
        modes=SimpleNamespace(sandbox=True),
        skills=SimpleNamespace(apply_action=apply_action),
        skill_catalog=None,
    )
    failure = evaluator._validate_repair_segments(
        session,
        {
            "segment_checks": [
                {
                    "segment_id": "window_1",
                    "entry_environment": {},
                    "entry_robot": {
                        "robot_location": "起点_1",
                        "robot_holding": "空",
                    },
                    "steps": [
                        {
                            "execution": {
                                "skill": "NavigateTo",
                                "parameters": {
                                    "target_location": "目标_1",
                                },
                            }
                        }
                    ],
                    "exit_contract": [
                        {
                            "predicate": "robot.robot.robot_location",
                            "required_value": "目标_1",
                        }
                    ],
                },
                {
                    "segment_id": "window_2",
                    "entry_environment": {},
                    "entry_robot": {
                        "robot_location": "目标_2",
                        "robot_holding": "空",
                    },
                    "steps": [
                        {
                            "execution": {
                                "skill": "NavigateTo",
                                "parameters": {
                                    "target_location": "中间点_2",
                                },
                            }
                        }
                    ],
                    "exit_contract": [
                        {
                            "predicate": "robot.robot.robot_location",
                            "required_value": "目标_2",
                        }
                    ],
                },
            ]
        },
    )

    assert failure is not None
    progress = evaluator._repair_segment_progress(failure)
    assert [item["repair_window_id"] for item in progress["accepted"]] == [
        "window_1"
    ]
    assert [item["repair_window_id"] for item in progress["failures"]] == [
        "window_2"
    ]
    assert progress["failures"][0]["validation_stage"] == "exit_contract"
    assert "checkpoint_environment" not in progress["failures"][0]
    assert "checkpoint_robot" not in progress["failures"][0]
    assert progress["failures"][0]["failed_preconditions"] == [
        {
            "predicate": "robot.robot.robot_location",
            "required_value": "目标_2",
            "actual_value": "中间点_2",
        }
    ]

    merge_context = evaluator._merge_segment_progress({}, progress)
    assert merge_context["active_window_ids"] == ["window_2"]
    assert list(merge_context["accepted_window_steps"]) == ["window_1"]
    retry_prompt = evaluator._candidate_retry_prompt(
        "base prompt",
        [evaluator._repair_candidate_feedback(session, failure, {})],
        active_window_ids=merge_context["active_window_ids"],
        accepted_window_ids=["window_1"],
    )
    retry_payload = json.loads(retry_prompt.split("\n\n", 1)[1])
    assert retry_payload["candidate_feedback"]["active_repair_window_ids"] == [
        "window_2"
    ]
    assert retry_payload["candidate_feedback"]["accepted_repair_window_ids"] == [
        "window_1"
    ]
