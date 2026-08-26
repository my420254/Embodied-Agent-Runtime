from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from benchmark.eai.behavior.framework.code.translator import build_behavior_scene_from_initial_env_cache
from benchmark.eai.virtualhome.framework.code.translator import build_scene_from_initial_env_cache
from domain.scene import flatten_scene


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def _object_map_jsonable(object_map: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in object_map.items():
        if isinstance(value, tuple):
            result[str(name)] = [str(item) for item in value]
        elif isinstance(value, list):
            result[str(name)] = [str(item) for item in value]
        elif isinstance(value, dict):
            result[str(name)] = {str(key): str(item) for key, item in value.items()}
        else:
            result[str(name)] = str(value)
    return result


def _flat_summary(scene: dict[str, Any], *, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    flat = flatten_scene(scene)
    return {
        "entity_count": len(flat),
        "room_count": len(scene.get("environment", {})) if isinstance(scene.get("environment"), dict) else 0,
        "entity_catalog": sorted(flat.keys()),
        **(extra or {}),
    }


def _common_source(cache: dict[str, Any]) -> dict[str, Any]:
    source = cache.get("source", {})
    source = source if isinstance(source, dict) else {}
    keep = (
        "kind",
        "graph_json_key_read",
        "program_lines_read",
        "case_id_alignment",
        "task",
        "task_id",
        "scene_id",
        "seed",
        "randomization",
    )
    return {key: source.get(key) for key in keep if key in source}


def _clean_virtualhome_cache(path: Path, case_input: dict[str, Any]) -> dict[str, Any]:
    cache = _read_json(path)
    scene, env_state, object_map = build_scene_from_initial_env_cache(
        cache,
        preferred_object_names=case_input.get("pddl_objects", []),
        pddl_goal=case_input.get("pddl_goal", []),
        allow_raw_cache=True,
    )
    payload = {
        "dataset": "virtualhome",
        "case_id": str(case_input.get("identifier") or cache.get("case_id") or path.stem),
        "source": {
            **_common_source(cache),
            "native_dataset_entry": "benchmark/datasets/native/eai/virtualhome",
            "extraction": "clean runtime scene from native VirtualHome init_graph",
        },
        "task": cache.get("task", {}) if isinstance(cache.get("task"), dict) else {},
        "flat_initial_environment": _flat_summary(scene),
        "runtime_initial_environment": {
            "scene": scene,
            "env_state": env_state,
            "object_map": _object_map_jsonable(object_map),
        },
    }
    _write_json(path, payload)
    return {"path": str(path), "bytes": path.stat().st_size, "entities": payload["flat_initial_environment"]["entity_count"]}


def _clean_behavior_cache(path: Path, case_input: dict[str, Any]) -> dict[str, Any]:
    cache = _read_json(path)
    scene, env_state, object_map = build_behavior_scene_from_initial_env_cache(cache, allow_raw_cache=True)
    old_flat = cache.get("flat_initial_environment", {}) if isinstance(cache.get("flat_initial_environment"), dict) else {}
    payload = {
        "dataset": "behavior",
        "case_id": str(case_input.get("identifier") or cache.get("case_id") or path.stem),
        "source": {
            **_common_source(cache),
            "native_dataset_entry": "benchmark/datasets/native/eai/behavior",
            "extraction": "clean runtime scene from native BEHAVIOR/iGibson initial state",
        },
        "task": cache.get("task", {}) if isinstance(cache.get("task"), dict) else {},
        "flat_initial_environment": _flat_summary(
            scene,
            extra={
                "name_mapping": old_flat.get("name_mapping", {}) if isinstance(old_flat.get("name_mapping"), dict) else {},
            },
        ),
        "runtime_initial_environment": {
            "scene": scene,
            "env_state": env_state,
            "object_map": _object_map_jsonable(object_map),
        },
    }
    _write_json(path, payload)
    return {"path": str(path), "bytes": path.stat().st_size, "entities": payload["flat_initial_environment"]["entity_count"]}


def _load_cases(dataset: str) -> list[dict[str, Any]]:
    path = Path("benchmark") / "datasets" / "extracted" / "eai" / dataset / "cases.json"
    payload = _read_json(path)
    cases = payload.get("cases", []) if isinstance(payload, dict) else []
    return [case for case in cases if isinstance(case, dict)]


def clean_dataset(dataset: str) -> dict[str, Any]:
    cases = _load_cases(dataset)
    results = []
    for case in cases:
        case_input = case.get("input", {}) if isinstance(case.get("input"), dict) else {}
        cache_path = Path(str(case_input.get("initial_environment_cache_path", "")))
        if not cache_path.exists():
            raise FileNotFoundError(f"missing EAI {dataset} initial env cache: {cache_path}")
        if dataset == "virtualhome":
            results.append(_clean_virtualhome_cache(cache_path, case_input))
        elif dataset == "behavior":
            results.append(_clean_behavior_cache(cache_path, case_input))
        else:
            raise ValueError(f"unsupported EAI dataset: {dataset}")
    return {
        "dataset": dataset,
        "case_count": len(cases),
        "total_cache_bytes": sum(int(item["bytes"]) for item in results),
        "min_cache_bytes": min((int(item["bytes"]) for item in results), default=0),
        "max_cache_bytes": max((int(item["bytes"]) for item in results), default=0),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rewrite EAI initial env caches into clean OurAgent runtime scene caches.")
    parser.add_argument("--dataset", choices=("all", "behavior", "virtualhome"), default="all")
    args = parser.parse_args(argv)
    datasets = ["behavior", "virtualhome"] if args.dataset == "all" else [str(args.dataset)]
    summary = [clean_dataset(dataset) for dataset in datasets]
    print(json.dumps({"cleaned": summary}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
