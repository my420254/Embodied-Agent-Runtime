from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from benchmark.eai.behavior.framework.code.adapter import EAIBenchmarkAdapter as BehaviorAdapter
from benchmark.eai.behavior.framework.code.config import load_config as load_behavior_config
from benchmark.eai.virtualhome.framework.code.adapter import (
    load_raw_virtualhome_problems,
    to_case_payload as virtualhome_case_payload,
)
from benchmark.eai.virtualhome.framework.code.config import load_config as load_virtualhome_config
from benchmark.eai.virtualhome.framework.code.translator import (
    parse_action_goals,
    parse_edge_goals,
    parse_node_goals,
    parse_objects_section,
)
from benchmark.datasets.clean_eai_initial_envs import clean_dataset
from config.settings import workspace_path


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def _load_id_to_task(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {str(key): str(value) for key, value in payload.items()} if isinstance(payload, dict) else {}


def _case_id_sort_key(case_id: str) -> tuple[int, str]:
    first = str(case_id).split("_", 1)[0]
    return (int(first) if first.isdigit() else 0, str(case_id))


def build_behavior_cases() -> Path:
    cfg = load_behavior_config()
    cases = BehaviorAdapter(
        cfg.raw_behavior_info_root,
        cfg.initial_envs_root,
        scene_id=cfg.scene_id,
    ).iter_cases()
    payload = {
        "dataset": "eai_behavior",
        "source": {
            "task_source": "embodied-agent-interface behavior_bddl_info",
            "task_source_root": str(cfg.raw_behavior_info_root),
            "environment_source": "igibson_behavior_native_loader",
            "initial_envs_root": str(cfg.initial_envs_root),
        },
        "case_count": len(cases),
        "cases": cases,
    }
    _write_json(cfg.extracted_cases_path, payload)
    return cfg.extracted_cases_path


def build_virtualhome_cases() -> Path:
    cfg = load_virtualhome_config()
    prompt_path = Path(os.getenv("OURAGENT_EAI_OFFICIAL_PROMPT_CACHE", "").strip()) if os.getenv("OURAGENT_EAI_OFFICIAL_PROMPT_CACHE", "").strip() else workspace_path(
        "embodied-agent-interface", "src", "virtualhome_eval", "evaluation",
        "action_sequencing", "prompts", "helm_prompts.json",
    )
    prompt_rows = json.loads(prompt_path.read_text(encoding="utf-8"))
    official_prompts = {
        str(row.get("identifier", "")): str(row.get("llm_prompt", ""))
        for row in prompt_rows if isinstance(row, dict) and row.get("identifier") and row.get("llm_prompt")
    }
    problems = {
        problem.identifier: problem
        for problem in load_raw_virtualhome_problems(
            cfg.raw_problem_pddl_root,
            cfg.id_to_task_path,
            cfg.initial_envs_root,
        )
    }
    id_to_task = _load_id_to_task(cfg.id_to_task_path)
    cases: list[dict[str, Any]] = []
    missing_problem_pddl: list[str] = []
    for case_id in sorted(id_to_task, key=_case_id_sort_key):
        if case_id in problems:
            case = virtualhome_case_payload(problems[case_id], scene_id=cfg.scene_id)
            prompt = official_prompts.get(case_id, "")
            if not prompt:
                raise ValueError(f"official VirtualHome action-sequencing prompt missing for {case_id}")
            objects = parse_objects_section(prompt)
            case["input"].update({
                "official_relevant_objects": objects,
                "official_node_goals": [list(goal) for goal in parse_node_goals(prompt)],
                "official_edge_goals": [list(goal) for goal in parse_edge_goals(prompt)],
                "official_action_goals": parse_action_goals(prompt),
                "official_prompt_cache_path": str(prompt_path),
            })
            cases.append(case)
            continue
        env_path = Path(cfg.initial_envs_root) / f"{case_id}.json"
        if not env_path.exists():
            raise FileNotFoundError(f"missing VirtualHome initial env cache for {case_id}: {env_path}")
        task_name = str(id_to_task.get(case_id) or case_id)
        case_input = {
            "identifier": case_id,
            "instruction": task_name,
            "benchmark_module": "benchmark.eai.virtualhome",
            "dataset": "virtualhome",
            "eval_type": "action_sequencing",
            "scene_id": cfg.scene_id,
            "pddl_objects": [],
            "pddl_goal": [],
            "problem_pddl_status": "missing_in_native_problem_pddl",
            "initial_environment_cache_path": str(env_path),
            "initial_environment_source": "virtualhome_original_init_graph",
            "environment_source": "virtualhome_original_init_graph",
        }
        prompt = official_prompts.get(case_id, "")
        if not prompt:
            raise ValueError(f"official VirtualHome action-sequencing prompt missing for {case_id}")
        case_input.update({
            "official_relevant_objects": parse_objects_section(prompt),
            "official_node_goals": [list(goal) for goal in parse_node_goals(prompt)],
            "official_edge_goals": [list(goal) for goal in parse_edge_goals(prompt)],
            "official_action_goals": parse_action_goals(prompt),
            "official_prompt_cache_path": str(prompt_path),
        })
        cases.append(
            {
                "case_id": case_id,
                "dataset": "eai",
                "input": case_input,
                "metadata": {
                    "scene_id": cfg.scene_id,
                    "task_name": task_name,
                    "source": "virtualhome_initial_env_cache",
                    "problem_pddl_path": "",
                    "problem_pddl_status": "missing_in_native_problem_pddl",
                    "initial_environment_cache_path": str(env_path),
                },
                "source_path": str(cfg.id_to_task_path),
            }
        )
        missing_problem_pddl.append(case_id)

    payload = {
        "dataset": "eai_virtualhome",
        "source": {
            "task_source": "embodied-agent-interface virtualhome id2task plus problem_pddl when present",
            "problem_pddl_root": str(cfg.raw_problem_pddl_root),
            "id_to_task_path": str(cfg.id_to_task_path),
            "environment_source": "virtualhome_original_init_graph",
            "initial_envs_root": str(cfg.initial_envs_root),
            "missing_problem_pddl_case_ids": missing_problem_pddl,
        },
        "case_count": len(cases),
        "cases": cases,
    }
    _write_json(cfg.extracted_cases_path, payload)
    valid_case_ids_path = Path(__file__).resolve().parents[1] / "eai" / "valid_virtualhome_action_sequencing_case_ids.json"
    _write_json(
        valid_case_ids_path,
        [str(case["case_id"]) for case in cases if str(case.get("input", {}).get("problem_pddl_status", "") or "") != "missing_in_native_problem_pddl"],
    )
    return cfg.extracted_cases_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build extracted EAI cases.json files from native task sources and cached initial environments.")
    parser.add_argument("--dataset", choices=("all", "behavior", "virtualhome"), default="all")
    parser.add_argument("--skip-clean-envs", action="store_true", help="Do not rewrite EAI initial env caches into clean runtime scene format.")
    args = parser.parse_args(argv)

    written: list[str] = []
    if args.dataset in {"all", "behavior"}:
        written.append(str(build_behavior_cases()))
    if args.dataset in {"all", "virtualhome"}:
        written.append(str(build_virtualhome_cases()))
    cleaned = []
    if not bool(args.skip_clean_envs):
        datasets = ["behavior", "virtualhome"] if args.dataset == "all" else [str(args.dataset)]
        cleaned = [clean_dataset(dataset) for dataset in datasets]
    print(json.dumps({"written": written, "cleaned": cleaned}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
