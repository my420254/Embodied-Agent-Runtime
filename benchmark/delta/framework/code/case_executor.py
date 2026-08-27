# ruff: noqa: E402  # sys.path 前置导入, case executor 有意为之
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from benchmark.delta.framework.code.task_environment import (
    FAIR_SCENE_MODE,
    build_delta_scene,
    load_delta_scene_graph,
    prepare_environment,
)
from benchmark.delta.framework.code.adapter import PAPER_MAIN_DOMAINS, load_delta_task_specs
from benchmark.delta.framework.code.config import load_config
from benchmark.delta.framework.code.pddl_plan_exporter import export_delta_pddl_plan, validate_delta_pddl_plan
from benchmark.delta.framework.code.native_actions import delta_native_plan_to_execution_calls
from benchmark.delta.framework.code.official_evaluator import evaluate_delta_goals
from benchmark.framework_task_bridge import (
    planning_graph,
    run_prepared_understanding_and_planning,
    understanding_graph,
)
from config.settings import activate_config


FAIR_INSTRUCTION_MODE = "goal_only"
SETTINGS_PATH = PROJECT_ROOT / "benchmark" / "delta" / "framework" / "code" / "config" / "settings.json"


# 和 DELTA 论文原方法的区别：
# DELTA 原 pipeline 不是让 LLM 直接输出最终机器人动作。它让 LLM 生成/修正
# domain.pddl、problem.pddl 和可选 subgoal PDDL，然后用 Fast Downward/PDDLGym
# 这类经典规划器生成 PDDL plan，再用 VAL/规划器执行结果判定成功。
#
# OurAgent-he 的 DELTA framework 口径：
# 模型直接输出 DELTA 官方动作对象；case executor 只把这些官方动作接到本地沙盒、
# 符号 evaluator 和 VAL 所需的执行接口。PDDL 导出只序列化已经通过 sandbox
# 校验的原生动作；不补任何动作，不注入 oracle subgoals。


def _ensure_benchmark_settings() -> None:
    activate_config(SETTINGS_PATH)


def synthesize_delta_instruction(case_input: dict) -> str:
    return str(case_input["instruction"])


def _first_sandbox_finding(planned: dict) -> dict:
    findings = planned.get("evaluator_findings", [])
    if isinstance(findings, list):
        for finding in findings:
            if isinstance(finding, dict):
                return finding
    trace = planned.get("benchmark_trace", {})
    if isinstance(trace, dict):
        planning_output = trace.get("planning_output", {})
        findings = planning_output.get("evaluator_findings", []) if isinstance(planning_output, dict) else []
        if isinstance(findings, list):
            for finding in findings:
                if isinstance(finding, dict):
                    return finding
    return {}


def _sandbox_failure_summary(planned: dict) -> dict:
    finding = _first_sandbox_finding(planned)
    if not finding:
        return {
            "reason": "",
            "repair_hint": "",
            "finding": {},
        }
    reason = str(finding.get("actual") or finding.get("error_type") or planned.get("feedback", "") or "").strip()
    repair_hint = str(finding.get("expected") or finding.get("repair_hint") or "").strip()
    return {
        "reason": reason,
        "repair_hint": repair_hint,
        "finding": finding,
    }


def _symbolic_official_alignment(*, goal_success_rate: float, val_success: bool, val_available: bool) -> dict:
    if not val_available:
        status = "official_unavailable"
    elif val_success:
        status = "aligned_success" if float(goal_success_rate) == 1.0 else "task_success_symbolic_mismatch"
    else:
        status = "aligned_failure" if float(goal_success_rate) != 1.0 else "official_failure_symbolic_mismatch"
    return {
        "status": status,
        "symbolic_goal_success_rate": float(goal_success_rate),
        "task_success": bool(val_success),
        "official_available": bool(val_available),
    }


def _final_execution_status(planned: dict, *, success: bool, val_success: bool = False) -> str:
    del val_success
    status = str(planned.get("execution_status", "") or "")
    if success and bool(planned.get("is_feasible", False)) and status in {"", "running"}:
        return "completed"
    return status


def _final_is_feasible(planned: dict, *, success: bool, val_success: bool = False) -> bool:
    del success, val_success
    if bool(planned.get("is_feasible", False)):
        return True
    return False


def _delta_execution_success(val_eval: dict) -> bool | None:
    if not bool(val_eval.get("available")):
        return None
    stdout = str(val_eval.get("stdout") or "")
    if "Plan executed successfully" in stdout:
        return True
    if bool(val_eval.get("success")):
        return True
    return False


