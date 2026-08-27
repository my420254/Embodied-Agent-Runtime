def summarize_domain_success(results: list[dict]) -> dict:
    """按 DELTA domain 汇总当前 framework 标准任务成功率。"""
    by_domain: dict[str, dict[str, int]] = {}
    route_counts: dict[str, int] = {}
    for result in results:
        domain = str(result.get("metadata", {}).get("domain", "unknown"))
        prediction = result.get("prediction", {})
        bucket = by_domain.setdefault(
            domain,
            {
                "count": 0,
                "task_success_count": 0,
                "official_available_count": 0,
                "official_task_success_count": 0,
                "symbolic_success_count": 0,
            },
        )
        bucket["count"] += 1
        task_success = bool(prediction.get("task_success"))
        if task_success:
            bucket["task_success_count"] += 1
        if bool(prediction.get("symbolic_success")):
            bucket["symbolic_success_count"] += 1
        if not prediction and str(result.get("error") or "").strip():
            route = "worker_failed"
        else:
            route = str(prediction.get("evaluation_route") or "missing_evaluation_route")
        route_counts[route] = route_counts.get(route, 0) + 1
        if bool(prediction.get("official_available")):
            bucket["official_available_count"] += 1
            if task_success:
                bucket["official_task_success_count"] += 1

    summary = {
        "count": sum(bucket["count"] for bucket in by_domain.values()),
        "task_success_count": sum(bucket["task_success_count"] for bucket in by_domain.values()),
        "official_available_count": sum(bucket["official_available_count"] for bucket in by_domain.values()),
        "official_task_success_count": sum(bucket["official_task_success_count"] for bucket in by_domain.values()),
        "symbolic_success_count": sum(bucket["symbolic_success_count"] for bucket in by_domain.values()),
    }
    summary["task_success_rate"] = (
        summary["task_success_count"] / summary["count"] if summary["count"] else 0.0
    )
    summary["official_task_success_rate"] = (
        summary["official_task_success_count"] / summary["official_available_count"]
        if summary["official_available_count"]
        else None
    )
    summary["symbolic_success_rate"] = (
        summary["symbolic_success_count"] / summary["count"] if summary["count"] else 0.0
    )
    summary["domains"] = {}
    for domain, bucket in sorted(by_domain.items()):
        official_available_count = bucket["official_available_count"]
        summary["domains"][domain] = {
            **bucket,
            "task_success_rate": bucket["task_success_count"] / bucket["count"] if bucket["count"] else 0.0,
            "official_task_success_rate": (
                bucket["official_task_success_count"] / official_available_count
                if official_available_count
                else None
            ),
            "symbolic_success_rate": bucket["symbolic_success_count"] / bucket["count"] if bucket["count"] else 0.0,
        }
    summary["_evaluation_route_counts"] = route_counts
    return summary
