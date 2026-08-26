from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from benchmark.delta.paper_method.code import run_recorded as runner  # noqa: E402


def _pct(value: int, total: int) -> float:
    return (float(value) / float(total) * 100.0) if total else 0.0


def _case_sort_key(path: Path) -> str:
    return path.parent.name


def _write_report(run_root: Path, manifest: dict[str, Any], summary: dict[str, Any], repair_rows: list[dict[str, Any]]) -> None:
    total = int(summary.get("total_case_records_seen") or 0)
    planner = int(summary.get("planner_success_cases") or 0)
    decomp = int(summary.get("planner_decomposed_success_cases") or 0)
    both = int(summary.get("strict_both_success_cases") or 0)
    repaired = sum(1 for row in repair_rows if row.get("status") == "done")
    repair_failed = sum(1 for row in repair_rows if row.get("status") == "failed")
    skipped = sum(1 for row in repair_rows if row.get("status") == "skipped")

    lines = [
        "# DELTA paper_method 9B 600 Run Accuracy Report",
        "",
        f"Generated at: `{runner.timestamp()}`",
        "",
        "## Run Status",
        "",
        f"- Run directory: `{run_root}`",
        f"- Model recorded in manifest: `{manifest.get('api_model')}`",
        f"- Ports: `{manifest.get('ports')}`",
        f"- Workers: `{manifest.get('workers')}`",
        f"- max_tokens: `{manifest.get('max_tokens')}`",
        f"- source-object guard: `{manifest.get('source_object_guard')}`",
        f"- Planner: `{manifest.get('planner')}`, max_time `{manifest.get('planner_max_time')}s`",
        f"- Planner repair Python: `{sys.executable}`",
        "",
        "## Repair Status",
        "",
        "- The original batch finished all LLM stages, but planner execution failed under `/usr/bin/python` because `pddlgym` was missing.",
        "- This report reflects a planner-only repair pass over the already generated PDDL and subgoals; no LLM stages were rerun.",
        f"- Planner repair rows: done `{repaired}`, failed `{repair_failed}`, skipped `{skipped}`.",
        "",
        "## Accuracy",
        "",
        "| Accuracy Field | Success | Rate |",
        "|---|---:|---:|",
        f"| Undecomposed planner + VAL | `{planner}/{total}` | `{_pct(planner, total):.2f}%` |",
        f"| Decomposed planner + VAL | `{decomp}/{total}` | `{_pct(decomp, total):.2f}%` |",
        f"| Strict both success | `{both}/{total}` | `{_pct(both, total):.2f}%` |",
        "",
        "## Artifact Completeness",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Case records seen | `{total}/600` |",
        f"| Status done | `{summary.get('done_cases')}/600` |",
        f"| Status failed | `{summary.get('failed_cases')}/600` |",
        f"| Stage1 domain PDDL files | `{summary.get('stage1_domain_files')}/600` |",
        f"| Stage3 problem PDDL files | `{summary.get('stage3_problem_files')}/600` |",
        f"| Stage4 subgoal files | `{summary.get('stage4_subgoal_files')}/600` |",
        f"| Fast Downward translate OK | `{summary.get('pddl_translate_ok_cases')}/600` |",
        f"| PDDL anomaly cases | `{summary.get('pddl_check_anomaly_cases')}/600` |",
        f"| API retry/error cases | `{summary.get('api_retry_error_cases')}` |",
        f"| API retry/error count | `{summary.get('api_retry_error_count')}` |",
        f"| Failed stage counts | `{summary.get('failed_stage_counts')}` |",
        "",
    ]
    runner._write_text(run_root / "ACCURACY_REPORT.md", "\n".join(lines))


