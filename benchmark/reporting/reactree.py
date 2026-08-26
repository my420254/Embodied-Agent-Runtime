from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from benchmark.reporting.sections import append_stage_artifact_overview


def _json_block(value: Any) -> str:
    return "```json\n" + json.dumps(value, ensure_ascii=False, indent=2) + "\n```"


def _text_block(value: str) -> str:
    return "```text\n" + str(value) + "\n```"


def _prediction(row: dict[str, Any]) -> dict[str, Any]:
    prediction = row.get("prediction", {})
    return prediction if isinstance(prediction, dict) else {}


def _trace(row: dict[str, Any]) -> dict[str, Any]:
    trace = _prediction(row).get("benchmark_trace", {})
    return trace if isinstance(trace, dict) else {}


def _sandbox_events(trace: dict[str, Any]) -> list[dict[str, Any]]:
    planning_output = trace.get("planning_output", {})
    if not isinstance(planning_output, dict):
        return []
    events = planning_output.get("planning_debug_events", [])
    return events if isinstance(events, list) else []


def _todo_contract_events(trace: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        event
        for event in _sandbox_events(trace)
        if isinstance(event, dict) and str(event.get("layer", "") or "").lower() == "todo_contract"
    ]


def _todo_contract_status(trace: dict[str, Any]) -> str:
    events = _todo_contract_events(trace)
    event_types = {str(event.get("type", "") or "").lower() for event in events if isinstance(event, dict)}
    if "rejected" in event_types:
        return "rejected"
    if "passed" in event_types:
        return "passed"
    return "not_recorded"


def _llm_turns(trace: dict[str, Any], module_name: str) -> list[dict[str, Any]]:
    turns = trace.get("llm_io", [])
    if not isinstance(turns, list):
        return []
    return [turn for turn in turns if isinstance(turn, dict) and turn.get("module") == module_name]


def _render_common_sections(lines: list[str], row: dict[str, Any], prediction: dict[str, Any], trace: dict[str, Any], planning_output: dict[str, Any]) -> None:
    sandbox_events = _sandbox_events(trace)
    sandbox_checks = [event for event in sandbox_events if event.get("layer") == "sandbox"]
    sandbox_failed = [event for event in sandbox_checks if event.get("ok") is False]
    todo_contract_events = _todo_contract_events(trace)
    understanding_turns = _llm_turns(trace, "understanding")
    planning_turns = _llm_turns(trace, "planning")

    lines.append("## 3. 要看的关键字段")
    lines.append("")
    lines.append("- `prediction.benchmark_trace.case_input`：这条数据原始输入")
    lines.append("- `prediction.benchmark_trace.prepared_environment`：场景准备结果")
    lines.append("- `prediction.benchmark_trace.understanding_input / understanding_output`：understanding 前后")
    lines.append("- `prediction.benchmark_trace.planning_input / planning_output`：planning 前后")
    lines.append("- `artifacts/contract_audit.json`：本次 todo_list 原生动作契约检查、动作格式、命中 skill schema")
    lines.append("- `prediction.benchmark_trace.llm_io`：每次模型输入输出")
    lines.append("- `prediction.benchmark_trace.planning_output.planning_debug_events`：每次 contract / sandbox / audit 事件")
    lines.append("- `prediction.benchmark_trace.planning_output.re_trac_memory`：re_trac 的 failed lessons")
    lines.append("- `prediction.benchmark_trace.planning_output.evaluator_findings`：结构化失败摘要")
    lines.append("")
    lines.append("## 4. Benchmark 原始输入")
    lines.append("")
    lines.append(_json_block(trace.get("case_input", row.get("input", {}))))
    lines.append("")
    lines.append("## 5. Framework 各阶段输入输出")
    lines.append("")
    lines.append("### Prepared Environment")
    lines.append(_json_block(trace.get("prepared_environment", {})))
    lines.append("")
    lines.append("### Understanding Input")
    lines.append(_json_block(trace.get("understanding_input", {})))
    lines.append("")
    lines.append("### Understanding Output")
    lines.append(_json_block(trace.get("understanding_output", {})))
    lines.append("")
    lines.append("### Planning Input")
    lines.append(_json_block(trace.get("planning_input", {})))
    lines.append("")
    lines.append("### Planning Output")
    lines.append(_json_block(planning_output))
    lines.append("")
    lines.append("## 6. Sandbox / ReTrac 统计")
    lines.append("")
    lines.append(_json_block(
        {
            "sandbox_check_count": len(sandbox_checks),
            "sandbox_failed_count": len(sandbox_failed),
            "todo_contract_status": _todo_contract_status(trace),
            "todo_contract_events": todo_contract_events,
            "re_trac_failed_lessons": planning_output.get("re_trac_memory", {}),
            "validated_steps_count": planning_output.get("validated_steps_count"),
            "evaluator_findings": planning_output.get("evaluator_findings", []),
            "failure_layer": planning_output.get("failure_layer"),
            "failed_action": planning_output.get("failed_action"),
            "checkpoint_env": planning_output.get("checkpoint_env"),
            "checkpoint_robot": planning_output.get("checkpoint_robot"),
        }
    ))
    lines.append("")
    lines.append("## 7. Contract / Sandbox / Audit 逐事件记录")
    lines.append("")
    lines.append(_json_block(sandbox_events))
    lines.append("")
    lines.append("## 8. LLM 全量输入输出")
    lines.append("")
    for index, turn in enumerate(trace.get("llm_io", []) if isinstance(trace.get("llm_io"), list) else [], start=1):
        lines.append(f"### Turn {index}: {turn.get('module', '')}")
        lines.append("")
        lines.append("#### Input")
        lines.append(_json_block(turn.get("input", "")))
        lines.append("")
        lines.append("#### Output")
        output = turn.get("output", "")
        if isinstance(output, str):
            lines.append(_text_block(output))
        else:
            lines.append(_json_block(output))
        lines.append("")
    lines.append("## 9. 初始提示词与后续修复提示")
    lines.append("")
    lines.append("### Understanding 初始提示")
    lines.append(_json_block(understanding_turns[0].get("input", "")) if understanding_turns else "无")
    lines.append("")
    lines.append("### Planning 初始提示")
    lines.append(_json_block(planning_turns[0].get("input", "")) if planning_turns else "无")
    lines.append("")
    lines.append("### Planning 后续修复轮")
    if len(planning_turns) <= 1:
        lines.append("无后续修复轮。")
    else:
        for index, turn in enumerate(planning_turns[1:], start=2):
            lines.append(f"#### Planning Turn {index}")
            lines.append(_json_block(turn.get("input", "")))
            lines.append("")
            output = turn.get("output", "")
            if isinstance(output, str):
                lines.append(_text_block(output))
            else:
                lines.append(_json_block(output))
            lines.append("")


