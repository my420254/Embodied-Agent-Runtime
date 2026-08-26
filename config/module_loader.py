from __future__ import annotations

from importlib import import_module
from typing import Any, Sequence

from config.settings import get_config


_MODULE_CACHE: dict[str, Any] = {}
_OBJECT_CACHE: dict[str, Any] = {}


def _config_value(keys: Sequence[str], default: str = "") -> str:
    value = get_config(*keys, default=default)
    return str(value or default or "").strip()


def resolve_module(module_name: str, *, required: bool = True, label: str = "module"):
    name = str(module_name or "").strip()
    if not name:
        if required:
            raise ValueError(f"{label} path is empty")
        return None
    if name not in _MODULE_CACHE:
        try:
            _MODULE_CACHE[name] = import_module(name)
        except Exception as e:
            raise RuntimeError(f"failed to load {label} {name}: {e}") from e
    return _MODULE_CACHE[name]


def resolve_object(dotted_path: str, *, required: bool = True, label: str = "object"):
    path = str(dotted_path or "").strip()
    if not path:
        if required:
            raise ValueError(f"{label} path is empty")
        return None
    if path in _OBJECT_CACHE:
        return _OBJECT_CACHE[path]
    module_name, _, attr_name = path.rpartition(".")
    if not module_name or not attr_name:
        if required:
            raise ValueError(f"{label} path must be module.attr: {path}")
        return None
    module = resolve_module(module_name, required=True, label=label)
    obj = getattr(module, attr_name, None)
    if obj is None and required:
        raise AttributeError(f"{path} is required by settings but was not found")
    _OBJECT_CACHE[path] = obj
    return obj


def resolve_callable(dotted_path: str, *, required: bool = True, label: str = "callable"):
    obj = resolve_object(dotted_path, required=required, label=label)
    if obj is None:
        return None
    if not callable(obj):
        raise TypeError(f"{label} must be callable: {dotted_path}")
    return obj


def configured_module(keys: Sequence[str], default_module: str, *, label: str = "configured module"):
    module_name = _config_value(keys, default_module)
    return resolve_module(module_name, required=True, label=label)


def call_configured_module_function(
    keys: Sequence[str],
    default_module: str,
    function_name: str,
    *args,
    label: str = "configured function",
    **kwargs,
) -> Any:
    module = configured_module(keys, default_module, label=label)
    function = getattr(module, function_name, None)
    if not callable(function):
        raise AttributeError(f"{module.__name__}.{function_name} is required by settings")
    return function(*args, **kwargs)
