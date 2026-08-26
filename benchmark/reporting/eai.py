from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from benchmark.reporting.rounds import write_rounds_bundle
from benchmark.reporting.sections import append_stage_artifact_overview


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_contract_audit(case_dir: Path) -> dict[str, Any]:
    audit_path = case_dir / "artifacts" / "contract_audit.json"
    if not audit_path.exists():
        return {}
    try:
        loaded = _read_json(audit_path)
    except Exception:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _evaluation_digest(dataset: str, evaluation_detail: Any) -> Any:
    if dataset != "behavior":
        if not isinstance(evaluation_detail, dict) or not evaluation_detail:
            return evaluation_detail
        first = next(iter(evaluation_detail.values()))
        return first
    if not isinstance(evaluation_detail, list) or not evaluation_detail:
        return evaluation_detail
    first = evaluation_detail[0] if isinstance(evaluation_detail[0], dict) else {}
    llm_rst = first.get("llm_rst", {}) if isinstance(first, dict) else {}
    execution_info = llm_rst.get("execution_info", []) if isinstance(llm_rst, dict) else []
    first_error = None
    if isinstance(execution_info, list):
        for step in execution_info:
            if isinstance(step, dict) and not step.get("execution_success", True):
                first_error = step
                break
    return {
        "error_type": llm_rst.get("error_type"),
        "goal_rst": llm_rst.get("goal_rst"),
        "satisfication_info": llm_rst.get("satisfication_info"),
        "first_execution_error": first_error,
    }


def _official_evaluator_failure_summary(dataset: str, evaluation_summary: Any, evaluation_detail: Any) -> dict[str, Any]:
    goal_eval = evaluation_summary.get("goal_evaluation", {}) if isinstance(evaluation_summary, dict) else {}
    task_sr = goal_eval.get("task_success_rate")
    passed = bool(isinstance(task_sr, (int, float)) and float(task_sr) >= 1.0)
    summary: dict[str, Any] = {
        "passed": passed,
        "task_success_rate": task_sr,
        "failure_type": "",
        "failure_reason": "",
    }
    if passed:
        return summary

    if dataset == "behavior" and isinstance(evaluation_detail, list) and evaluation_detail:
        first = evaluation_detail[0] if isinstance(evaluation_detail[0], dict) else {}
        llm_rst = first.get("llm_rst", {}) if isinstance(first, dict) else {}
        error_type = llm_rst.get("error_type", {}) if isinstance(llm_rst, dict) else {}
        if isinstance(error_type, dict):
            active_errors = {
                str(key): value
                for key, value in error_type.items()
                if str(key) != "execution_success" and value not in (None, False, 0, "", [])
            }
            if active_errors:
                summary["failure_type"] = "runtime_error"
                summary["failure_reason"] = "; ".join(f"{key}: {value}" for key, value in active_errors.items())
                return summary

        sat_info = llm_rst.get("satisfication_info", {}) if isinstance(llm_rst, dict) else {}
        unsatisfied = sat_info.get("unsatisfied", []) if isinstance(sat_info, dict) else []
        if isinstance(unsatisfied, list) and unsatisfied:
            summary["failure_type"] = "unsatisfied_goals"
            summary["failure_reason"] = f"unsatisfied_goals={unsatisfied}"
            return summary

        execution_info = llm_rst.get("execution_info", []) if isinstance(llm_rst, dict) else []
        if isinstance(execution_info, list):
            for step in execution_info:
                if isinstance(step, dict) and not step.get("execution_success", True):
                    errors = step.get("errors", []) if isinstance(step.get("errors"), list) else []
                    error_text = "; ".join(
                        f"{err.get('error_type')}: {err.get('error_reason')}" for err in errors if isinstance(err, dict)
                    )
                    summary["failure_type"] = "execution_failure"
                    summary["failure_reason"] = error_text or f"first_failed_step={step.get('step')}"
                    return summary

    if dataset == "virtualhome":
        metadata = evaluation_summary.get("metadata", {}) if isinstance(evaluation_summary, dict) else {}
        if isinstance(metadata, dict) and metadata:
            summary["failure_type"] = str(metadata.get("evaluator", "") or "virtualhome_evaluator")
            summary["failure_reason"] = str(metadata.get("fallback_reason", "") or "task_success_rate=0.0")
            return summary

    summary["failure_type"] = "official_evaluator_failed"
    summary["failure_reason"] = f"task_success_rate={task_sr}"
    return summary


