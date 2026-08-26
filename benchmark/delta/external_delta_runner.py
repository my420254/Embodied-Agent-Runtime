from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from config.json_utils import parse_json_from_llm
from benchmark.datasets.extracted_cases import load_extracted_cases
from benchmark.delta.framework.code.adapter import PAPER_MAIN_DOMAINS, load_delta_task_specs
from benchmark.delta.framework.code.config import load_config as load_delta_config
from benchmark.delta.framework.code.native_actions import (
    delta_action_contract_lines,
    delta_native_plan_to_execution_calls,
    parse_delta_native_actions,
)
from benchmark.delta.framework.code.official_evaluator import evaluate_delta_goals
from benchmark.delta.framework.code.task_environment import load_delta_scene_graph
from benchmark.experiment_utils import (
    ExperimentTimer,
    PROJECT_ROOT,
    WORKSPACE_ROOT,
    chat_completion,
    clear_proxy_env,
    endpoint_slots,
    load_case_ids_file,
    read_json,
    run_subprocess,
    safe_case_name,
    safe_name,
    select_cases,
    split_cases,
    timestamp,
    write_json,
)


ALL_DOMAINS = ("clean", "dining", "pc", "office")
ALL_SCENES = ("allensville", "shelbiana", "parole")


def _delta_python() -> str:
    return os.getenv("DELTA_PYTHON", str(WORKSPACE_ROOT / "envs" / "delta_py38" / "bin" / "python"))


def _delta_repo_root() -> Path:
    return Path(os.getenv("DELTA_REPO_ROOT", str(WORKSPACE_ROOT / "DELTA"))).resolve()


def _result_root(mode: str) -> Path:
    return PROJECT_ROOT / "benchmark" / "delta" / mode / "results"


def _shim_root(mode: str) -> Path:
    return PROJECT_ROOT / "benchmark" / "delta" / mode / "shims"


def _case_id(domain: str, scene: str) -> str:
    return f"{domain}:{scene}"


def _iter_cases(domains: list[str], scenes: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "case_id": _case_id(domain, scene),
            "domain": domain,
            "scene": scene,
            "input": {"domain": domain, "scene": scene},
        }
        for domain in domains
        for scene in scenes
    ]


def _load_bare_cases(domains: list[str], scenes: list[str]) -> list[dict[str, Any]]:
    selected_domains = {str(domain).strip().lower() for domain in domains if str(domain).strip()}
    selected_scenes = {str(scene).strip().lower() for scene in scenes if str(scene).strip()}
    cases = load_extracted_cases(load_delta_config().extracted_cases_path)
    selected: list[dict[str, Any]] = []
    for case in cases:
        metadata = case.get("metadata", {}) if isinstance(case.get("metadata"), dict) else {}
        domain = str(metadata.get("domain") or "").strip().lower()
        scene = str(metadata.get("scene") or "").strip().lower()
        if selected_domains and domain not in selected_domains:
            continue
        if selected_scenes and scene not in selected_scenes:
            continue
        selected.append(case)
    return selected


def _parse_success_rate(log_path: Path) -> float | None:
    if not log_path.exists():
        return None
    text = log_path.read_text(encoding="utf-8", errors="ignore")
    matches = re.findall(r"Success rate[^:]*:\s*([0-9.]+)", text)
    if not matches:
        return None
    try:
        return float(matches[-1])
    except ValueError:
        return None


def _delta_goal_pddls(case_input: dict[str, Any]) -> list[str]:
    domain = str(case_input.get("domain", "") or "").strip()
    scene_name = str(case_input.get("scene_name", "") or "").strip()
    if not domain or not scene_name:
        raise ValueError("DELTA case input must include domain and scene_name for evaluator lookup")
    for spec in load_delta_task_specs(load_delta_config().repo_root, domains=PAPER_MAIN_DOMAINS):
        if spec.domain == domain and spec.scene == scene_name:
            return list(spec.subgoal_pddl)
    raise ValueError(f"DELTA native task not found for domain={domain!r}, scene_name={scene_name!r}")


