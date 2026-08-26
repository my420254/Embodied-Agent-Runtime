from graph.planning.evaluation import evaluator, flags as evaluation_flags
from graph.planning import llm_decomposer
from graph.planning import node as planning_node
from graph.planning.evaluation.validation.state_diff import (
    _build_state_audit_context,
    _build_state_diff,
)
from graph.planning import config as planning_config
from adapters.tracing import JsonlTraceRecorder
from adapters.sandbox import apply_sandbox_action
from re_trac import build_failed_step_retrac_state


class FakeResponse:
    def __init__(self, content: str):
        self.content = content


class FakeLLM:
    def __init__(self, content: str):
        self.content = content
        self.messages = []

    def invoke(self, messages):
        self.messages.append(messages)
        return FakeResponse(self.content)


def _set_repair_strategy(monkeypatch, strategy):
    monkeypatch.setattr(
        evaluator,
        "get_config",
        lambda *keys, default=None: (
            strategy
            if keys == ("planning", "evaluation", "repair_strategy")
            else default
        ),
    )


def _valid_state(iteration_count=1):
    return {
        "todo_list": [
            {
                "step": 1,
                "execution": {
                    "skill": "NavigateTo",
                    "parameters": {"target_location": "厨房操作台_1"},
                },
            }
        ],
        "env_state": {"robot_location": "桌子", "robot_holding": "空"},
        "structured_task": {"intent": "测试任务"},
        "iteration_count": iteration_count,
        "repair_memory": {"failed_lessons": []},
        "relevant_item_names": ["起点_1", "错误位置_1", "橱柜_1"],
        "skill_closure": ["NavigateTo", "Open", "Pickup", "Put"],
        "environment": {
            "起点_1": {"type": "receptacle", "states": {}, "direct_parent": "厨房_1"},
            "错误位置_1": {"type": "receptacle", "states": {}, "direct_parent": "厨房_1"},
            "橱柜_1": {
                "type": "cabinet",
                "states": {"isOpen": False},
                "is_container": True,
                "direct_parent": "厨房_1",
            },
            "厨房操作台_1": {
                "type": "receptacle",
                "states": {},
                "direct_parent": "厨房_1",
            },
        },
        "validated_steps": [],
        "injected_playbook_rule_ids": [],
    }


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
        current.update(planning_node.decompose_task(current))
        if current.get("execution_status") == "failed":
            return current
        current.update(evaluator.assemble_repair_candidate(current))
    raise AssertionError("planning/evaluation repair cycle did not terminate")


def _sda_house_env():
    return {
        "冰箱_1": {
            "direct_parent": "厨房_1",
            "type": "appliance",
            "states": {"isOpen": False, "isToggled": True},
            "is_container": True,
            "full_path": ["厨房_1"],
        },
        "冷藏室_1": {
            "direct_parent": "冰箱_1",
            "type": "compartment",
            "states": {},
            "is_container": True,
            "full_path": ["厨房_1", "冰箱_1"],
        },
        "鸡蛋_1": {
            "direct_parent": "冷藏室_1",
            "type": "food",
            "states": {"isCold": True, "isCooked": False},
            "is_container": False,
            "full_path": ["厨房_1", "冰箱_1", "冷藏室_1"],
        },
        "顶层橱柜_1": {
            "direct_parent": "厨房_1",
            "type": "cabinet",
            "states": {"isOpen": False},
            "is_container": True,
            "full_path": ["厨房_1"],
        },
        "陶瓷盘_1": {
            "direct_parent": "顶层橱柜_1",
            "type": "receptacle",
            "states": {},
            "is_container": True,
            "full_path": ["厨房_1", "顶层橱柜_1"],
        },
        "厨房操作台_1": {
            "direct_parent": "厨房_1",
            "type": "receptacle",
            "states": {},
            "is_container": True,
            "full_path": ["厨房_1"],
        },
        "微波炉_1": {
            "direct_parent": "厨房_1",
            "type": "appliance",
            "states": {"isOpen": False, "isToggled": False},
            "is_container": True,
            "full_path": ["厨房_1"],
        },
        "双人床_1": {
            "direct_parent": "卧室_1",
            "type": "receptacle",
            "states": {},
            "is_container": True,
            "full_path": ["卧室_1"],
        },
    }


def _todo_step(num, skill, params):
    return {"step": num, "execution": {"skill": skill, "parameters": params}}