def build_case_report(row: dict[str, Any], *, raw_result_path: Path, config: dict[str, Any]) -> str:
    prediction = _prediction(row)
    trace = _trace(row)
    planning_output = trace.get("planning_output", {}) if isinstance(trace.get("planning_output"), dict) else {}
    title = str(config.get("title", "ReActree Report") or "ReActree Report")
    variant = str(config.get("variant", "") or "")

    lines: list[str] = []
    lines.append(f"# {title}: {row.get('case_id', '')}")
    lines.append("")
    lines.append("## 1. 文件位置")
    lines.append("")
    lines.append(f"- 结果文件：`{raw_result_path}`")
    append_stage_artifact_overview(lines, raw_result_path.parent / "artifacts")
    lines.append("")
    lines.append("## 2. 当前结果摘要")
    lines.append("")

    summary_payload = {
        "case_id": row.get("case_id"),
        "dataset": row.get("dataset"),
        "task_success": prediction.get("task_success"),
        "task_success_rate": prediction.get("task_success_rate"),
        "goal_success_rate": prediction.get("goal_success_rate"),
        "subgoal_success_rate": prediction.get("subgoal_success_rate"),
        "evaluation_mode": prediction.get("evaluation_mode"),
        "official_available": prediction.get("official_available"),
        "execution_success": prediction.get("execution_success"),
        "execution_status": prediction.get("execution_status"),
        "is_feasible": prediction.get("is_feasible"),
        "feedback": prediction.get("feedback"),
        "evaluation_error": prediction.get("evaluation_error"),
        "llm_call_count": prediction.get("llm_call_count"),
        "todo_contract_status": _todo_contract_status(trace),
        "todo_contract_event_count": len(_todo_contract_events(trace)),
    }
    if variant == "alfred":
        summary_payload["terminate_info"] = prediction.get("terminate_info")
        summary_payload["final_world_state_available"] = isinstance(prediction.get("final_world_state"), dict)

    lines.append(_json_block(summary_payload))
    lines.append("")
    _render_common_sections(lines, row, prediction, trace, planning_output)

    lines.append("")
    if variant == "alfred":
        lines.append("## 10. 官方原生动作 / evaluator 桥接调用")
        lines.append("")
        lines.append("### Official Actions")
        lines.append(_json_block(prediction.get("official_actions", [])))
        lines.append("")
        lines.append("### Evaluator Execution Calls")
        lines.append(_json_block(prediction.get("evaluator_execution_calls", [])))
        lines.append("")
        lines.append("### Action Trace")
        lines.append(_json_block(prediction.get("action_trace", [])))
        lines.append("")
        lines.append("### Final World State")
        lines.append(_json_block(prediction.get("final_world_state", {})))
        lines.append("")
    else:
        lines.append("## 10. 官方原生动作 / 官方评测摘要")
        lines.append("")
        lines.append("### Official Actions")
        lines.append(_json_block(prediction.get("official_actions", [])))
        lines.append("")
        lines.append("### Evaluator Execution Calls")
        lines.append(_json_block(prediction.get("evaluator_execution_calls", [])))
        lines.append("")
        lines.append("### Evaluation Summary")
        lines.append(
            _json_block(
                {
                    "goal_success_rate": prediction.get("goal_success_rate"),
                    "subgoal_success_rate": prediction.get("subgoal_success_rate"),
                    "evaluation_mode": prediction.get("evaluation_mode"),
                    "official_available": prediction.get("official_available"),
                    "execution_success": prediction.get("execution_success"),
                    "action_trace": prediction.get("action_trace", []),
                }
            )
        )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_case_report(*, row: dict[str, Any], output_path: str | Path, source_hint: str | Path | None = None, config: dict[str, Any]) -> Path:
    output_path = Path(output_path)
    hint = Path(source_hint) if source_hint is not None else output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_case_report(row, raw_result_path=hint, config=config), encoding="utf-8")
    return output_path


def write_case_report_from_file(*, raw_result_path: str | Path, output_path: str | Path, case_id: str | None = None, config: dict[str, Any]) -> Path:
    raw_result_path = Path(raw_result_path)
    payload = json.loads(raw_result_path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        rows = [payload]
    else:
        raise ValueError(f"{raw_result_path} must contain a result object or result list")
    row: dict[str, Any] | None = None
    if case_id is not None:
        for candidate in rows:
            if str(candidate.get("case_id")) == str(case_id):
                row = candidate
                break
    if row is None:
        if not rows:
            raise ValueError(f"{raw_result_path} contains no result rows")
        row = rows[-1]
    return write_case_report(row=row, output_path=output_path, source_hint=raw_result_path, config=config)
