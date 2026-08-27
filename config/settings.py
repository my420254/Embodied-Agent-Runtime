from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = Path(os.getenv("OURAGENT_WORKSPACE_ROOT", str(PROJECT_ROOT.parent))).resolve()
CONFIG_FILE = "config/settings.json"
JsonObject = Dict[str, Any]


def project_path(*parts: str) -> Path:
    return PROJECT_ROOT.joinpath(*parts)


def workspace_path(*parts: str) -> Path:
    return WORKSPACE_ROOT.joinpath(*parts)


def _resolve_config_path(filename: str) -> Path:
    path = Path(str(filename or ""))
    if path.is_absolute():
        return path
    return project_path(str(path))


def _deep_merge(base: JsonObject, override: JsonObject) -> JsonObject:
    merged = dict(base)
    for key, value in override.items():
        current = merged.get(key)
        if isinstance(current, dict) and isinstance(value, dict):
            merged[key] = _deep_merge(current, value)
        else:
            merged[key] = value
    return merged


def _load_json_config(filename: str) -> JsonObject:
    config_path = _resolve_config_path(filename)
    if not config_path.exists():
        raise FileNotFoundError(f"required config file not found: {config_path}")
    try:
        with config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"{filename} 加载失败: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{filename} must contain a JSON object")
    return data


def _same_config_file(left: str | Path, right: str | Path) -> bool:
    try:
        return _resolve_config_path(str(left)).resolve() == _resolve_config_path(str(right)).resolve()
    except (OSError, RuntimeError, ValueError):
        return str(left) == str(right)


def load_app_config(filename: str | Path | None = None) -> JsonObject:
    return _load_json_config(str(filename or CONFIG_FILE))


APP_CONFIG = load_app_config()
_DEFAULT_CONFIG_PATH = _resolve_config_path(CONFIG_FILE).resolve()
_ACTIVE_CONFIG_FILE = str(_DEFAULT_CONFIG_PATH)
_ACTIVE_APP_CONFIG = APP_CONFIG


def activate_config(filename: str | Path | None = None) -> JsonObject:
    """Select the settings file used by get_config for the current process."""
    global _ACTIVE_CONFIG_FILE, _ACTIVE_APP_CONFIG
    target = str(filename or CONFIG_FILE)
    if _same_config_file(target, CONFIG_FILE):
        _ACTIVE_CONFIG_FILE = str(_DEFAULT_CONFIG_PATH)
        _ACTIVE_APP_CONFIG = APP_CONFIG
        return _ACTIVE_APP_CONFIG
    override = _load_json_config(target)
    _ACTIVE_CONFIG_FILE = str(_resolve_config_path(target).resolve())
    _ACTIVE_APP_CONFIG = _deep_merge(APP_CONFIG, override)
    return _ACTIVE_APP_CONFIG


def active_config_file() -> str:
    return _ACTIVE_CONFIG_FILE


def active_app_config() -> JsonObject:
    return _ACTIVE_APP_CONFIG


def get_config(*keys: str, default: Any = None) -> Any:
    current: Any = active_app_config()
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current
def _resolve_model_setting(
    module: str,
    env_suffix: str,
    module_key: str,
    global_env_name: str,
    global_key: str,
    module_cfg: JsonObject,
    model_cfg: JsonObject,
) -> Any:
    module_env = os.getenv(f"LANGGRAPH_JSZN_{module.upper()}_{env_suffix}")
    if module_env is not None:
        return module_env
    if module_key in module_cfg and module_cfg[module_key] is not None:
        return module_cfg[module_key]
    global_env = os.getenv(global_env_name)
    if global_env is not None:
        return global_env
    return model_cfg.get(global_key)


def _resolve_model_number_setting(
    module: str,
    env_suffix: str,
    module_key: str,
    global_env_names: list[str],
    module_cfg: JsonObject,
    default: Any,
    caster: Callable[[Any], Any],
) -> Any:
    env_names = [f"LANGGRAPH_JSZN_{module.upper()}_{env_suffix}", f"LANGGRAPH_JSZN_{env_suffix}", *global_env_names]
    for env_name in env_names:
        raw = os.getenv(env_name)
        if raw is None or str(raw).strip() == "":
            continue
        try:
            return caster(raw)
        except (TypeError, ValueError):
            continue
    if module_key in module_cfg and module_cfg[module_key] is not None:
        return module_cfg[module_key]
    return default


def _parse_bool_setting(value: Any) -> bool | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return None


def _enable_thinking_override(module: str) -> bool | None:
    for env_name in (
        f"LANGGRAPH_JSZN_{module.upper()}_ENABLE_THINKING",
        "LANGGRAPH_JSZN_ENABLE_THINKING",
        "OURAGENT_LLM_ENABLE_THINKING",
    ):
        parsed = _parse_bool_setting(os.getenv(env_name))
        if parsed is not None:
            return parsed
    return None


def get_model_config(module: str) -> JsonObject:
    model_cfg = get_config("model", default={}) or {}
    module_cfg = (model_cfg.get("modules") or {}).get(module, {})
    config = {
        "base_url": _resolve_model_setting(
            module,
            "API_BASE",
            "api_base",
            "LANGGRAPH_JSZN_API_BASE",
            "api_base",
            module_cfg,
            model_cfg,
        ),
        "api_key": _resolve_model_setting(
            module,
            "API_KEY",
            "api_key",
            "LANGGRAPH_JSZN_API_KEY",
            "api_key",
            module_cfg,
            model_cfg,
        ),
        "model": _resolve_model_setting(
            module,
            "API_MODEL",
            "model_name",
            "LANGGRAPH_JSZN_API_MODEL",
            "model_name",
            module_cfg,
            model_cfg,
        ),
        "temperature": _resolve_model_number_setting(
            module,
            "TEMPERATURE",
            "temperature",
            ["OURAGENT_LLM_TEMPERATURE"],
            module_cfg,
            0.1,
            float,
        ),
        "max_tokens": _resolve_model_number_setting(
            module,
            "MAX_TOKENS",
            "max_tokens",
            ["OURAGENT_LLM_MAX_TOKENS"],
            module_cfg,
            2048,
            int,
        ),
        "timeout": _resolve_model_number_setting(
            module,
            "TIMEOUT",
            "timeout",
            ["OURAGENT_LLM_TIMEOUT"],
            module_cfg,
            model_cfg.get("timeout", 120),
            float,
        ),
    }
    extra_body = module_cfg.get("extra_body", model_cfg.get("extra_body"))
    thinking_override = _enable_thinking_override(module)
    if thinking_override is not None:
        extra_body = dict(extra_body or {})
        chat_template_kwargs = dict(extra_body.get("chat_template_kwargs") or {})
        chat_template_kwargs["enable_thinking"] = thinking_override
        extra_body["chat_template_kwargs"] = chat_template_kwargs
    if extra_body:
        config["extra_body"] = extra_body
    return config
