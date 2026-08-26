from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = Path(os.getenv("OURAGENT_WORKSPACE_ROOT", str(PROJECT_ROOT.parent))).resolve()
CONFIG_FILE = "config/settings.json"

# 定义一个函数 project_path，接受可变数量的字符串参数 parts，返回一个 Path 对象，表示项目根目录下的路径。joinpath()方法用于将多个路径组件连接成一个完整的路径。
# *parts: str 表示 parts 是一个字符串类型的可变参数，可以接受任意数量的字符串参数，并将它们作为一个元组传递给函数。不使用*时，parts 将被视为一个单独的参数，而不是多个参数。
# 比如*parts: str，如果调用 project_path("data", "input.json")，则 parts 将是一个包含两个元素的元组 ("data", "input.json")，函数内部可以通过 parts[0] 和 parts[1] 来访问这两个参数。
# 如果不使用*，即 parts: str，那么调用 project_path("data", "input.json") 将会导致错误，因为函数期望一个字符串参数，而不是两个。
def project_path(*parts: str) -> Path:
    return PROJECT_ROOT.joinpath(*parts)


def workspace_path(*parts: str) -> Path:
    return WORKSPACE_ROOT.joinpath(*parts)


def _resolve_config_path(filename: str) -> Path:
    path = Path(str(filename or ""))
    if path.is_absolute():
        return path
    return project_path(str(path))


def _deep_merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        current = merged.get(key)
        if isinstance(current, dict) and isinstance(value, dict):
            merged[key] = _deep_merge(current, value)
        else:
            merged[key] = value
    return merged


def _load_json_config(filename: str) -> dict:
    config_path = _resolve_config_path(filename)
    if not config_path.exists():
        raise FileNotFoundError(f"required config file not found: {config_path}")
    try:
        with config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise RuntimeError(f"{filename} 加载失败: {e}") from e
    if not isinstance(data, dict):
        raise ValueError(f"{filename} must contain a JSON object")
    return data



def _same_config_file(left: str | Path, right: str | Path) -> bool:
    try:
        return _resolve_config_path(str(left)).resolve() == _resolve_config_path(str(right)).resolve()
    except Exception:
        return str(left) == str(right)


def load_app_config(filename: str | Path | None = None) -> dict:
    return _load_json_config(str(filename or CONFIG_FILE))


APP_CONFIG = load_app_config()
_DEFAULT_CONFIG_PATH = _resolve_config_path(CONFIG_FILE).resolve()
_ACTIVE_CONFIG_FILE = str(_DEFAULT_CONFIG_PATH)
_ACTIVE_APP_CONFIG = APP_CONFIG


def activate_config(filename: str | Path | None = None) -> dict:
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


def active_app_config() -> dict:
    return _ACTIVE_APP_CONFIG


def get_config(*keys: str, default: Any = None) -> Any:
    current: Any = active_app_config()
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current
#这个函数 _resolve_model_setting 用于解析模型配置项的值，按照优先级从环境变量、模块配置、全局环境变量和全局配置中查找。
#它接受多个参数，包括模块名称、环境变量后缀、模块配置键、全局环境变量名称、全局配置键以及模块和模型的配置字典。
#函数首先尝试从环境变量中获取值，如果存在则返回；如果模块配置中存在对应键且不为 None，则返回该值；接着尝试从全局环境变量获取值，如果存在则返回；最后返回模型配置中的全局键对应的值。
#比如对于模型配置项 "api_key"，函数会依次检查环境变量 "LANGGRAPH_JSZN_{MODULE}_API_KEY"，模块配置中的 "api_key"，全局环境变量 "LANGGRAPH_JSZN_API_KEY"，以及模型配置中的 "api_key" 键，
#返回第一个找到的非 None 值。
#每个参数的含义如下：
# - module: 模块名称，用于构建环境变量名和查找模块配置。
# - env_suffix: 环境变量后缀，用于构建环境变量名。
# - module_key: 模块配置键，用于查找模块配置中的值。
# - global_env_name: 全局环境变量名称，用于查找全局环境变量中的值。
# - global_key: 全局配置键，用于查找模型配置中的值。
# - module_cfg: 模块配置字典，包含模块特定的配置项。
# - model_cfg: 模型配置字典，包含全局的模型配置项。
def _resolve_model_setting(
    module: str,
    env_suffix: str,
    module_key: str,
    global_env_name: str,
    global_key: str,
    module_cfg: dict,
    model_cfg: dict,
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
    module_cfg: dict,
    default: Any,
    caster,
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


# 定义一个函数 get_model_config，接受一个模块名称作为参数，返回一个字典类型的模型配置。该函数会根据模块名称从全局配置中获取对应的模块配置，并使用 _resolve_model_setting 函数解析每个配置项的值。
# 返回的配置字典包含以下键：
# - "base_url": 模型的 API 基础 URL。
# - "api_key": 模型的 API 密钥。
# - "model": 模型名称。
# - "temperature": 模型的温度参数，默认为 0.1。
# - "max_tokens": 模型的最大 token 数量，默认为 2048。
# - "timeout": 模型的超时时间，默认为模块配置中的 timeout 或全局模型配置中的 timeout。
# 如果模块配置或全局模型配置中存在 "extra_body" 键，则会将其添加到返回的配置字典中。
def get_model_config(module: str) -> dict:
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
