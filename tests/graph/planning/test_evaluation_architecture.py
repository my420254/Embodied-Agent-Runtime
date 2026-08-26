import ast
import sys
from dataclasses import fields, replace
from pathlib import Path

from graph.planning.evaluation import evaluator, flags
from graph.planning import node as planning_node
from graph.planning.evaluation.dependencies import EvaluationDependencies
from graph.planning.evaluation.models import (
    CandidateRevision,
    EvaluationFailure,
    EvaluationFailureCode,
    EvaluationSession,
)
from graph.planning.evaluation.repair_strategies import (
    RepairAssembly,
    RepairDiagnosis,
    RepairStrategyRegistry,
)
from graph.planning.evaluation.outcomes.handoff import CheckpointFailureHandoff


EVALUATION_DIR = Path(__file__).parents[3] / "graph" / "planning" / "evaluation"
PROJECT_ROOT = Path(__file__).parents[3]
REPAIR_ROOT = EVALUATION_DIR / "repair_strategies"
REPAIR_PACKAGES = ("sda", "vcr", "retrac")
REPAIR_MODULE_PREFIX = "graph.planning.evaluation.repair_strategies"


class _Strategy:
    def __init__(self, name):
        self.name = name

    def find_errors(self, context):
        raise AssertionError("selection tests must not execute a strategy")

    def reassemble(self, diagnosis, generated_todo_list):
        raise AssertionError("selection tests must not execute a strategy")


def _dependencies():
    return EvaluationDependencies(
        apply_sandbox_action=lambda *args, **kwargs: (True, "", ""),
        get_full_flat_house=lambda env: env,
        get_planning_llm=lambda: None,
        load_skill_catalog=lambda profile=None: None,
        load_enabled_skill_prompts=lambda profile=None: "",
        record_rule_feedback=lambda *args, **kwargs: None,
        learn_from_success=lambda *args, **kwargs: None,
        save_evaluator_finding=lambda *args, **kwargs: None,
        trace_recorder_factory=lambda: None,
        get_skill_handlers=lambda profile=None: {},
        repair_registry=RepairStrategyRegistry(),
        failure_handoff=CheckpointFailureHandoff(),
    )


def test_internal_evaluation_modules_do_not_import_compatibility_facade():
    violations = []
    for path in EVALUATION_DIR.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        if path.name == "evaluator.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module == "evaluator" or module.endswith(".evaluation.evaluator"):
                    violations.append(f"{path.name}:{node.lineno}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.endswith(".evaluation.evaluator"):
                        violations.append(f"{path.name}:{node.lineno}")

    assert violations == []


def test_only_evaluator_projects_stage_outcomes_with_reporter():
    violations = []
    allowed = {
        EVALUATION_DIR / "evaluator.py",
        EVALUATION_DIR / "outcomes" / "reporter.py",
    }
    for path in EVALUATION_DIR.rglob("*.py"):
        if path in allowed or "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            modules = []
            if isinstance(node, ast.ImportFrom) and node.module:
                modules = [node.module]
            elif isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            if any(module.endswith("outcomes.reporter") for module in modules):
                violations.append(f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}")

    assert violations == []


def test_evaluation_simulation_is_request_local_and_result_driven():
    simulation_source = (
        EVALUATION_DIR / "pipeline" / "simulation.py"
    ).read_text(encoding="utf-8")
    session_fields = {item.name for item in fields(EvaluationSession)}

    assert "simulation" in session_fields
    assert not {
        "sim_env",
        "sim_robot",
        "trajectory_records",
        "validated_steps",
    } & session_fields
    assert "reset_sandbox_from_runtime" not in simulation_source
    assert "save_scene" not in simulation_source


def test_repair_packages_only_import_stdlib_own_package_and_contracts():
    violations = []
    for package in REPAIR_PACKAGES:
        package_root = REPAIR_ROOT / package
        assert package_root.is_dir()
        for path in package_root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.split(".", 1)[0] not in sys.stdlib_module_names:
                            violations.append(
                                f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}"
                                f" -> {alias.name}"
                            )
                elif isinstance(node, ast.ImportFrom):
                    if node.level == 0:
                        root = (node.module or "").split(".", 1)[0]
                        if root not in sys.stdlib_module_names:
                            violations.append(
                                f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}"
                                f" -> {node.module}"
                            )
                    elif node.level == 1:
                        continue
                    elif node.level == 2 and node.module == "contracts":
                        continue
                    else:
                        violations.append(
                            f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}"
                            f" -> level={node.level}:{node.module or ''}"
                        )

    assert violations == []