def test_evaluate_feasibility_fails_closed_on_malformed_audit(monkeypatch):
    monkeypatch.setattr(evaluation_flags, "ENABLE_SANDBOX_EVALUATOR", True)
    monkeypatch.setattr(evaluator, "get_full_flat_house", lambda env: env)
    monkeypatch.setattr(evaluator, "apply_sandbox_action", lambda *args, **kwargs: (True, "", ""))
    monkeypatch.setattr(evaluator, "get_planning_llm", lambda: FakeLLM("{}"))
    monkeypatch.setattr(evaluator, "save_evaluator_finding_to_playbook", lambda *args, **kwargs: None)
    monkeypatch.setattr(evaluator, "record_rule_feedback", lambda *args, **kwargs: 0)
    monkeypatch.setattr(evaluator, "load_enabled_skill_prompts", lambda: "")

    result = evaluator.evaluate_feasibility(_valid_state())

    assert result["is_feasible"] is False
    assert "状态差异审计异常" in result["feedback"]
    assert "禁止缺省放行" in result["feedback"]


def test_evaluator_uses_iteration_limit_as_final_failure_code(monkeypatch):
    monkeypatch.setattr(evaluator, "save_evaluator_finding_to_playbook", lambda *args, **kwargs: None)
    monkeypatch.setattr(evaluator, "record_rule_feedback", lambda *args, **kwargs: 0)

    state = _valid_state()
    state["todo_list"] = []
    state["iteration_count"] = planning_config.get_planning_max_iterations()
    state["feature_flags"] = {
        "evaluation_repair_attempts": 0,
        "state_diff_audit": False,
        "semantic_audit": False,
    }

    result = evaluator.evaluate_feasibility(state)

    assert result["execution_status"] == "failed"
    assert result["failure_layer"] == "planning"
    assert result["failure_category"] == "iteration_limit"


def test_sandbox_evaluator_flag_reads_config(monkeypatch):
    monkeypatch.setattr(evaluation_flags, "ENABLE_SANDBOX_EVALUATOR", None)

    def fake_get_config(*keys, default=None):
        if keys == ("planning", "features"):
            return {"sandbox_evaluator": False}
        return default

    monkeypatch.setattr(planning_config, "get_config", fake_get_config)

    assert evaluation_flags.is_sandbox_evaluator_enabled() is False
    assert evaluation_flags.is_sandbox_evaluator_enabled(
        {"feature_flags": {"sandbox_evaluator": True}}
    ) is True


def test_evaluate_feasibility_rejects_empty_todo_list_for_normal_task(monkeypatch):
    monkeypatch.setattr(evaluation_flags, "ENABLE_SANDBOX_EVALUATOR", True)
    monkeypatch.setattr(evaluator, "save_evaluator_finding_to_playbook", lambda *args, **kwargs: None)
    monkeypatch.setattr(evaluator, "record_rule_feedback", lambda *args, **kwargs: 0)

    state = _valid_state()
    state["todo_list"] = []
    state["structured_task"] = {"intent": "把苹果放到盘子"}
    state["feature_flags"] = {
        "evaluation_repair_attempts": 0,
        "state_diff_audit": False,
        "semantic_audit": False,
    }

    result = evaluator.evaluate_feasibility(state)

    assert result["is_feasible"] is False
    assert "必须输出标准动作序列" in result["feedback"]
    assert result["validated_steps"] == []


def test_evaluate_feasibility_rejects_empty_todo_list_for_cancel_intent_too(monkeypatch):
    monkeypatch.setattr(evaluation_flags, "ENABLE_SANDBOX_EVALUATOR", True)
    monkeypatch.setattr(evaluator, "save_evaluator_finding_to_playbook", lambda *args, **kwargs: None)
    monkeypatch.setattr(evaluator, "record_rule_feedback", lambda *args, **kwargs: 0)
    state = _valid_state()
    state["todo_list"] = []
    state["structured_task"] = {"intent": "取消当前任务"}
    state["feature_flags"] = {
        "evaluation_repair_attempts": 0,
        "state_diff_audit": False,
        "semantic_audit": False,
    }

    result = evaluator.evaluate_feasibility(state)

    assert result["is_feasible"] is False
    assert "必须输出标准动作序列" in result["feedback"]


def test_evaluate_feasibility_allows_success_on_configured_final_iteration(monkeypatch):
    def apply_action(sim_env, sim_robot, skill, parameters, **kwargs):
        if skill == "NavigateTo":
            sim_robot["robot_location"] = parameters["target_location"]
        return True, "", ""

    monkeypatch.setattr(evaluation_flags, "ENABLE_SANDBOX_EVALUATOR", True)
    monkeypatch.setattr(evaluator, "get_full_flat_house", lambda env: env)
    monkeypatch.setattr(evaluator, "apply_sandbox_action", apply_action)
    monkeypatch.setattr(evaluator, "get_planning_llm", lambda: FakeLLM('{"is_passed": true}'))
    monkeypatch.setattr(evaluator, "record_rule_feedback", lambda *args, **kwargs: 0)
    monkeypatch.setattr(evaluator, "learn_from_success", lambda *args, **kwargs: False)
    monkeypatch.setattr(evaluator, "load_enabled_skill_prompts", lambda: "")

    state = _valid_state(iteration_count=3)
    state["feature_flags"] = {"state_diff_audit": False, "semantic_audit": False}
    state["cognitive_planning_trace"] = {"trace_id": "trace-test"}

    result = evaluator.evaluate_feasibility(state)

    assert result["is_feasible"] is True, result
    assert result.get("execution_status") != "failed"
    assert result["cognitive_planning_trace"]["sandbox"] == {
        "enabled": True,
        "passed": True,
        "issue_type": "",
        "fix": "",
        "failure_category": "",
        "failed_step": None,
        "validated_step_count": 1,
    }


