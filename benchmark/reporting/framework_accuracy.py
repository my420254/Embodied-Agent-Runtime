from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]

FRAMEWORKS: dict[str, dict[str, str]] = {
    "delta": {
        "label": "DELTA",
        "kind": "delta",
        "results_root": "benchmark/delta/framework/results",
        "launch_config": "benchmark/delta/framework/code/config/launch_config.json",
    },
    "eai_behavior": {
        "label": "EAI BEHAVIOR",
        "kind": "eai",
        "results_root": "benchmark/eai/behavior/framework/results",
        "launch_config": "benchmark/eai/behavior/framework/code/config/launch_config.json",
    },
    "eai_virtualhome": {
        "label": "EAI VirtualHome",
        "kind": "eai",
        "results_root": "benchmark/eai/virtualhome/framework/results",
        "launch_config": "benchmark/eai/virtualhome/framework/code/config/launch_config.json",
    },
    "reactree_wah": {
        "label": "ReActree WAH",
        "kind": "reactree",
        "results_root": "benchmark/reactree/wah/framework/results",
        "launch_config": "benchmark/reactree/wah/framework/code/config/launch_config.json",
    },
    "reactree_alfred": {
        "label": "ReActree ALFRED",
        "kind": "reactree",
        "results_root": "benchmark/reactree/alfred/framework/results",
        "launch_config": "benchmark/reactree/alfred/framework/code/config/launch_config.json",
    },
}


