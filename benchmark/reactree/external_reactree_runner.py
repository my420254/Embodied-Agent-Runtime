from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from benchmark.experiment_utils import (
    ExperimentTimer,
    PROJECT_ROOT,
    WORKSPACE_ROOT,
    acquire_resource_locks,
    chat_completion,
    clear_proxy_env,
    endpoint_slots,
    load_case_ids_file,
    read_json,
    release_resource_locks,
    run_subprocess,
    safe_case_name,
    safe_name,
    select_cases,
    split_cases,
    timestamp,
    write_json,
)
from benchmark.datasets.extracted_cases import load_extracted_cases
from benchmark.reactree.alfred.framework.code.config import (
    extracted_cases_path_for_eval_set,
    load_config as load_alfred_config,
)
from benchmark.reactree.alfred.framework.code.metrics import summarize_gsr_ssr as summarize_alfred
from benchmark.reactree.alfred.framework.code.official_evaluator import (
    evaluate_alfred_goals,
)
from benchmark.reactree.wah.framework.code.adapter import load_tasks as load_wah_tasks
from benchmark.reactree.wah.framework.code.config import load_config as load_wah_config
from benchmark.reactree.wah.framework.code.metrics import summarize_gsr_ssr as summarize_wah
from benchmark.reactree.wah.framework.code.official_evaluator import (
    evaluate_reactree_goals,
    reactree_task_from_case_input,
)


WAH_ACTION_PREFIXES = ("go to ", "pick up ", "put down ", "open ", "close ", "turn on ", "turn off ")
ALFRED_ACTION_PREFIXES = (
    "go to ",
    "pick up ",
    "put down ",
    "open ",
    "close ",
    "turn on ",
    "turn off ",
    "slice ",
    "drop ",
)
TERMINALS = {"done", "failure"}


def _result_root(dataset: str, mode: str) -> Path:
    return PROJECT_ROOT / "benchmark" / "reactree" / dataset / mode / "results"


def _reactree_python() -> str:
    return os.getenv("REACTREE_PYTHON", str(WORKSPACE_ROOT / "envs" / "reactree_py38" / "bin" / "python"))


def _sentence_transformer_path() -> str:
    minilm = Path("/home/zmy/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/1110a243fdf4706b3f48f1d95db1a4f5529b4d41")
    if minilm.exists():
        return str(minilm)
    return str(
        WORKSPACE_ROOT
        / "hf_cache"
        / "models--sentence-transformers--all-roberta-large-v1"
        / "snapshots"
        / "cf74d8acd4f198de950bf004b262e6accfed5d2c"
    )


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


def _start_xvfb(display: str, *, screen: str, run_root: Path) -> subprocess.Popen:
    normalized = _normalize_display(display)
    log_path = run_root / "xvfb" / f"display_{normalized}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [
            "Xvfb",
            f":{normalized}",
            "-screen",
            "0",
            str(screen or "1024x768x24"),
            "-nolisten",
            "tcp",
        ],
        stdout=log_file,
        stderr=subprocess.STDOUT,
        close_fds=True,
    )
    setattr(process, "_ouragent_log_file", log_file)
    return process


def _stop_xvfb_processes(processes: list[subprocess.Popen]) -> None:
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


def _ensure_display(display: str, *, args: Any, run_root: Path) -> subprocess.Popen | None:
    normalized = _normalize_display(display)
    ok, reason = _display_probe(normalized)
    if ok:
        raise SystemExit(f"ALFRED X display 已被占用，不能保证仿真隔离: :{normalized}")
    if bool(getattr(args, "dry_run", False)) or bool(getattr(args, "no_auto_xvfb", False)):
        raise SystemExit(
            f"ALFRED simulator X display 不可用: :{normalized} ({reason})。"
            "请换可用 display，或允许 runner 自动启动 Xvfb。"
        )
    process = _start_xvfb(normalized, screen=str(getattr(args, "xvfb_screen", "") or "1024x768x24"), run_root=run_root)
    last_reason = reason
    for _ in range(20):
        time.sleep(0.25)
        ok, last_reason = _display_probe(normalized)
        if ok:
            return process
        if process.poll() is not None:
            break
    _stop_xvfb_processes([process])
    raise SystemExit(f"无法自动启动 Xvfb :{normalized}: {last_reason}")


def _expand_x_displays(requested: list[str], unit_count: int) -> list[str]:
    required = max(1, int(unit_count))
    if len(requested) >= required:
        return requested
    try:
        start = int(requested[0])
    except (TypeError, ValueError, IndexError):
        raise SystemExit(
            "ALFRED 并发运行要求每个 worker 使用独立数字 X display。"
            f"当前 unit_count={unit_count}, x_displays={requested}。"
        )
    return [str(start + index) for index in range(required)]


