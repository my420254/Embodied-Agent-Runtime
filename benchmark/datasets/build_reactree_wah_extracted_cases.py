from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from benchmark.reactree.wah.framework.code.adapter import load_tasks
from benchmark.reactree.wah.framework.code.config import load_config
from benchmark.reactree.wah.framework.code.task_environment import build_wah_scene
from benchmark.task_environment_bridge import scene_entity_catalog


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def _runtime_env_state(scene: dict[str, Any]) -> dict[str, Any]:
    return {
        "robot_location": scene.get("robot_location", "未知"),
        "robot_holding": scene.get("robot_inventory") or "空",
    }


def build_reactree_wah_cases() -> Path:
    cfg = load_config()
    cases: list[dict[str, Any]] = []
    env_files: dict[str, str] = {}
    for task in load_tasks(cfg.testset_path):
        env_path = cfg.extracted_envs_root / f"{task.task_id}.json"
        if str(task.task_id) not in env_files:
            scene = build_wah_scene(task.init_graph, task.init_room)
            _write_json(
                env_path,
                {
                    "dataset": "reactree_wah",
                    "task_id": task.task_id,
                    "env_id": task.env_id,
                    "init_room": task.init_room,
                    "source": {
                        "kind": "reactree_case_runtime_scene",
                        "testset_path": str(cfg.testset_path),
                        "extraction": "clean runtime scene from ReAcTree WAH native init_graph",
                    },
                    "flat_initial_environment": {
                        "entity_count": len(scene_entity_catalog(scene)),
                        "room_count": len(scene.get("environment", {})) if isinstance(scene.get("environment"), dict) else 0,
                        "entity_catalog": scene_entity_catalog(scene),
                    },
                    "runtime_initial_environment": {
                        "scene": scene,
                        "env_state": _runtime_env_state(scene),
                    },
                },
            )
            env_files[str(task.task_id)] = str(env_path)
        for instruction_idx, instruction in enumerate(task.nl_instructions):
            case_id = f"{task.task_id}:{instruction_idx}"
            case_input = {
                "dataset": "reactree",
                "benchmark_module": "benchmark.reactree",
                "task_id": task.task_id,
                "task_name": task.task_name,
                "instruction_idx": instruction_idx,
                "instruction": instruction,
                "env_id": task.env_id,
                "init_room": task.init_room,
                "init_graph_cache_path": str(env_path),
                "task_source": "reactree_wah_testset",
                "environment_source": "reactree_case_runtime_scene",
            }
            cases.append(
                {
                    "case_id": case_id,
                    "dataset": "reactree",
                    "input": case_input,
                    "metadata": {
                        "task_id": task.task_id,
                        "task_name": task.task_name,
                        "env_id": task.env_id,
                        "init_room": task.init_room,
                        "instruction_idx": instruction_idx,
                        "node_count": len(task.init_graph.get("nodes", [])),
                        "edge_count": len(task.init_graph.get("edges", [])),
                    },
                    "source_path": task.source_path,
                }
            )
    payload = {
        "dataset": "reactree_wah",
        "source": {
            "native_root": str(cfg.repo_root),
            "testset_path": str(cfg.testset_path),
            "task_source": "dataset/wah_nl_test_rev.json",
            "environment_source": "clean runtime scene from case init_graph/init_room",
        },
        "case_count": len(cases),
        "environment_files": env_files,
        "cases": cases,
    }
    _write_json(cfg.extracted_cases_path, payload)
    return cfg.extracted_cases_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build extracted ReAcTree-WAH cases and init graph caches.")
    parser.parse_args(argv)
    path = build_reactree_wah_cases()
    print(json.dumps({"written": str(path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