def _read_json(path: Path, fallback: Any = None) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _resolve_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def _safe_float(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        text = str(value).strip()
        return float(text) if text else default
    except Exception:
        return default


def _rate_to_fraction(value: Any) -> float | None:
    if value is None:
        return None
    numeric = _safe_float(value, default=float("nan"))
    if numeric != numeric:
        return None
    if numeric > 1.0:
        numeric = numeric / 100.0
    if numeric < 0.0:
        return 0.0
    return min(1.0, numeric)


def _percent(numerator: float, denominator: float) -> float | None:
    if denominator <= 0:
        return None
    return numerator / denominator * 100.0


def _round_rate(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


def _format_percent(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.2f}%"


def _counter_increment(counter: dict[str, int], key: Any) -> None:
    label = str(key or "unknown")
    counter[label] = counter.get(label, 0) + 1


def _status_counts(worker_results: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in worker_results:
        status = str(item.get("status") or "")
        if not status and isinstance(item.get("row"), dict):
            status = "failed" if item["row"].get("error") else "done"
        _counter_increment(counts, status or "unknown")
    return counts


def _row_payload(worker_result: dict[str, Any]) -> dict[str, Any]:
    row = worker_result.get("row", {})
    return row if isinstance(row, dict) else {}


def _prediction(row: dict[str, Any]) -> dict[str, Any]:
    prediction = row.get("prediction", {})
    return prediction if isinstance(prediction, dict) else {}


def _worker_results(run_root: Path) -> list[dict[str, Any]]:
    payload = _read_json(run_root / "merged_results.json", [])
    if isinstance(payload, list) and payload:
        return [item for item in payload if isinstance(item, dict)]
    cases_root = run_root / "cases"
    loaded: list[dict[str, Any]] = []
    if cases_root.exists():
        for result_path in sorted(cases_root.glob("*/worker_result.json")):
            result = _read_json(result_path, {})
            if isinstance(result, dict) and result:
                loaded.append(result)
    if loaded:
        return loaded
    return []


def _launch_config(dataset_key: str) -> dict[str, Any]:
    config_path = FRAMEWORKS.get(dataset_key, {}).get("launch_config")
    if not config_path:
        return {}
    loaded = _read_json(_resolve_path(config_path), {})
    return loaded if isinstance(loaded, dict) else {}


def _expected_count(dataset_key: str) -> int | None:
    defaults = _launch_config(dataset_key).get("defaults", {})
    if not isinstance(defaults, dict):
        return None
    value = defaults.get("expected_count")
    try:
        return int(value) if value is not None else None
    except Exception:
        return None


def _launch_manifest(run_root: Path) -> dict[str, Any]:
    manifest = _read_json(run_root / "launch_manifest.json", {})
    return manifest if isinstance(manifest, dict) else {}


def _rate_sum(percent: Any, count: int) -> float:
    value = _safe_float(percent, 0.0)
    return value / 100.0 * float(max(0, count))


def _add_expected_metadata(dataset_key: str, run_root: Path, summary: dict[str, Any]) -> dict[str, Any]:
    expected = _expected_count(dataset_key)
    manifest = _launch_manifest(run_root)
    scheduled_command_count = manifest.get("scheduled_command_count")
    if not isinstance(scheduled_command_count, int) and isinstance(manifest.get("commands"), list):
        scheduled_command_count = len(manifest["commands"])
    observed = int(summary.get("case_count", 0) or 0)
    summary["expected_count"] = expected
    summary["coverage_vs_expected_percent"] = _round_rate(_percent(observed, expected or 0))
    summary["missing_expected_case_count"] = max(0, int(expected) - observed) if expected is not None else None
    summary["launch_manifest"] = {
        "status": manifest.get("status"),
        "selected_case_count": manifest.get("selected_case_count"),
        "resumed_case_count": manifest.get("resumed_case_count"),
        "scheduled_command_count": scheduled_command_count,
        "result_count": manifest.get("result_count"),
        "result_status_counts": manifest.get("result_status_counts", {}),
    }
    source_files = summary.setdefault("source_files", {})
    if isinstance(source_files, dict):
        source_files["launch_manifest_json"] = str(run_root / "launch_manifest.json")
    if expected is None or expected <= 0:
        return summary

    all_samples = summary.get("all_samples", {}) if isinstance(summary.get("all_samples"), dict) else {}
    kind = summary.get("kind")
    adjusted: dict[str, Any] = {
        "case_count": expected,
        "observed_case_count": observed,
        "coverage_percent": _round_rate(_percent(observed, expected)),
    }
    if kind == "delta":
        task_success_count = int(all_samples.get("task_success_count", 0) or 0)
        adjusted.update(
            {
                "metric": "task_success_missing_cases_count_as_zero",
                "task_success_count": task_success_count,
                "task_success_rate_percent": _round_rate(_percent(task_success_count, expected)),
            }
        )
    elif kind == "eai":
        rate_sum = _rate_sum(all_samples.get("task_success_rate_percent"), observed)
        task_success_count = int(all_samples.get("task_success_count", 0) or 0)
        adjusted.update(
            {
                "metric": "task_success_rate_missing_cases_count_as_zero",
                "task_success_count": task_success_count,
                "task_success_rate_percent": _round_rate(_percent(rate_sum, expected)),
                "task_success_case_rate_percent": _round_rate(_percent(task_success_count, expected)),
            }
        )
    elif kind == "reactree":
        gsr_sum = _rate_sum(all_samples.get("gsr_percent"), observed)
        ssr_sum = _rate_sum(all_samples.get("ssr_percent"), observed)
        task_success_count = int(all_samples.get("task_success_count", 0) or 0)
        adjusted.update(
            {
                "metric": "GSR/SSR_missing_cases_count_as_zero",
                "task_success_count": task_success_count,
                "task_success_rate_percent": _round_rate(_percent(task_success_count, expected)),
                "gsr_percent": _round_rate(_percent(gsr_sum, expected)),
                "ssr_percent": _round_rate(_percent(ssr_sum, expected)),
            }
        )
    if len(adjusted) > 3:
        summary["expected_adjusted"] = adjusted
    return summary


def _latest_run_root(results_root: Path) -> Path | None:
    if not results_root.exists():
        return None
    candidates = []
    for path in results_root.iterdir():
        if not path.is_dir():
            continue
        if (path / "summary.json").exists() or (path / "merged_results.json").exists() or (path / "cases").exists():
            candidates.append(path)
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _load_eai_cases(run_root: Path) -> list[dict[str, Any]]:
    summary = _read_json(run_root / "summary.json", {})
    cases = summary.get("cases", []) if isinstance(summary, dict) else []
    if isinstance(cases, list) and cases:
        return [case for case in cases if isinstance(case, dict)]

    cases_root = run_root / "cases"
    loaded: list[dict[str, Any]] = []
    if cases_root.exists():
        for meta_path in sorted(cases_root.glob("*/case.json")):
            meta = _read_json(meta_path, {})
            if isinstance(meta, dict) and meta:
                loaded.append(meta)
    return loaded


def _eai_task_success_rate(case: dict[str, Any]) -> float | None:
    direct = _rate_to_fraction(case.get("task_success_rate"))
    if direct is not None:
        return direct
    summary = case.get("evaluation_summary", {})
    if isinstance(summary, dict):
        goal_eval = summary.get("goal_evaluation", {})
        if isinstance(goal_eval, dict):
            return _rate_to_fraction(goal_eval.get("task_success_rate"))
    return None


def _status_counts_from_cases(cases: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for case in cases:
        _counter_increment(counts, case.get("status") or "unknown")
    return counts


def _contract_status_counts(run_root: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    cases_root = run_root / "cases"
    if not cases_root.exists():
        return counts
    for audit_path in sorted(cases_root.glob("*/artifacts/contract_audit.json")):
        audit = _read_json(audit_path, {})
        status = "missing"
        if isinstance(audit, dict):
            status = str(audit.get("status") or "missing")
        _counter_increment(counts, status)
    return counts


def summarize_eai_framework_run(dataset_key: str, run_root: Path) -> dict[str, Any]:
    cases = _load_eai_cases(run_root)
    total = len(cases)
    available_rates: list[float] = []
    all_sample_rate_sum = 0.0
    task_success_count = 0
    for case in cases:
        rate = _eai_task_success_rate(case)
        if rate is not None:
            available_rates.append(rate)
            all_sample_rate_sum += rate
            if rate >= 0.999999:
                task_success_count += 1

    official_count = len(available_rates)
    official_rate_sum = sum(available_rates)
    summary = {
        "dataset": dataset_key,
        "label": FRAMEWORKS[dataset_key]["label"],
        "kind": "eai",
        "run_root": str(run_root),
        "run_name": run_root.name,
        "source_files": {
            "summary_json": str(run_root / "summary.json"),
            "case_json_glob": str(run_root / "cases" / "*" / "case.json"),
        },
        "case_count": total,
        "status_counts": _status_counts_from_cases(cases),
        "contract_status_counts": _contract_status_counts(run_root),
        "all_samples": {
            "metric": "task_success_rate",
            "case_count": total,
            "task_success_count": task_success_count,
            "task_success_rate_percent": _round_rate(_percent(all_sample_rate_sum, total)),
            "task_success_case_rate_percent": _round_rate(_percent(task_success_count, total)),
        },
        "official_available_subset": {
            "metric": "official_task_success_rate",
            "case_count": official_count,
            "task_success_count": task_success_count,
            "coverage_percent": _round_rate(_percent(official_count, total)),
            "task_success_rate_percent": _round_rate(_percent(official_rate_sum, official_count)),
            "task_success_case_rate_percent": _round_rate(_percent(task_success_count, official_count)),
        },
        "missing_official_eval_count": total - official_count,
    }
    return summary


def summarize_delta_framework_run(dataset_key: str, run_root: Path) -> dict[str, Any]:
    worker_results = _worker_results(run_root)
    total = len(worker_results)
    task_success_count = 0
    official_available_count = 0
    official_task_success_count = 0
    symbolic_success_count = 0
    route_counts: dict[str, int] = {}
    by_domain: dict[str, dict[str, int]] = {}

    for worker_result in worker_results:
        row = _row_payload(worker_result)
        prediction = _prediction(row)
        task_success = bool(prediction.get("task_success"))
        if task_success:
            task_success_count += 1
        if bool(prediction.get("symbolic_success")):
            symbolic_success_count += 1
        if prediction:
            _counter_increment(route_counts, prediction.get("evaluation_route") or "missing_evaluation_route")
        domain = str(row.get("metadata", {}).get("domain", "unknown")) if isinstance(row.get("metadata"), dict) else "unknown"
        domain_bucket = by_domain.setdefault(
            domain,
            {
                "count": 0,
                "task_success_count": 0,
                "official_available_count": 0,
                "official_task_success_count": 0,
                "symbolic_success_count": 0,
            },
        )
        domain_bucket["count"] += 1
        if task_success:
            domain_bucket["task_success_count"] += 1
        if bool(prediction.get("symbolic_success")):
            domain_bucket["symbolic_success_count"] += 1
        if bool(prediction.get("official_available")):
            official_available_count += 1
            domain_bucket["official_available_count"] += 1
            if task_success:
                official_task_success_count += 1
                domain_bucket["official_task_success_count"] += 1

    domains: dict[str, Any] = {}
    for domain, bucket in sorted(by_domain.items()):
        official_count = bucket["official_available_count"]
        domains[domain] = {
            **bucket,
            "task_success_rate_percent": _round_rate(_percent(bucket["task_success_count"], bucket["count"])),
            "official_task_success_rate_percent": _round_rate(
                _percent(bucket["official_task_success_count"], official_count)
            ),
            "symbolic_success_rate_percent": _round_rate(_percent(bucket["symbolic_success_count"], bucket["count"])),
        }

    return {
        "dataset": dataset_key,
        "label": FRAMEWORKS[dataset_key]["label"],
        "kind": "delta",
        "run_root": str(run_root),
        "run_name": run_root.name,
        "source_files": {
            "summary_json": str(run_root / "summary.json"),
            "merged_results_json": str(run_root / "merged_results.json"),
        },
        "case_count": total,
        "status_counts": _status_counts(worker_results),
        "contract_status_counts": _contract_status_counts(run_root),
        "all_samples": {
            "metric": "task_success",
            "case_count": total,
            "task_success_count": task_success_count,
            "task_success_rate_percent": _round_rate(_percent(task_success_count, total)),
            "symbolic_success_count": symbolic_success_count,
            "symbolic_success_rate_percent": _round_rate(_percent(symbolic_success_count, total)),
        },
        "official_available_subset": {
            "metric": "official_VAL_task_success",
            "case_count": official_available_count,
            "task_success_count": official_task_success_count,
            "coverage_percent": _round_rate(_percent(official_available_count, total)),
            "task_success_rate_percent": _round_rate(
                _percent(official_task_success_count, official_available_count)
            ),
        },
        "evaluation_route_counts": route_counts,
        "domains": domains,
    }


def _reactree_official_available(prediction: dict[str, Any]) -> bool:
    return prediction.get("official_available") is True


def summarize_reactree_framework_run(dataset_key: str, run_root: Path) -> dict[str, Any]:
    worker_results = _worker_results(run_root)
    total = len(worker_results)
    all_gsr_sum = 0.0
    all_ssr_sum = 0.0
    official_gsr_sum = 0.0
    official_ssr_sum = 0.0
    official_count = 0
    task_success_count = 0
    official_task_success_count = 0
    modes: dict[str, int] = {}

    for worker_result in worker_results:
        row = _row_payload(worker_result)
        prediction = _prediction(row)
        gsr = _safe_float(prediction.get("goal_success_rate"), 0.0)
        ssr = _safe_float(prediction.get("subgoal_success_rate"), 0.0)
        all_gsr_sum += gsr
        all_ssr_sum += ssr
        if gsr >= 0.999999:
            task_success_count += 1
        _counter_increment(modes, prediction.get("evaluation_mode") if prediction else "missing_prediction")
        if _reactree_official_available(prediction):
            official_count += 1
            official_gsr_sum += gsr
            official_ssr_sum += ssr
            if gsr >= 0.999999:
                official_task_success_count += 1

    return {
        "dataset": dataset_key,
        "label": FRAMEWORKS[dataset_key]["label"],
        "kind": "reactree",
        "run_root": str(run_root),
        "run_name": run_root.name,
        "source_files": {
            "summary_json": str(run_root / "summary.json"),
            "merged_results_json": str(run_root / "merged_results.json"),
        },
        "case_count": total,
        "status_counts": _status_counts(worker_results),
        "contract_status_counts": _contract_status_counts(run_root),
        "all_samples": {
            "metric": "GSR/SSR",
            "case_count": total,
            "task_success_count": task_success_count,
            "task_success_rate_percent": _round_rate(_percent(task_success_count, total)),
            "gsr_percent": _round_rate(_percent(all_gsr_sum, total)),
            "ssr_percent": _round_rate(_percent(all_ssr_sum, total)),
        },
        "official_available_subset": {
            "metric": "official_GSR/SSR",
            "case_count": official_count,
            "task_success_count": official_task_success_count,
            "coverage_percent": _round_rate(_percent(official_count, total)),
            "task_success_rate_percent": _round_rate(_percent(official_task_success_count, official_count)),
            "gsr_percent": _round_rate(_percent(official_gsr_sum, official_count)),
            "ssr_percent": _round_rate(_percent(official_ssr_sum, official_count)),
        },
        "evaluation_modes": modes,
    }


def summarize_framework_run(dataset_key: str, run_root: str | Path) -> dict[str, Any]:
    if dataset_key not in FRAMEWORKS:
        raise ValueError(f"unknown framework dataset: {dataset_key}")
    resolved = _resolve_path(run_root)
    kind = FRAMEWORKS[dataset_key]["kind"]
    if kind == "delta":
        return _add_expected_metadata(dataset_key, resolved, summarize_delta_framework_run(dataset_key, resolved))
    if kind == "eai":
        return _add_expected_metadata(dataset_key, resolved, summarize_eai_framework_run(dataset_key, resolved))
    if kind == "reactree":
        return _add_expected_metadata(dataset_key, resolved, summarize_reactree_framework_run(dataset_key, resolved))
    raise ValueError(f"unsupported framework kind: {kind}")


def resolve_framework_run_roots(overrides: dict[str, str | Path] | None = None, *, auto_latest: bool = True) -> dict[str, Path]:
    overrides = overrides or {}
    roots: dict[str, Path] = {}
    for dataset_key, config in FRAMEWORKS.items():
        if dataset_key in overrides and str(overrides[dataset_key]).strip():
            roots[dataset_key] = _resolve_path(overrides[dataset_key])
            continue
        if not auto_latest:
            continue
        latest = _latest_run_root(_resolve_path(config["results_root"]))
        if latest is not None:
            roots[dataset_key] = latest
    return roots


def summarize_framework_runs(
    run_roots: dict[str, str | Path] | None = None,
    *,
    auto_latest: bool = True,
) -> dict[str, Any]:
    resolved = resolve_framework_run_roots(run_roots, auto_latest=auto_latest)
    datasets: dict[str, Any] = {}
    missing: list[str] = []
    for dataset_key in FRAMEWORKS:
        run_root = resolved.get(dataset_key)
        if run_root is None:
            missing.append(dataset_key)
            continue
        datasets[dataset_key] = summarize_framework_run(dataset_key, run_root)
    return {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S %z"),
        "datasets": datasets,
        "missing_datasets": missing,
    }


def _all_sample_metric_text(summary: dict[str, Any]) -> str:
    all_samples = summary.get("all_samples", {})
    kind = summary.get("kind")
    if kind == "reactree":
        return f"GSR {_format_percent(all_samples.get('gsr_percent'))}, SSR {_format_percent(all_samples.get('ssr_percent'))}"
    if kind in {"delta", "eai"}:
        return _format_percent(all_samples.get("task_success_rate_percent"))
    return "n/a"


def _official_metric_text(summary: dict[str, Any]) -> str:
    official = summary.get("official_available_subset", {})
    kind = summary.get("kind")
    if kind == "reactree":
        return f"GSR {_format_percent(official.get('gsr_percent'))}, SSR {_format_percent(official.get('ssr_percent'))}"
    if kind in {"delta", "eai"}:
        return _format_percent(official.get("task_success_rate_percent"))
    return "n/a"


def _expected_adjusted_text(summary: dict[str, Any]) -> str:
    adjusted = summary.get("expected_adjusted", {})
    if not isinstance(adjusted, dict):
        return "n/a"
    kind = summary.get("kind")
    if kind == "reactree":
        return f"GSR {_format_percent(adjusted.get('gsr_percent'))}, SSR {_format_percent(adjusted.get('ssr_percent'))}"
    if kind in {"delta", "eai"}:
        return _format_percent(adjusted.get("task_success_rate_percent"))
    return "n/a"


def _counts_text(counts: dict[str, int]) -> str:
    if not counts:
        return ""
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def render_framework_accuracy_markdown(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Framework Accuracy Report")
    lines.append("")
    lines.append(f"- Generated at: `{payload.get('generated_at', '')}`")
    if payload.get("missing_datasets"):
        lines.append(f"- Missing datasets: `{', '.join(payload['missing_datasets'])}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(
        "| Dataset | Run | Cases | Status | All samples | Expected-adjusted | Official available | Official subset |"
    )
    lines.append("| --- | --- | ---: | --- | ---: | ---: | ---: | ---: |")
    for dataset_key, summary in payload.get("datasets", {}).items():
        official = summary.get("official_available_subset", {})
        coverage = _format_percent(official.get("coverage_percent"))
        official_cases = official.get("case_count", 0)
        expected = summary.get("expected_count")
        case_text = str(summary.get("case_count", 0))
        if expected is not None:
            case_text = f"{summary.get('case_count', 0)}/{expected} ({_format_percent(summary.get('coverage_vs_expected_percent'))})"
        lines.append(
            "| "
            + " | ".join(
                [
                    str(summary.get("label") or dataset_key),
                    f"`{summary.get('run_name', '')}`",
                    case_text,
                    _counts_text(summary.get("status_counts", {})),
                    _all_sample_metric_text(summary),
                    _expected_adjusted_text(summary),
                    f"{official_cases} ({coverage})",
                    _official_metric_text(summary),
                ]
            )
            + " |"
        )
    lines.append("")
    lines.append("## Metric Rules")
    lines.append("")
    lines.append("- DELTA task success is `prediction.task_success`, derived only from VAL `prediction.val_success` when `prediction.official_available=true`; symbolic success is diagnostic only.")
    lines.append("- EAI task success uses official evaluator `goal_evaluation.task_success_rate` copied into `case.json.task_success_rate`; missing evaluator output counts as zero in all-sample rate.")
    lines.append("- ReActree task success is `goal_success_rate == 1.0`; GSR/SSR remain separate coverage diagnostics. Rows without `official_available=true` count as zero in all-sample GSR/SSR and are excluded from official subset.")
    lines.append("- Expected-adjusted metrics use the configured full-run expected count as denominator and count missing cases as zero.")
    lines.append("")
    lines.append("## Details")
    for dataset_key, summary in payload.get("datasets", {}).items():
        lines.append("")
        lines.append(f"### {summary.get('label') or dataset_key}")
        lines.append("")
        lines.append(f"- Run root: `{summary.get('run_root', '')}`")
        if summary.get("expected_count") is not None:
            lines.append(
                f"- Expected coverage: `{summary.get('case_count', 0)}/{summary.get('expected_count')} "
                f"({_format_percent(summary.get('coverage_vs_expected_percent'))})`"
            )
            if summary.get("missing_expected_case_count"):
                lines.append(f"- Missing expected cases: `{summary.get('missing_expected_case_count')}`")
        manifest = summary.get("launch_manifest", {})
        if isinstance(manifest, dict) and manifest.get("status"):
            lines.append(
                "- Launch manifest: "
                f"`status={manifest.get('status')}, selected={manifest.get('selected_case_count')}, "
                f"scheduled={manifest.get('scheduled_command_count')}, result_count={manifest.get('result_count')}`"
            )
        lines.append(f"- Status counts: `{_counts_text(summary.get('status_counts', {}))}`")
        lines.append(f"- Contract status counts: `{_counts_text(summary.get('contract_status_counts', {}))}`")
        if summary.get("kind") == "delta":
            lines.append(f"- Evaluation route counts: `{_counts_text(summary.get('evaluation_route_counts', {}))}`")
            domains = summary.get("domains", {})
            if domains:
                lines.append("")
                lines.append("| Domain | Cases | Task success | Official cases | Official task success | Symbolic success |")
                lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
                for domain, item in domains.items():
                    lines.append(
                        f"| {domain} | {item.get('count', 0)} | "
                        f"{_format_percent(item.get('task_success_rate_percent'))} | "
                        f"{item.get('official_available_count', 0)} | "
                        f"{_format_percent(item.get('official_task_success_rate_percent'))} | "
                        f"{_format_percent(item.get('symbolic_success_rate_percent'))} |"
                    )
        if summary.get("kind") == "reactree":
            lines.append(f"- Evaluation modes: `{_counts_text(summary.get('evaluation_modes', {}))}`")
        if summary.get("kind") == "eai":
            lines.append(f"- Missing official evaluator outputs: `{summary.get('missing_official_eval_count', 0)}`")
    lines.append("")
    return "\n".join(lines)


def _parse_run_overrides(args: argparse.Namespace) -> dict[str, str]:
    overrides = {
        "delta": args.delta_run,
        "eai_behavior": args.eai_behavior_run,
        "eai_virtualhome": args.eai_virtualhome_run,
        "reactree_wah": args.reactree_wah_run,
        "reactree_alfred": args.reactree_alfred_run,
    }
    for item in args.run or []:
        if "=" not in item:
            raise SystemExit(f"--run must be DATASET=PATH, got: {item}")
        dataset_key, path = item.split("=", 1)
        dataset_key = dataset_key.strip()
        if dataset_key not in FRAMEWORKS:
            raise SystemExit(f"unknown dataset for --run: {dataset_key}")
        overrides[dataset_key] = path.strip()
    return {key: value for key, value in overrides.items() if str(value or "").strip()}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize framework accuracy from structured benchmark results.")
    parser.add_argument("--run", action="append", default=[], help="Override one run root as DATASET=PATH.")
    parser.add_argument("--delta-run", default="")
    parser.add_argument("--eai-behavior-run", default="")
    parser.add_argument("--eai-virtualhome-run", default="")
    parser.add_argument("--reactree-wah-run", default="")
    parser.add_argument("--reactree-alfred-run", default="")
    parser.add_argument("--no-auto-latest", action="store_true", help="Only summarize explicitly provided run roots.")
    parser.add_argument("--output-md", default="benchmark/framework_accuracy_report.md")
    parser.add_argument("--output-json", default="")
    parser.add_argument("--print-json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_md = _resolve_path(args.output_md)
    output_json = _resolve_path(args.output_json) if args.output_json else output_md.with_suffix(".json")
    payload = summarize_framework_runs(_parse_run_overrides(args), auto_latest=not bool(args.no_auto_latest))
    markdown = render_framework_accuracy_markdown(payload)
    _write_json(output_json, payload)
    _write_text(output_md, markdown)
    if args.print_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(str(output_md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