def _delta_bare_prompt(case_input: dict[str, Any]) -> str:
    domain = str(case_input.get("domain", "") or "").strip().lower()
    scene_graph = load_delta_scene_graph(case_input)
    return "\n".join(
        [
            "You are given one DELTA robot planning task.",
            "Plan directly from the public task fields and the initial scene graph.",
            "Output JSON only. Do not explain. Do not use markdown.",
            "Output schema: a JSON list of DELTA official action objects.",
            'Each step must be an object in braces, for example [{"action":"goto","agent":"robot","room_1":"living_room","room_2":"kitchen"}].',
            "Do not output one JSON block per step. Do not use arrays for action objects.",
            "Use exact room and object names from the scene graph.",
            "Do not use hidden subgoals, ground-truth plans, evaluator output, simulator results, or external information.",
            "",
            f"Case id: {case_input.get('task_id', '')}",
            f"Domain: {domain}",
            f"Scene: {case_input.get('scene_name', '')}",
            f"Instruction: {case_input.get('instruction', '')}",
            "",
            "Allowed DELTA action object schemas:",
            *delta_action_contract_lines(domain),
            "",
            "Public domain predicate descriptions:",
            json.dumps(case_input.get("delta_env_state", []), ensure_ascii=False, indent=2),
            "",
            "Public additional action descriptions:",
            json.dumps(case_input.get("add_act", []), ensure_ascii=False, indent=2),
            "",
            "Initial scene graph:",
            json.dumps(scene_graph, ensure_ascii=False, indent=2),
        ]
    )


def _strip_code_fence(text: str) -> str:
    cleaned = str(text or "").strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[A-Za-z0-9_-]*\n", "", cleaned)
        cleaned = re.sub(r"\n```$", "", cleaned)
    return cleaned.strip()


def _coerce_delta_actions_json(raw_text: str) -> str:
    stripped = _strip_code_fence(raw_text)
    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, list):
            return json.dumps(parsed, ensure_ascii=False)
        if isinstance(parsed, dict) and isinstance(parsed.get("actions"), list):
            return json.dumps(parsed["actions"], ensure_ascii=False)
    except Exception:
        pass
    repaired = _repair_delta_pseudo_action_blocks(raw_text)
    if repaired:
        return json.dumps(repaired, ensure_ascii=False)
    try:
        parsed = parse_json_from_llm(raw_text)
        if isinstance(parsed, list):
            return json.dumps(parsed, ensure_ascii=False)
        if isinstance(parsed, dict) and isinstance(parsed.get("actions"), list):
            return json.dumps(parsed["actions"], ensure_ascii=False)
    except Exception:
        pass
    return raw_text


def _repair_delta_pseudo_action_blocks(raw_text: str) -> list[dict[str, str]]:
    repaired: list[dict[str, str]] = []
    block_pattern = re.compile(r"\[\s*\"([A-Za-z_][\w-]*)\"\s*,(?P<body>.*?)\]", re.DOTALL)
    pair_pattern = re.compile(r"\"([A-Za-z_][\w-]*)\"\s*:\s*\"([^\"]*)\"")
    for match in block_pattern.finditer(str(raw_text or "")):
        action = str(match.group(1) or "").strip().lower()
        pairs = {str(key): str(value) for key, value in pair_pattern.findall(match.group("body") or "")}
        if action and pairs:
            repaired.append({"action": action, **pairs})
    return repaired