def _repair_case(case_json: Path, *, planner_max_time: float, force: bool) -> dict[str, Any]:
    row = runner.read_json(case_json, {})
    if not isinstance(row, dict):
        return {"case": str(case_json), "status": "failed", "error": "case_json_not_object"}

    case_id = str(row.get("case_id") or case_json.parent.name)
    if row.get("status") == "done" and row.get("planner_result_file") and not force:
        return {"case_id": case_id, "status": "skipped"}

    pddl_files = row.get("pddl_files") if isinstance(row.get("pddl_files"), dict) else {}
    missing = [key for key in ("domain", "problem", "subgoals_json") if not pddl_files.get(key)]
    if missing:
        return {"case_id": case_id, "status": "failed", "error": f"missing_pddl_files:{missing}"}

    case_root = Path(row.get("case_root") or case_json.parent)
    domain = str(row.get("domain") or "")
    scene = str(row.get("scene") or "")
    subgoals = runner.read_json(pddl_files["subgoals_json"], [])
    if not isinstance(subgoals, list):
        subgoals = []

    previous = {
        "status": row.get("status"),
        "failed_stage": row.get("failed_stage"),
        "error": row.get("error"),
    }
    try:
        planner_result = runner._run_standard_planner(
            case_root=case_root,
            domain=domain,
            generated_domain_file=Path(pddl_files["domain"]),
            generated_problem_file=Path(pddl_files["problem"]),
            validation_domain_file=runner._src_domain_path(domain),
            validation_problem_file=runner._src_problem_path(scene, domain),
            subgoals=subgoals,
            max_time=planner_max_time,
        )
        row.update(
            {
                "status": "done",
                "updated_at": runner.timestamp(),
                "planner_result_file": str(case_root / "planner" / "planner_result.json"),
                "planner_success": bool(planner_result.get("planner_success")),
                "planner_decomposed_success": bool(planner_result.get("planner_decomposed_success")),
                "planner_result": planner_result,
                "planner_repair": {
                    "repaired_at": runner.timestamp(),
                    "python": sys.executable,
                    "previous": previous,
                },
            }
        )
        row.pop("failed_stage", None)
        row.pop("error", None)
        row.pop("traceback", None)
        runner.write_json(case_json, row)
        return {
            "case_id": case_id,
            "status": "done",
            "planner_success": row["planner_success"],
            "planner_decomposed_success": row["planner_decomposed_success"],
        }
    except Exception as exc:
        row.update(
            {
                "status": "failed",
                "updated_at": runner.timestamp(),
                "failed_stage": "planner_repair",
                "error": repr(exc),
                "traceback": traceback.format_exc(),
                "planner_repair": {
                    "repaired_at": runner.timestamp(),
                    "python": sys.executable,
                    "previous": previous,
                },
            }
        )
        runner.write_json(case_json, row)
        return {"case_id": case_id, "status": "failed", "error": repr(exc)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Repair DELTA paper_method run by rerunning planner over existing PDDL.")
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--planner-max-time", type=float, default=60.0)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run_root = Path(args.run_root).resolve()
    manifest = runner.read_json(run_root / "manifest.json", {})
    if not isinstance(manifest, dict):
        manifest = {}

    case_jsons = sorted((run_root / "cases").glob("*/case.json"), key=_case_sort_key)
    if args.limit is not None:
        case_jsons = case_jsons[: max(0, int(args.limit))]

    start = time.time()
    repair_rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, int(args.workers or 1)), thread_name_prefix="planner-repair") as pool:
        futures = [
            pool.submit(
                _repair_case,
                case_json,
                planner_max_time=float(args.planner_max_time),
                force=bool(args.force),
            )
            for case_json in case_jsons
        ]
        for index, future in enumerate(as_completed(futures), start=1):
            row = future.result()
            repair_rows.append(row)
            print(
                f"[{index}/{len(futures)}] {row.get('case_id')} status={row.get('status')} "
                f"orig={row.get('planner_success')} decomp={row.get('planner_decomposed_success')}",
                flush=True,
            )

    rows = runner._scan_rows(run_root)
    summary = runner._summarize(run_root, rows)
    manifest["planner_repair_pass"] = {
        "repaired_at": runner.timestamp(),
        "python": sys.executable,
        "workers": max(1, int(args.workers or 1)),
        "planner_max_time": float(args.planner_max_time),
        "limit": args.limit,
        "force": bool(args.force),
        "elapsed_seconds": time.time() - start,
        "repair_rows": {
            "done": sum(1 for row in repair_rows if row.get("status") == "done"),
            "failed": sum(1 for row in repair_rows if row.get("status") == "failed"),
            "skipped": sum(1 for row in repair_rows if row.get("status") == "skipped"),
        },
    }
    runner.write_json(run_root / "manifest.json", manifest)
    runner._write_run_audit(run_root, manifest, summary)
    _write_report(run_root, manifest, summary, repair_rows)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
