from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


CONTEXT_FIELDS = (
    "anchor_variant",
    "baseline_output_source",
    "eval_type",
    "input_dataset",
    "model_label",
    "scene_id",
)
CONTEXT_GROUP_FIELDS = ("anchor_variant", "baseline_output_source", "model_label")


def _load_artifacts(paths: list[str | Path]) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for path in paths:
        source = Path(path)
        loaded = json.loads(source.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            loaded = dict(loaded)
            loaded["source_path"] = str(source)
            artifacts.append(loaded)
    return sorted(artifacts, key=lambda item: (str(item.get("dataset", "")), str(item.get("source_path", ""))))


def _int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _rate(numerator: int | float, denominator: int | float) -> float:
    return (float(numerator) / float(denominator)) if denominator else 0.0


def _ordered_union(values: list[Any]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value)
        if text and text not in seen:
            ordered.append(text)
            seen.add(text)
    return ordered


def _counter_add(target: dict[str, int], source: Any) -> None:
    if not isinstance(source, dict):
        return
    for key, value in source.items():
        target[str(key)] = target.get(str(key), 0) + _int(value)


def _artifact_index(artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for artifact in artifacts:
        total = _int(artifact.get("total_case_count"))
        supported = _int(artifact.get("supported_case_count"))
        rows.append(
            {
                "source_path": str(artifact.get("source_path", "")),
                "dataset": artifact.get("dataset"),
                "input_dataset": artifact.get("input_dataset"),
                "eval_type": artifact.get("eval_type"),
                "scene_id": artifact.get("scene_id"),
                "model_label": artifact.get("model_label"),
                "runner_output_path": artifact.get("runner_output_path"),
                "variant": artifact.get("variant"),
                "variants": list(artifact.get("variants", []) or []),
                "variant_count": _int(artifact.get("variant_count")),
                "anchor_variant": artifact.get("anchor_variant"),
                "baseline_output_source": artifact.get("baseline_output_source"),
                "total_case_count": total,
                "supported_case_count": supported,
                "unsupported_case_count": _int(artifact.get("unsupported_case_count")),
                "support_coverage_rate": _rate(supported, total),
            }
        )
    return rows


def _variant_names(artifacts: list[dict[str, Any]]) -> list[str]:
    names: list[Any] = []
    for artifact in artifacts:
        names.extend(artifact.get("variants", []) or [])
        summary = artifact.get("summary", {})
        if isinstance(summary, dict):
            names.extend(summary.keys())
    return _ordered_union(names)


def _aggregate_route_metrics(route_metrics: list[dict[str, Any]]) -> dict[str, Any]:
    total_cases = sum(_int(metric.get("case_count")) for metric in route_metrics)
    result: dict[str, Any] = {"case_count": total_cases}
    metric_names = sorted(
        {
            str(key)
            for metric in route_metrics
            for key in metric
            if key != "case_count" and isinstance(metric, dict)
        }
    )
    for name in metric_names:
        result[name] = _rate(
            sum(_float(metric.get(name)) * _int(metric.get("case_count")) for metric in route_metrics),
            total_cases,
        )
    return result


def _aggregate_summary(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for variant in _variant_names(artifacts):
        rows = [
            artifact.get("summary", {}).get(variant, {})
            for artifact in artifacts
            if isinstance(artifact.get("summary"), dict) and isinstance(artifact.get("summary", {}).get(variant), dict)
        ]
        total_cases = sum(_int(row.get("case_count")) for row in rows)
        variant_payload: dict[str, Any] = {
            "variant": variant,
            "case_count": total_cases,
        }
        for metric in ("planning_legal_rate", "sandbox_pass_rate", "task_success_rate", "avg_latency_ms"):
            variant_payload[metric] = _rate(
                sum(_float(row.get(metric)) * _int(row.get("case_count")) for row in rows),
                total_cases,
            )

        route_counts: dict[str, int] = {}
        failure_categories: dict[str, int] = {}
        route_metric_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            _counter_add(route_counts, row.get("orchestration_route_counts", {}))
            _counter_add(failure_categories, row.get("failure_categories", {}))
            metrics = row.get("orchestration_route_metrics", {})
            if isinstance(metrics, dict):
                for route, metric in metrics.items():
                    if isinstance(metric, dict):
                        route_metric_rows[str(route)].append(metric)

        variant_payload["orchestration_route_counts"] = dict(sorted(route_counts.items()))
        variant_payload["orchestration_route_metrics"] = {
            route: _aggregate_route_metrics(metrics)
            for route, metrics in sorted(route_metric_rows.items())
        }
        variant_payload["failure_categories"] = dict(sorted(failure_categories.items()))
        summary[variant] = variant_payload
    return summary


def _route_hotspots(summary: dict[str, Any]) -> dict[str, Any]:
    hotspots: dict[str, Any] = {}
    for variant, payload in summary.items():
        metrics = payload.get("orchestration_route_metrics", {})
        if not isinstance(metrics, dict):
            continue
        rows = [
            {
                "route": route,
                "case_count": _int(metric.get("case_count")),
                "task_success_rate": _float(metric.get("task_success_rate")),
                "avg_latency_ms": _float(metric.get("avg_latency_ms")),
                "avg_kg_query_count": _float(metric.get("avg_kg_query_count")),
                "avg_scene_query_count": _float(metric.get("avg_scene_query_count")),
            }
            for route, metric in metrics.items()
            if isinstance(metric, dict)
        ]
        hotspots[variant] = {
            "top_routes_by_case_count": sorted(rows, key=lambda item: (-item["case_count"], item["route"]))[:5],
            "lowest_success_routes": sorted(rows, key=lambda item: (item["task_success_rate"], item["route"]))[:5],
            "highest_latency_routes": sorted(rows, key=lambda item: (-item["avg_latency_ms"], item["route"]))[:5],
        }
    return hotspots


def _unsupported_reason_counts(artifacts: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    counts = {variant: {} for variant in _variant_names(artifacts)}
    for artifact in artifacts:
        cases_by_variant = artifact.get("variant_unsupported_cases", {})
        if not isinstance(cases_by_variant, dict):
            continue
        for variant, cases in cases_by_variant.items():
            bucket = counts.setdefault(str(variant), {})
            if not isinstance(cases, list):
                continue
            for case in cases:
                if not isinstance(case, dict):
                    continue
                reason = str(case.get("reason", "")).strip()
                if reason:
                    bucket[reason] = bucket.get(reason, 0) + 1
    return {variant: dict(sorted(reasons.items())) for variant, reasons in counts.items()}


def _comparison_rows(artifacts: list[dict[str, Any]], variant: str) -> list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]]:
    rows: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    for artifact in artifacts:
        comparisons = artifact.get("variant_comparisons", {})
        case_comparisons = artifact.get("case_comparisons", {})
        variant_payload = comparisons.get(variant) if isinstance(comparisons, dict) else None
        case_payload = case_comparisons.get(variant) if isinstance(case_comparisons, dict) else None
        if isinstance(variant_payload, dict) and isinstance(case_payload, dict):
            rows.append((artifact, variant_payload, case_payload))
    return rows


def _variant_comparison_summary(artifacts: list[dict[str, Any]], *, include_per_anchor: bool = True) -> dict[str, Any]:
    result: dict[str, Any] = {}
    variants = _ordered_union(
        [
            variant
            for artifact in artifacts
            for variant in (artifact.get("variant_comparisons", {}) or {}).keys()
            if isinstance(artifact.get("variant_comparisons", {}), dict)
        ]
    )
    for variant in variants:
        rows = _comparison_rows(artifacts, variant)
        compared_count = sum(_int(case_payload.get("compared_case_count")) for _, _, case_payload in rows)
        metric_fields = sorted(
            {
                key
                for _, comparison, _ in rows
                for key in comparison
                if key.endswith("_delta_vs_anchor") and not key.startswith("route_")
            }
        )
        route_names = sorted(
            {
                str(route)
                for _, comparison, _ in rows
                for route in (comparison.get("route_case_share_deltas_vs_anchor", {}) or {}).keys()
                if isinstance(comparison.get("route_case_share_deltas_vs_anchor", {}), dict)
            }
        )
        payload = {
            "artifact_count": len(rows),
            "compared_case_count": compared_count,
            "metric_fields": metric_fields,
            "metric_deltas": {
                field: _rate(
                    sum(_float(comparison.get(field)) * _int(case_payload.get("compared_case_count")) for _, comparison, case_payload in rows),
                    compared_count,
                )
                for field in metric_fields
            },
            "route_names": route_names,
            "route_case_share_deltas": {
                route: _rate(
                    sum(
                        _float((comparison.get("route_case_share_deltas_vs_anchor", {}) or {}).get(route, 0.0))
                        * _int(case_payload.get("compared_case_count"))
                        for _, comparison, case_payload in rows
                    ),
                    compared_count,
                )
                for route in route_names
            },
        }
        anchor_counts: dict[str, int] = {}
        for artifact, _, _ in rows:
            anchor = str(artifact.get("anchor_variant", ""))
            if anchor:
                anchor_counts[anchor] = anchor_counts.get(anchor, 0) + 1
        if include_per_anchor:
            payload["anchor_variant_counts"] = dict(sorted(anchor_counts.items()))

        if include_per_anchor:
            per_anchor: dict[str, Any] = {}
            for anchor in sorted(anchor_counts):
                subset = [artifact for artifact, _, _ in rows if str(artifact.get("anchor_variant", "")) == anchor]
                per_anchor[anchor] = _variant_comparison_summary(subset, include_per_anchor=False).get(variant, {})
            payload["per_anchor_variant"] = per_anchor
        result[variant] = payload
    return result


def _case_comparison_counts(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    variants = _ordered_union(
        [
            variant
            for artifact in artifacts
            for variant in (artifact.get("case_comparisons", {}) or {}).keys()
            if isinstance(artifact.get("case_comparisons", {}), dict)
        ]
    )
    count_fields = (
        "compared_case_count",
        "improved_case_count",
        "regressed_case_count",
        "tied_case_count",
        "missing_anchor_case_count",
        "missing_variant_case_count",
    )
    for variant in variants:
        rows = [
            artifact.get("case_comparisons", {}).get(variant, {})
            for artifact in artifacts
            if isinstance(artifact.get("case_comparisons", {}), dict)
            and isinstance(artifact.get("case_comparisons", {}).get(variant), dict)
        ]
        payload = {"metric_order": list(rows[0].get("metric_order", []) or []) if rows else []}
        for field in count_fields:
            payload[field] = sum(_int(row.get(field)) for row in rows)
        result[variant] = payload
    return result


def _task_comparisons(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, dict[str, dict[str, int]]] = defaultdict(dict)
    fields = (
        "compared_case_count",
        "improved_case_count",
        "regressed_case_count",
        "tied_case_count",
        "missing_anchor_case_count",
        "missing_variant_case_count",
    )
    for artifact in artifacts:
        comparisons = artifact.get("task_comparisons", {})
        if not isinstance(comparisons, dict):
            continue
        for variant, tasks in comparisons.items():
            if not isinstance(tasks, dict):
                continue
            for task_name, payload in tasks.items():
                if not isinstance(payload, dict):
                    continue
                bucket = result[str(variant)].setdefault(str(task_name), {field: 0 for field in fields})
                for field in fields:
                    bucket[field] += _int(payload.get(field))
    return {variant: dict(sorted(tasks.items())) for variant, tasks in sorted(result.items())}


def _comparison_hotspots(task_comparisons: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for variant, tasks in task_comparisons.items():
        rows = [
            {"task_name": task_name, **payload}
            for task_name, payload in tasks.items()
            if isinstance(payload, dict)
        ]
        result[variant] = {
            "top_improved_tasks": [
                {
                    "task_name": row["task_name"],
                    "improved_case_count": row["improved_case_count"],
                    "compared_case_count": row["compared_case_count"],
                }
                for row in sorted(rows, key=lambda item: (-item["improved_case_count"], item["task_name"]))
                if row.get("improved_case_count", 0) > 0
            ][:5],
            "top_regressed_tasks": [
                {
                    "task_name": row["task_name"],
                    "regressed_case_count": row["regressed_case_count"],
                    "compared_case_count": row["compared_case_count"],
                }
                for row in sorted(rows, key=lambda item: (-item["regressed_case_count"], item["task_name"]))
                if row.get("regressed_case_count", 0) > 0
            ][:5],
            "top_missing_variant_tasks": [
                {
                    "task_name": row["task_name"],
                    "missing_variant_case_count": row["missing_variant_case_count"],
                    "compared_case_count": row["compared_case_count"],
                }
                for row in sorted(rows, key=lambda item: (-item["missing_variant_case_count"], item["task_name"]))
                if row.get("missing_variant_case_count", 0) > 0
            ][:5],
        }
    return result


def _context_counts(artifacts: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {field: {} for field in CONTEXT_FIELDS}
    for artifact in artifacts:
        for field in CONTEXT_FIELDS:
            value = str(artifact.get(field, ""))
            if value:
                counts[field][value] = counts[field].get(value, 0) + 1
    return {field: dict(sorted(values.items())) for field, values in counts.items()}


def _summarize_artifacts(
    artifacts: list[dict[str, Any]],
    *,
    include_context_groups: bool,
    include_dataset_breakdown: bool,
) -> dict[str, Any]:
    total = sum(_int(artifact.get("total_case_count")) for artifact in artifacts)
    supported = sum(_int(artifact.get("supported_case_count")) for artifact in artifacts)
    unsupported = sum(_int(artifact.get("unsupported_case_count")) for artifact in artifacts)

    variant_supported: dict[str, int] = {}
    supported_tasks: dict[str, int] = {}
    unsupported_tasks: dict[str, int] = {}
    for artifact in artifacts:
        _counter_add(variant_supported, artifact.get("variant_supported_case_counts", {}))
        _counter_add(supported_tasks, artifact.get("supported_task_counts", {}))
        _counter_add(unsupported_tasks, artifact.get("unsupported_task_counts", {}))

    summary = _aggregate_summary(artifacts)
    task_comparisons = _task_comparisons(artifacts)
    payload: dict[str, Any] = {
        "artifact_count": len(artifacts),
        "total_case_count": total,
        "supported_case_count": supported,
        "unsupported_case_count": unsupported,
        "support_coverage_rate": _rate(supported, total),
        "variant_supported_case_counts": dict(sorted(variant_supported.items())),
        "variant_support_coverage_rates": {
            variant: _rate(count, total)
            for variant, count in sorted(variant_supported.items())
        },
        "supported_task_counts": dict(sorted(supported_tasks.items())),
        "unsupported_task_counts": dict(sorted(unsupported_tasks.items())),
        "context_counts": _context_counts(artifacts),
        "artifact_index": _artifact_index(artifacts),
        "unsupported_reason_counts": _unsupported_reason_counts(artifacts),
        "summary": summary,
        "route_hotspots": _route_hotspots(summary),
        "variant_comparison_summary": _variant_comparison_summary(artifacts),
        "case_comparison_counts": _case_comparison_counts(artifacts),
        "task_comparisons": task_comparisons,
        "comparison_hotspots": _comparison_hotspots(task_comparisons),
    }
    if include_context_groups:
        payload["context_groups"] = {}
        for field in CONTEXT_GROUP_FIELDS:
            groups: dict[str, Any] = {}
            values = sorted({str(artifact.get(field, "")) for artifact in artifacts if str(artifact.get(field, ""))})
            for value in values:
                subset = [artifact for artifact in artifacts if str(artifact.get(field, "")) == value]
                groups[value] = _summarize_artifacts(
                    subset,
                    include_context_groups=False,
                    include_dataset_breakdown=False,
                )
            payload["context_groups"][field] = groups
    if include_dataset_breakdown:
        payload["datasets"] = {}
        for dataset in sorted({str(artifact.get("dataset", "")) for artifact in artifacts if str(artifact.get("dataset", ""))}):
            subset = [artifact for artifact in artifacts if str(artifact.get("dataset", "")) == dataset]
            payload["datasets"][dataset] = _summarize_artifacts(
                subset,
                include_context_groups=False,
                include_dataset_breakdown=False,
            )
    else:
        payload["datasets"] = sorted({str(artifact.get("dataset", "")) for artifact in artifacts if str(artifact.get("dataset", ""))})
    return payload


def summarize_cognitive_eval_artifact_paths(paths: list[str | Path]) -> dict[str, Any]:
    return _summarize_artifacts(
        _load_artifacts(paths),
        include_context_groups=True,
        include_dataset_breakdown=True,
    )


__all__ = ["summarize_cognitive_eval_artifact_paths"]
