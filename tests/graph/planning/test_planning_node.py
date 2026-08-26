import pytest

from graph.planning import node as planning_node
from graph.planning import llm_decomposer
from graph.planning.repair import PlanningRegenerationError
from graph.planning.evaluation.outcomes.continuation import strip_repeated_prefix


class FakeResponse:
    content = "not json"


class FakeLLM:
    def invoke(self, messages):
        return FakeResponse()


def _task(intent="把苹果放到盘子"):
    return {
        "intent": intent,
        "required_item_names": {
            "targets": {"primary": ["苹果_1"], "alternatives": []},
            "tools": {"primary": ["刀_1"], "alternatives": []},
            "receptacles": {"primary": ["盘子_1"], "alternatives": []},
        },
    }


def _state(**overrides):
    state = {
        "structured_task": _task(),
        "relevant_item_names": ["盘子_1", "苹果_1"],
        "environment": {
            "苹果_1": {"direct_parent": "桌子_1", "states": {}},
            "盘子_1": {"direct_parent": "桌子_1", "states": {}},
        },
        "env_state": {"robot_location": "桌子_1", "robot_holding": "空"},
        "iteration_count": 0,
    }
    state.update(overrides)
    return state


def _stub_decomposition(monkeypatch, *, parsed=None, capture=None):
    captured = capture if capture is not None else {}

    def messages(**kwargs):
        captured["messages"] = kwargs
        return [], []

    monkeypatch.setattr(llm_decomposer, "build_planning_messages", messages)
    monkeypatch.setattr(planning_node, "get_planning_llm", lambda: FakeLLM())
    monkeypatch.setattr(
        llm_decomposer,
        "parse_json_from_llm",
        lambda *args, **kwargs: parsed
        if parsed is not None
        else {
            "todo_list": [
                {
                    "execution": {
                        "skill": "NavigateTo",
                        "parameters": {"target_location": "盘子_1"},
                    }
                }
            ]
        },
    )
    monkeypatch.setattr(
        llm_decomposer,
        "_normalize_todo_list",
        lambda todo, *args, **kwargs: todo,
    )
    return captured


def test_decompose_task_consumes_request_environment(monkeypatch):
    captured = _stub_decomposition(monkeypatch)

    result = planning_node.decompose_task(_state())

    assert captured["messages"]["current_env"] == _state()["environment"]
    assert captured["messages"]["names_info"] == _task()["required_item_names"]
    assert result["feature_flags"]["sandbox_evaluator"] is True


def test_decompose_task_consumes_evaluator_continuation(monkeypatch):
    captured = _stub_decomposition(
        monkeypatch,
        parsed={
            "todo_list": [
                {
                    "execution": {
                        "skill": "Pickup",
                        "parameters": {"target_item": "苹果_1"},
                    }
                }
            ]
        },
    )
    validated = {
        "step": 1,
        "execution": {
            "skill": "NavigateTo",
            "parameters": {"target_location": "桌子_1"},
        },
    }
    continuation = {
        "validated_steps": [validated],
        "current_env": {"苹果_1": {"direct_parent": "桌子_1"}},
        "current_robot": {"robot_location": "桌子_1", "robot_holding": "空"},
        "next_step_num": 2,
        "failed_lessons": "第 2 步失败",
        "repair_handoff": {"mode": "repair_from_failed_step"},
    }

    result = planning_node.decompose_task(
        _state(planning_continuation=continuation)
    )

    assert captured["messages"]["validated_steps"] == [validated]
    assert captured["messages"]["current_env"] == continuation["current_env"]
    assert captured["messages"]["next_step_num"] == 2
    assert [step["step"] for step in result["todo_list"]] == [1, 2]


def test_decompose_task_invokes_replanning_for_evaluation_request(monkeypatch):
    original = [
        {
            "step": 1,
            "execution": {
                "skill": "NavigateTo",
                "parameters": {"target_location": "错误位置_1"},
            },
        }
    ]
    request = {
        "version": "evaluation_repair_v1",
        "round": 1,
        "stage": "sandbox",
        "prompt": "修正导航目标",
        "assembly_mode": "strategy",
        "strategy_name": "vcr",
        "merge_context": {},
    }
    generated = [
        {
            "execution": {
                "skill": "NavigateTo",
                "parameters": {"target_location": "盘子_1"},
            }
        }
    ]
    calls = []
    monkeypatch.setattr(
        planning_node,
        "_regenerate_evaluation_repair",
        lambda actual_request, profile: calls.append(
            (actual_request, profile)
        )
        or generated,
    )
    monkeypatch.setattr(
        planning_node,
        "run_llm_decomposition",
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("repair requests must bypass initial decomposition")
        ),
    )

    result = planning_node.decompose_task(
        _state(
            todo_list=original,
            evaluation_repair_request=request,
            skill_profile="core_household",
        )
    )

    assert calls == [(request, "core_household")]
    assert result["todo_list"] == original
    assert result["repair_todo_list"] == generated
    assert result["evaluation_repair_request"] == request