def test_evaluate_feasibility_persists_cognitive_trace_when_enabled(monkeypatch, tmp_path):
    trace_log = tmp_path / "cognitive_traces.jsonl"
    monkeypatch.setattr(evaluation_flags, "ENABLE_SANDBOX_EVALUATOR", True)
    monkeypatch.setattr(evaluator, "get_full_flat_house", lambda env: env)
    monkeypatch.setattr(evaluator, "apply_sandbox_action", lambda *args, **kwargs: (True, "", ""))
    monkeypatch.setattr(evaluator, "get_planning_llm", lambda: FakeLLM('{"is_passed": true}'))
    monkeypatch.setattr(evaluator, "record_rule_feedback", lambda *args, **kwargs: 0)
    monkeypatch.setattr(evaluator, "learn_from_success", lambda *args, **kwargs: False)
    monkeypatch.setattr(evaluator, "load_enabled_skill_prompts", lambda: "")
    monkeypatch.setattr(evaluator, "JsonlTraceRecorder", lambda: JsonlTraceRecorder(trace_log))

    state = _valid_state()
    state["feature_flags"] = {
        "cognitive_trace_write": True,
        "state_diff_audit": False,
        "semantic_audit": False,
    }
    state["cognitive_planning_trace"] = {"trace_id": "trace-persist", "task": "泡茶"}

    result = evaluator.evaluate_feasibility(state)
    records = JsonlTraceRecorder(trace_log).read_recent(limit=1)

    assert result["is_feasible"] is True
    assert result["cognitive_planning_trace"]["trace_storage"]["written"] is True
    assert records[0]["trace_id"] == "trace-persist"
    assert records[0]["sandbox"]["passed"] is True


def test_evaluate_feasibility_when_sandbox_disabled_still_rejects_empty_todo(monkeypatch):
    monkeypatch.setattr(evaluation_flags, "ENABLE_SANDBOX_EVALUATOR", False)
    monkeypatch.setattr(evaluator, "save_evaluator_finding_to_playbook", lambda *args, **kwargs: None)
    monkeypatch.setattr(evaluator, "record_rule_feedback", lambda *args, **kwargs: 0)

    state = _valid_state()
    state["todo_list"] = []
    state["cognitive_planning_trace"] = {"trace_id": "trace-test"}
    state["feature_flags"] = {
        "evaluation_repair_attempts": 0,
        "state_diff_audit": False,
        "semantic_audit": False,
    }

    result = evaluator.evaluate_feasibility(state)

    assert result["is_feasible"] is False
    assert "必须输出标准动作序列" in result["feedback"]
    assert result["cognitive_planning_trace"]["sandbox"]["enabled"] is False
    assert result["cognitive_planning_trace"]["sandbox"]["passed"] is False
    assert result["cognitive_planning_trace"]["sandbox"]["issue_type"] == "序列验证失败"
    assert result["cognitive_planning_trace"]["sandbox"]["failure_category"] == "empty_plan"