def test_repair_strategy_packages_do_not_import_each_other():
    violations = []
    for package in REPAIR_PACKAGES:
        package_root = REPAIR_ROOT / package
        other_packages = set(REPAIR_PACKAGES) - {package}
        for path in package_root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    modules = [node.module or ""]
                else:
                    continue
                for module in modules:
                    absolute_cross_import = any(
                        module == f"{REPAIR_MODULE_PREFIX}.{other}"
                        or module.startswith(f"{REPAIR_MODULE_PREFIX}.{other}.")
                        for other in other_packages
                    )
                    relative_cross_import = (
                        isinstance(node, ast.ImportFrom)
                        and node.level == 2
                        and module.split(".", 1)[0] in other_packages
                    )
                    if absolute_cross_import or relative_cross_import:
                        violations.append(
                            f"{path.relative_to(PROJECT_ROOT)}:{node.lineno} -> {module}"
                        )

    assert violations == []


def _relative_imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.level > 0
    }


def test_only_registry_imports_concrete_repair_packages():
    violations = []
    allowed = REPAIR_ROOT / "registry.py"
    for path in PROJECT_ROOT.rglob("*.py"):
        if "tests" in path.parts or path == allowed:
            continue
        if any(package in path.parts for package in REPAIR_PACKAGES) and REPAIR_ROOT in path.parents:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            modules = []
            if isinstance(node, ast.ImportFrom) and node.module:
                modules = [node.module]
            elif isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            for module in modules:
                if any(
                    module == f"{REPAIR_MODULE_PREFIX}.{package}"
                    or module.startswith(f"{REPAIR_MODULE_PREFIX}.{package}.")
                    for package in REPAIR_PACKAGES
                ):
                    violations.append(
                        f"{path.relative_to(PROJECT_ROOT)}:{node.lineno} -> {module}"
                    )

    assert violations == []


def test_evaluation_layers_use_explicit_module_names():
    root_modules = {
        "__init__.py",
        "composition.py",
        "dependencies.py",
            "evaluator.py",
            "flags.py",
            "models.py",
        }
    assert {path.name for path in EVALUATION_DIR.glob("*.py")} == root_modules
    assert (EVALUATION_DIR / "pipeline" / "candidate.py").is_file()
    assert (EVALUATION_DIR / "pipeline" / "session.py").is_file()
    assert (EVALUATION_DIR / "pipeline" / "simulation.py").is_file()
    assert (EVALUATION_DIR / "pipeline" / "skills.py").is_file()
    assert (EVALUATION_DIR / "validation" / "legality.py").is_file()
    assert (EVALUATION_DIR / "validation" / "native_evaluator.py").is_file()
    assert (EVALUATION_DIR / "validation" / "state_recovery.py").is_file()
    assert not (EVALUATION_DIR / "validation" / "evaluator.py").exists()
    assert (EVALUATION_DIR / "outcomes" / "reporter.py").is_file()
    assert (EVALUATION_DIR / "outcomes" / "handoff.py").is_file()
    assert not (EVALUATION_DIR / "audits" / "entity_scope.py").exists()
    assert (EVALUATION_DIR / "audits" / "state_diff.py").is_file()
    assert (EVALUATION_DIR / "audits" / "semantic.py").is_file()

    removed = {
        "audits.py",
        "core.py",
        "repair.py",
        "repair_cycle.py",
    }
    assert not removed & {path.name for path in EVALUATION_DIR.glob("*.py")}
    assert not (REPAIR_ROOT / "base.py").exists()


def test_planning_runtime_does_not_import_concrete_repair_packages():
    violations = []
    planning_root = PROJECT_ROOT / "graph" / "planning"
    for path in planning_root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            modules = []
            if isinstance(node, ast.ImportFrom) and node.module:
                modules = [node.module]
            elif isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            if any(
                module.startswith(REPAIR_MODULE_PREFIX + ".")
                for module in modules
            ):
                violations.append(f"{path.name}:{node.lineno}")

    assert violations == []


