import json
from pathlib import Path

from .settings import project_path


def _resolve_project_path(filename: str) -> Path:
    path = Path(str(filename or ""))
    if path.is_absolute():
        return path
    return project_path(str(path))


def load_project_json(filename: str, fallback=None):
    if fallback is None:
        fallback = {}
    try:
        with _resolve_project_path(filename).open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[系统警报] {filename} 加载失败: {e}")
        return fallback


def save_project_json(filename: str, data) -> None:
    with _resolve_project_path(filename).open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

