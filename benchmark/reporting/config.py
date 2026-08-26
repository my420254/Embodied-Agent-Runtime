from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CONFIG_DIR = Path(__file__).resolve().parent / "configs"


def load_report_config(name: str) -> dict[str, Any]:
    config_name = str(name or "").strip()
    if not config_name:
        raise ValueError("report config name is required")
    path = CONFIG_DIR / f"{config_name}.json"
    if not path.exists():
        raise FileNotFoundError(f"missing report config: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"invalid report config: {path}")
    return data