def test_repair_runtime_directories_match_selected_integration_shape():
    assert (PROJECT_ROOT / "SDA").exists()
    assert not (PROJECT_ROOT / "VCR").exists()
    assert (PROJECT_ROOT / "re_trac").exists()


def test_repair_strategy_packages_reflect_their_execution_shape():
    for package in REPAIR_PACKAGES:
        package_root = REPAIR_ROOT / package
        assert (package_root / "diagnosis.py").is_file()
        assert (package_root / "assembly.py").is_file()
    vcr_root = REPAIR_ROOT / "vcr"
    assert (vcr_root / "core.py").is_file()
    assert (vcr_root / "causal_checkpoint.py").is_file()
    assert not (vcr_root / "micro_planner.py").exists()
    assert not (vcr_root / "strategy.py").exists()
    assert not (REPAIR_ROOT / "sda" / "adaptive_subtree.py").exists()
    assert not (REPAIR_ROOT / "retrac" / "adapter.py").exists()
    assert not (REPAIR_ROOT / "retrac" / "state.py").exists()


def test_planning_repair_runtime_has_single_public_entry_shape():
    planning_root = PROJECT_ROOT / "graph" / "planning"

    assert (planning_root / "repair" / "__init__.py").is_file()
    assert (planning_root / "repair" / "continuation.py").is_file()
    assert (planning_root / "repair" / "regeneration.py").is_file()
    assert not (planning_root / "repair.py").exists()
    assert not (planning_root / "repair" / "repair_strategy.py").exists()
    assert not (planning_root / "repair" / "repair_context.py").exists()
    assert not (planning_root / "output_parser.py").exists()


def test_every_repair_strategy_exposes_only_diagnosis_and_assembly_flow_methods():
    for package in REPAIR_PACKAGES:
        path = REPAIR_ROOT / package / "diagnosis.py"
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        strategy = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name.endswith("RepairStrategy")
        )
        public_methods = {
            node.name
            for node in strategy.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and not node.name.startswith("_")
        }

        assert public_methods == {"find_errors", "reassemble"}


def test_planning_state_exposes_only_current_strategy_artifacts():
    state_source = (PROJECT_ROOT / "graph" / "state.py").read_text(encoding="utf-8")
    reporter_source = (EVALUATION_DIR / "outcomes" / "reporter.py").read_text(
        encoding="utf-8"
    )
    legacy_fields = {"vcr_state", "retrac_state"}

    assert all(field not in state_source for field in legacy_fields)
    assert all(field not in reporter_source for field in legacy_fields)


def test_repair_strategies_expose_registry_without_workflow_orchestrator():
    assert (REPAIR_ROOT / "registry.py").is_file()
    assert not (REPAIR_ROOT / "orchestrator.py").exists()


def test_evaluation_session_owns_loaded_skill_dependencies():
    session_source = (EVALUATION_DIR / "pipeline" / "session.py").read_text(encoding="utf-8")
    skills_source = (EVALUATION_DIR / "pipeline" / "skills.py").read_text(encoding="utf-8")
    evaluator_source = (EVALUATION_DIR / "evaluator.py").read_text(encoding="utf-8")

    assert "load_skill_snapshot(context.skill_profile, dependencies)" in session_source
    assert "dependencies.load_skill_catalog(profile)" in skills_source
    assert "dependencies.get_skill_handlers(profile)" in skills_source
    assert "dependencies.load_enabled_skill_prompts" in skills_source
    assert "skill_catalog=session.skill_catalog" in evaluator_source
    assert "skill_handlers=session.skill_handlers" in evaluator_source


def test_repair_registry_selects_one_strategy_without_cross_strategy_coordination():
    default = _Strategy("default")
    alternate = _Strategy("alternate")
    registry = RepairStrategyRegistry(
        (default, alternate),
        default_strategy="default",
    )

    assert registry.select().strategy is default
    assert registry.select("alternate").strategy is alternate


def test_repair_registry_rejects_unknown_canonical_strategy():
    registry = RepairStrategyRegistry(
        (_Strategy("first"), _Strategy("second"))
    )

    selection = registry.select("missing")

    assert selection.strategy is None
    assert selection.selected_names == ("missing",)
    assert "未知修复策略" in selection.error


