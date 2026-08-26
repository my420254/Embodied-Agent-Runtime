from __future__ import annotations

import argparse
import json
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from config.json_utils import parse_json_from_llm
from benchmark.eai.behavior.framework.code.config import load_config as load_behavior_config
from benchmark.eai.behavior.framework.code.official_evaluator import (
    dump_outputs as dump_behavior_outputs,
    evaluate_behavior_action_sequencing_outputs,
    official_object_table as behavior_official_object_table,
)
from benchmark.eai.behavior.framework.code.native_actions import (
    SUPPORTED_BEHAVIOR_ACTIONS,
    behavior_official_export_name_map,
    export_behavior_native_plan_for_official_evaluator,
    parse_behavior_native_actions,
)
from benchmark.eai.virtualhome.framework.code.config import load_config as load_virtualhome_config
from benchmark.eai.virtualhome.framework.code.native_actions import (
    export_virtualhome_native_plan_for_official_evaluator,
    parse_virtualhome_native_actions,
)
from benchmark.eai.virtualhome.framework.code.official_evaluator import (
    dump_outputs as dump_virtualhome_outputs,
    evaluate_action_sequencing_outputs,
    official_goal_id_hints as virtualhome_official_goal_id_hints,
    official_object_table as virtualhome_official_object_table,
)
from benchmark.eai.virtualhome.framework.code.translator import _VIRTUALHOME_ACTION_ARITY
from benchmark.datasets.extracted_cases import load_extracted_cases
from benchmark.experiment_utils import (
    ExperimentTimer,
    PROJECT_ROOT,
    chat_completion,
    endpoint_slots,
    load_case_ids_file,
    read_json,
    safe_case_name,
    safe_name,
    select_cases,
    split_cases,
    timestamp,
    write_json,
)
from config.settings import workspace_path


def _result_root(dataset: str, mode: str) -> Path:
    return PROJECT_ROOT / "benchmark" / "eai" / dataset / mode / "results"


def _paper_prompt_path(dataset: str) -> Path:
    override = os.getenv("OURAGENT_EAI_OFFICIAL_PROMPT_CACHE", "").strip()
    if override:
        return Path(override)
    if dataset == "behavior":
        return workspace_path(
            "embodied-agent-interface",
            "src",
            "behavior_eval",
            "evaluation",
            "action_sequencing",
            "resources",
            "prompts",
            "helm_prompts.json",
        )
    return workspace_path(
        "embodied-agent-interface",
        "src",
        "virtualhome_eval",
        "evaluation",
        "action_sequencing",
        "prompts",
        "helm_prompts.json",
    )


def _load_paper_cases(dataset: str) -> list[dict[str, Any]]:
    path = _paper_prompt_path(dataset)
    rows = read_json(path, [])
    cases: list[dict[str, Any]] = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        case_id = str(row.get("identifier", "") or "")
        prompt = str(row.get("llm_prompt", "") or "")
        if not case_id or not prompt:
            continue
        cases.append(
            {
                "case_id": case_id,
                "dataset": dataset,
                "input": {
                    "identifier": case_id,
                    "dataset": dataset,
                    "llm_prompt": prompt,
                    "prompt_source": "eai_action_sequencing_official_prompt",
                },
                "reference": {},
                "metadata": {"source": "paper_method_prompt"},
                "source_path": str(path),
            }
        )
    return cases


def _load_bare_cases(dataset: str) -> list[dict[str, Any]]:
    if dataset == "behavior":
        cfg = load_behavior_config()
        return load_extracted_cases(cfg.extracted_cases_path)
    cfg = load_virtualhome_config()
    return load_extracted_cases(cfg.extracted_cases_path)


def _runtime_environment(case_input: dict[str, Any]) -> dict[str, Any]:
    cache_path_text = str(case_input.get("initial_environment_cache_path", "") or "").strip()
    if not cache_path_text:
        return {}
    cache_path = Path(cache_path_text)
    if not cache_path.is_file():
        return {}
    cache_payload = read_json(cache_path, {})
    runtime = cache_payload.get("runtime_initial_environment", {}) if isinstance(cache_payload, dict) else {}
    return runtime if isinstance(runtime, dict) else {}


def _bare_environment_payload(case_input: dict[str, Any]) -> dict[str, Any]:
    runtime = _runtime_environment(case_input)
    if not runtime:
        raise ValueError(
            "bare baseline requires the extracted initial_environment_cache_path with "
            "runtime_initial_environment.scene/env_state/object_map"
        )
    return {
        "scene": runtime.get("scene", {}),
        "env_state": runtime.get("env_state", {}),
        "object_map": runtime.get("object_map", {}),
    }


