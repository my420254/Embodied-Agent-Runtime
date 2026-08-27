from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from benchmark.delta.framework.code.config import load_config
from benchmark.delta.framework.code.metrics import summarize_domain_success
from benchmark.datasets.extracted_cases import load_extracted_cases
from benchmark.experiment_utils import (
    add_common_launch_args,
    assert_framework_run_py_entrypoint,
    assert_expected_case_count,
    case_input,
    case_field,
    case_metadata,
    launch_case_workers,
    launch_case_ids,
    launch_defaults,
    launch_expected_count,
    launch_limit,
    launch_ports,
    launch_preflight_payload,
    launch_run_name,
    launch_run_root,
    launch_trace,
    launch_trace_llm_io,
    launch_unit_count,
    launch_worker_timeout_s,
    launch_workers,
    list_values,
    load_launch_config,
    read_json,
    resolve_endpoint_slots,
    write_row_summary,
)
from config.settings import activate_config


CONFIG_PATH = Path(__file__).resolve().parent / "config" / "launch_config.json"
SETTINGS_PATH = Path(__file__).resolve().parent / "config" / "settings.json"
CODE_ROOT = Path(__file__).resolve().parent
WORKER_MODULE = "benchmark.delta.framework.code._case_worker"
BENCHMARK_NAME = "delta"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run DELTA through the OurAgent-he framework path."
    )
    add_common_launch_args(parser)
    parser.add_argument("--domain", action="append", default=[])
    parser.add_argument("--domains", nargs="*", default=[])
    parser.add_argument("--scene", action="append", default=[])
    parser.add_argument("--scenes", nargs="*", default=[])
    parser.add_argument("--episodes", type=int, default=None)
    parser.add_argument("--shard-by", choices=("case", "domain", "scene"), default="")
    parser.add_argument("--validate-bin", default="")
    parser.add_argument("--skip-val", action="store_true")
    return parser


def _select_delta_cases(
    cases: list[Any], *, case_ids: list[str], limit: int | None
) -> list[Any]:
    selected = list(cases)
    if case_ids:
        requested = {str(item) for item in case_ids}
        selected = [
            case
            for case in selected
            if str(case_field(case, "case_id", "")) in requested
            or str(case_metadata(case).get("base_case_id", "")) in requested
            or str(case_input(case).get("base_task_id", "")) in requested
        ]
        found = {str(case_field(case, "case_id", "")) for case in selected} | {
            str(case_metadata(case).get("base_case_id", ""))
            for case in selected
            if case_metadata(case).get("base_case_id")
        }
        missing = [case_id for case_id in case_ids if case_id not in found]
        if missing:
            raise SystemExit("unknown DELTA case ids: " + ", ".join(missing))
    if limit is not None:
        selected = selected[: max(0, int(limit))]
    if not selected:
        raise SystemExit("no DELTA cases selected")
    return selected


def main(argv: list[str] | None = None) -> int:
    assert_framework_run_py_entrypoint()
    args = _parser().parse_args(argv)
    launch_cfg = load_launch_config(CONFIG_PATH)
    defaults = launch_defaults(launch_cfg)
    run_name = launch_run_name(args, defaults, "delta_framework")
    run_root = launch_run_root(
        launch_cfg, run_name, "benchmark/delta/framework/results"
    )
    if args.summary:
        print(
            json.dumps(
                read_json(run_root / "summary.json", {}), ensure_ascii=False, indent=2
            )
        )
        return 0

    cfg = load_config()
    domains = list_values(defaults.get("domains", []), args.domain, args.domains)
    scenes = list_values(defaults.get("scenes", []), args.scene, args.scenes)
    episodes = args.episodes if args.episodes is not None else defaults.get("episodes")
    cases = load_extracted_cases(cfg.extracted_cases_path)
    if episodes is not None:
        max_episode = int(episodes)
        cases = [
            case
            for case in cases
            if int(
                case_metadata(case).get("episode", case_input(case).get("episode", 0))
                or 0
            )
            <= max_episode
        ]
    if domains:
        domain_set = set(domains)
        cases = [
            case
            for case in cases
            if str(case_metadata(case).get("domain", "")) in domain_set
        ]
    if scenes:
        scene_set = set(scenes)
        cases = [
            case
            for case in cases
            if str(case_metadata(case).get("scene", "")) in scene_set
        ]
    limit = launch_limit(args, defaults)
    cases = _select_delta_cases(
        cases, case_ids=launch_case_ids(args, defaults), limit=limit
    )
    expected_count = launch_expected_count(
        args, defaults, default_enabled=not domains and not scenes
    )
    assert_expected_case_count(cases, expected_count, BENCHMARK_NAME)

    workers = launch_workers(args, defaults)
    ports = launch_ports(args, defaults)
    activate_config(SETTINGS_PATH)
    endpoint_slots = resolve_endpoint_slots(
        benchmark_name=BENCHMARK_NAME,
        ports=ports,
        workers=workers,
        api_model=str(args.api_model or defaults.get("api_model") or ""),
        api_key=str(args.api_key or defaults.get("api_key") or ""),
    )
    split_cfg = (
        launch_cfg.get("split", {}) if isinstance(launch_cfg.get("split"), dict) else {}
    )
    shard_by = str(args.shard_by or split_cfg.get("shard_by") or "domain")
    group_key = None
    if shard_by == "domain":

        def group_key(case: dict[str, Any]) -> str:
            return str(case_metadata(case).get("domain", ""))
    elif shard_by == "scene":

        def group_key(case: dict[str, Any]) -> str:
            return str(case_metadata(case).get("scene", ""))

    unit_count = launch_unit_count(args, endpoint_slots, defaults)
    if bool(args.preflight):
        print(
            json.dumps(
                launch_preflight_payload(
                    benchmark_name=BENCHMARK_NAME,
                    cases=cases,
                    endpoint_slots=endpoint_slots,
                    unit_count=unit_count,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    results = launch_case_workers(
        benchmark_name=BENCHMARK_NAME,
        run_root=run_root,
        worker_module=WORKER_MODULE,
        cases=cases,
        endpoint_slots=endpoint_slots,
        unit_count=unit_count,
        group_key=group_key,
        worker_options={
            "validate_binary": str(args.validate_bin or ""),
            "skip_val": bool(args.skip_val),
        },
        trace=launch_trace(defaults),
        trace_llm_io=launch_trace_llm_io(args, defaults),
        dry_run=bool(args.dry_run),
        resume=bool(args.resume),
        worker_timeout_s=launch_worker_timeout_s(args, defaults),
        reproducibility_paths={
            "settings": SETTINGS_PATH,
            "prompts": CODE_ROOT / "config" / "prompts.json",
            "skills": CODE_ROOT / "skills",
            "extracted_cases": cfg.extracted_cases_path,
            "framework_code": CODE_ROOT,
        },
    )
    summary = write_row_summary(run_root, results, summarize_domain_success)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