def _resolve_x_displays(args: Any, *, run_root: Path, unit_count: int) -> tuple[list[str], list[subprocess.Popen], list[Any]]:
    requested = [_normalize_display(item) for item in getattr(args, "x_displays", []) if _normalize_display(item)]
    if not requested and getattr(args, "x_display", None) is not None:
        requested = [_normalize_display(getattr(args, "x_display") or "0")]
    if not requested:
        requested = ["0"]
    requested = _expand_x_displays(list(dict.fromkeys(requested)), unit_count)
    if bool(getattr(args, "dry_run", False)):
        return requested, [], []
    resource_locks = acquire_resource_locks("reactree_alfred_x_display", requested, run_root=run_root)
    processes: list[subprocess.Popen] = []
    try:
        for display in requested:
            process = _ensure_display(display, args=args, run_root=run_root)
            if process is not None:
                processes.append(process)
    except Exception:
        _stop_xvfb_processes(processes)
        release_resource_locks(resource_locks)
        raise
    return requested, processes, resource_locks


def _reactree_subprocess_env(*, full_observable: bool = False) -> dict[str, str]:
    env = clear_proxy_env()
    env["OURAGENT_PROJECT_ROOT"] = str(PROJECT_ROOT)
    env["OURAGENT_WORKSPACE_ROOT"] = str(WORKSPACE_ROOT)
    env["OURAGENT_REACTREE_ROOT"] = str(WORKSPACE_ROOT / "ReAcTree")
    compat_path = PROJECT_ROOT / "benchmark" / "reactree" / "reactree_py38_compat"
    existing_pythonpath = str(env.get("PYTHONPATH", "") or "")
    env["PYTHONPATH"] = str(compat_path) + (os.pathsep + existing_pythonpath if existing_pythonpath else "")
    if full_observable:
        env["OURAGENT_REACTREE_FULL_OBSERVABLE"] = "1"
    else:
        env.pop("OURAGENT_REACTREE_FULL_OBSERVABLE", None)
    return env


def _load_cases(dataset: str, *, eval_set: str = "valid_seen") -> list[dict[str, Any]]:
    if dataset == "wah":
        cfg = load_wah_config()
        native_tasks = {int(task.task_id): task for task in load_wah_tasks(cfg.testset_path)}
        cases = load_extracted_cases(cfg.extracted_cases_path)
        selected: list[dict[str, Any]] = []
        for case in cases:
            case_input = case.get("input", {}) if isinstance(case.get("input"), dict) else {}
            try:
                task_id = int(case_input.get("task_id", -1))
            except (TypeError, ValueError):
                task_id = -1
            task = native_tasks.get(task_id)
            if task is None:
                continue
            case_input.setdefault("init_graph", task.init_graph)
            case_input.setdefault("task_goal", task.task_goal if isinstance(task.task_goal, dict) else {})
            case_input.setdefault("task_source", "reactree_wah_testset")
            case_input.setdefault("environment_source", "reactree_extracted_runtime_scene")
            selected.append(case)
        return selected
    cases = load_extracted_cases(extracted_cases_path_for_eval_set(eval_set))
    return [
        case
        for case in cases
        if str((case.get("metadata", {}) if isinstance(case.get("metadata"), dict) else {}).get("eval_set") or eval_set)
        == eval_set
    ]


def _instruction_idx(case: dict[str, Any]) -> int:
    case_input = case.get("input", {}) if isinstance(case.get("input"), dict) else {}
    metadata = case.get("metadata", {}) if isinstance(case.get("metadata"), dict) else {}
    value = case_input.get("instruction_idx", metadata.get("instruction_idx", 0))
    return int(value or 0)


def _strip_code_fence(text: str) -> str:
    cleaned = str(text or "").strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[A-Za-z0-9_-]*\n", "", cleaned)
        cleaned = re.sub(r"\n```$", "", cleaned)
    return cleaned.strip()


def _parse_actions(text: str, prefixes: tuple[str, ...]) -> list[str]:
    cleaned = _strip_code_fence(text)
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            parsed = parsed.get("actions", [])
        if isinstance(parsed, list):
            actions = []
            for item in parsed:
                line = str(item).strip()
                lowered = line.lower()
                if lowered in TERMINALS:
                    actions.append(lowered)
                    continue
                for prefix in prefixes:
                    if lowered.startswith(prefix):
                        actions.append(prefix + line[len(prefix) :].strip())
                        break
            return actions
    except Exception:
        pass
    actions = []
    for raw_line in cleaned.splitlines():
        line = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", raw_line).strip().strip('"').strip("'")
        lowered = line.lower()
        if lowered in TERMINALS:
            actions.append(lowered)
            continue
        for prefix in prefixes:
            if lowered.startswith(prefix):
                actions.append(prefix + line[len(prefix) :].strip())
                break
    return actions


