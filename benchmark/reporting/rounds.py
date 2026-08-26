from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any


_RESUME_RE = re.compile(
    r"(?:仅)?从第\s*(\d+)\s*步开始续写"
    r"|第\s*(\d+)\s*步(?=[^\n。]{0,30}(?:拦截|失败))"
)
_SAFE_LABEL_RE = re.compile(r"[^A-Za-z0-9_.-]+")


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _message_role(message: dict[str, Any]) -> str:
    return str(message.get("type") or message.get("role") or "").strip().lower()


def _render_messages_markdown(messages: list[dict[str, Any]] | Any, *, title: str) -> str:
    lines = [f"# {title}", ""]
    if not isinstance(messages, list):
        lines.append("未记录。")
        return "\n".join(lines).rstrip() + "\n"
    for index, message in enumerate(messages, start=1):
        if not isinstance(message, dict):
            continue
        role = _message_role(message) or "unknown"
        content = str(message.get("content", "") or "")
        lines.append(f"## Message {index}: {role}")
        lines.append("")
        lines.append(content)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _latest_human_prompt(messages: list[dict[str, Any]] | Any) -> str:
    if not isinstance(messages, list):
        return ""
    for message in reversed(messages):
        if isinstance(message, dict) and _message_role(message) in {"human", "user"}:
            return str(message.get("content", "") or "")
    return ""


def _resume_step_from_prompt(prompt: str) -> int | None:
    match = _RESUME_RE.search(str(prompt or ""))
    if not match:
        return None
    try:
        return int(match.group(1) or match.group(2))
    except ValueError:
        return None


def _load_trace_artifact(case_dir: Path, filename: str, default: Any) -> Any:
    path = case_dir / "artifacts" / filename
    if not path.exists():
        return default
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default
    return value


def _safe_label(value: Any, fallback: str = "unknown") -> str:
    label = _SAFE_LABEL_RE.sub("_", str(value or "").strip()).strip("._-")
    return label or fallback