def test_evaluate_feasibility_regenerates_sda_suffix_from_causal_root(monkeypatch):
    _set_repair_strategy(monkeypatch, "sda")
    monkeypatch.setattr(evaluation_flags, "ENABLE_SANDBOX_EVALUATOR", True)
    monkeypatch.setattr(evaluator, "get_full_flat_house", lambda scene_file: _sda_house_env())
    monkeypatch.setattr(evaluator, "apply_sandbox_action", apply_sandbox_action)
    monkeypatch.setattr(evaluator, "record_rule_feedback", lambda *args, **kwargs: 0)
    monkeypatch.setattr(evaluator, "learn_from_success", lambda *args, **kwargs: False)
    repair_llm = FakeLLM(
        '{"todo_list": ['
        '{"execution": {"skill": "NavigateTo", "parameters": {"target_location": "顶层橱柜_1"}}},'
        '{"execution": {"skill": "Open", "parameters": {"target_container": "顶层橱柜_1"}}},'
        '{"execution": {"skill": "NavigateTo", "parameters": {"target_location": "冰箱_1"}}},'
        '{"execution": {"skill": "Pickup", "parameters": {"target_item": "鸡蛋_1"}}},'
        '{"execution": {"skill": "NavigateTo", "parameters": {"target_location": "陶瓷盘_1"}}},'
        '{"execution": {"skill": "Put", "parameters": {"target_item": "鸡蛋_1", "destination": "陶瓷盘_1"}}}'
        ']}'
    )
    monkeypatch.setattr(evaluator, "get_planning_llm", lambda: repair_llm)
    monkeypatch.setattr(
        planning_node,
        "get_planning_llm",
        evaluator.get_planning_llm,
    )

    todo = [
        _todo_step(1, "NavigateTo", {"target_location": "冰箱_1"}),
        _todo_step(2, "Open", {"target_container": "冰箱_1"}),
        _todo_step(3, "Pickup", {"target_item": "鸡蛋_1"}),
        _todo_step(4, "Close", {"target_container": "冰箱_1"}),
        _todo_step(5, "NavigateTo", {"target_location": "顶层橱柜_1"}),
        _todo_step(6, "Open", {"target_container": "顶层橱柜_1"}),
        _todo_step(7, "Pickup", {"target_item": "陶瓷盘_1"}),
        _todo_step(8, "Close", {"target_container": "顶层橱柜_1"}),
        _todo_step(9, "Put", {"target_item": "鸡蛋_1", "destination": "陶瓷盘_1"}),
        _todo_step(10, "NavigateTo", {"target_location": "微波炉_1"}),
        _todo_step(11, "Open", {"target_container": "微波炉_1"}),
        _todo_step(12, "Put", {"target_item": "陶瓷盘_1", "destination": "微波炉_1"}),
        _todo_step(13, "Close", {"target_container": "微波炉_1"}),
        _todo_step(14, "ToggleOn", {"target_device": "微波炉_1"}),
        _todo_step(15, "Heat", {"target_item": "鸡蛋_1", "heating_device": "微波炉_1"}),
        _todo_step(16, "ToggleOff", {"target_device": "微波炉_1"}),
        _todo_step(17, "Open", {"target_container": "微波炉_1"}),
        _todo_step(18, "Pickup", {"target_item": "陶瓷盘_1"}),
        _todo_step(19, "Close", {"target_container": "微波炉_1"}),
        _todo_step(20, "NavigateTo", {"target_location": "双人床_1"}),
        _todo_step(21, "Put", {"target_item": "陶瓷盘_1", "destination": "双人床_1"}),
        _todo_step(22, "Close", {"target_container": "冰箱_1"}),
        _todo_step(23, "Close", {"target_container": "微波炉_1"}),
        _todo_step(24, "Close", {"target_container": "顶层橱柜_1"}),
    ]
    state = {
        "todo_list": todo,
        "env_state": {"robot_location": "厨房操作台_1", "robot_holding": "空"},
        "structured_task": {"intent": "把鸡蛋放进盘子加热后放到床上，并关好设备"},
        "iteration_count": 1,
        "repair_memory": {"failed_lessons": []},
        "environment": _sda_house_env(),
        "validated_steps": [],
        "injected_playbook_rule_ids": [],
        "skill_profile": "core_household",
        "feature_flags": {
            "sandbox_evaluator": True,
            "semantic_audit": False,
            "state_diff_audit": False,
            "playbook_write": False,
            "playbook_retrieval": False,
        },
    }

    result = _run_planning_evaluation_cycle(state)

    assert result["is_feasible"] is True, result
    assert result["repair_history"][0]["assembled"] is True
    assert not {"sda_state", "vcr_state", "retrac_state"} & result.keys()
    prompt = next(
        messages[0].content
        for messages in repair_llm.messages
        if '"complete_todo_list"' in messages[0].content
    )
    assert '"root_cause_step": 3' in prompt
    assert '"regenerate_start_step": 3' in prompt
    assert '"id": "replace_root_cause_action"' in prompt
    assert '"id": "keep_root_cause_and_restore_precondition"' in prompt
    assert '"before": "空"' in prompt
    assert '"after": "鸡蛋_1"' in prompt
    assert '"first_generated_step_replaces_original_step": 3' in prompt
    assert "在执行原第 4 步动作或其等价动作之前" in prompt
    assert "开/关容器时必须保持空手" in prompt
    assert '"complete_todo_list"' in prompt
    assert "sandbox_suggested_subtree" not in prompt
    assert "checkpoint_state" not in prompt


def test_state_diff_compares_all_entity_states():
    diff = _build_state_diff(
        {
            "苹果_1": {"direct_parent": "桌子_1", "states": {"isClean": True}},
            "灯_1": {"direct_parent": "客厅_1", "states": {"isToggled": False}},
        },
        {"robot_location": "桌子_1", "robot_holding": "空"},
        {
            "苹果_1": {"direct_parent": "桌子_1", "states": {"isClean": True}},
            "灯_1": {"direct_parent": "客厅_1", "states": {"isToggled": True}},
        },
        {"robot_location": "桌子_1", "robot_holding": "空"},
    )

    assert diff["entity_count_compared"] == 2
    assert diff["changed_entity_count"] == 1
    assert diff["entities"][0]["name"] == "灯_1"
    assert diff["entities"][0]["before"]["states"] == {"isToggled": False}
    assert diff["entities"][0]["after"]["states"] == {"isToggled": True}


