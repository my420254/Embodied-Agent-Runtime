import sys as _sys

from . import project_io as io
from .settings import (
    APP_CONFIG,
    CONFIG_FILE,
    PROJECT_ROOT,
    activate_config,
    active_config_file,
    get_config,
    get_model_config,
    load_app_config,
    project_path,
)

_sys.modules.setdefault(__name__ + ".io", io)

__all__ = [
    "APP_CONFIG",
    "CONFIG_FILE",
    "PROJECT_ROOT",
    "activate_config",
    "active_config_file",
    "get_config",
    "get_model_config",
    "io",
    "load_app_config",
    "project_path",
]