def _load_wah_utils(repo_root: Path):
    src_path = str(repo_root / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    from wah.wah_utils import make_name_id_dict

    return make_name_id_dict


def _wah_parent_maps(graph: dict[str, Any]) -> tuple[dict[int, tuple[str, int]], dict[int, int | None]]:
    nodes = {int(node["id"]): node for node in graph.get("nodes", [])}
    direct_parent: dict[int, tuple[str, int]] = {}
    for edge in graph.get("edges", []):
        relation = str(edge.get("relation_type", "")).upper()
        if relation in {"INSIDE", "ON"}:
            direct_parent[int(edge["from_id"])] = (relation, int(edge["to_id"]))

    def resolve_room(object_id: int) -> int | None:
        current = object_id
        seen: set[int] = set()
        while current in direct_parent and current not in seen:
            seen.add(current)
            _, parent_id = direct_parent[current]
            parent = nodes.get(parent_id)
            if not parent:
                return None
            if str(parent.get("category")) == "Rooms":
                return parent_id
            current = parent_id
        return None

    return direct_parent, {node_id: resolve_room(node_id) for node_id in nodes}


def _state_text(states: Any) -> str:
    if isinstance(states, dict):
        active = [str(key) for key, value in sorted(states.items()) if value not in (False, None, "", "空")]
    elif isinstance(states, list):
        active = [str(item).lower() for item in states if str(item).strip()]
    else:
        active = []
    return f" [{', '.join(active)}]" if active else ""


def _wah_runtime_scene_snapshot(scene: dict[str, Any], env_state: dict[str, Any] | None = None) -> str:
    environment = scene.get("environment", {}) if isinstance(scene, dict) else {}
    env_state = env_state if isinstance(env_state, dict) else {}
    if not isinstance(environment, dict) or not environment:
        return ""

    room_names = sorted(str(room) for room in environment.keys())
    parts = [
        "Rooms: " + ", ".join(room_names),
        f"Robot starts in: {scene.get('robot_location') or env_state.get('robot_location') or 'unknown'}",
        "Initial environment snapshot:",
    ]

    def walk(container: dict[str, Any], *, room_label: str, parent_label: str) -> list[str]:
        lines: list[str] = []
        contains = container.get("contains", {}) if isinstance(container, dict) else {}
        if not isinstance(contains, dict):
            return lines
        for name, info in sorted(contains.items(), key=lambda item: str(item[0])):
            item = info if isinstance(info, dict) else {}
            relation = str(item.get("direct_relation", "") or "").strip().lower()
            if parent_label == room_label:
                location = f"room {room_label}"
            elif relation:
                location = f"{relation} {parent_label} (room {room_label})"
            else:
                location = f"inside {parent_label} (room {room_label})"
            lines.append(f"- {name}{_state_text(item.get('states', {}))} -> {location}")
            lines.extend(walk(item, room_label=room_label, parent_label=str(name)))
        return lines

    for room_label in room_names:
        room = environment.get(room_label, {})
        parts.append(f"[{room_label}]")
        parts.extend(walk(room if isinstance(room, dict) else {}, room_label=room_label, parent_label=room_label))
    return "\n".join(parts)


def _wah_environment_snapshot(case_input: dict[str, Any]) -> str:
    cache_path = Path(str(case_input.get("init_graph_cache_path", "") or ""))
    if cache_path.exists():
        payload = read_json(cache_path, {})
        runtime = payload.get("runtime_initial_environment", {}) if isinstance(payload, dict) else {}
        scene = runtime.get("scene", {}) if isinstance(runtime, dict) else {}
        env_state = runtime.get("env_state", {}) if isinstance(runtime, dict) else {}
        rendered = _wah_runtime_scene_snapshot(scene, env_state)
        if rendered:
            return rendered

    cfg = load_wah_config()
    repo_root = cfg.repo_root
    make_name_id_dict = _load_wah_utils(repo_root)
    obj_dict = read_json(repo_root / "resource" / "wah_obj_dict_sim2nl.json", {})
    graph = case_input.get("init_graph", {})
    nodes = {int(node["id"]): node for node in graph.get("nodes", [])}
    name_id_dict_sim2nl, _ = make_name_id_dict(graph, obj_dict)
    direct_parent, room_parent = _wah_parent_maps(graph)

    room_names: dict[int, str] = {}
    room_lines: dict[str, list[str]] = defaultdict(list)
    for node_id, node in nodes.items():
        if str(node.get("category")) != "Rooms":
            continue
        nl_name, nl_idx = name_id_dict_sim2nl.get((str(node["class_name"]), node_id), (str(node["class_name"]), 1))
        room_names[node_id] = f"{nl_name} {nl_idx}"

    ignored = {"Rooms", "Floor", "Ceiling", "Walls", "Doors", "Windows"}
    for node_id, node in nodes.items():
        if str(node.get("category")) in ignored:
            continue
        nl_info = name_id_dict_sim2nl.get((str(node["class_name"]), node_id))
        if not nl_info:
            continue
        label = f"{nl_info[0]} {nl_info[1]}"
        states = [str(state).lower() for state in node.get("states", [])]
        state_text = f" [{', '.join(states)}]" if states else ""
        room_label = room_names.get(room_parent.get(node_id) or -1, case_input.get("init_room", "unknown"))
        relation = direct_parent.get(node_id)
        if relation is None:
            line = f"- {label}{state_text} -> room {room_label}"
        else:
            rel, parent_id = relation
            parent = nodes.get(parent_id)
            if parent and str(parent.get("category")) == "Rooms":
                line = f"- {label}{state_text} -> room {room_label}"
            else:
                parent_info = name_id_dict_sim2nl.get((str(parent.get("class_name", "")), parent_id)) if parent else None
                parent_label = f"{parent_info[0]} {parent_info[1]}" if parent_info else f"object_{parent_id}"
                line = f"- {label}{state_text} -> {'inside' if rel == 'INSIDE' else 'on'} {parent_label} (room {room_label})"
        room_lines[room_label].append(line)

    parts = [
        "Rooms: " + ", ".join(sorted(room_names.values())),
        f"Robot starts in: {case_input.get('init_room', 'unknown')}",
        "Initial environment snapshot:",
    ]
    for room_label in sorted(room_lines):
        parts.append(f"[{room_label}]")
        parts.extend(sorted(room_lines[room_label]))
    return "\n".join(parts)


def _wah_prompt(case_input: dict[str, Any]) -> str:
    return "\n".join(
        [
            "You are solving a Watch-and-Help household task in one shot.",
            "Output a JSON object with one key: actions.",
            'Format: {"actions": ["go to kitchen 1", "pick up apple 1", "done"]}',
            "Do not output markdown. Do not explain.",
            "",
            "Allowed actions:",
            "- go to <room or object>",
            "- pick up <object>",
            "- put down <object>",
            "- open <container>",
            "- close <container>",
            "- turn on <device>",
            "- turn off <device>",
            "- done",
            "- failure",
            "",
            f"Task: {case_input.get('instruction', '')}",
            "",
            "Raw task_goal from dataset:",
            json.dumps(case_input.get("task_goal", {}), ensure_ascii=False, indent=2),
            "",
            _wah_environment_snapshot(case_input),
        ]
    )


def _alfred_task_json(case_input: dict[str, Any]) -> dict[str, Any]:
    cfg = load_alfred_config()
    path = cfg.annotation_root / case_input["task"] / "pp" / f"ann_{int(case_input['repeat_idx'])}.json"
    return read_json(path, {})


def _alfred_initial_scene(case_input: dict[str, Any]) -> dict[str, Any]:
    cache_path = Path(str(case_input.get("initial_scene_cache_path", "") or ""))
    if not cache_path:
        raise ValueError("ALFRED bare baseline case is missing initial_scene_cache_path")
    payload = read_json(cache_path, {})
    if isinstance(payload, dict) and isinstance(payload.get("initial_scene"), dict):
        return payload["initial_scene"]
    if isinstance(payload, dict) and isinstance(payload.get("all_objects"), list):
        return payload
    raise ValueError(f"ALFRED initial scene cache must contain initial_scene: {cache_path}")


def _alfred_environment_snapshot(case_input: dict[str, Any]) -> str:
    initial_scene = _alfred_initial_scene(case_input)
    visible_groups = [str(item) for item in initial_scene.get("visible_groups", []) if str(item).strip()]
    objects = []
    for item in initial_scene.get("all_objects", []) or []:
        if not isinstance(item, dict):
            continue
        objects.append(
            {
                "name": item.get("name"),
                "direct_parent": item.get("direct_parent"),
                "is_receptacle": item.get("is_receptacle"),
                "states": item.get("states", {}),
                "properties": item.get("properties", []),
                "object_type": item.get("object_type"),
            }
        )
    return "\n".join(
        [
            "Initial observation text:",
            str(initial_scene.get("text", "") or ""),
            "",
            "Visible object groups:",
            json.dumps(visible_groups, ensure_ascii=False, indent=2),
            "",
            "Object catalog from extracted initial scene cache:",
            json.dumps(objects, ensure_ascii=False, indent=2),
        ]
    )


def _alfred_prompt(case_input: dict[str, Any], *, x_display: str, use_sim_observation: bool) -> str:
    task_json = _alfred_task_json(case_input)
    repeat_idx = int(case_input["repeat_idx"])
    task_desc = str(task_json.get("turk_annotations", {}).get("anns", [{}])[repeat_idx].get("task_desc") or case_input.get("instruction", ""))
    del x_display, use_sim_observation
    return "\n".join(
        [
            "You are solving an ALFRED household task in one shot.",
            "Output a JSON object with one key: actions.",
            'Format: {"actions": ["go to Cabinet (2)", "pick up Mug (1)", "done"]}',
            "Do not output markdown. Do not explain.",
            "",
            "Allowed actions:",
            "- go to <ObjectName (id)>",
            "- pick up <ObjectName (id)>",
            "- put down <ObjectName (id)>",
            "- open <ObjectName (id)>",
            "- close <ObjectName (id)>",
            "- turn on <ObjectName (id)>",
            "- turn off <ObjectName (id)>",
            "- slice <ObjectName (id)>",
            "- drop <ObjectName (id)>",
            "- done",
            "- failure",
            "",
            f"Task: {task_desc}",
            f"Task type: {task_json.get('task_type', '')}",
            "",
            "Raw PDDL params:",
            json.dumps(task_json.get("pddl_params", {}), ensure_ascii=False, indent=2),
            "",
            _alfred_environment_snapshot(case_input),
        ]
    )


def _run_bare_case(
    *,
    dataset: str,
    run_root: Path,
    case: dict[str, Any],
    slot: dict[str, Any],
    max_tokens: int,
    temperature: float,
    official_timeout_s: int,
    official_base_port: int,
    official_port_id: int,
    x_display: str,
    use_sim_observation: bool,
    reuse_unity: bool,
    dry_run: bool,
    resume: bool,
) -> dict[str, Any]:
    case_id = str(case["case_id"])
    case_input = case.get("input", {}) if isinstance(case.get("input"), dict) else {}
    case_root = run_root / "cases" / safe_case_name(case_id)
    prompt = _wah_prompt(case_input) if dataset == "wah" else _alfred_prompt(
        case_input,
        x_display=x_display,
        use_sim_observation=use_sim_observation and not dry_run,
    )
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
            "mode": "bare_baseline",
            "dataset": dataset,
            "case_id": case_id,
            "status": "dry_run",
            "prompt": str(prompt_path),
            "api_base": slot["api_base"],
            "api_model": slot["api_model"],
            "max_tokens": max_tokens,
            "temperature": temperature,
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
    if dataset == "wah":
        official_actions = _parse_actions(raw_text, WAH_ACTION_PREFIXES)
        task = reactree_task_from_case_input(case_input)
        prediction = evaluate_reactree_goals(
            init_graph=case_input.get("init_graph", {}),
            task_goal=case_input.get("task_goal", {}),
            evaluator_execution_calls=[],
            official_actions=official_actions,
            repo_root=load_wah_config().repo_root,
            task=task,
            reactree_python=load_wah_config().reactree_python,
            timeout_s=official_timeout_s,
            base_port=official_base_port,
            port_id=official_port_id,
            reuse_unity=reuse_unity,
        )
    else:
        official_actions = _parse_actions(raw_text, ALFRED_ACTION_PREFIXES)
        prediction = evaluate_alfred_goals(
            case_input,
            [],
            official_actions=official_actions,
            x_display=x_display,
            reactree_python=load_alfred_config().reactree_python,
            timeout_s=official_timeout_s,
        )
    payload = {
        "mode": "bare_baseline",
        "dataset": dataset,
        "case_id": case_id,
        "status": "done",
        "success": float(prediction.get("goal_success_rate", 0.0) or 0.0) >= 1.0,
        "prompt": str(prompt_path),
        "raw_response": raw_text,
        "official_actions": official_actions,
        "prediction": prediction,
        "api_base": slot["api_base"],
        "api_model": slot["api_model"],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "updated_at": timestamp(),
    }
    write_json(raw_path, payload)
    write_json(meta_path, payload)
    return payload


def _run_wah_paper_case(
    *,
    run_root: Path,
    case: dict[str, Any],
    slot: dict[str, Any],
    official_timeout_s: int,
    official_base_port: int,
    official_port_id: int,
    reuse_unity: bool,
    config_name: str,
    full_observable: bool,
    paper_overrides: list[str],
    dry_run: bool,
    resume: bool,
) -> dict[str, Any]:
    case_id = str(case["case_id"])
    case_input = case.get("input", {}) if isinstance(case.get("input"), dict) else {}
    case_root = run_root / "cases" / safe_case_name(case_id)
    raw_path = case_root / "raw_output.json"
    meta_path = case_root / "case.json"
    log_path = case_root / "run.log"
    testset_path = case_root / "artifacts" / "paper_method_testset.json"
    result_path = case_root / "artifacts" / "paper_method_results.jsonl"
    wrapper = PROJECT_ROOT / "benchmark" / "reactree" / "wah" / "paper_method" / "code" / "evaluate_wrapper.py"
    entrypoint = str(wrapper) if full_observable else "src/evaluate.py"
    if resume:
        existing = read_json(meta_path, {})
        if isinstance(existing, dict) and existing.get("status") == "done":
            return {**existing, "skipped": True}
    write_json(testset_path, [reactree_task_from_case_input(case_input)])
    command = [
        str(load_wah_config().reactree_python),
        entrypoint,
        f"--config-name={config_name}",
        "exp_type=evaluate",
        f"dataset.wah_testset={testset_path}",
        f"+dataset.resume_results_path={result_path}",
        f"llm_agent.api_base={slot['api_base']}",
        f"llm_agent.api_key={slot['api_key']}",
        f"llm_agent.model_name={slot['api_model']}",
        "llm_agent.max_steps=199",
        "llm_agent.max_decisions=199",
        f"llm_agent.sentence_transformer_model={_sentence_transformer_path()}",
        "llm_agent.sentence_transformer_local_only=True",
        f"environment.base_port={official_base_port}",
        f"environment.port_id={official_port_id}",
        "environment.use_editor=False",
        "environment.vis_log=False",
        "environment.executable_args.x_display=0",
        f"environment.executable_args.timeout_wait={official_timeout_s}",
        "prompt.sys_prompt_root_dir=resource/wah/sys_prompt",
    ]
    command.append("environment.executable_args.file_name=null" if reuse_unity else f"environment.executable_args.file_name={load_wah_config().repo_root / 'virtualhome' / 'simulation' / 'unity_simulator' / 'linux_exec.x86_64'}")
    if not any(str(override).lstrip("+").startswith("environment.executable_args.no_graphics=") for override in paper_overrides):
        command.append("+environment.executable_args.no_graphics=True")
    command.extend(paper_overrides)
    payload = {
        "mode": "paper_method",
        "dataset": "wah",
        "case_id": case_id,
        "observability": "fully_observable" if full_observable else "paper_original",
        "paper_overrides": paper_overrides,
        "status": "dry_run" if dry_run else "running",
        "command": command,
        "log": str(log_path),
        "raw_output": str(raw_path),
        "api_base": slot["api_base"],
        "api_model": slot["api_model"],
    }
    write_json(meta_path, payload)
    if dry_run:
        write_json(raw_path, payload)
        return payload
    env = _reactree_subprocess_env(full_observable=full_observable)
    rc = run_subprocess(command, cwd=load_wah_config().repo_root, env=env, log_path=log_path)
    rows = []
    if result_path.exists():
        for line in result_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    prediction = rows[-1] if rows else {}
    payload.update(
        {
            "status": "done" if rc == 0 and prediction else "failed",
            "returncode": rc,
            "prediction": prediction,
            "success": float(prediction.get("goal_success_rate", 0.0) or 0.0) >= 1.0,
            "updated_at": timestamp(),
        }
    )
    write_json(raw_path, payload)
    write_json(meta_path, payload)
    return payload


def _run_alfred_paper_batch(
    *,
    run_root: Path,
    run_name: str,
    slot: dict[str, Any],
    config_name: str,
    eval_set: str,
    x_display: str,
    eval_portion: int,
    eval_subset_seed: int,
    planner_seed: int,
    reset: bool,
    dry_run: bool,
    full_observable: bool,
    paper_overrides: list[str],
    worker_timeout_s: int | None,
) -> dict[str, Any]:
    paper_run_dir = run_root / "paper_run"
    result_path = paper_run_dir / "results.jsonl"
    wrapper = PROJECT_ROOT / "benchmark" / "reactree" / "alfred" / "paper_method" / "code" / "evaluate_wrapper.py"
    prompt_root = (
        "resource/alfred/sys_prompt_qwen_adapted"
        if str(slot.get("api_model", "")).lower().startswith("qwen")
        else "resource/alfred/sys_prompt"
    )
    command = [
        str(load_alfred_config().reactree_python),
        str(wrapper),
        f"--config-name={config_name}",
        "exp_type=evaluate",
        f"hydra.run.dir={paper_run_dir}",
        f"dataset.eval_set={eval_set}",
        f"+dataset.resume_results_path={result_path}",
        f"llm_agent.model_name={slot['api_model']}",
        f"llm_agent.api_base={slot['api_base']}",
        f"llm_agent.api_key={slot['api_key']}",
        "llm_agent.working_memory=True",
        "llm_agent.ic_ex_select_type=rag",
        "llm_agent.max_steps=100",
        "llm_agent.max_decisions=100",
        "llm_agent.openai_tokenizer=cl100k_base",
        f"llm_agent.sentence_transformer_model={_sentence_transformer_path()}",
        "llm_agent.sentence_transformer_local_only=True",
        f"prompt.sys_prompt_root_dir={prompt_root}",
        "prompt.ic_ex_root_dir=resource/alfred/em_llm",
        f"alfred.x_display='{x_display}'",
        f"alfred.eval_portion_in_percent={eval_portion}",
        f"alfred.random_seed_for_eval_subset={eval_subset_seed}",
        f"+planner.random_seed={planner_seed}",
    ]
    command.extend(paper_overrides)
    payload = {
        "mode": "paper_method",
        "dataset": "alfred",
        "run_name": run_name,
        "eval_set": eval_set,
        "observability": "fully_observable" if full_observable else "paper_original",
        "paper_overrides": paper_overrides,
        "worker_timeout_s": worker_timeout_s,
        "status": "dry_run" if dry_run else "running",
        "command": command,
        "raw_output": str(run_root / "raw_output.json"),
        "log": str(run_root / "run.log"),
        "api_base": slot["api_base"],
        "api_model": slot["api_model"],
        "prompt_root": prompt_root,
    }
    write_json(run_root / "manifest_paper_command.json", payload)
    if dry_run:
        write_json(run_root / "raw_output.json", payload)
        return payload
    if reset and paper_run_dir.exists():
        shutil.rmtree(paper_run_dir)
    rc = run_subprocess(
        command,
        cwd=load_alfred_config().repo_root,
        env=_reactree_subprocess_env(full_observable=full_observable),
        log_path=run_root / "run.log",
        timeout_s=worker_timeout_s,
    )
    rows = []
    if result_path.exists():
        for line in result_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    payload.update(
        {
            "status": "done" if rc == 0 else "failed",
            "returncode": rc,
            "result_path": str(result_path),
            "total_cases": len(rows),
            "success_count": sum(1 for row in rows if row.get("success")),
            "updated_at": timestamp(),
        }
    )
    write_json(run_root / "raw_output.json", payload)
    return payload


def _parser(dataset: str, mode: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=f"Run ReActree {dataset} {mode}.")
    parser.add_argument("--ports", nargs="*", type=int, default=[])
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--run-name", default="")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--case-ids-file", default="")
    parser.add_argument("--api-model", default="")
    parser.add_argument("--api-key", default="")
    parser.add_argument("--max-tokens", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=None)
    parser.add_argument("--official-timeout-s", type=int, default=180)
    parser.add_argument("--official-base-port", type=int, default=8900)
    parser.add_argument("--official-port-ids", nargs="*", type=int, default=[])
    parser.add_argument("--x-display", default=None)
    parser.add_argument("--x-displays", nargs="*", default=[])
    parser.add_argument("--no-auto-xvfb", action="store_true")
    parser.add_argument("--xvfb-screen", default="1024x768x24")
    parser.add_argument("--reuse-unity", action="store_true")
    parser.add_argument("--config-name", default="")
    parser.add_argument("--eval-portion", type=int, default=100)
    parser.add_argument("--eval-set", default="valid_seen")
    parser.add_argument("--eval-subset-seed", type=int, default=1)
    parser.add_argument("--planner-seed", type=int, default=0)
    parser.add_argument("--no-sim-observation", action="store_true")
    parser.add_argument("--full-observable", action="store_true")
    parser.add_argument("--instruction-level", action="store_true")
    parser.add_argument("--paper-override", action="append", default=[])
    parser.add_argument("--worker-timeout-s", type=int, default=None)
    return parser


