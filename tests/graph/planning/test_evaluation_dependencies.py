from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from threading import Barrier

from graph.planning.evaluation import evaluator, flags
from graph.planning.evaluation.dependencies import EvaluationDependencies
from graph.planning.evaluation.repair_strategies import (
    RepairStrategyRegistry,
)
from graph.planning.evaluation.models import (
    EvaluationFailure,
    EvaluationFailureCode,
    SimulationResult,
)
from graph.planning.evaluation.outcomes.handoff import CheckpointFailureHandoff
from graph.planning.evaluation.pipeline.session import (
    build_evaluation_context,
    create_evaluation_session,
    resolve_evaluation_modes,
)
from graph.planning.evaluation.pipeline.simulation import run_base_simulation
from skills.planning_catalog import load_planning_catalog


class _Recorder:
    def record(self, trace):
        return trace.get("trace_id", "trace")


def _dependencies(calls):
    def apply_action(env, robot, skill, parameters, profile=None):
        calls.append((skill, dict(parameters)))
        return True, "", ""

    return EvaluationDependencies(
        apply_sandbox_action=apply_action,
        get_full_flat_house=lambda env: env,
        get_planning_llm=lambda: None,
        load_skill_catalog=load_planning_catalog,
        load_enabled_skill_prompts=lambda profile=None: "",
        record_rule_feedback=lambda *args, **kwargs: None,
        learn_from_success=lambda *args, **kwargs: None,
        save_evaluator_finding=lambda *args, **kwargs: None,
        trace_recorder_factory=_Recorder,
        get_skill_handlers=lambda profile=None: {},
        repair_registry=RepairStrategyRegistry(),
        failure_handoff=CheckpointFailureHandoff(),
    )


def _request_state(todo_list=None):
    return {
        "todo_list": todo_list
        or [
            {
                "step": 1,
                "execution": {
                    "skill": "NavigateTo",
                    "parameters": {"target_location": "厨房_1"},
                },
            }
        ],
        "env_state": {"robot_location": "客厅_1", "robot_holding": "空"},
        "structured_task": {"intent": "去厨房"},
        "iteration_count": 1,
        "feature_flags": {
            "sandbox_evaluator": True,
            "semantic_audit": False,
            "state_diff_audit": False,
        },
        "environment": {
            "厨房_1": {
                "direct_parent": "房屋_1",
                "type": "room",
                "states": {},
                "full_path": ["房屋_1"],
            }
        },
        "repair_memory": {"failed_lessons": []},
        "injected_playbook_rule_ids": [],
    }


def test_evaluator_accepts_explicit_infrastructure_dependencies(monkeypatch):
    calls = []
    monkeypatch.setattr(flags, "ENABLE_SANDBOX_EVALUATOR", None)
    monkeypatch.setattr(
        evaluator,
        "resolve_repair_strategy",
        lambda _reader: (_ for _ in ()).throw(
            AssertionError("explicit dependencies must not read repair config")
        ),
    )
    state = {
        "todo_list": [
            {
                "step": 1,
                "execution": {
                    "skill": "NavigateTo",
                    "parameters": {"target_location": "厨房_1"},
                },
            }
        ],
        "env_state": {"robot_location": "客厅_1", "robot_holding": "空"},
        "structured_task": {"intent": "去厨房"},
        "iteration_count": 1,
        "feature_flags": {
            "sandbox_evaluator": True,
            "semantic_audit": False,
            "state_diff_audit": False,
        },
        "environment": {
            "厨房_1": {
                "direct_parent": "房屋_1",
                "type": "room",
                "states": {},
                "full_path": ["房屋_1"],
            }
        },
        "repair_memory": {"failed_lessons": []},
        "injected_playbook_rule_ids": [],
    }

    result = evaluator.evaluate_feasibility(state, _dependencies(calls))

    assert result["is_feasible"] is True
    assert calls == [("NavigateTo", {"target_location": "厨房_1"})]


def test_simulation_returns_a_result_before_the_session_publishes_it(monkeypatch):
    monkeypatch.setattr(flags, "ENABLE_SANDBOX_EVALUATOR", None)
    dependencies = _dependencies([])
    state = evaluator.with_planning_config(_request_state())
    context = build_evaluation_context(state, dependencies)
    modes = resolve_evaluation_modes(state, context.feature_flags, dependencies)
    session = create_evaluation_session(context, modes, dependencies)
    assert not isinstance(session, EvaluationFailure)
    pending = session.simulation

    result = run_base_simulation(session)

    assert isinstance(result, SimulationResult)
    assert result.simulated is True
    assert len(result.validated_steps) == 1
    assert session.simulation is pending

    session.record_simulation(result)
    assert session.simulation is result


