from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from benchmark.reactree.alfred.framework.code.adapter import load_tasks, to_case_payload
from benchmark.reactree.alfred.framework.code.config import extracted_cases_path_for_eval_set, load_config
from benchmark.reactree.alfred.framework.code.task_environment import prepare_alfred_initial_scene_cache


def _safe_case_name(value: str) -> str:
    label = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value).strip()).strip("._-")
    return label or "case"


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    tmp_path.replace(path)


def _load_case_ids_file(path: str | Path | None) -> set[str]:
    if not path:
        return set()
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    try:
        loaded = json.loads(text)
    except json.JSONDecodeError:
        return {line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")}
    if isinstance(loaded, list):
        return {str(item) for item in loaded if str(item).strip()}
    if isinstance(loaded, dict):
        values = loaded.get("case_ids") or loaded.get("cases") or []
        return {str(item) for item in values if str(item).strip()} if isinstance(values, list) else set()
    return set()


def _annotation_path(task: str, repeat_idx: int) -> Path:
    cfg = load_config()
    return cfg.annotation_root / task / "pp" / f"ann_{int(repeat_idx)}.json"


def _case_cache_path(case_id: str) -> Path:
    return load_config().extracted_envs_root / f"{_safe_case_name(case_id)}.json"


def _cache_path_is_valid(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    if not isinstance(payload, dict):
        return False
    initial_scene = payload.get("initial_scene")
    if isinstance(initial_scene, dict) and isinstance(initial_scene.get("all_objects"), list):
        return True
    return isinstance(payload.get("all_objects"), list)


def build_reactree_alfred_cases(*, eval_set: str = "valid_seen") -> list[dict[str, Any]]:
    cfg = load_config()
    cases: list[dict[str, Any]] = []
    for task in load_tasks(cfg.split_json, eval_set=eval_set):
        case = to_case_payload(task, eval_set=eval_set)
        case_id = str(case["case_id"])
        case_input = case.get("input", {}) if isinstance(case.get("input"), dict) else {}
        cache_path = _case_cache_path(case_id)
        case_input.update(
            {
                "initial_scene_cache_path": str(cache_path),
                "task_source": "alfred_pp_annotation_json",
                "environment_source": "alfred_official_scene_prepare_cache",
            }
        )
        case["input"] = case_input
        case["metadata"] = {
            **(case.get("metadata", {}) if isinstance(case.get("metadata"), dict) else {}),
            "eval_set": eval_set,
            "annotation_path": str(_annotation_path(str(case_input.get("task", "")), int(case_input.get("repeat_idx", 0)))),
            "initial_scene_cache_path": str(cache_path),
        }
        cases.append(case)
    return cases


def _normalize_display(display: Any) -> str:
    text = str(display or "").strip()
    return text[1:] if text.startswith(":") else text


def _display_probe(display: str) -> tuple[bool, str]:
    normalized = _normalize_display(display)
    env = dict(os.environ)
    env["DISPLAY"] = f":{normalized}"
    try:
        completed = subprocess.run(
            ["xdpyinfo"],
            env=env,
            check=False,
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=5,
        )
    except FileNotFoundError:
        return False, "xdpyinfo not found"
    except subprocess.TimeoutExpired:
        return False, "xdpyinfo timed out"
    if completed.returncode == 0:
        return True, ""
    return False, (completed.stderr or "").strip().splitlines()[-1] if completed.stderr else "xdpyinfo failed"


def _start_xvfb(display: str, *, screen: str, log_root: Path) -> subprocess.Popen:
    normalized = _normalize_display(display)
    log_path = log_root / "xvfb" / f"display_{normalized}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        ["Xvfb", f":{normalized}", "-screen", "0", str(screen or "1024x768x24"), "-nolisten", "tcp"],
        stdout=log_file,
        stderr=subprocess.STDOUT,
        close_fds=True,
    )
    setattr(process, "_ouragent_log_file", log_file)
    return process


def _stop_processes(processes: list[subprocess.Popen]) -> None:
    for process in processes:
        if process.poll() is None:
            process.terminate()
    for process in processes:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        log_file = getattr(process, "_ouragent_log_file", None)
        if log_file is not None:
            try:
                log_file.close()
            except Exception:
                pass


def _ensure_displays(
    displays: list[str],
    *,
    no_auto_xvfb: bool,
    screen: str,
    log_root: Path,
) -> list[subprocess.Popen]:
    processes: list[subprocess.Popen] = []
    for display in displays:
        ok, reason = _display_probe(display)
        if ok:
            continue
        if no_auto_xvfb:
            raise RuntimeError(f"ALFRED simulator X display unavailable: :{display} ({reason})")
        process = _start_xvfb(display, screen=screen, log_root=log_root)
        processes.append(process)
        last_reason = reason
        for _ in range(20):
            time.sleep(0.25)
            ok, last_reason = _display_probe(display)
            if ok:
                break
            if process.poll() is not None:
                break
        if not ok:
            _stop_processes(processes)
            raise RuntimeError(f"failed to start Xvfb :{display}: {last_reason}")
    return processes


def _extract_one(case: dict[str, Any], *, x_display: str, force: bool) -> dict[str, Any]:
    case_id = str(case.get("case_id", ""))
    case_input = case.get("input", {}) if isinstance(case.get("input"), dict) else {}
    cache_path = Path(str(case_input.get("initial_scene_cache_path") or _case_cache_path(case_id)))
    if _cache_path_is_valid(cache_path) and not force:
        return {"case_id": case_id, "status": "cached", "cache_path": str(cache_path)}
    initial_scene = prepare_alfred_initial_scene_cache(case_input, x_display=x_display)
    objects = initial_scene.get("all_objects", []) if isinstance(initial_scene, dict) else []
    visible_groups = initial_scene.get("visible_groups", []) if isinstance(initial_scene, dict) else []
    _write_json(
        cache_path,
        {
            "dataset": "reactree_alfred",
            "case_id": case_id,
            "task": str(case_input.get("task", "")),
            "repeat_idx": int(case_input.get("repeat_idx", 0)),
            "source": {
                "kind": "alfred_official_scene_prepare",
                "split_json": str(load_config().split_json),
                "annotation_path": str(_annotation_path(str(case_input.get("task", "")), int(case_input.get("repeat_idx", 0)))),
            },
            "object_count": len(objects) if isinstance(objects, list) else 0,
            "visible_group_count": len(visible_groups) if isinstance(visible_groups, list) else 0,
            "initial_scene": initial_scene,
        },
    )
    return {"case_id": case_id, "status": "extracted", "cache_path": str(cache_path)}


def _selected_extraction_cases(
    cases: list[dict[str, Any]],
    *,
    case_ids: set[str],
    extract_limit: int | None,
    missing_only: bool,
) -> list[dict[str, Any]]:
    selected = []
    for case in cases:
        if case_ids and str(case.get("case_id", "")) not in case_ids:
            continue
        if missing_only:
            case_input = case.get("input", {}) if isinstance(case.get("input"), dict) else {}
            cache_path = Path(str(case_input.get("initial_scene_cache_path") or ""))
            if _cache_path_is_valid(cache_path):
                continue
        selected.append(case)
    if extract_limit is not None:
        selected = selected[: max(0, int(extract_limit))]
    return selected


def write_manifest(cases: list[dict[str, Any]], *, eval_set: str, extraction_results: list[dict[str, Any]]) -> Path:
    cfg = load_config()
    cache_paths = [
        Path(str((case.get("input", {}) if isinstance(case.get("input"), dict) else {}).get("initial_scene_cache_path", "")))
        for case in cases
    ]
    valid_cache_count = sum(1 for path in cache_paths if _cache_path_is_valid(path))
    missing_cache_count = sum(1 for path in cache_paths if not path.exists())
    invalid_cache_count = sum(1 for path in cache_paths if path.exists() and not _cache_path_is_valid(path))
    payload = {
        "dataset": "reactree_alfred",
        "source": {
            "native_root": str(cfg.repo_root),
            "split_json": str(cfg.split_json),
            "annotation_root": str(cfg.annotation_root),
            "eval_set": eval_set,
            "task_source": "alfred/data/splits/oct21.json + alfred/data/json_2.1.0/*/pp/ann_*.json",
            "environment_source": "AI2-THOR reset/restore_scene/init_reset over native ALFRED annotations",
        },
        "case_count": len(cases),
        "environment_cache_status": {
            "cached": valid_cache_count,
            "missing": missing_cache_count,
            "invalid": invalid_cache_count,
            "extracted_this_run": sum(1 for item in extraction_results if item.get("status") == "extracted"),
            "skipped_existing_this_run": sum(1 for item in extraction_results if item.get("status") == "cached"),
            "failed_this_run": sum(1 for item in extraction_results if item.get("status") == "failed"),
        },
        "cases": cases,
    }
    split_path = extracted_cases_path_for_eval_set(eval_set)
    _write_json(split_path, payload)
    if str(eval_set or "") == "valid_seen":
        _write_json(cfg.extracted_cases_path, payload)
    return split_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build extracted ReAcTree-ALFRED cases and optional initial scene caches.")
    parser.add_argument("--eval-set", default="valid_seen")
    parser.add_argument("--extract-missing", action="store_true", help="Enter AI2-THOR to create missing initial scene caches.")
    parser.add_argument("--force", action="store_true", help="Re-extract caches even when they already exist.")
    parser.add_argument("--case-id", action="append", default=[], help="Restrict cache extraction to selected case ids; manifest still lists the eval set.")
    parser.add_argument("--case-ids-file", default="")
    parser.add_argument("--missing-only", action="store_true", help="Extract only cases whose initial scene cache file is missing.")
    parser.add_argument("--extract-limit", type=int, default=None)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--x-displays", nargs="*", default=["0"])
    parser.add_argument("--no-auto-xvfb", action="store_true")
    parser.add_argument("--xvfb-screen", default="1024x768x24")
    parser.add_argument("--progress-every", type=int, default=25)
    args = parser.parse_args(argv)

    cases = build_reactree_alfred_cases(eval_set=str(args.eval_set or "valid_seen"))
    extraction_results: list[dict[str, Any]] = []
    processes: list[subprocess.Popen] = []
    if bool(args.extract_missing):
        case_ids = {str(item) for item in args.case_id if str(item).strip()}
        case_ids.update(_load_case_ids_file(args.case_ids_file))
        selected = _selected_extraction_cases(
            cases,
            case_ids=case_ids,
            extract_limit=args.extract_limit,
            missing_only=bool(args.missing_only),
        )
        displays = [_normalize_display(item) for item in args.x_displays if _normalize_display(item)] or ["0"]
        workers = max(1, int(args.workers or 1))
        if len(displays) < workers:
            raise SystemExit(f"ALFRED extraction needs at least one X display per worker: workers={workers}, x_displays={displays}")
        processes = _ensure_displays(
            displays[:workers],
            no_auto_xvfb=bool(args.no_auto_xvfb),
            screen=str(args.xvfb_screen or "1024x768x24"),
            log_root=load_config().extracted_envs_root,
        )
        try:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = []
                for index, case in enumerate(selected):
                    future = pool.submit(
                        _extract_one,
                        case,
                        x_display=displays[index % workers],
                        force=bool(args.force),
                    )
                    setattr(future, "_ouragent_case_id", str(case.get("case_id", "")))
                    futures.append(future)
                print(
                    json.dumps({"extracting": len(futures), "workers": workers, "x_displays": displays[:workers]}, ensure_ascii=False),
                    flush=True,
                )
                progress_every = max(1, int(args.progress_every or 25))
                done = 0
                for future in as_completed(futures):
                    try:
                        extraction_results.append(future.result())
                    except Exception as exc:
                        extraction_results.append(
                            {
                                "case_id": str(getattr(future, "_ouragent_case_id", "")),
                                "status": "failed",
                                "error": repr(exc),
                            }
                        )
                    done += 1
                    if done == len(futures) or done % progress_every == 0:
                        print(
                            json.dumps(
                                {
                                    "done": done,
                                    "total": len(futures),
                                    "extracted": sum(1 for item in extraction_results if item.get("status") == "extracted"),
                                    "cached": sum(1 for item in extraction_results if item.get("status") == "cached"),
                                    "failed": sum(1 for item in extraction_results if item.get("status") == "failed"),
                                },
                                ensure_ascii=False,
                            ),
                            flush=True,
                        )
        finally:
            _stop_processes(processes)

    path = write_manifest(cases, eval_set=str(args.eval_set or "valid_seen"), extraction_results=extraction_results)
    failed = [item for item in extraction_results if item.get("status") == "failed"]
    print(
        json.dumps(
            {
                "written": str(path),
                "case_count": len(cases),
                "extraction_results": {
                    "extracted": sum(1 for item in extraction_results if item.get("status") == "extracted"),
                    "cached": sum(1 for item in extraction_results if item.get("status") == "cached"),
                    "failed": len(failed),
                },
                "failed_samples": failed[:5],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
