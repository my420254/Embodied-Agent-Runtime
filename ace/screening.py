from __future__ import annotations

import copy
from typing import Any

from ace.schema import now_iso, safe_section
from ace.storage import load_section_playbook_unlocked, playbook_lock, save_section_playbook_unlocked


SUCCESS_STATUSES = {"success", "succeeded", "completed", "fully_completed", "ok", "passed"}
FAILURE_STATUSES = {"failed", "failure", "error", "timeout"}


def _nested_get(data, *keys):
    cur = data
    for key in keys:
        if isinstance(cur, dict):
            cur = cur.get(key)
        elif isinstance(cur, list) and isinstance(key, int) and 0 <= key < len(cur):
            cur = cur[key]
        else:
            return None
    return cur


def extract_run_metrics(payload: dict[str, Any] | None) -> dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {}
    prediction = payload.get("prediction") if isinstance(payload.get("prediction"), dict) else {}

    success = payload.get("success")
    if success is None:
        success = prediction.get("success")

    status = (
        payload.get("execution_status")
        or prediction.get("execution_status")
        or payload.get("status")
        or prediction.get("status")
        or ""
    )
    status_text = str(status).lower()

    if success is None and status_text:
        if status_text in SUCCESS_STATUSES:
            success = True
        elif status_text in FAILURE_STATUSES:
            success = False
    success = bool(success)

    failed_step = (
        payload.get("failed_step")
        or prediction.get("failed_step")
        or _nested_get(prediction, "evaluator_findings", 0, "failed_step")
    )
    completed_steps = payload.get("completed_steps") or prediction.get("completed_steps")
    retry_count = payload.get("retry_count") or prediction.get("retry_count") or 0
    sandbox_failures = payload.get("sandbox_failures") or prediction.get("sandbox_failures") or 0

    return {
        "success": success,
        "failed_step": int(failed_step or 0),
        "completed_steps": int(completed_steps or 0),
        "retry_count": int(retry_count or 0),
        "sandbox_failures": int(sandbox_failures or 0),
        "raw_status": status,
    }


def score_metrics(metrics: dict[str, Any]) -> int:
    progress = max(metrics.get("failed_step", 0), metrics.get("completed_steps", 0))
    return (
        (1_000_000 if metrics.get("success") else 0)
        + (int(progress or 0) * 100)
        - (int(metrics.get("retry_count", 0) or 0) * 10)
        - (int(metrics.get("sandbox_failures", 0) or 0) * 20)
    )


def classify_comparison(record: dict[str, Any]) -> str:
    baseline = extract_run_metrics(record.get("without_rule") or record.get("baseline"))
    candidate = extract_run_metrics(record.get("with_rule") or record.get("candidate"))

    if not baseline["success"] and candidate["success"]:
        return "helpful"
    if baseline["success"] and not candidate["success"]:
        return "harmful"

    baseline_score = score_metrics(baseline)
    candidate_score = score_metrics(candidate)
    if candidate_score > baseline_score:
        return "helpful"
    if candidate_score < baseline_score:
        return "harmful"
    return "neutral"


def build_counterexample(record: dict[str, Any], outcome: str) -> dict[str, Any]:
    return {
        "case_id": record.get("case_id", ""),
        "outcome": outcome,
        "reason": record.get("reason", "candidate rule performed worse than baseline"),
        "without_rule": copy.deepcopy(record.get("without_rule") or record.get("baseline") or {}),
        "with_rule": copy.deepcopy(record.get("with_rule") or record.get("candidate") or {}),
    }


def apply_screening_records(
    section: str,
    records: list[dict[str, Any]],
    *,
    promote_helpful_threshold: int = 3,
    max_harmful_for_promotion: int = 0,
    deprecate_harmful_threshold: int = 1,
) -> dict[str, int]:
    section = safe_section(section)
    summary = {
        "processed": 0,
        "helpful": 0,
        "harmful": 0,
        "neutral": 0,
        "promoted": 0,
        "deprecated": 0,
        "missing_rule": 0,
    }
    now = now_iso()

    with playbook_lock(section):
        data = load_section_playbook_unlocked(section)
        by_id = {rule.get("id"): rule for rule in data.get("rules", []) if rule.get("id")}

        for record in records:
            rule_id = record.get("rule_id")
            rule = by_id.get(rule_id)
            if not rule:
                summary["missing_rule"] += 1
                continue

            outcome = classify_comparison(record)
            summary["processed"] += 1
            summary[outcome] += 1

            if outcome == "helpful":
                rule["helpful_count"] = int(rule.get("helpful_count", 0) or 0) + 1
            elif outcome == "harmful":
                rule["harmful_count"] = int(rule.get("harmful_count", 0) or 0) + 1
                rule.setdefault("counterexamples", []).append(build_counterexample(record, outcome))
            else:
                rule["neutral_count"] = int(rule.get("neutral_count", 0) or 0) + 1

            helpful = int(rule.get("helpful_count", 0) or 0)
            harmful = int(rule.get("harmful_count", 0) or 0)
            status = rule.get("status", "promoted")

            if status == "candidate" and helpful >= promote_helpful_threshold and harmful <= max_harmful_for_promotion:
                rule["status"] = "promoted"
                summary["promoted"] += 1
            elif status == "candidate" and helpful == 0 and harmful >= deprecate_harmful_threshold:
                rule["status"] = "deprecated"
                rule["deprecated"] = True
                rule["deprecated_reason"] = "counterexample screening failed"
                summary["deprecated"] += 1

            rule["updated_at"] = now

        save_section_playbook_unlocked(section, data)

    return summary