def test_recovery_context_is_one_recheck_scoped_not_rebuilt_from_history(monkeypatch):
    monkeypatch.setattr(flags, "ENABLE_SANDBOX_EVALUATOR", None)
    dependencies = _dependencies([])
    action = {"execution": {"skill": "ToggleOff", "parameters": {}}}
    stale = evaluator.with_planning_config(_request_state())
    stale["repair_history"] = [
        {
            "stage": "state_diff_recovery",
            "generated_count": 1,
            "actions": [action],
        }
    ]
    context = build_evaluation_context(stale, dependencies)
    modes = resolve_evaluation_modes(stale, context.feature_flags, dependencies)
    stale_session = create_evaluation_session(context, modes, dependencies)

    assert not isinstance(stale_session, EvaluationFailure)
    assert stale_session.pending_recovery_actions == []

    current = {
        **stale,
        "evaluation_recheck": True,
        "evaluation_revision_context": {
            "source": "state_diff_recovery",
            "artifacts": {"recovery_actions": [action]},
        },
    }
    current_context = build_evaluation_context(current, dependencies)
    current_modes = resolve_evaluation_modes(
        current,
        current_context.feature_flags,
        dependencies,
    )
    current_session = create_evaluation_session(
        current_context,
        current_modes,
        dependencies,
    )

    assert not isinstance(current_session, EvaluationFailure)
    assert current_session.pending_recovery_actions == [action]


def test_scene_loader_failure_is_not_silently_replaced_with_grounded_state(monkeypatch):
    monkeypatch.setattr(flags, "ENABLE_SANDBOX_EVALUATOR", None)

    def fail_scene_load(_env):
        raise OSError("runtime snapshot unavailable")

    dependencies = replace(
        _dependencies([]),
        get_full_flat_house=fail_scene_load,
    )

    result = evaluator.evaluate_feasibility(_request_state(), dependencies)

    assert result["is_feasible"] is False
    assert result["failure_category"] == "scene_load"
    assert result["scene_load"] == {
        "passed": False,
        "error": "runtime snapshot unavailable",
    }


def test_evaluator_does_not_invoke_planning_model_for_legality_failure(monkeypatch):
    monkeypatch.setattr(flags, "ENABLE_SANDBOX_EVALUATOR", None)

    def fail_planning_model():
        raise AssertionError("evaluation must not invoke the planning model")

    dependencies = replace(
        _dependencies([]),
        get_planning_llm=fail_planning_model,
    )
    invalid = [
        {
            "step": 1,
            "execution": {"skill": "InventedSkill", "parameters": {}},
        }
    ]

    result = evaluator.evaluate_feasibility(
        _request_state(invalid),
        dependencies,
    )

    assert result["failure_category"] == "invalid_action"
    assert result["evaluation_repair_request"]["stage"] == "legality"


def test_concurrent_evaluations_mutate_only_request_local_scene_snapshots(monkeypatch):
    monkeypatch.setattr(flags, "ENABLE_SANDBOX_EVALUATOR", None)
    shared_env = {
        "厨房_1": {
            "direct_parent": "房屋_1",
            "type": "receptacle",
            "states": {},
            "is_container": True,
            "full_path": ["房屋_1"],
        }
    }
    barrier = Barrier(2)
    observed_markers = []

    def apply_action(env, robot, _skill, _parameters, **_kwargs):
        observed_markers.append(env["厨房_1"]["states"].get("request_marker"))
        barrier.wait(timeout=5)
        env["厨房_1"]["states"]["request_marker"] = robot["request_marker"]
        return True, "", ""

    dependencies = replace(
        _dependencies([]),
        apply_sandbox_action=apply_action,
        get_full_flat_house=lambda _path: shared_env,
    )

    def evaluate(marker):
        state = _request_state()
        state["env_state"]["request_marker"] = marker
        state["environment"] = shared_env
        return evaluator.evaluate_feasibility(state, dependencies)

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(evaluate, ("first", "second")))

    assert all(result["is_feasible"] is True for result in results)
    assert observed_markers == [None, None]
    assert shared_env["厨房_1"]["states"] == {}


def test_default_failure_handoff_is_strategy_neutral():
    handoff = CheckpointFailureHandoff()
    failure = EvaluationFailure(
        code=EvaluationFailureCode.UNKNOWN,
        issue_type="failed",
        fix_advice="repair",
        todo_list=[],
    )
    result = handoff.project_failure(failure, {}, include_handoff=True)

    assert type(handoff).__module__.endswith("evaluation.outcomes.handoff")
    assert result["repair_memory"]["failed_lessons"] == [
        "第 ? 步物理拦截: failed -> 修复要求: repair"
    ]
    assert result["repair_handoff"]["version"] == "checkpoint_handoff_v1"
    assert result["planning_continuation"]["repair_handoff"] == result["repair_handoff"]
    assert result["planning_continuation"]["next_step_num"] == 1
    assert "re_trac_memory" not in result
    assert "re_trac_state" not in result