def test_planning_owns_model_repair_flow_while_evaluation_owns_assembly():
    evaluation_source = (EVALUATION_DIR / "evaluator.py").read_text(encoding="utf-8")
    planning_source = (
        PROJECT_ROOT / "graph" / "planning" / "node.py"
    ).read_text(encoding="utf-8")

    assert "regenerate_todo_list" not in evaluation_source
    assert "while True:" not in evaluation_source
    assert "_regenerate_evaluation_repair" in planning_source
    assert "validate_evaluation_repair_request(request)" in planning_source
    assert 'workflow.add_node("assemble_repair", assemble_repair_candidate)' in planning_source
    assert "validate_evaluation_repair_request(request)" in evaluation_source
    assert "selection.strategy.reassemble(diagnosis, generated_steps)" in evaluation_source


def test_planning_drives_repair_request_model_output_assembly_and_reentry(
    monkeypatch,
):
    calls = []
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
    replacement = {
        "step": 2,
        "execution": {
            "skill": "NavigateTo",
            "parameters": {"target_location": "橱柜_1"},
        },
    }

    class _RecordingStrategy:
        name = "recording"

        def find_errors(self, context):
            calls.append(("find_errors", context.todo_list))
            return RepairDiagnosis(
                strategy_name=self.name,
                prompt="repair complete candidate",
            )

        def reassemble(self, diagnosis, generated_todo_list):
            calls.append(("reassemble", generated_todo_list))
            return RepairAssembly(
                strategy_name=self.name,
                success=True,
                todo_list=[original[0], *generated_todo_list],
            )

    registry = RepairStrategyRegistry(
        (_RecordingStrategy(),),
        default_strategy="recording",
    )
    dependencies = replace(
        _dependencies(),
        repair_registry=registry,
    )
    candidate_calls = []

    def evaluate_once(session):
        candidate_calls.append([dict(step) for step in session.todo_list])
        if len(candidate_calls) == 1:
            return EvaluationFailure(
                code=EvaluationFailureCode.NAVIGATION_PRECONDITION,
                issue_type="前置位置依赖未满足",
                fix_advice="先导航到橱柜",
                step=original[1],
                checkpoint_env={},
                checkpoint_robot={},
            )
        return None

    monkeypatch.setattr(flags, "ENABLE_SANDBOX_EVALUATOR", None)
    monkeypatch.setattr(evaluator, "with_planning_config", lambda state: state)
    monkeypatch.setattr(evaluator, "evaluate_candidate", evaluate_once)
    monkeypatch.setattr(evaluator, "run_evaluation_audits", lambda *_args: None)
    monkeypatch.setattr(planning_node, "with_planning_config", lambda state: state)
    monkeypatch.setattr(
        planning_node,
        "_regenerate_evaluation_repair",
        lambda request, profile: calls.append(("regenerate", request["prompt"]))
        or [replacement],
    )
    state = {
        "todo_list": original,
        "env_state": {"robot_location": "起点_1", "robot_holding": "空"},
        "structured_task": {"intent": "打开橱柜"},
        "environment": {
            "起点_1": {"type": "receptacle", "states": {}},
            "错误位置_1": {"type": "receptacle", "states": {}},
            "橱柜_1": {"type": "cabinet", "states": {"isOpen": False}, "is_container": True},
        },
        "feature_flags": {
            "sandbox_evaluator": True,
            "semantic_audit": False,
            "state_diff_audit": False,
        },
    }

    diagnosed = evaluator.evaluate_feasibility(state, dependencies)
    planned = planning_node.decompose_task({**state, **diagnosed})
    assembled = evaluator.assemble_repair_candidate(
        {**state, **diagnosed, **planned},
        dependencies,
    )
    result = evaluator.evaluate_feasibility(
        {**state, **diagnosed, **planned, **assembled},
        dependencies,
    )

    assert result["is_feasible"] is True
    assert candidate_calls == [original, [original[0], replacement]]
    assert [name for name, *_rest in calls] == [
        "find_errors",
        "regenerate",
        "reassemble",
    ]
    assert calls[0][1] == original


