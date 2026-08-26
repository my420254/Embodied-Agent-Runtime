from __future__ import annotations

import argparse
import json
import socket
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from benchmark.experiment_utils import read_json, write_json
from benchmark.reactree.wah.framework.code.config import load_config as load_wah_config
from benchmark.reactree.wah.framework.code.metrics import summarize_gsr_ssr
from benchmark.reactree.wah.framework.code.official_evaluator import (
    evaluate_reactree_goals,
    reactree_task_from_case_input,
)


def timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Re-evaluate WAH official Unity metrics from existing bare outputs.")
    parser.add_argument("--run-name", default="reactree_wah_bare_full_qwen36_official_100_20260817")
    parser.add_argument("--official-base-port", type=int, default=9940)
    parser.add_argument("--official-port-ids", nargs="*", type=int, default=[0, 1, 2, 3, 4, 5])
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--timeout-s", type=int, default=180)
    parser.add_argument("--cooldown-s", type=float, default=1.5)
    parser.add_argument("--max-port-retries", type=int, default=2)
    return parser.parse_args()


def result_root(run_name: str) -> Path:
    return PROJECT_ROOT / "benchmark" / "reactree" / "wah" / "bare_baseline" / "results" / run_name


def bindable(port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("127.0.0.1", int(port)))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def assert_ports_free(base_port: int, port_ids: list[int]) -> None:
    busy_ports = [base_port + port_id for port_id in port_ids if not bindable(base_port + port_id)]
    if busy_ports:
        formatted = ", ".join(str(port) for port in busy_ports)
        raise SystemExit(f"WAH Unity ports are busy: {formatted}")


def is_port_launch_error(prediction: dict[str, Any]) -> bool:
    error = str(prediction.get("error") or "")
    return "port" in error.lower() or "launch the environment" in error.lower()


def load_rows(run_root: Path) -> list[dict[str, Any]]:
    summary_path = run_root / "summary.json"
    summary = read_json(summary_path, {})
    rows = summary.get("cases") if isinstance(summary, dict) else None
    if isinstance(rows, list) and rows:
        return [dict(row) for row in rows if isinstance(row, dict)]
    case_rows: list[dict[str, Any]] = []
    for meta_path in sorted((run_root / "cases").glob("*/case.json")):
        row = read_json(meta_path, {})
        if isinstance(row, dict):
            case_rows.append(row)
    return case_rows


def case_root_for_row(run_root: Path, row: dict[str, Any]) -> Path:
    prompt = str(row.get("prompt") or "")
    if prompt:
        return Path(prompt).parent
    return run_root / "cases" / str(row.get("case_id", "")).replace(":", "__")


def backup_previous_summary(run_root: Path) -> None:
    summary_path = run_root / "summary.json"
    if not summary_path.exists():
        return
    backup_root = run_root / "artifacts" / "reeval_backups"
    backup_root.mkdir(parents=True, exist_ok=True)
    backup_path = backup_root / f"summary_before_wah_official_reeval_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    backup_path.write_text(summary_path.read_text(encoding="utf-8"), encoding="utf-8")


def reevaluate_one(
    *,
    index: int,
    row: dict[str, Any],
    run_root: Path,
    base_port: int,
    port_ids: list[int],
    port_locks: dict[int, threading.Lock],
    timeout_s: int,
    cooldown_s: float,
    max_port_retries: int,
) -> dict[str, Any]:
    cfg = load_wah_config()
    case_root = case_root_for_row(run_root, row)
    case_payload = read_json(case_root / "input.json", {})
    case_input = case_payload.get("input", {}) if isinstance(case_payload, dict) else {}
    if not isinstance(case_input, dict):
        case_input = {}
    official_actions = row.get("official_actions", [])
    if not isinstance(official_actions, list):
        official_actions = []
    task = reactree_task_from_case_input(case_input)
    attempts: list[dict[str, Any]] = []
    prediction: dict[str, Any] = {}
    for attempt in range(max(1, max_port_retries + 1)):
        port_id = port_ids[(index + attempt) % len(port_ids)]
        with port_locks[port_id]:
            prediction = evaluate_reactree_goals(
                init_graph=case_input.get("init_graph", {}),
                task_goal=case_input.get("task_goal", {}),
                evaluator_execution_calls=[],
                official_actions=official_actions,
                repo_root=cfg.repo_root,
                task=task,
                reactree_python=cfg.reactree_python,
                timeout_s=timeout_s,
                base_port=base_port,
                port_id=port_id,
                reuse_unity=False,
            )
            attempts.append(
                {
                    "attempt": attempt + 1,
                    "port": base_port + port_id,
                    "official_available": prediction.get("official_available"),
                    "error": prediction.get("error", ""),
                }
            )
            time.sleep(max(0.0, cooldown_s))
        if prediction.get("official_available") is True or not is_port_launch_error(prediction):
            break
    updated = dict(row)
    updated["prediction"] = prediction
    updated["success"] = float(prediction.get("goal_success_rate", 0.0) or 0.0) >= 1.0
    updated["status"] = "done"
    updated["wah_official_reevaluated_at"] = timestamp()
    updated["wah_official_reeval_attempts"] = attempts
    write_json(case_root / "raw_output.json", updated)
    write_json(case_root / "case.json", updated)
    return updated


def write_summary(run_root: Path, rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    rows.sort(key=lambda item: str(item.get("case_id", "")))
    summary = {
        "run_name": run_root.name,
        "dataset": "wah",
        "total_cases": len(rows),
        "done_cases": sum(1 for row in rows if row.get("status") == "done"),
        "failed_cases": sum(1 for row in rows if row.get("status") == "failed"),
        **summarize_gsr_ssr(rows),
        "wah_official_reevaluated_at": timestamp(),
        "wah_official_reeval_base_port": int(args.official_base_port),
        "wah_official_reeval_port_ids": list(args.official_port_ids),
        "wah_official_reeval_workers": int(args.workers),
        "cases": rows,
    }
    write_json(run_root / "merged_results.json", rows)
    write_json(run_root / "summary.json", summary)
    return summary


def main() -> int:
    args = parse_args()
    run_root = result_root(args.run_name)
    if not run_root.exists():
        raise SystemExit(f"run root not found: {run_root}")
    port_ids = list(args.official_port_ids or [0])
    assert_ports_free(int(args.official_base_port), port_ids)
    rows = load_rows(run_root)
    if not rows:
        raise SystemExit(f"no rows found under {run_root}")
    backup_previous_summary(run_root)
    port_locks = {port_id: threading.Lock() for port_id in port_ids}
    reevaluated_rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, int(args.workers))) as pool:
        futures = [
            pool.submit(
                reevaluate_one,
                index=index,
                row=row,
                run_root=run_root,
                base_port=int(args.official_base_port),
                port_ids=port_ids,
                port_locks=port_locks,
                timeout_s=int(args.timeout_s),
                cooldown_s=float(args.cooldown_s),
                max_port_retries=int(args.max_port_retries),
            )
            for index, row in enumerate(rows)
        ]
        for future in as_completed(futures):
            reevaluated_rows.append(future.result())
    summary = write_summary(run_root, reevaluated_rows, args)
    print(json.dumps({key: value for key, value in summary.items() if key != "cases"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