def test_repair_model_failure_preserves_complete_candidate(monkeypatch):
    original = [
        {
            "step": 1,
            "execution": {
                "skill": "NavigateTo",
                "parameters": {"target_location": "错误位置_1"},
            },
        }
    ]
    request = {
        "version": "evaluation_repair_v1",
        "round": 1,
        "stage": "legality",
        "prompt": "重新生成完整计划",
        "assembly_mode": "complete",
        "strategy_name": "",
        "merge_context": {},
    }
    monkeypatch.setattr(
        planning_node,
        "_regenerate_evaluation_repair",
        lambda *_args: (_ for _ in ()).throw(
            PlanningRegenerationError("model_invocation", "model unavailable")
        ),
    )

    result = planning_node.decompose_task(
        _state(todo_list=original, evaluation_repair_request=request)
    )

    assert result["execution_status"] == "failed"
    assert result["failure_category"] == "model_invocation"
    assert result["todo_list"] == original


def test_invalid_repair_request_fails_before_model_invocation(monkeypatch):
    original = [
        {
            "step": 1,
            "execution": {
                "skill": "NavigateTo",
                "parameters": {"target_location": "错误位置_1"},
            },
        }
    ]
    monkeypatch.setattr(
        planning_node,
        "_regenerate_evaluation_repair",
        lambda *_args: (_ for _ in ()).throw(
            AssertionError("invalid requests must not reach the model")
        ),
    )

    result = planning_node.decompose_task(
        _state(
            todo_list=original,
            evaluation_repair_request={
                "version": "evaluation_repair_v0",
                "prompt": "stale request",
            },
        )
    )

    assert result["execution_status"] == "failed"
    assert result["failure_category"] == "repair_request"
    assert result["todo_list"] == original
    assert "版本" in result["error_feedback"]


def test_compiled_planning_graph_executes_repair_loop(monkeypatch):
    pytest.importorskip("langgraph")
    events = []
    original = [
        {
            "step": 1,
            "execution": {"skill": "NavigateTo", "parameters": {}},
        }
    ]
    repaired = [
        {
            "step": 1,
            "execution": {"skill": "Open", "parameters": {}},
        }
    ]
    request = {
        "version": "evaluation_repair_v1",
        "round": 1,
        "stage": "sandbox",
        "prompt": "repair candidate",
        "assembly_mode": "strategy",
        "strategy_name": "vcr",
        "merge_context": {},
    }

    def decompose(state):
        if state.get("evaluation_repair_request"):
            events.append("replan")
            return {
                "repair_todo_list": repaired,
                "iteration_count": 2,
                "evaluation_revision_context": {},
            }
        events.append("decompose")
        return {"todo_list": original, "iteration_count": 1}

    def evaluate(state):
        if events.count("evaluate") == 0:
            events.append("evaluate")
            return {
                "is_feasible": False,
                "evaluation_repair_request": request,
                "repair_todo_list": [],
                "evaluation_recheck": False,
                "evaluation_revision_context": {},
            }
        events.append("reevaluate")
        return {
            "is_feasible": True,
            "evaluation_repair_request": {},
            "repair_todo_list": [],
            "evaluation_recheck": False,
            "evaluation_revision_context": {},
        }

    def assemble(state):
        events.append("assemble")
        assert state["repair_todo_list"] == repaired
        return {
            "todo_list": repaired,
            "is_feasible": False,
            "evaluation_repair_request": {},
            "repair_todo_list": [],
            "evaluation_recheck": True,
            "evaluation_revision_context": {},
        }

    monkeypatch.setattr(planning_node, "decompose_task", decompose)
    monkeypatch.setattr(planning_node, "evaluate_candidate", evaluate)
    monkeypatch.setattr(planning_node, "assemble_repair_candidate", assemble)

    result = planning_node.build_planning_graph().invoke(
        _state(
            todo_list=[],
            is_feasible=False,
            evaluation_repair_request={},
            repair_todo_list=[],
            evaluation_recheck=False,
            evaluation_revision_context={},
        )
    )

    assert events == [
        "decompose",
        "evaluate",
        "replan",
        "assemble",
        "reevaluate",
    ]
    assert result["is_feasible"] is True
    assert result["todo_list"] == repaired


def test_decompose_task_runtime_feature_flags_override_planning_config(monkeypatch):
    _stub_decomposition(monkeypatch)

    result = planning_node.decompose_task(
        _state(
            structured_task=_task("去厨房"),
            feature_flags={"sandbox_evaluator": False, "semantic_audit": False},
        )
    )

    assert result["feature_flags"]["sandbox_evaluator"] is False
    assert result["feature_flags"]["semantic_audit"] is False
    assert result["feature_flags"]["playbook_retrieval"] is True


def test_decompose_task_reports_planning_parse_error(monkeypatch):
    _stub_decomposition(monkeypatch)
    monkeypatch.setattr(
        llm_decomposer,
        "parse_json_from_llm",
        lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("bad json")),
    )

    result = planning_node.decompose_task(_state())

    assert result["todo_list"] == []
    assert "规划层输出解析失败" in result["feedback"]


def test_strip_repeated_prefix_keeps_only_new_suffix():
    open_step = {
        "step": 1,
        "execution": {"skill": "Open", "parameters": {"target": "冰箱_1"}},
    }
    pickup_step = {
        "step": 2,
        "execution": {"skill": "Pickup", "parameters": {"target": "牛奶_1"}},
    }

    assert strip_repeated_prefix([open_step], [open_step, pickup_step]) == [
        pickup_step
    ]