def _behavior_raw_prompt(case_input: dict[str, Any]) -> str:
    return "\n".join(
        [
            "You are given one BEHAVIOR action-sequencing task.",
            "Plan directly from the supplied initial symbolic environment and target condition.",
            "Do not use a hidden plan, a simulator result, or any external information.",
            "Output JSON only. Do not explain. Do not use markdown.",
            'Output schema: [{"action": "ACTION_NAME", "object": "exact_object_name"}].',
            f"Allowed action names: {', '.join(sorted(SUPPORTED_BEHAVIOR_ACTIONS))}.",
            "",
            f"Identifier: {case_input.get('identifier', '')}",
            f"Task name: {case_input.get('instruction', '')}",
            "",
            "Target condition:",
            json.dumps(case_input.get("raw_goal_condition", []), ensure_ascii=False, indent=2),
            "",
            "Object categories:",
            json.dumps(case_input.get("name_category", {}), ensure_ascii=False, indent=2),
            "",
            "Initial symbolic environment:",
            json.dumps(_bare_environment_payload(case_input), ensure_ascii=False, indent=2),
        ]
    )


def _virtualhome_raw_prompt(case_input: dict[str, Any]) -> str:
    return "\n".join(
        [
            "You are given one VirtualHome action-sequencing task.",
            "Plan directly from the supplied initial symbolic environment and PDDL goal.",
            "Do not use a hidden plan, a simulator result, or any external information.",
            "Output JSON only. Do not explain. Do not use markdown.",
            'Output schema: [{"action": "ACTION_NAME", "args": ["exact_entity_name", "..."]}].',
            "Every action argument must be an exact object/receptacle entity from the initial environment object catalog.",
            "Do not use room names such as bedroom, home_office, kitchen, or living_room as action arguments.",
            "For WALK/RUN/FIND, target the object you need to interact with, for example WALK couch, not WALK home_office.",
            f"Allowed action arities: {json.dumps(_VIRTUALHOME_ACTION_ARITY, ensure_ascii=False, sort_keys=True)}.",
            "",
            f"Identifier: {case_input.get('identifier', '')}",
            f"Task name: {case_input.get('instruction', '')}",
            "",
            "PDDL objects:",
            json.dumps(case_input.get("pddl_objects", []), ensure_ascii=False, indent=2),
            "",
            "PDDL init:",
            json.dumps(case_input.get("pddl_init", []), ensure_ascii=False, indent=2),
            "",
            "PDDL goal:",
            json.dumps(case_input.get("pddl_goal", []), ensure_ascii=False, indent=2),
            "",
            "Initial symbolic environment:",
            json.dumps(_bare_environment_payload(case_input), ensure_ascii=False, indent=2),
        ]
    )


def _prompt_for_case(mode: str, dataset: str, case: dict[str, Any]) -> str:
    case_input = case.get("input", {}) if isinstance(case.get("input"), dict) else {}
    if mode == "paper_method":
        return str(case_input.get("llm_prompt", "") or "")
    if dataset == "behavior":
        return _behavior_raw_prompt(case_input)
    return _virtualhome_raw_prompt(case_input)


