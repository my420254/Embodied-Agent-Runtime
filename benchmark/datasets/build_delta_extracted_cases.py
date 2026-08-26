from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from benchmark.delta.framework.code.adapter import PAPER_MAIN_DOMAINS, load_delta_task_specs
from benchmark.delta.framework.code.config import load_config


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def build_delta_cases(*, episodes: int = 50) -> Path:
    cfg = load_config()
    cases: list[dict[str, Any]] = []
    env_files: dict[str, str] = {}
    env_root = cfg.extracted_envs_root
    for spec in load_delta_task_specs(cfg.repo_root, domains=PAPER_MAIN_DOMAINS):
        env_path = env_root / f"{spec.scene}.json"
        if spec.scene not in env_files:
            _write_json(
                env_path,
                {
                    "dataset": "delta",
                    "scene_name": spec.scene,
                    "source": {
                        "kind": "delta_data_scene_graph_py",
                        "native_root": str(cfg.repo_root),
                        "native_module": "data/scene_graph.py",
                    },
                    "scene_graph": spec.scene_graph,
                },
            )
            env_files[spec.scene] = str(env_path)
        for episode in range(1, int(episodes) + 1):
            base_case_id = f"{spec.domain}:{spec.scene}"
            case_id = f"{base_case_id}:episode-{episode:02d}"
            case_input = {
                "dataset": "delta",
                "benchmark_module": "benchmark.delta",
                "task_id": case_id,
                "base_task_id": base_case_id,
                "instruction": spec.goal,
                "domain": spec.domain,
                "scene_name": spec.scene,
                "scene_graph_cache_path": str(env_path),
                "task_source": "delta_data_example_py",
                "environment_source": "delta_data_scene_graph_py",
                "delta_env_state": spec.env_state,
                "add_obj": spec.add_obj,
                "add_act": spec.add_act,
                "episode": episode,
            }
            cases.append(
                {
                    "case_id": case_id,
                    "dataset": "delta",
                    "input": case_input,
                    "metadata": {
                        "domain": spec.domain,
                        "scene": spec.scene,
                        "base_case_id": base_case_id,
                        "episode": episode,
                        "trial_kind": "paper_main_episode",
                    },
                    "source_path": base_case_id,
                }
            )
    payload = {
        "dataset": "delta",
        "source": {
            "native_root": str(cfg.repo_root),
            "task_source": "data/example.py",
            "environment_source": "data/scene_graph.py",
            "episodes_per_domain_scene": int(episodes),
        },
        "case_count": len(cases),
        "environment_files": env_files,
        "cases": cases,
    }
    cases_path = cfg.extracted_cases_path
    _write_json(cases_path, payload)
    return cases_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build extracted DELTA cases and scene graph caches.")
    parser.add_argument("--episodes", type=int, default=50)
    args = parser.parse_args(argv)
    path = build_delta_cases(episodes=int(args.episodes))
    print(json.dumps({"written": str(path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