def _effective_delta_native_plan(planned: dict) -> list[dict]:
    native_plan = list(planned.get("todo_list", []) or [])
    if native_plan:
        return native_plan
    sda_state = planned.get("sda_state") or {}
    todo_traj = sda_state.get("todo_trajectory") or {}
    return list(todo_traj.get("original_todo_list") or [])


def _planning_failed_before_official_eval(planned: dict, official_actions: list[dict]) -> bool:
    status = str(planned.get("execution_status", "") or "").strip().lower()
    if status == "failed":
        return True
    if bool(planned.get("is_feasible", False)):
        return False
    failure_layer = str(planned.get("failure_layer", "") or "").strip().lower()
    if failure_layer in {"understanding", "planning", "planning_evaluator", "sandbox"}:
        return True
    return not official_actions and not bool(planned.get("todo_llm_output", ""))


def _planning_failed_delta_result(
    planned: dict,
    *,
    instruction: str,
    official_actions: list[dict],
    evaluator_execution_calls: list[dict],
) -> dict:
    reason = str(
        planned.get("error_feedback")
        or planned.get("feedback")
        or planned.get("clarification_question")
        or "framework planning failed before official DELTA evaluation"
    ).strip()
    sandbox_summary = _sandbox_failure_summary(planned)
    val_eval = {
        "available": False,
        "success": False,
        "skipped": True,
        "error": reason,
    }
    pddl_export = {
        "skipped": True,
        "reason": reason,
        "execution_calls_len": len(evaluator_execution_calls),
    }
    return {
        "task_success": False,
        "task_success_rate": 0.0,
        "evaluation_route": "framework_failed_before_official_eval",
        "val_success": False,
        "val_available": False,
        "symbolic_success": False,
        "official_available": False,
        "execution_success": None,
        "fairness": {
            "instruction_source": FAIR_INSTRUCTION_MODE,
            "scene_mode": FAIR_SCENE_MODE,
            "uses_delta_natural_language_subgoals_in_prompt": False,
            "subgoal_pddl_used_only_after_planning_for_evaluation": False,
        },
        "effective_instruction": instruction,
        "evaluation_mode": "delta_framework_no_official_submission",
        "pddl_plan": pddl_export,
        "pddl_validation": val_eval,
        "goal_success_rate": 0.0,
        "satisfied_goals": [],
        "unsatisfied_goals": [],
        "symbolic_official_alignment": {
            "status": "framework_failed_before_official_eval",
            "symbolic_goal_success_rate": 0.0,
            "task_success": False,
            "official_available": False,
        },
        "official_failure_reason": reason,
        "sandbox_failure_reason": sandbox_summary["reason"],
        "sandbox_repair_hint": sandbox_summary["repair_hint"],
        "execution_status": str(planned.get("execution_status", "") or "failed"),
        "is_feasible": False,
        "feedback": planned.get("feedback", ""),
        "official_actions_len": len(official_actions),
        "official_actions": official_actions,
        "evaluator_execution_calls_len": len(evaluator_execution_calls),
        "evaluator_execution_calls": evaluator_execution_calls,
        "todo_llm_output": planned.get("todo_llm_output", ""),
        "todo_parse_error": planned.get("todo_parse_error", ""),
        "environment": planned.get("environment", {}),
        "benchmark_trace": planned.get("benchmark_trace", {}),
    }


def _native_delta_goal_pddls(case_input: dict) -> list[str]:
    domain = str(case_input.get("domain", "") or "").strip()
    scene_name = str(case_input.get("scene_name", "") or "").strip()
    if not domain or not scene_name:
        raise ValueError("DELTA case_input must include domain and scene_name for private evaluator lookup")
    cfg = load_config()
    for spec in load_delta_task_specs(cfg.repo_root, domains=PAPER_MAIN_DOMAINS):
        if spec.domain == domain and spec.scene == scene_name:
            return list(spec.subgoal_pddl)
    raise ValueError(f"DELTA native task not found for domain={domain!r}, scene_name={scene_name!r}")