def _normalize_output(dataset: str, case_id: str, raw_text: str, case_input: dict[str, Any]) -> str:
    normalized_case_input = dict(case_input)
    if dataset == "virtualhome" and not str(normalized_case_input.get("initial_environment_cache_path", "") or "").strip():
        normalized_case_input["initial_environment_cache_path"] = str(load_virtualhome_config().initial_envs_root / f"{case_id}.json")
    runtime = _runtime_environment(normalized_case_input)
    current_env = runtime.get("object_map", {}) if isinstance(runtime, dict) else {}
    if dataset == "behavior":
        try:
            _, native_plan = parse_behavior_native_actions(raw_text, current_env=current_env)
        except Exception:
            return raw_text
        name_category = case_input.get("name_category", {})
        official_export_map = behavior_official_export_name_map(
            official_object_table=behavior_official_object_table(case_id),
            name_category=name_category if isinstance(name_category, dict) else {},
        )
        return export_behavior_native_plan_for_official_evaluator(
            native_plan,
            official_export_name_map=official_export_map,
        )
    if dataset == "virtualhome":
        validation_env = dict(current_env) if isinstance(current_env, dict) else {}
        for name in normalized_case_input.get("pddl_objects", []) or []:
            text = str(name or "").strip()
            if text:
                validation_env.setdefault(text, ["", ""])
        try:
            _, native_plan = parse_virtualhome_native_actions(raw_text, current_env=validation_env)
        except Exception:
            try:
                parsed = parse_json_from_llm(raw_text)
                if not isinstance(parsed, dict):
                    return raw_text
                normalized_steps = [
                    {"action": str(action).upper(), "args": args if isinstance(args, list) else [args]}
                    for action, args in parsed.items()
                ]
                _, native_plan = parse_virtualhome_native_actions(
                    json.dumps(normalized_steps, ensure_ascii=False),
                    current_env=validation_env,
                )
            except Exception:
                return raw_text
        cache_path = str(normalized_case_input.get("initial_environment_cache_path", "") or "").strip()
        return export_virtualhome_native_plan_for_official_evaluator(
            native_plan,
            official_object_table=virtualhome_official_object_table(
                case_id,
                initial_environment_cache_path=cache_path,
            ),
            preferred_ids_by_base=virtualhome_official_goal_id_hints(
                case_id,
                initial_environment_cache_path=cache_path,
            ),
        )
    return raw_text


def _run_case(
    *,
    mode: str,
    dataset: str,
    run_root: Path,
    case: dict[str, Any],
    slot: dict[str, Any],
    max_tokens: int,
    temperature: float,
    dry_run: bool,
    resume: bool,
) -> dict[str, Any]:
    case_id = str(case["case_id"])
    case_root = run_root / "cases" / safe_case_name(case_id)
    prompt = _prompt_for_case(mode, dataset, case)
    prompt_path = case_root / "prompt.md"
    raw_path = case_root / "raw_output.json"
    meta_path = case_root / "case.json"
    if resume:
        existing = read_json(meta_path, {})
        if isinstance(existing, dict) and existing.get("status") == "done":
            return {**existing, "skipped": True}
    write_json(case_root / "input.json", case)
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding="utf-8")
    if dry_run:
        payload = {
            "mode": mode,
            "dataset": dataset,
            "case_id": case_id,
            "status": "dry_run",
            "prompt": str(prompt_path),
            "source_path": case.get("source_path", ""),
            "api_base": slot["api_base"],
            "api_model": slot["api_model"],
        }
        write_json(raw_path, payload)
        write_json(meta_path, payload)
        return payload
    raw_text = chat_completion(
        prompt=prompt,
        api_base=str(slot["api_base"]),
        api_key=str(slot["api_key"]),
        model_name=str(slot["api_model"]),
        max_tokens=max_tokens,
        temperature=temperature,
    )
    llm_output = _normalize_output(dataset, case_id, raw_text, case.get("input", {}) if isinstance(case.get("input"), dict) else {})
    output_item = {"identifier": case_id, "llm_output": llm_output}
    payload = {
        "mode": mode,
        "dataset": dataset,
        "case_id": case_id,
        "status": "done",
        "prompt": str(prompt_path),
        "raw_response": raw_text,
        "evaluator_output": output_item,
        "source_path": case.get("source_path", ""),
        "api_base": slot["api_base"],
        "api_model": slot["api_model"],
        "prompt_chars": len(prompt),
        "updated_at": timestamp(),
    }
    write_json(raw_path, payload)
    write_json(meta_path, payload)
    return payload


def _evaluate(dataset: str, run_root: Path, run_name: str, outputs: list[dict[str, Any]], *, skip_eval: bool) -> dict[str, Any]:
    generated_root = run_root / "artifacts" / "generated"
    evaluated_root = run_root / "artifacts" / "evaluated"
    if dataset == "behavior":
        output_path = generated_root / "behavior" / "action_sequencing" / f"{run_name}_outputs.json"
        dump_behavior_outputs(output_path, outputs)
        eval_summary = {} if skip_eval else evaluate_behavior_action_sequencing_outputs(
            llm_response_root=generated_root,
            evaluate_output_root=evaluated_root,
        )
    else:
        output_path = generated_root / "virtualhome" / "action_sequencing" / f"{run_name}_outputs.json"
        dump_virtualhome_outputs(output_path, outputs)
        eval_summary = {} if skip_eval else evaluate_action_sequencing_outputs(
            llm_response_root=generated_root,
            evaluate_output_root=evaluated_root,
            scene_id=load_virtualhome_config().scene_id,
        )
    return {
        "generated_output": str(output_path),
        "evaluated_root": str(evaluated_root),
        "official_evaluation": eval_summary,
    }