def test_native_retrac_prefix_is_preserved_for_suffix_planning(monkeypatch):
    prefix = [{"step": 1, "action": "goto", "from": "living_room", "to": "lobby"}]
    failed = {"step": 2, "action": "pick", "item": "banana_peel", "room": "lobby"}
    checkpoint_env = {
        "banana_peel": {"direct_parent": "lobby", "states": {}},
        "lobby": {"direct_parent": "未知环境", "states": {}},
    }
    checkpoint_robot = {"robot_location": "lobby", "robot_holding": "空"}
    retrac_state = build_failed_step_retrac_state(
        failure_kind="sandbox_intercept",
        issue_type="room precondition failed",
        issue="第 2 步物理拦截: room precondition failed",
        fix_advice="continue from lobby",
        todo_list=prefix + [failed],
        validated_steps=prefix,
        failed_step=failed,
        sim_env=checkpoint_env,
        sim_robot=checkpoint_robot,
        validated_native_actions=prefix,
        failed_native_step=failed,
    )
    assert retrac_state["native_trajectory"]["validated_prefix"] == prefix

    captured = {}

    def fake_parser(_text, **kwargs):
        assert kwargs["current_env"] == checkpoint_env
        return "[]", [{"action": "goto", "from": "lobby", "to": "kitchen"}]

    def fake_build_messages(**kwargs):
        captured.update(kwargs)
        return [], []

    monkeypatch.setattr(llm_decomposer, "resolve_callable", lambda *args, **kwargs: fake_parser)
    monkeypatch.setattr(llm_decomposer, "build_planning_messages", fake_build_messages)

    state = {
        "planning_output_mode": "native_actions",
        "native_action_parser_path": "tests.fake_parser",
        "structured_task": {"intent": "clean room"},
        "task_input_payload": {"llm_prompt": "clean room"},
        "task_context": {},
        "environment": {"living_room": {"direct_parent": "未知环境", "states": {}}},
        "env_state": {"robot_location": "living_room", "robot_holding": "空"},
        "re_trac_state": retrac_state,
        "feature_flags": {"state_diff_audit": False, "semantic_audit": False},
    }

    result = llm_decomposer.run_llm_decomposition(
        state,
        llm_provider=lambda: FakeLLM('[{"action":"goto","from":"lobby","to":"kitchen"}]'),
    )

    assert captured["current_robot"] == checkpoint_robot
    assert captured["validated_steps"] == prefix
    assert captured["next_step_num"] == 2
    assert result["todo_list"] == [
        {"step": 1, "action": "goto", "from": "living_room", "to": "lobby"},
        {"step": 2, "action": "goto", "from": "lobby", "to": "kitchen"},
    ]


def test_state_audit_context_includes_unchanged_relevant_final_state():
    env = {
        "冰箱_1": {"type": "receptacle", "direct_parent": "厨房_1", "states": {"isOpen": False}},
        "厨房_1": {"type": "room", "direct_parent": "未知环境", "states": {}},
    }
    context = _build_state_audit_context(
        env,
        {"robot_location": "冰箱_1", "robot_holding": "空"},
        env,
        {"robot_location": "冰箱_1", "robot_holding": "空"},
        [{"step": 1, "execution": {"skill": "Close", "parameters": {"target_container": "冰箱_1"}}}],
        {
            "required_item_names": {
                "receptacles": {"primary": ["冰箱_1"], "alternatives": []},
            }
        },
    )

    fridge = next(item for item in context["entities"] if item["name"] == "冰箱_1")
    assert fridge["changed"] is False
    assert fridge["after"]["states"]["isOpen"] is False