def _summary(run_root: Path, dataset: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    metric_summary = summarize_wah(rows) if dataset == "wah" else summarize_alfred(rows)
    summary = {
        "run_name": run_root.name,
        "dataset": dataset,
        "total_cases": len(rows),
        "done_cases": sum(1 for row in rows if row.get("status") == "done"),
        "failed_cases": sum(1 for row in rows if row.get("status") == "failed"),
        **metric_summary,
        "cases": rows,
    }
    write_json(run_root / "merged_results.json", rows)
    write_json(run_root / "summary.json", summary)
    return summary


def main_for(dataset: str, mode: str, argv: list[str] | None = None) -> int:
    args = _parser(dataset, mode).parse_args(argv)
    run_name = safe_name(args.run_name or f"{mode}_full")
    run_root = _result_root(dataset, mode) / run_name
    if args.summary:
        print(json.dumps(read_json(run_root / "summary.json", {}), ensure_ascii=False, indent=2))
        return 0
    if args.reset and run_root.exists():
        shutil.rmtree(run_root)
    experiment_timer = ExperimentTimer(run_root, {"runner": "reactree_external", "dataset": dataset, "mode": mode, "resume": bool(args.resume)})
    slots = endpoint_slots(args.ports, workers=args.workers, module="planning", api_model=args.api_model, api_key=args.api_key)
    max_tokens = int(args.max_tokens if args.max_tokens is not None else slots[0].get("max_tokens", 4096))
    temperature = float(args.temperature if args.temperature is not None else slots[0].get("temperature", 0.0))

    worker_count = max(1, int(args.workers or 1))
    xvfb_processes: list[subprocess.Popen] = []
    resource_locks: list[Any] = []
    try:
        if dataset == "alfred":
            unit_count = 1 if mode == "paper_method" else worker_count
            x_displays, xvfb_processes, resource_locks = _resolve_x_displays(
                args,
                run_root=run_root,
                unit_count=unit_count,
            )
            setattr(args, "x_displays", x_displays)

        if dataset == "alfred" and mode == "paper_method":
            payload = _run_alfred_paper_batch(
                run_root=run_root,
                run_name=run_name,
                slot=slots[0],
                config_name=str(args.config_name or "alfred_reactree"),
                eval_set=str(args.eval_set or "valid_seen"),
                x_display=str((args.x_displays or ["0"])[0]),
                eval_portion=int(args.eval_portion),
                eval_subset_seed=int(args.eval_subset_seed),
                planner_seed=int(args.planner_seed),
                reset=bool(args.reset),
                dry_run=bool(args.dry_run),
                full_observable=bool(args.full_observable),
                paper_overrides=list(args.paper_override or []),
                worker_timeout_s=args.worker_timeout_s,
            )
            summary = {"run_name": run_name, "dataset": dataset, **payload}
            write_json(run_root / "summary.json", summary)
            experiment_timer.finish("dry_run" if args.dry_run else "completed", {"worker_count": worker_count})
            print(json.dumps(summary, ensure_ascii=False, indent=2))
            return 0

        requested_ids = [*args.case_id, *load_case_ids_file(args.case_ids_file)]
        loaded_cases = _load_cases(dataset, eval_set=str(args.eval_set or "valid_seen"))
        if dataset == "wah" and mode == "paper_method" and not bool(args.instruction_level) and not requested_ids:
            loaded_cases = [case for case in loaded_cases if _instruction_idx(case) == 0]
        cases = select_cases(
            loaded_cases,
            case_ids=requested_ids,
            limit=args.limit,
        )
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
                "official_timeout_s": args.official_timeout_s,
                "official_base_port": args.official_base_port,
                "official_port_ids": list(args.official_port_ids or []),
                "x_displays": list(args.x_displays or []),
                "official_auto_xvfb": bool(dataset == "alfred" and xvfb_processes),
                "observability": "fully_observable" if args.full_observable else "paper_original",
                "paper_overrides": list(args.paper_override or []),
                "instruction_level": bool(args.instruction_level),
                "eval_set": str(args.eval_set or "valid_seen"),
                "input_regime": "extracted_reactree_wah_cases_with_native_evaluator_fields"
                if dataset == "wah" and mode == "bare_baseline"
                else "extracted_reactree_cases",
                "case_count": len(cases),
                "case_ids": [case["case_id"] for case in cases],
                "started_at": timestamp(),
            },
        )
        rows: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=worker_count) as pool:
            futures = []
            for index, chunk in enumerate(chunks):
                slot = slots[index % len(slots)]
                official_port_id = (args.official_port_ids or list(range(worker_count)))[index % max(1, len(args.official_port_ids or list(range(worker_count))))]
                x_display = str((args.x_displays or [str(index)])[index % max(1, len(args.x_displays or [str(index)]))])
                def run_chunk(
                    chunk_cases: list[dict[str, Any]],
                    *,
                    chunk_slot: dict[str, Any],
                    chunk_official_port_id: int,
                    chunk_x_display: str,
                ) -> list[dict[str, Any]]:
                    chunk_rows: list[dict[str, Any]] = []
                    for chunk_case in chunk_cases:
                        if mode == "paper_method":
                            chunk_rows.append(
                                _run_wah_paper_case(
                                    run_root=run_root,
                                    case=chunk_case,
                                    slot=chunk_slot,
                                    official_timeout_s=int(args.official_timeout_s),
                                    official_base_port=int(args.official_base_port),
                                    official_port_id=int(chunk_official_port_id),
                                    reuse_unity=bool(args.reuse_unity),
                                    config_name=str(args.config_name or "wah_headless_reactree"),
                                    full_observable=bool(args.full_observable),
                                    paper_overrides=list(args.paper_override or []),
                                    dry_run=bool(args.dry_run),
                                    resume=bool(args.resume),
                                )
                            )
                        else:
                            chunk_rows.append(
                                _run_bare_case(
                                    dataset=dataset,
                                    run_root=run_root,
                                    case=chunk_case,
                                    slot=chunk_slot,
                                    max_tokens=max_tokens,
                                    temperature=temperature,
                                    official_timeout_s=int(args.official_timeout_s),
                                    official_base_port=int(args.official_base_port),
                                    official_port_id=int(chunk_official_port_id),
                                    x_display=chunk_x_display,
                                    use_sim_observation=not bool(args.no_sim_observation),
                                    reuse_unity=bool(args.reuse_unity),
                                    dry_run=bool(args.dry_run),
                                    resume=bool(args.resume),
                                )
                            )
                    return chunk_rows

                futures.append(
                    pool.submit(
                        run_chunk,
                        chunk,
                        chunk_slot=slot,
                        chunk_official_port_id=int(official_port_id),
                        chunk_x_display=x_display,
                    )
                )
            for future in as_completed(futures):
                rows.extend(future.result())
        rows.sort(key=lambda item: str(item.get("case_id", "")))
        summary = _summary(run_root, dataset, rows)
        experiment_timer.finish("dry_run" if args.dry_run else "completed", {"case_count": len(rows), "worker_count": worker_count})
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    finally:
        _stop_xvfb_processes(xvfb_processes)
        release_resource_locks(resource_locks)