def _summary(run_root: Path, rows: list[dict[str, Any]], evaluation: dict[str, Any]) -> dict[str, Any]:
    summary = {
        "run_name": run_root.name,
        "total_cases": len(rows),
        "done_cases": sum(1 for row in rows if row.get("status") == "done"),
        "failed_cases": sum(1 for row in rows if row.get("status") == "failed"),
        **evaluation,
        "cases": rows,
    }
    write_json(run_root / "merged_results.json", rows)
    write_json(run_root / "summary.json", summary)
    return summary


def _parser(dataset: str, mode: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=f"Run EAI {dataset} {mode}.")
    parser.add_argument("--ports", nargs="*", type=int, default=[])
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--run-name", default="")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-eval", action="store_true")
    parser.add_argument("--valid-only", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--case-ids-file", default="")
    parser.add_argument("--api-model", default="")
    parser.add_argument("--api-key", default="")
    parser.add_argument("--max-tokens", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=None)
    return parser


def _is_valid_virtualhome_case(case: dict[str, Any]) -> bool:
    case_input = case.get("input", {}) if isinstance(case.get("input"), dict) else {}
    return str(case_input.get("problem_pddl_status", "") or "") != "missing_in_native_problem_pddl"


def main_for(dataset: str, mode: str, argv: list[str] | None = None) -> int:
    parser = _parser(dataset, mode)
    args = parser.parse_args(argv)
    run_name = safe_name(args.run_name or f"{mode}_full")
    run_root = _result_root(dataset, mode) / run_name
    if args.summary:
        print(json.dumps(read_json(run_root / "summary.json", {}), ensure_ascii=False, indent=2))
        return 0
    if args.reset and run_root.exists():
        shutil.rmtree(run_root)
    experiment_timer = ExperimentTimer(run_root, {"runner": "eai_external", "dataset": dataset, "mode": mode, "resume": bool(args.resume)})

    cases = _load_paper_cases(dataset) if mode == "paper_method" else _load_bare_cases(dataset)
    if args.valid_only:
        if dataset != "virtualhome":
            parser.error("--valid-only is only defined for EAI VirtualHome")
        valid_ids = {
            str(case.get("case_id", "") or "")
            for case in _load_bare_cases("virtualhome")
            if _is_valid_virtualhome_case(case)
        }
        cases = [case for case in cases if str(case.get("case_id", "") or "") in valid_ids]
    requested_ids = [*args.case_id, *load_case_ids_file(args.case_ids_file)]
    cases = select_cases(cases, case_ids=requested_ids, limit=args.limit)
    slots = endpoint_slots(args.ports, workers=args.workers, module="planning", api_model=args.api_model, api_key=args.api_key)
    max_tokens = int(args.max_tokens if args.max_tokens is not None else slots[0].get("max_tokens", 4096))
    temperature = float(args.temperature if args.temperature is not None else slots[0].get("temperature", 0.0))
    worker_count = max(1, int(args.workers or 1))
    chunks = split_cases(cases, worker_count)
    write_json(
        run_root / "manifest.json",
        {
            "mode": mode,
            "dataset": dataset,
            "run_name": run_name,
            "run_root": str(run_root),
            "ports": args.ports,
            "workers": worker_count,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "case_count": len(cases),
            "case_ids": [case["case_id"] for case in cases],
            "input_regime": "official_action_sequencing_prompt_cache"
            if mode == "paper_method"
            else "extracted_runtime_environment",
            "valid_only": bool(args.valid_only),
            "started_at": timestamp(),
        },
    )
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
                        dataset=dataset,
                        run_root=run_root,
                        case=case,
                        slot=slot,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        dry_run=bool(args.dry_run),
                        resume=bool(args.resume),
                    )
                )
        for future in as_completed(futures):
            rows.append(future.result())
    rows.sort(key=lambda item: str(item.get("case_id", "")))
    eval_outputs = [row["evaluator_output"] for row in rows if isinstance(row.get("evaluator_output"), dict)]
    evaluation = {"generated_output": "", "evaluated_root": "", "official_evaluation": {}}
    if eval_outputs:
        evaluation = _evaluate(dataset, run_root, run_name, eval_outputs, skip_eval=bool(args.skip_eval))
    summary = _summary(run_root, rows, evaluation)
    experiment_timer.finish("dry_run" if args.dry_run else "completed", {"case_count": len(rows), "worker_count": worker_count})
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0