def test_evaluate_feasibility_state_diff_audit_passes_goal_diff(monkeypatch):
    monkeypatch.setattr(evaluation_flags, "ENABLE_SANDBOX_EVALUATOR", True)
    monkeypatch.setattr(
        evaluator,
        "get_full_flat_house",
        lambda scene_file: {
            "苹果_1": {"type": "food", "direct_parent": "桌子_1", "states": {"isClean": True}},
            "桌子_1": {"type": "surface", "direct_parent": "厨房_1", "states": {}},
        },
    )

    def fake_apply(sim_env, sim_robot, act, params, profile=None):
        target = params["target_item"]
        sim_robot["robot_holding"] = target
        sim_env[target]["direct_parent"] = "robot_hand"
        return True, "", ""

    monkeypatch.setattr(evaluator, "apply_sandbox_action", fake_apply)
    monkeypatch.setattr(
        evaluator.audit_llm,
        "_run_state_diff_audit",
        lambda **kwargs: {
            "is_passed": True,
            "issue": "",
            "fix_advice": "",
            "accepted_diffs": [{"path": "苹果_1.direct_parent", "reason": "task_goal"}],
            "unexpected_diffs": [],
        },
    )
    monkeypatch.setattr(evaluator, "record_rule_feedback", lambda *args, **kwargs: 0)
    monkeypatch.setattr(evaluator, "learn_from_success", lambda *args, **kwargs: False)
    monkeypatch.setattr(evaluator, "load_enabled_skill_prompts", lambda: "")

    state = _valid_state()
    state["feature_flags"] = {"state_diff_audit": True, "semantic_audit": False}
    state["structured_task"] = {"intent": "拿起苹果"}
    state["env_state"] = {"robot_location": "桌子_1", "robot_holding": "空"}
    state["todo_list"] = [
        {
            "step": 1,
            "execution": {"skill": "Pickup", "parameters": {"target_item": "苹果_1"}},
        }
    ]

    result = evaluator.evaluate_feasibility(state)

    assert result["is_feasible"] is True
    assert result["state_diff_audit"]["passed"] is True
    assert result["state_diff_audit"]["state_diff"]["entity_count_compared"] == 2
    assert result["state_diff_audit"]["state_diff"]["changed_entity_count"] == 1
    assert result["state_diff_audit"]["state_diff"]["robot"]["changed"] is True


def test_evaluate_feasibility_state_diff_audit_rejects_unexpected_diff(monkeypatch):
    monkeypatch.setattr(evaluation_flags, "ENABLE_SANDBOX_EVALUATOR", True)
    monkeypatch.setattr(
        evaluator,
        "get_full_flat_house",
            lambda scene_file: {
                "苹果_1": {"type": "food", "direct_parent": "桌子_1", "states": {"isClean": True}},
                "桌子_1": {"type": "surface", "direct_parent": "厨房_1", "states": {}},
                "盘子_1": {"type": "receptacle", "direct_parent": "桌子_1", "states": {}},
                "灯_1": {"type": "device", "direct_parent": "客厅_1", "states": {"isToggled": False}},
            },
    )

    def fake_apply(sim_env, sim_robot, act, params, profile=None):
        sim_env["苹果_1"]["direct_parent"] = "盘子_1"
        sim_env["灯_1"]["states"]["isToggled"] = True
        return True, "", ""

    monkeypatch.setattr(evaluator, "apply_sandbox_action", fake_apply)
    monkeypatch.setattr(
        evaluator.audit_llm,
        "_run_state_diff_audit",
        lambda **kwargs: {
            "is_passed": False,
            "issue": "灯_1 被无关打开",
            "fix_advice": "删除无关 ToggleOn 或补充恢复步骤",
            "accepted_diffs": [{"path": "苹果_1.direct_parent", "reason": "task_goal"}],
            "unexpected_diffs": [{"path": "灯_1.states.isToggled", "reason": "unrelated"}],
        },
    )
    monkeypatch.setattr(evaluator, "save_evaluator_finding_to_playbook", lambda *args, **kwargs: None)
    monkeypatch.setattr(evaluator, "record_rule_feedback", lambda *args, **kwargs: 0)
    monkeypatch.setattr(evaluator, "load_enabled_skill_prompts", lambda: "")

    state = _valid_state()
    state["feature_flags"] = {"state_diff_audit": True, "semantic_audit": False}
    state["structured_task"] = {"intent": "把苹果放到盘子"}
    state["env_state"] = {"robot_location": "桌子_1", "robot_holding": "空"}
    state["todo_list"] = [
        {
            "step": 1,
            "execution": {"skill": "Put", "parameters": {"target_item": "苹果_1", "destination": "盘子_1"}},
        }
    ]

    result = _run_planning_evaluation_cycle(state)

    assert result["is_feasible"] is False
    assert "状态差异审计拦截" in result["feedback"]
    assert result["failure_category"] == "state_diff_audit"
    assert result["state_diff_audit"]["passed"] is False
    assert result["state_diff_audit"]["state_diff"]["changed_entity_count"] == 2
    assert result["repair_handoff"]["mode"] == "append_recovery_after_valid_plan"
    assert result["repair_handoff"]["failure_kind"] == "state_diff_audit"
    assert result["repair_handoff"]["failure_code"] == "state_diff_audit"
    assert result["repair_handoff"]["trajectory"]["next_step_num"] == len(result["todo_list"]) + 1


