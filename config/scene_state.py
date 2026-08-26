import copy
import json
from pathlib import Path
from tempfile import gettempdir
from typing import Any

from config.settings import get_config, project_path


SCENE_ROOT_DIR = get_config("scenes", "root_dir", default="scenes")
INITIAL_SCENE_FILE = get_config("scenes", "initial_scene", default="default/house.json")
# Runtime / sandbox 只有内存 session，不再从独立配置路径读取。
RUNTIME_DUMP_DIR = get_config("scenes", "runtime_dump_dir", default=".scene_sessions")
SANDBOX_DUMP_DIR = get_config("scenes", "sandbox_dump_dir", default=".scene_sessions")
SESSION_DUMP_ENABLED = get_config("scenes", "dump_sessions", default=False)

_RUNTIME_SESSION: Any | None = None
_SANDBOX_SESSION: Any | None = None


def scene_path(scene_file: str) -> Path:
    path = project_path(SCENE_ROOT_DIR, scene_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _dump_path(scene_file: str) -> Path:
    if Path(scene_file).is_absolute():
        path = Path(scene_file)
    else:
        path = project_path(scene_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def load_seed_scene(fallback=None) -> Any:
    if fallback is None:
        fallback = {}
    try:
        with scene_path(INITIAL_SCENE_FILE).open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[系统警报] seed scene 加载失败: {e}")
        return copy.deepcopy(fallback)


def new_runtime_session(seed_scene: Any | None = None) -> Any:
    global _RUNTIME_SESSION
    base = load_seed_scene(fallback={}) if seed_scene is None else seed_scene
    _RUNTIME_SESSION = copy.deepcopy(base)
    return copy.deepcopy(_RUNTIME_SESSION)


def clone_sandbox_session(runtime_state: Any | None = None) -> Any:
    global _SANDBOX_SESSION
    if runtime_state is None:
        runtime_state = get_runtime_session()
    _SANDBOX_SESSION = copy.deepcopy(runtime_state)
    return copy.deepcopy(_SANDBOX_SESSION)


def snapshot_scene(session: Any) -> Any:
    return copy.deepcopy(session)


def restore_scene(snapshot: Any) -> Any:
    return copy.deepcopy(snapshot)


def get_runtime_session() -> Any:
    global _RUNTIME_SESSION
    if _RUNTIME_SESSION is None:
        new_runtime_session()
    return copy.deepcopy(_RUNTIME_SESSION)


def set_runtime_session(session: Any) -> None:
    global _RUNTIME_SESSION
    _RUNTIME_SESSION = copy.deepcopy(session)


def get_sandbox_session() -> Any:
    global _SANDBOX_SESSION
    if _SANDBOX_SESSION is None:
        clone_sandbox_session()
    return copy.deepcopy(_SANDBOX_SESSION)


def set_sandbox_session(session: Any) -> None:
    global _SANDBOX_SESSION
    _SANDBOX_SESSION = copy.deepcopy(session)


def load_scene(scene_file: str | None = None, fallback=None) -> Any:
    if fallback is None:
        fallback = {}
    if scene_file is None or scene_file == INITIAL_SCENE_FILE:
        return load_seed_scene(fallback=fallback)
    try:
        with _dump_path(scene_file).open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[系统警报] {scene_file} 加载失败: {e}")
        return copy.deepcopy(fallback)


def save_scene(data: Any, scene_file: str | None = None) -> None:
    if scene_file is None or scene_file == INITIAL_SCENE_FILE:
        raise ValueError("save_scene does not write the default seed scene; use runtime/sandbox session APIs instead")
    with _dump_path(scene_file).open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_runtime_scene() -> Any:
    return get_runtime_session()


def save_runtime_scene(data: Any) -> None:
    set_runtime_session(data)


def load_sandbox_scene() -> Any:
    return get_sandbox_session()


def save_sandbox_scene(data: Any) -> None:
    set_sandbox_session(data)


def reset_runtime_from_initial() -> None:
    new_runtime_session()


def reset_sandbox_from_runtime() -> None:
    clone_sandbox_session()


def dump_runtime_session(scene_file: str | None = None) -> Path:
    target = scene_file or f"{RUNTIME_DUMP_DIR}/runtime_session.json"
    path = _dump_path(target)
    with path.open("w", encoding="utf-8") as f:
        json.dump(get_runtime_session(), f, ensure_ascii=False, indent=2)
    return path


def dump_sandbox_session(scene_file: str | None = None) -> Path:
    target = scene_file or f"{SANDBOX_DUMP_DIR}/sandbox_session.json"
    path = _dump_path(target)
    with path.open("w", encoding="utf-8") as f:
        json.dump(get_sandbox_session(), f, ensure_ascii=False, indent=2)
    return path


def maybe_dump_sessions() -> None:
    if not SESSION_DUMP_ENABLED:
        return
    dump_runtime_session(str(Path(gettempdir()) / "ouragent_runtime_session.json"))
    dump_sandbox_session(str(Path(gettempdir()) / "ouragent_sandbox_session.json"))