def write_rounds_bundle(case_dir: Path, prediction: dict[str, Any], *, include_rounds: bool = True) -> dict[str, Any]:
    if not include_rounds:
        return {
            "llm_round_count": 0,
            "intercept_count": 0,
            "interceptions_file": "",
            "rounds": [],
            "intercepts": [],
        }

    benchmark_trace = prediction.get("benchmark_trace", {}) if isinstance(prediction, dict) else {}
    if not isinstance(benchmark_trace, dict):
        benchmark_trace = {}
    artifact_llm_io = _load_trace_artifact(case_dir, "llm_io.json", [])
    artifact_planning_output = _load_trace_artifact(case_dir, "planning_output.json", {})
    if not isinstance(benchmark_trace.get("llm_io"), list) and isinstance(artifact_llm_io, list):
        benchmark_trace = {**benchmark_trace, "llm_io": artifact_llm_io}
    if not isinstance(benchmark_trace.get("planning_output_full"), dict) and isinstance(artifact_planning_output, dict):
        benchmark_trace = {**benchmark_trace, "planning_output_full": artifact_planning_output}
    llm_io = benchmark_trace.get("llm_io", []) if isinstance(benchmark_trace, dict) else []
    planning_output = (
        benchmark_trace.get("planning_output_full")
        or benchmark_trace.get("planning_output")
        or {}
    ) if isinstance(benchmark_trace, dict) else {}
    debug_events = planning_output.get("planning_debug_events", []) if isinstance(planning_output, dict) else []
    re_trac = planning_output.get("re_trac_memory", {}) if isinstance(planning_output, dict) else {}
    failed_lessons = re_trac.get("failed_lessons", []) if isinstance(re_trac, dict) else []
    if not isinstance(debug_events, list):
        debug_events = []
    if not isinstance(failed_lessons, list):
        failed_lessons = []

    rounds_dir = case_dir / "artifacts" / "rounds"
    shutil.rmtree(rounds_dir, ignore_errors=True)
    rounds_dir.mkdir(parents=True, exist_ok=True)

    rounds: list[dict[str, Any]] = []
    initial_round: dict[str, Any] | None = None
    repairs: list[dict[str, Any]] = []
    if isinstance(llm_io, list):
        for index, item in enumerate(llm_io, start=1):
            if not isinstance(item, dict):
                continue
            module = str(item.get("module", "") or "unknown").strip().lower()
            process_name = str(item.get("process_name") or module or "unknown").strip().lower()
            prompt_name = str(item.get("prompt_name") or module or "unknown").strip()
            call_stage = str(item.get("call_stage") or "").strip()
            input_messages = item.get("input", [])
            output_text = str(item.get("output", "") or "")
            label = _safe_label(prompt_name, fallback=module)
            input_file = rounds_dir / f"round_{index:02d}_{label}_input.md"
            output_file = rounds_dir / f"round_{index:02d}_{label}_output.txt"
            _write_text(input_file, _render_messages_markdown(input_messages, title=f"Round {index} {prompt_name} Input"))
            _write_text(output_file, output_text)
            latest_human = _latest_human_prompt(input_messages)
            round_record = {
                "round": index,
                "module": module,
                "process_name": process_name,
                "prompt_name": prompt_name,
                "call_stage": call_stage,
                "attempt": item.get("attempt"),
                "planning_iteration": item.get("planning_iteration"),
                "resume_from_step": _resume_step_from_prompt(latest_human),
                "input_file": str(input_file),
                "output_file": str(output_file),
            }
            rounds.append(
                round_record
            )
            if process_name == "planning" and initial_round is None:
                initial_round = dict(round_record)
            elif process_name == "planning":
                repairs.append(
                    {
                        "repair_index": len(repairs) + 1,
                        "resume_from_step": round_record.get("resume_from_step"),
                        "repair_prompt": latest_human,
                        "input_file": str(input_file),
                        "output_file": str(output_file),
                        "prompt_name": prompt_name,
                        "call_stage": call_stage,
                    }
                )

    intercepts: list[dict[str, Any]] = []
    for event in debug_events:
        if not isinstance(event, dict):
            continue
        event_layer = str(event.get("layer", "") or "").lower()
        event_type = str(event.get("type", "") or "").lower()
        is_intercept = (
            (event_layer == "planning_evaluator" and event_type in {"audit_failure", "llm_rejected"})
            or (event_layer == "state_diff_audit" and event_type in {"rejected", "exception"})
            or (event_layer == "todo_contract" and event_type == "rejected")
            or (event_layer == "sandbox" and event_type == "step_check" and event.get("ok") is False)
        )
        if is_intercept:
            result = event.get("result", {}) if isinstance(event.get("result"), dict) else {}
            step_info = event.get("step_info", {}) if isinstance(event.get("step_info"), dict) else {}
            todo_step = event.get("todo_step", {}) if isinstance(event.get("todo_step"), dict) else {}
            if not step_info and todo_step:
                step_info = todo_step
            intercepts.append(
                {
                    "intercept_index": len(intercepts) + 1,
                    "layer": event_layer,
                    "event_type": event_type,
                    "failed_step": event.get("step") if event.get("step") is not None else step_info.get("step"),
                    "action": str(event.get("skill") or step_info.get("action") or ""),
                    "parameters": event.get("parameters") if isinstance(event.get("parameters"), dict) else step_info.get("parameters", {}),
                    "issue": str(result.get("issue") or event.get("issue") or event.get("issue_type") or event.get("type") or ""),
                    "repair_hint": str(result.get("fix_advice") or event.get("fix") or event.get("suggestion") or ""),
                    "raw": json.dumps(event, ensure_ascii=False),
                }
            )

    interceptions_file = rounds_dir / "interceptions.md"
    lines = ["# Interceptions", ""]
    if not intercepts:
        lines.extend(["未记录拦截。", ""])
    else:
        for intercept in intercepts:
            lines.extend(
                [
                    f"## Interception {intercept.get('intercept_index')}",
                    f"- layer: {intercept.get('layer')}",
                    f"- event type: {intercept.get('event_type')}",
                    f"- failed step: {intercept.get('failed_step')}",
                    f"- action: {intercept.get('action')}",
                    f"- parameters: {json.dumps(intercept.get('parameters', {}), ensure_ascii=False)}",
                    f"- issue: {intercept.get('issue')}",
                    f"- repair hint: {intercept.get('repair_hint')}",
                    f"- raw: {intercept.get('raw')}",
                    "",
                ]
            )
    _write_text(interceptions_file, "\n".join(lines).rstrip() + "\n")

    sandbox_intercept_count = sum(
        1
        for ev in debug_events
        if isinstance(ev, dict) and ev.get("layer") == "sandbox" and ev.get("ok") is False
    )
    sda_triggered = any(
        isinstance(ev, dict) and ev.get("layer") == "sda"
        for ev in debug_events
    )
    retrac_triggered = bool(failed_lessons or planning_output.get("re_trac_state"))
    repair_strategy = str(planning_output.get("repair_strategy", "") or "").strip()
    if not repair_strategy:
        for ev in debug_events:
            if isinstance(ev, dict) and ev.get("layer") == "repair_strategy":
                repair_strategy = str(ev.get("strategy", "") or "").strip()
                if repair_strategy:
                    break
    if not repair_strategy:
        repair_strategy = "none"
    state_diff_audit_result = planning_output.get("state_diff_audit", {})
    state_diff_triggered = any(
        isinstance(ev, dict)
        and ev.get("layer") == "state_diff_audit"
        and str(ev.get("type", "")).lower() in {"rejected", "exception"}
        for ev in debug_events
    ) or (
        isinstance(state_diff_audit_result, dict) and state_diff_audit_result.get("passed") is False
    )
    todo_contract_events = [
        ev
        for ev in debug_events
        if isinstance(ev, dict) and str(ev.get("layer", "") or "").lower() == "todo_contract"
    ]
    todo_contract_rejected = any(
        str(ev.get("type", "") or "").lower() == "rejected"
        for ev in todo_contract_events
    )
    todo_contract_passed = any(
        str(ev.get("type", "") or "").lower() == "passed"
        for ev in todo_contract_events
    )
    if todo_contract_rejected:
        todo_contract_status = "rejected"
    elif todo_contract_passed:
        todo_contract_status = "passed"
    else:
        todo_contract_status = "not_recorded"

    feature_summary = {
        "repair_strategy": repair_strategy,
        "todo_contract_status": todo_contract_status,
        "todo_contract_event_count": len(todo_contract_events),
        "sandbox_intercepted": sandbox_intercept_count > 0,
        "sandbox_intercept_count": sandbox_intercept_count,
        "sda_triggered": sda_triggered,
        "retrac_triggered": retrac_triggered,
        "state_diff_audit_triggered": state_diff_triggered,
    }
    terminal_failure = ""
    if isinstance(planning_output, dict) and (
        planning_output.get("is_feasible") is False
        or str(planning_output.get("execution_status", "") or "").strip().lower() == "failed"
    ):
        terminal_failure = str(planning_output.get("feedback", "") or planning_output.get("error_feedback", "") or "").strip()

    summary = {
        "llm_round_count": len(rounds),
        "intercept_count": len(intercepts),
        "interceptions_file": str(interceptions_file),
        "initial_round": initial_round,
        "feature_summary": feature_summary,
        "rounds": rounds,
        "intercepts": intercepts,
        "repairs": repairs,
        "terminal_failure": terminal_failure,
    }
    _write_json(rounds_dir / "rounds_index.json", summary)
    return summary