def test_evaluate_feasibility_sandbox_failure_populates_repair_handoff(monkeypatch):
    _set_repair_strategy(monkeypatch, "retrac")
    monkeypatch.setattr(evaluation_flags, "ENABLE_SANDBOX_EVALUATOR", True)
    monkeypatch.setattr(
        evaluator,
        "get_full_flat_house",
        lambda scene_file: {
            "冰箱_1": {"type": "receptacle", "direct_parent": "厨房", "states": {"isOpen": False}},
            "冷冻室_1": {"type": "receptacle", "direct_parent": "冰箱_1", "states": {}},
            "冷冻猪肉_1": {"type": "food", "direct_parent": "冷冻室_1", "states": {"isFrozen": True}},
        },
    )

    def fake_apply(sim_env, sim_robot, act, params, profile=None):
        if act == "NavigateTo" and params.get("target_location") == "冷冻室_1":
            return False, "前置位置依赖未满足", "冰箱内部不是独立导航目标"
        return True, "", ""

    monkeypatch.setattr(evaluator, "apply_sandbox_action", fake_apply)
    monkeypatch.setattr(evaluator, "get_planning_llm", lambda: FakeLLM('{"is_passed": true}'))
    monkeypatch.setattr(evaluator, "record_rule_feedback", lambda *args, **kwargs: 0)
    monkeypatch.setattr(evaluator, "learn_from_success", lambda *args, **kwargs: False)
    monkeypatch.setattr(evaluator, "save_evaluator_finding_to_playbook", lambda *args, **kwargs: None)
    monkeypatch.setattr(evaluator, "load_enabled_skill_prompts", lambda: "")

    state = _valid_state()
    state["feature_flags"] = {
        "state_diff_audit": False,
        "semantic_audit": False,
    }
    state["structured_task"] = {"intent": "打开冰箱取冷冻猪肉_1"}
    state["env_state"] = {"robot_location": "厨房", "robot_holding": "空"}
    state["todo_list"] = [
        {"step": 1, "execution": {"skill": "NavigateTo", "parameters": {"target_location": "冰箱_1"}}},
        {"step": 2, "execution": {"skill": "Open", "parameters": {"target_container": "冰箱_1"}}},
        {"step": 3, "execution": {"skill": "NavigateTo", "parameters": {"target_location": "冷冻室_1"}}},
        {"step": 4, "execution": {"skill": "Pickup", "parameters": {"target_item": "冷冻猪肉_1"}}},
    ]

    result = evaluator.evaluate_feasibility(state)

    assert result["is_feasible"] is False
    assert result["repair_handoff"]["mode"] == "repair_from_failed_step"
    assert result["repair_handoff"]["failure_kind"] == "sandbox_failure"
    assert result["repair_handoff"]["trajectory"]["wrong_step"]["skill"] == "NavigateTo"
    assert result["repair_handoff"]["trajectory"]["discarded_suffix"][0]["step"] == 3


def test_evaluate_feasibility_sda_rolls_back_before_causal_pickup(monkeypatch):
    _set_repair_strategy(monkeypatch, "sda")
    monkeypatch.setattr(evaluation_flags, "ENABLE_SANDBOX_EVALUATOR", True)
    monkeypatch.setattr(
        evaluator,
        "get_full_flat_house",
        lambda scene_file: {
            "冰箱_1": {"type": "receptacle", "direct_parent": "厨房", "states": {"isOpen": False}},
            "顶层橱柜_1": {"type": "receptacle", "direct_parent": "厨房", "states": {"isOpen": False}},
            "鸡蛋_1": {"type": "food", "direct_parent": "冰箱_1", "states": {}},
        },
    )

    def fake_apply(sim_env, sim_robot, act, params, profile=None):
        if act == "NavigateTo":
            sim_robot["robot_location"] = params["target_location"]
            return True, "", ""
        if act == "Open":
            if sim_robot["robot_holding"] != "空":
                return False, "单臂约束违规", "开/关容器时必须保持空手"
            sim_env[params["target_container"]]["states"]["isOpen"] = True
            return True, "", ""
        if act == "Pickup":
            target = params["target_item"]
            sim_robot["robot_holding"] = target
            sim_env[target]["direct_parent"] = "robot_hand"
            return True, "", ""
        return False, "调用无效动作", "测试未实现该动作"

    monkeypatch.setattr(evaluator, "apply_sandbox_action", fake_apply)
    monkeypatch.setattr(evaluator, "save_evaluator_finding_to_playbook", lambda *args, **kwargs: None)
    monkeypatch.setattr(evaluator, "record_rule_feedback", lambda *args, **kwargs: 0)
    monkeypatch.setattr(
        evaluator,
        "get_planning_llm",
        lambda: FakeLLM(
            '{"todo_list": ['
            '{"execution": {"skill": "NavigateTo", "parameters": {"target_location": "顶层橱柜_1"}}},'
            '{"execution": {"skill": "Open", "parameters": {"target_container": "顶层橱柜_1"}}},'
            '{"execution": {"skill": "NavigateTo", "parameters": {"target_location": "冰箱_1"}}},'
            '{"execution": {"skill": "Pickup", "parameters": {"target_item": "鸡蛋_1"}}},'
            '{"execution": {"skill": "NavigateTo", "parameters": {"target_location": "顶层橱柜_1"}}}'
            ']}'
        ),
    )
    monkeypatch.setattr(
        planning_node,
        "get_planning_llm",
        evaluator.get_planning_llm,
    )

    state = _valid_state()
    state["feature_flags"] = {
        "state_diff_audit": False,
        "semantic_audit": False,
    }
    state["structured_task"] = {"intent": "把冰箱里的鸡蛋放到顶层橱柜里的盘子"}
    state["env_state"] = {"robot_location": "厨房操作台_1", "robot_holding": "空"}
    state["todo_list"] = [
        {"step": 1, "execution": {"skill": "NavigateTo", "parameters": {"target_location": "冰箱_1"}}},
        {"step": 2, "execution": {"skill": "Open", "parameters": {"target_container": "冰箱_1"}}},
        {"step": 3, "execution": {"skill": "Pickup", "parameters": {"target_item": "鸡蛋_1"}}},
        {"step": 4, "execution": {"skill": "NavigateTo", "parameters": {"target_location": "顶层橱柜_1"}}},
        {"step": 5, "execution": {"skill": "Open", "parameters": {"target_container": "顶层橱柜_1"}}},
    ]

    result = _run_planning_evaluation_cycle(state)

    assert result["is_feasible"] is True
    assert result["repair_history"][0]["assembled"] is True
    assert not {"sda_state", "vcr_state", "retrac_state"} & result.keys()