def _resolve_evaluator_paths_from_case_meta(
    case_meta: dict[str, Any],
    evaluation_summary_path: Path | None,
    evaluation_detail_path: Path | None,
) -> tuple[Path | None, Path | None]:
    summary_path = evaluation_summary_path
    detail_path = evaluation_detail_path
    artifacts = case_meta.get("artifacts", []) if isinstance(case_meta, dict) else []
    if isinstance(artifacts, list):
        for artifact in artifacts:
            try:
                path = Path(str(artifact))
            except Exception:
                continue
            path_str = str(path).replace("\\", "/")
            if summary_path is None and ("/summary/" in path_str or path.name == "summary.json"):
                summary_path = path
            if detail_path is None and ("/log/" in path_str or path.name == "error_info.json"):
                detail_path = path
    return summary_path, detail_path


def write_case_report(
    *,
    output_path: Path,
    case_meta_path: Path,
    raw_output_path: Path,
    trace_json_path: Path | None = None,
    evaluation_summary_path: Path | None = None,
    evaluation_detail_path: Path | None = None,
    config: dict[str, Any],
    dataset: str | None = None,
) -> None:
    case_meta = _read_json(case_meta_path) if case_meta_path.exists() else {}
    evaluation_summary_path, evaluation_detail_path = _resolve_evaluator_paths_from_case_meta(
        case_meta,
        evaluation_summary_path,
        evaluation_detail_path,
    )
    raw_output = _read_json(raw_output_path) if raw_output_path.exists() else []
    trace_row = _read_json(trace_json_path) if trace_json_path and trace_json_path.exists() else {}
    evaluation_summary = _read_json(evaluation_summary_path) if evaluation_summary_path and evaluation_summary_path.exists() else None
    evaluation_detail = _read_json(evaluation_detail_path) if evaluation_detail_path and evaluation_detail_path.exists() else None

    prediction = {}
    if isinstance(trace_row, dict):
        prediction = trace_row.get("prediction", {}) if isinstance(trace_row.get("prediction"), dict) else {}
    if not prediction and isinstance(raw_output, list) and raw_output and isinstance(raw_output[0], dict):
        prediction = raw_output[0]

    dataset = str(dataset or config.get("dataset", case_meta.get("dataset", "")) or "")
    case_dir = output_path.parent
    planning_result = prediction.get("planning_result", {}) if isinstance(prediction, dict) else {}
    rounds = write_rounds_bundle(case_dir, prediction, include_rounds=bool(config.get("include_rounds", True)))
    contract_audit = _load_contract_audit(case_dir)
    goal_eval = case_meta.get("evaluation_summary", {}).get("goal_evaluation", {}) if isinstance(case_meta, dict) else {}
    traj_eval = case_meta.get("evaluation_summary", {}).get("trajectory_evaluation", {}) if isinstance(case_meta, dict) else {}
    framework_passed = bool(
        isinstance(planning_result, dict)
        and planning_result.get("is_feasible") is True
        and str(planning_result.get("execution_status", "") or "").strip().lower() != "failed"
    )
    framework_intercept_count = len(rounds.get("intercepts", []) if isinstance(rounds.get("intercepts"), list) else [])
    framework_terminal_failure = str(rounds.get("terminal_failure", "") or "").strip()
    evaluator_failure = _official_evaluator_failure_summary(dataset, evaluation_summary, evaluation_detail)

    title = str(config.get("title", "Case Report") or "Case Report")
    lines = [
        f"# {title}: {case_meta.get('case_id', case_dir.name)}",
        "",
        f"- dataset: `{dataset}`",
        f"- mode: `{case_meta.get('mode', '')}`",
        f"- status: `{case_meta.get('status', '')}`",
        f"- case meta: `{case_meta_path}`",
        f"- raw output: `{raw_output_path}`",
        f"- trace json: `{trace_json_path}`" if trace_json_path else "- trace json: ``",
        f"- evaluator summary: `{evaluation_summary_path}`" if evaluation_summary_path else "- evaluator summary: ``",
        f"- evaluator detail: `{evaluation_detail_path}`" if evaluation_detail_path else "- evaluator detail: ``",
        "",
    ]
    append_stage_artifact_overview(lines, case_dir / "artifacts")
    lines.extend(
        [
            "",
            "## Result Summary",
            f"- task_success: `{prediction.get('task_success')}`",
            f"- task_success_rate: `{prediction.get('task_success_rate', goal_eval.get('task_success_rate'))}`",
            f"- official_available: `{prediction.get('official_available')}`",
            f"- execution_success: `{prediction.get('execution_success')}`",
            f"- execution_success_rate: `{traj_eval.get('execution_success_rate')}`",
            f"- planning execution_status: `{planning_result.get('execution_status')}`",
            f"- planning is_feasible: `{planning_result.get('is_feasible')}`",
            f"- planning feedback: `{str(planning_result.get('feedback', '') or '').replace(chr(10), ' / ')}`",
            f"- todo_contract status: `{contract_audit.get('status', '')}`",
            f"- todo_contract audit: `{case_dir / 'artifacts' / 'contract_audit.json'}`",
            "",
            "## Failure Summary",
            f"- framework passed: `{framework_passed}`",
            f"- framework intercept count: `{framework_intercept_count}`",
            f"- framework terminal failure: `{framework_terminal_failure.replace(chr(10), ' / ')}`",
            f"- official evaluator passed: `{evaluator_failure.get('passed')}`",
            f"- official evaluator failure type: `{evaluator_failure.get('failure_type')}`",
            f"- official evaluator failure reason: `{str(evaluator_failure.get('failure_reason', '')).replace(chr(10), ' / ')}`",
            "",
            "## Prompt / Round Files",
            f"- interceptions summary: `{rounds.get('interceptions_file', '')}`",
            f"- rounds index: `{case_dir / 'artifacts' / 'rounds' / 'rounds_index.json'}`",
            "",
            "## Sequence",
        ]
    )

    initial_round = rounds.get("initial_round") or {}
    if initial_round:
        lines.extend(
            [
                "### Initial Planning",
                f"- input file: `{initial_round.get('input_file', '')}`",
                f"- output file: `{initial_round.get('output_file', '')}`",
            ]
        )
    lines.append("")

    intercepts = rounds.get("intercepts", []) if isinstance(rounds.get("intercepts"), list) else []
    repairs = rounds.get("repairs", []) if isinstance(rounds.get("repairs"), list) else []
    for index, intercept in enumerate(intercepts, start=1):
        lines.extend(
            [
                f"### Interception {index}",
                f"- failed step: `{intercept.get('failed_step')}`",
                f"- issue: `{intercept.get('issue')}`",
                f"- repair hint: `{intercept.get('repair_hint')}`",
                f"- raw record: `{intercept.get('raw')}`",
                "",
            ]
        )
        if index <= len(repairs):
            repair = repairs[index - 1]
            lines.extend(
                [
                    f"### Repair {index}",
                    f"- resume from step: `{repair.get('resume_from_step')}`",
                    f"- repair prompt: `{str(repair.get('repair_prompt', '')).replace(chr(10), ' / ')}`",
                    f"- input file: `{repair.get('input_file')}`",
                    f"- output file: `{repair.get('output_file')}`",
                ]
            )
            lines.append("")

    lines.extend(
        [
            "## Evaluator",
            f"- summary file: `{evaluation_summary_path}`" if evaluation_summary_path else "- summary file: ``",
            f"- detail file: `{evaluation_detail_path}`" if evaluation_detail_path else "- detail file: ``",
            "",
            "## Evaluator Detail Digest",
            "```json",
            json.dumps(_evaluation_digest(dataset, evaluation_detail), ensure_ascii=False, indent=2),
            "```",
            "",
        ]
    )

    if framework_terminal_failure:
        lines.extend(
            [
                "## Terminal Failure",
                f"- terminal failure: `{framework_terminal_failure.replace(chr(10), ' / ')}`",
                "",
            ]
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