def _run_bare_case(
    *,
    run_root: Path,
    case: dict[str, Any],
    slot: dict[str, Any],
    max_tokens: int,
    temperature: float,
    resume: bool,
    dry_run: bool,
) -> dict[str, Any]:
    case_id = str(case["case_id"])
    case_input = case.get("input", {}) if isinstance(case.get("input"), dict) else {}
    case_root = run_root / "cases" / safe_case_name(case_id)
    prompt_path = case_root / "prompt.md"
    raw_path = case_root / "raw_output.json"
    meta_path = case_root / "case.json"
    if resume:
        existing = read_json(meta_path, {})
        if isinstance(existing, dict) and existing.get("status") == "done":
            return {**existing, "skipped": True}

    prompt = _delta_bare_prompt(case_input)
    write_json(case_root / "input.json", case)
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding="utf-8")
    base_payload = {
        "mode": "bare_baseline",
        "dataset": "delta",
        "case_id": case_id,
        "prompt": str(prompt_path),
        "source_path": case.get("source_path", ""),
        "api_base": slot["api_base"],
        "api_model": slot["api_model"],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if dry_run:
        payload = {**base_payload, "status": "dry_run"}
        write_json(raw_path, payload)
        write_json(meta_path, payload)
        return payload

    try:
        raw_text = chat_completion(
            prompt=prompt,
            api_base=str(slot["api_base"]),
            api_key=str(slot["api_key"]),
            model_name=str(slot["api_model"]),
            max_tokens=max_tokens,
            temperature=temperature,
        )
    except Exception as exc:
        payload = {
            **base_payload,
            "status": "failed",
            "error": f"{type(exc).__name__}: {exc}",
            "updated_at": timestamp(),
        }
        write_json(raw_path, payload)
        write_json(meta_path, payload)
        return payload

    parse_error = ""
    normalized_text = _coerce_delta_actions_json(raw_text)
    native_plan: list[dict[str, Any]] = []
    try:
        _, native_plan = parse_delta_native_actions(normalized_text, state=case_input)
    except Exception as exc:
        parse_error = f"{type(exc).__name__}: {exc}"

    evaluator_execution_calls = delta_native_plan_to_execution_calls(native_plan) if native_plan else []
    try:
        prediction = evaluate_delta_goals(
            load_delta_scene_graph(case_input),
            evaluator_execution_calls,
            _delta_goal_pddls(case_input),
        )
    except Exception as exc:
        prediction = {
            "evaluation_mode": "delta_symbolic_goal_verifier",
            "success": False,
            "goal_success_rate": 0.0,
            "error": f"{type(exc).__name__}: {exc}",
        }
    success = bool(prediction.get("success")) or float(prediction.get("goal_success_rate", 0.0) or 0.0) >= 1.0
    payload = {
        **base_payload,
        "status": "done",
        "success": success,
        "raw_response": raw_text,
        "normalized_response": normalized_text,
        "parse_error": parse_error,
        "official_actions": native_plan,
        "official_actions_len": len(native_plan),
        "evaluator_execution_calls": evaluator_execution_calls,
        "prediction": prediction,
        "goal_success_rate": float(prediction.get("goal_success_rate", 0.0) or 0.0),
        "updated_at": timestamp(),
    }
    write_json(raw_path, payload)
    write_json(meta_path, payload)
    return payload


def _build_command(mode: str, *, model: str, episodes: int, domain: str, scene: str, max_time: float, temperature: float) -> list[str]:
    if mode == "bare_baseline":
        return [
            _delta_python(),
            "baselines/llm_as_planner.py",
            "-m",
            model,
            "-t",
            str(temperature),
            "-e",
            str(episodes),
            "-d",
            domain,
            "-s",
            scene,
        ]
    return [
        _delta_python(),
        "-c",
        "import sys; sys.path.pop(0); exec(open('delta.py').read())",
        "-m",
        model,
        "-t",
        str(temperature),
        "-e",
        str(episodes),
        "-d",
        domain,
        "-s",
        scene,
        "--max-time",
        str(max_time),
    ]


def _run_case(
    *,
    mode: str,
    run_root: Path,
    run_name: str,
    case: dict[str, Any],
    slot: dict[str, Any],
    episodes: int,
    max_time: float,
    resume: bool,
    dry_run: bool,
) -> dict[str, Any]:
    if mode == "bare_baseline":
        return _run_bare_case(
            run_root=run_root,
            case=case,
            slot=slot,
            max_tokens=int(slot.get("max_tokens", 4096)),
            temperature=float(slot.get("temperature", 0.0)),
            resume=resume,
            dry_run=dry_run,
        )

    domain = str(case["domain"])
    scene = str(case["scene"])
    case_id = str(case["case_id"])
    case_root = run_root / "cases" / safe_case_name(case_id)
    raw_path = case_root / "raw_output.json"
    meta_path = case_root / "case.json"
    log_path = case_root / "run.log"
    artifact_root = case_root / "artifacts"
    if resume:
        existing = read_json(meta_path, {})
        if isinstance(existing, dict) and existing.get("status") == "done":
            return {**existing, "skipped": True}

    model = str(slot["api_model"])
    max_tokens = int(slot.get("max_tokens", 4096))
    temperature = float(slot.get("temperature", 0.0))
    command = _build_command(mode, model=model, episodes=episodes, domain=domain, scene=scene, max_time=max_time, temperature=temperature)
    payload = {
        "mode": mode,
        "case_id": case_id,
        "domain": domain,
        "scene": scene,
        "status": "dry_run" if dry_run else "running",
        "input": {"domain": domain, "scene": scene, "episodes": episodes, "temperature": temperature, "max_tokens": max_tokens},
        "api_base": slot["api_base"],
        "api_model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "command": command,
        "log": str(log_path),
        "raw_output": str(raw_path),
        "artifacts": [str(artifact_root)],
        "started_at": timestamp(),
    }
    write_json(meta_path, payload)
    if dry_run:
        write_json(raw_path, payload)
        return payload

    env = clear_proxy_env()
    env["PYTHONPATH"] = f"{_shim_root(mode)}:{env.get('PYTHONPATH', '')}"
    env["DELTA_VLLM_BASE_URL"] = str(slot["api_base"])
    env["DELTA_VLLM_API_KEY"] = str(slot["api_key"])
    env["DELTA_VLLM_MODEL"] = model
    env["DELTA_VLLM_MAX_NEW_TOKENS"] = str(max_tokens)
    env["DELTA_VLLM_TIMEOUT_SEC"] = os.getenv("DELTA_VLLM_TIMEOUT_SEC", "900")
    env["DELTA_RESULT_ROOT"] = str(artifact_root)
    env["DELTA_RUN_TAG"] = f"{run_name}_{safe_case_name(case_id)}"
    env["PYTHONUNBUFFERED"] = "1"

    rc = run_subprocess(command, cwd=_delta_repo_root(), env=env, log_path=log_path)
    success_rate = _parse_success_rate(log_path)
    success_count = int(round((success_rate or 0.0) * episodes / 100.0)) if success_rate is not None else 0
    payload.update(
        {
            "status": "done" if rc == 0 else "failed",
            "returncode": rc,
            "success_rate": success_rate,
            "success_count": success_count,
            "episodes_completed": episodes if rc == 0 else 0,
            "updated_at": timestamp(),
        }
    )
    write_json(raw_path, payload)
    write_json(meta_path, payload)
    return payload


def _summary(run_root: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    total_episodes = sum(int(row.get("episodes_completed", 0) or 0) for row in rows)
    success_episodes = sum(int(row.get("success_count", 0) or 0) for row in rows)
    completed_rows = [row for row in rows if row.get("status") == "done"]
    success_cases = sum(1 for row in completed_rows if bool(row.get("success", False)))
    goal_rates = [
        float(row.get("goal_success_rate", (row.get("prediction", {}) if isinstance(row.get("prediction"), dict) else {}).get("goal_success_rate", 0.0)) or 0.0)
        for row in completed_rows
    ]
    summary = {
        "run_name": run_root.name,
        "total_cases": len(rows),
        "done_cases": sum(1 for row in rows if row.get("status") == "done"),
        "failed_cases": sum(1 for row in rows if row.get("status") == "failed"),
        "success_cases": success_cases,
        "case_success_rate": (success_cases / len(completed_rows) * 100.0) if completed_rows else 0.0,
        "goal_success_rate": (sum(goal_rates) / len(goal_rates)) if goal_rates else 0.0,
        "total_episodes": total_episodes,
        "success_episodes": success_episodes,
        "success_rate": (success_episodes / total_episodes * 100.0) if total_episodes else 0.0,
        "cases": rows,
    }
    write_json(run_root / "merged_results.json", rows)
    write_json(run_root / "summary.json", summary)
    return summary


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--ports", nargs="*", type=int, default=[])
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--run-name", default="")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--case-ids-file", default="")
    parser.add_argument("--domain", action="append", default=[])
    parser.add_argument("--scene", action="append", default=[])
    parser.add_argument("--episodes", type=int, default=50)
    parser.add_argument("--max-time", type=float, default=60.0)
    parser.add_argument("--api-model", default="")
    parser.add_argument("--api-key", default="")
    parser.add_argument("--reset", action="store_true")
    return parser


def main_for_mode(mode: str, argv: list[str] | None = None) -> int:
    args = build_parser(f"Run DELTA {mode}.").parse_args(argv)
    run_name = safe_name(args.run_name or f"{mode}_full")
    run_root = _result_root(mode) / run_name
    if args.summary:
        print(json.dumps(read_json(run_root / "summary.json", {}), ensure_ascii=False, indent=2))
        return 0
    if args.reset and run_root.exists():
        shutil.rmtree(run_root)
    experiment_timer = ExperimentTimer(run_root, {"runner": "delta_external", "mode": mode, "resume": bool(args.resume)})

    domains = args.domain or list(ALL_DOMAINS)
    scenes = args.scene or list(ALL_SCENES)
    requested_ids = [*args.case_id, *load_case_ids_file(args.case_ids_file)]
    cases = (
        _load_bare_cases(domains, scenes)
        if mode == "bare_baseline"
        else _iter_cases(domains, scenes)
    )
    cases = select_cases(cases, case_ids=requested_ids, limit=args.limit)
    slots = endpoint_slots(args.ports, workers=args.workers, module="planning", api_model=args.api_model, api_key=args.api_key)
    worker_count = max(1, int(args.workers or 1))
    chunks = split_cases(cases, worker_count)
    manifest = {
        "mode": mode,
        "run_name": run_name,
        "run_root": str(run_root),
        "ports": args.ports,
        "workers": worker_count,
        "episodes": args.episodes,
        "case_count": len(cases),
        "input_regime": "extracted_delta_cases_direct_native_actions"
        if mode == "bare_baseline"
        else "delta_external_paper_domain_scene",
        "endpoint_slots": [
            {
                "port": slot.get("port"),
                "api_base": slot.get("api_base"),
                "api_model": slot.get("api_model"),
                "max_tokens": slot.get("max_tokens"),
                "temperature": slot.get("temperature"),
            }
            for slot in slots
        ],
        "case_ids": [case["case_id"] for case in cases],
        "started_at": timestamp(),
    }
    write_json(run_root / "manifest.json", manifest)

    rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=worker_count) as pool:
        futures = []
        for index, chunk in enumerate(chunks):
            slot = slots[index % len(slots)]
            for case in chunk:
                futures.append(
                    pool.submit(
                        _run_case,
                        mode=mode,
                        run_root=run_root,
                        run_name=run_name,
                        case=case,
                        slot=slot,
                        episodes=int(args.episodes),
                        max_time=float(args.max_time),
                        resume=bool(args.resume),
                        dry_run=bool(args.dry_run),
                    )
                )
        for future in as_completed(futures):
            rows.append(future.result())
    rows.sort(key=lambda item: str(item.get("case_id", "")))
    summary = _summary(run_root, rows)
    experiment_timer.finish("dry_run" if args.dry_run else "completed", {"case_count": len(rows), "worker_count": worker_count})
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0