def test_evaluate_feasibility_vcr_repairs_counterfactually_viable_suffix(monkeypatch):
    _set_repair_strategy(monkeypatch, "vcr")
    monkeypatch.setattr(evaluation_flags, "ENABLE_SANDBOX_EVALUATOR", True)
    monkeypatch.setattr(
        evaluator,
        "get_full_flat_house",
        lambda scene_file: {
            "起点_1": {"type": "receptacle", "direct_parent": "厨房", "states": {}, "is_container": True},
            "错误位置_1": {"type": "receptacle", "direct_parent": "厨房", "states": {}, "is_container": True},
            "橱柜_1": {"type": "cabinet", "direct_parent": "厨房", "states": {"isOpen": False}, "is_container": True},
        },
    )
    monkeypatch.setattr(evaluator, "record_rule_feedback", lambda *args, **kwargs: 0)
    monkeypatch.setattr(evaluator, "learn_from_success", lambda *args, **kwargs: False)
    monkeypatch.setattr(
        evaluator,
        "get_planning_llm",
        lambda: FakeLLM(
            '{"todo_list": ['
            '{"execution": {"skill": "NavigateTo", '
            '"parameters": {"target_location": "橱柜_1"}}},'
            '{"execution": {"skill": "Open", '
            '"parameters": {"target_container": "橱柜_1"}}}'
            ']}'
        ),
    )
    monkeypatch.setattr(
        planning_node,
        "get_planning_llm",
        evaluator.get_planning_llm,
    )

    state = _valid_state()
    state["feature_flags"] = {
        "state_diff_audit": False,
        "semantic_audit": False,
    }
    state["env_state"] = {"robot_location": "起点_1", "robot_holding": "空"}
    state["structured_task"] = {
        "intent": "打开橱柜",
        "goal_state": {"橱柜_1": {"states": {"isOpen": True}}},
    }
    state["todo_list"] = [
        {"step": 1, "execution": {"skill": "NavigateTo", "parameters": {"target_location": "错误位置_1"}}},
        {"step": 2, "execution": {"skill": "Open", "parameters": {"target_container": "橱柜_1"}}},
    ]

    result = _run_planning_evaluation_cycle(state)

    assert result["is_feasible"] is True, result
    assert result["todo_list"] == [
        {"step": 1, "execution": {"skill": "NavigateTo", "parameters": {"target_location": "橱柜_1"}}},
        {"step": 2, "execution": {"skill": "Open", "parameters": {"target_container": "橱柜_1"}}},
    ]
    assert result["repair_history"][0]["assembled"] is True
    assert not {"sda_state", "vcr_state", "retrac_state"} & result.keys()
    assert result["repair_history"][0]["assembled"] is True


def test_evaluate_feasibility_rejects_unknown_repair_strategy(monkeypatch):
    _set_repair_strategy(monkeypatch, "unknown")
    monkeypatch.setattr(evaluator, "save_evaluator_finding_to_playbook", lambda *args, **kwargs: None)
    monkeypatch.setattr(evaluator, "record_rule_feedback", lambda *args, **kwargs: 0)
    state = _valid_state()

    result = evaluator.evaluate_feasibility(state)

    assert result["is_feasible"] is False
    assert "修复模式配置冲突" in result["feedback"]
    assert "无效修复策略配置" in result["feedback"]
