from __future__ import annotations

import argparse
import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from benchmark.eai.behavior.framework.code.translator import build_behavior_scene_from_initial_env_cache
from benchmark.eai.virtualhome.framework.code.translator import build_scene_from_prompt
from domain.scene import flatten_scene
from config.settings import workspace_path


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


@lru_cache(maxsize=1)
def _behavior_taxonomy_abilities() -> tuple[Path, dict[str, dict[str, Any]]]:
    override = os.getenv("OURAGENT_BDDL_TAXONOMY", "").strip()
    path = Path(override) if override else Path(
        "/data/zmy/envs/eai-eval/lib/python3.8/site-packages/bddl/hierarchy_owned.json"
    )
    payload = _read_json(path)
    abilities: dict[str, dict[str, Any]] = {}

    def walk(node: Any) -> None:
        if not isinstance(node, dict):
            return
        name = str(node.get("name") or "").strip()
        raw = node.get("abilities")
        if name and isinstance(raw, dict):
            abilities[name] = raw
        for child in node.get("children", []) if isinstance(node.get("children"), list) else []:
            walk(child)

    walk(payload)
    return path, abilities


def _inject_behavior_abilities(
    scene: dict[str, Any], object_map: dict[str, Any], abilities_by_category: dict[str, dict[str, Any]]
) -> None:
    categories = {
        str(name): str(info.get("category") or "")
        for name, info in object_map.items()
        if isinstance(info, dict)
    }

    def walk(node: Any) -> None:
        if not isinstance(node, dict):
            return
        environment = node.get("environment")
        if isinstance(environment, dict):
            for room in environment.values():
                walk(room)
        contains = node.get("contains")
        if isinstance(contains, dict):
            for name, child in contains.items():
                if isinstance(child, dict):
                    category = categories.get(str(name), "")
                    raw = abilities_by_category.get(category, {})
                    child["abilities"] = sorted(str(key) for key in raw)
                    walk(child)

    walk(scene)


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


@lru_cache(maxsize=1)
def _official_virtualhome_prompts() -> tuple[Path, dict[str, str]]:
    override = os.getenv("OURAGENT_EAI_OFFICIAL_PROMPT_CACHE", "").strip()
    prompt_path = Path(override) if override else workspace_path(
        "embodied-agent-interface", "src", "virtualhome_eval", "evaluation",
        "action_sequencing", "prompts", "helm_prompts.json",
    )
    rows = _read_json(prompt_path)
    prompts = {
        str(row.get("identifier", "")): str(row.get("llm_prompt", ""))
        for row in rows if isinstance(row, dict) and row.get("identifier") and row.get("llm_prompt")
    }
    return prompt_path, prompts


def _attach_virtualhome_close_edges(
    scene: dict[str, Any], object_map: dict[str, tuple[str, str]], case_id: str
) -> int:
    native_graph = workspace_path(
        "embodied-agent-interface", "src", "virtualhome_eval", "dataset",
        "programs_processed_precond_nograb_morepreconds", "init_and_final_graphs",
        "TrimmedTestScene1_graph", "results_intentions_march-13-18", f"file{case_id}.json",
    )
    if not native_graph.exists():
        return 0
    payload = _read_json(native_graph)
    edges = payload.get("init_graph", {}).get("edges", []) if isinstance(payload, dict) else []
    canonical_by_id = {str(value[1]): str(name) for name, value in object_map.items() if len(value) >= 2}
    nearby: dict[str, set[str]] = {name: set() for name in object_map}
    for edge in edges if isinstance(edges, list) else []:
        if not isinstance(edge, dict) or str(edge.get("relation_type", "")).upper() != "CLOSE":
            continue
        left = canonical_by_id.get(str(edge.get("from_id", "")))
        right = canonical_by_id.get(str(edge.get("to_id", "")))
        if left and right and left != right:
            nearby[left].add(right)
            nearby[right].add(left)

    def walk(node: Any) -> None:
        if not isinstance(node, dict):
            return
        for key, value in node.items():
            if not isinstance(value, dict):
                continue
            if key in nearby and nearby[key]:
                value["nearby"] = sorted(nearby[key])
            walk(value)

    walk(scene)
    return sum(bool(values) for values in nearby.values())


def _clean_virtualhome_cache(path: Path, case_input: dict[str, Any]) -> dict[str, Any]:
    cache = _read_json(path)
    prompt_path, prompts = _official_virtualhome_prompts()
    case_id = str(case_input.get("identifier") or cache.get("case_id") or path.stem)
    prompt = prompts.get(case_id, "")
    if not prompt:
        raise ValueError(f"official VirtualHome action-sequencing prompt missing for {case_id}")
    scene, env_state, object_map = build_scene_from_prompt(prompt)
    close_edge_entity_count = _attach_virtualhome_close_edges(scene, object_map, case_id)
    payload = {
        "dataset": "virtualhome",
        "case_id": case_id,
        "source": {
            **_common_source(cache),
            "native_dataset_entry": "benchmark/datasets/native/eai/virtualhome",
            "extraction": "runtime scene from official VirtualHome action-sequencing prompt current state",
            "official_prompt_cache": str(prompt_path),
            "initial_close_edges": "native init_graph restricted to official relevant object ids",
        },
        "task": {
            **(cache.get("task", {}) if isinstance(cache.get("task"), dict) else {}),
            "official_node_goals": case_input.get("official_node_goals", []),
            "official_edge_goals": case_input.get("official_edge_goals", []),
            "official_action_goals": case_input.get("official_action_goals", []),
        },
        "flat_initial_environment": _flat_summary(
            scene, extra={"close_edge_entity_count": close_edge_entity_count}
        ),
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
    taxonomy_path, abilities_by_category = _behavior_taxonomy_abilities()
    _inject_behavior_abilities(scene, object_map, abilities_by_category)
    old_flat = cache.get("flat_initial_environment", {}) if isinstance(cache.get("flat_initial_environment"), dict) else {}
    payload = {
        "dataset": "behavior",
        "case_id": str(case_input.get("identifier") or cache.get("case_id") or path.stem),
        "source": {
            **_common_source(cache),
            "native_dataset_entry": "benchmark/datasets/native/eai/behavior",
            "extraction": "clean runtime scene from native BEHAVIOR/iGibson initial state",
            "object_abilities": f"official BDDL owned taxonomy: {taxonomy_path}",
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