def test_repair_assembly_rejects_stale_request_without_dropping_candidate():
    original = [
        {
            "step": 1,
            "execution": {
                "skill": "NavigateTo",
                "parameters": {"target_location": "错误位置_1"},
            },
        }
    ]
    result = evaluator.assemble_repair_candidate(
        {
            "todo_list": original,
            "repair_todo_list": [
                {
                    "execution": {
                        "skill": "NavigateTo",
                        "parameters": {"target_location": "橱柜_1"},
                    }
                }
            ],
            "evaluation_repair_request": {
                "version": "evaluation_repair_v0",
                "round": 1,
                "stage": "sandbox",
                "prompt": "stale request",
                "assembly_mode": "strategy",
                "strategy_name": "recording",
                "merge_context": {},
            },
        },
        _dependencies(),
    )

    assert result["execution_status"] == "failed"
    assert result["failure_category"] == "repair_assembly"
    assert result["todo_list"] == original
    assert "版本" in result["error_feedback"]


def test_evaluator_stops_before_audits_when_candidate_evaluation_fails(monkeypatch):
    calls = []
    failure = EvaluationFailure(
        code=EvaluationFailureCode.UNKNOWN,
        issue_type="simulation failed",
        fix_advice="retry the candidate",
    )

    monkeypatch.setattr(flags, "ENABLE_SANDBOX_EVALUATOR", None)
    monkeypatch.setattr(evaluator, "with_planning_config", lambda state: state)
    monkeypatch.setattr(
        evaluator,
        "evaluate_candidate",
        lambda session: calls.append("candidate_evaluation") or failure,
    )
    monkeypatch.setattr(
        evaluator,
        "run_evaluation_audits",
        lambda session, dependencies: (_ for _ in ()).throw(
            AssertionError("audits must not run after simulation failure")
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
        "environment": {"厨房_1": {"type": "receptacle", "states": {}}},
        "feature_flags": {
            "sandbox_evaluator": True,
            "semantic_audit": False,
            "state_diff_audit": False,
        },
    }

    result = evaluator.evaluate_feasibility(state, _dependencies())

    assert result["is_feasible"] is False
    assert result["failure_category"] == "unknown"
    assert "simulation failed" in result["feedback"]
    assert calls == ["candidate_evaluation"]


def test_candidate_revision_reenters_the_complete_candidate_pipeline(monkeypatch):
    candidate_plans = []
    audit_calls = []

    monkeypatch.setattr(flags, "ENABLE_SANDBOX_EVALUATOR", None)
    monkeypatch.setattr(evaluator, "with_planning_config", lambda state: state)
    monkeypatch.setattr(
        evaluator,
        "evaluate_candidate",
        lambda session: candidate_plans.append(
            [step["execution"]["skill"] for step in session.todo_list]
        ),
    )

    def audits(session, dependencies):
        audit_calls.append(len(session.todo_list))
        if len(audit_calls) == 1:
            return CandidateRevision(
                todo_list=session.todo_list
                + [
                    {
                        "step": 2,
                        "execution": {
                            "skill": "ToggleOff",
                            "parameters": {"target_device": "灯_1"},
                        },
                    }
                ],
                source="state_diff_recovery",
                artifacts={"recovery_actions": [{"execution": {"skill": "ToggleOff"}}]},
            )
        return None

    monkeypatch.setattr(evaluator, "run_evaluation_audits", audits)
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
        "environment": {"厨房_1": {"type": "receptacle", "states": {}}},
        "feature_flags": {
            "sandbox_evaluator": False,
            "semantic_audit": False,
            "state_diff_audit": False,
        },
    }

    first = evaluator.evaluate_feasibility(state, _dependencies())
    assert first["evaluation_recheck"] is True
    assert first["evaluation_revision_context"] == {
        "source": "state_diff_recovery",
        "artifacts": {
            "recovery_actions": [{"execution": {"skill": "ToggleOff"}}]
        },
    }
    assert "actions" not in first["repair_history"][0]
    result = evaluator.evaluate_feasibility(
        {**state, **first},
        _dependencies(),
    )

    assert result["is_feasible"] is True
    assert result["evaluation_revision_context"] == {}
    assert candidate_plans == [
        ["NavigateTo"],
        ["NavigateTo", "ToggleOff"],
    ]
    assert audit_calls == [1, 2]