def run_case(
    case_input: dict,
    *,
    plan_output_dir: str | Path | None = None,
    validate_binary: str | Path | None = None,
    skip_val: bool = False,
) -> dict:
    _ensure_benchmark_settings()
    selected_graph = load_delta_scene_graph(case_input)
    scene = build_delta_scene(selected_graph, case_input["instruction"], case_input=case_input)
    instruction = synthesize_delta_instruction(case_input)
    benchmark_input = {
        **case_input,
        "benchmark_module": "benchmark.delta",
        "benchmark_settings_file": str(SETTINGS_PATH),
        "instruction": instruction,
    }
    prepared = prepare_environment(
        benchmark_input,
        scene=scene,
        env_state=None,
    )
    planned = run_prepared_understanding_and_planning(
        case_input=benchmark_input,
        prepared=prepared,
        understanding_graph_runner=understanding_graph,
        planning_graph_runner=planning_graph,
    )
    official_actions = _effective_delta_native_plan(planned)
    evaluator_execution_calls = delta_native_plan_to_execution_calls(official_actions) if official_actions else []
    if _planning_failed_before_official_eval(planned, official_actions):
        return _planning_failed_delta_result(
            planned,
            instruction=instruction,
            official_actions=official_actions,
            evaluator_execution_calls=evaluator_execution_calls,
        )

    # subgoal_pddl 是评测答案，不在 case/worker/context 中流动；
    # evaluator 按 case 的 domain/scene 从 DELTA native 数据私下读取。
    goal_pddls = _native_delta_goal_pddls(case_input)
    goal_eval = evaluate_delta_goals(selected_graph, evaluator_execution_calls, goal_pddls)
    symbolic_success = bool(goal_eval["success"])

    plan_dir = Path(plan_output_dir) if plan_output_dir is not None else PROJECT_ROOT / "benchmark" / "delta" / "framework" / "results" / "_standalone" / "generated" / "pddl_plans"
    plan_path = plan_dir / f"{str(case_input.get('task_id', 'delta_case')).replace(':', '_')}.plan"
    pddl_export = export_delta_pddl_plan(
        case_input=case_input,
        scene_graph=selected_graph,
        execution_calls=evaluator_execution_calls,
        output_path=plan_path,
    )
    if pddl_export["export_errors"]:
        val_eval = {
            "available": False,
            "success": False,
            "skipped": True,
            "error": "PDDL export failed before VAL: " + "; ".join(pddl_export["export_errors"]),
        }
        success = False
        evaluation_route = "pddl_export_failed"
    elif skip_val:
        val_eval = {
            "available": False,
            "success": False,
            "skipped": True,
            "error": "VAL skipped by --skip-val",
        }
        success = symbolic_success
        evaluation_route = "symbolic_fallback_skip_val"
    else:
        val_eval = validate_delta_pddl_plan(
            domain_file=pddl_export["domain_file"],
            problem_file=pddl_export["problem_file"],
            plan_file=pddl_export["plan_path"],
            validate_binary=validate_binary,
        )
        if val_eval.get("available"):
            success = bool(val_eval["success"])
            evaluation_route = "val"
        else:
            success = symbolic_success
            evaluation_route = "symbolic_fallback_no_val"
    val_success = bool(val_eval.get("success"))
    val_available = bool(val_eval.get("available"))
    sandbox_summary = _sandbox_failure_summary(planned)
    symbolic_official_alignment = _symbolic_official_alignment(
        goal_success_rate=float(goal_eval["goal_success_rate"]),
        val_success=val_success,
        val_available=val_available,
    )

    return {
        "task_success": val_success,
        "task_success_rate": 1.0 if val_success else 0.0,
        "evaluation_route": evaluation_route,
        "val_success": val_success,
        "val_available": val_available,
        "symbolic_success": symbolic_success,
        "official_available": val_available,
        "execution_success": _delta_execution_success(val_eval),
        "fairness": {
            "instruction_source": FAIR_INSTRUCTION_MODE,
            "scene_mode": FAIR_SCENE_MODE,
            "uses_delta_natural_language_subgoals_in_prompt": False,
            "subgoal_pddl_used_only_after_planning_for_evaluation": True,
        },
        "effective_instruction": instruction,
        "evaluation_mode": "delta_val_pddl_plan" if evaluation_route == "val" else goal_eval["evaluation_mode"],
        "pddl_plan": pddl_export,
        "pddl_validation": val_eval,
        "goal_success_rate": goal_eval["goal_success_rate"],
        "satisfied_goals": goal_eval["satisfied_goals"],
        "unsatisfied_goals": goal_eval["unsatisfied_goals"],
        "symbolic_official_alignment": symbolic_official_alignment,
        "official_failure_reason": "" if val_success else str(val_eval.get("error") or "").strip(),
        "sandbox_failure_reason": sandbox_summary["reason"],
        "sandbox_repair_hint": sandbox_summary["repair_hint"],
        "execution_status": _final_execution_status(planned, success=success, val_success=val_success),
        "is_feasible": _final_is_feasible(planned, success=success, val_success=val_success),
        "feedback": planned.get("feedback", ""),
        "official_actions_len": len(official_actions),
        "official_actions": official_actions,
        "evaluator_execution_calls_len": len(evaluator_execution_calls),
        "evaluator_execution_calls": evaluator_execution_calls,
        "todo_llm_output": planned.get("todo_llm_output", ""),
        "todo_parse_error": planned.get("todo_parse_error", ""),
        "environment": planned.get("environment", {}),
        "benchmark_trace": planned.get("benchmark_trace", {}),
    }
