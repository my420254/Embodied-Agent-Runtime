# flags.py —— 评估器特性开关与参数读取。
# 这里集中管理：
#   - 全局强制开关 ENABLE_SANDBOX_EVALUATOR（测试会 monkeypatch 本模块的这个变量）
#   - 各特性是否开启的判断函数（is_sandbox_evaluator_enabled 等）
#   - 修复策略的上限参数读取（配置读取器可注入）
from __future__ import annotations

from typing import Any, Callable

from config.settings import get_config
from graph.planning.config import (
    merge_planning_feature_flags,
    planning_feature_enabled,
)
from graph.state import PlanningState


# 测试或调试时可用的全局强制开关：
# - None: 按 feature flag + config 正常判断是否启用沙盒评估
# - True / False: 直接覆盖正常配置
# 这是 ENABLE_SANDBOX_EVALUATOR 的规范存储位置。
ENABLE_SANDBOX_EVALUATOR: bool | None = None


def _get_override() -> bool | None:
    return ENABLE_SANDBOX_EVALUATOR


def _read_config(*keys, default=None, config_reader: Callable[..., Any] = get_config):
    return config_reader(*keys, default=default)


def _feature_enabled(feature_flags: dict | None, name: str, default: bool = True) -> bool:
    return planning_feature_enabled(feature_flags, name, default)


def is_sandbox_evaluator_enabled(state: PlanningState | None = None) -> bool:
    override = _get_override()
    if override is not None:
        return bool(override)
    strict_benchmark_flags = bool(state.get("benchmark_strict_feature_flags", False)) if isinstance(state, dict) else False
    feature_flags = merge_planning_feature_flags(
        state.get("feature_flags", {}) if isinstance(state, dict) else {},
        include_defaults=not strict_benchmark_flags,
    )
    return bool(feature_flags.get("sandbox_evaluator", True))


def _sda_max_backtrack_depth(config_reader: Callable[..., Any] = get_config) -> int:
    try:
        return int(_read_config("planning", "sda", "max_backtrack_depth", default=0, config_reader=config_reader) or 0)
    except (TypeError, ValueError):
        return 0


def _vcr_max_segment_actions(config_reader: Callable[..., Any] = get_config) -> int:
    try:
        return int(_read_config("planning", "vcr", "max_segment_actions", default=24, config_reader=config_reader) or 24)
    except (TypeError, ValueError):
        return 24


def _vcr_max_backtrack_depth(config_reader: Callable[..., Any] = get_config) -> int:
    try:
        return int(_read_config("planning", "vcr", "max_backtrack_depth", default=0, config_reader=config_reader) or 0)
    except (TypeError, ValueError):
        return 0


def _vcr_merge_gap_actions(config_reader: Callable[..., Any] = get_config) -> int:
    try:
        return max(
            0,
            int(
                _read_config(
                    "planning",
                    "vcr",
                    "merge_gap_actions",
                    default=0,
                    config_reader=config_reader,
                )
                or 0
            ),
        )
    except (TypeError, ValueError):
        return 0


__all__ = [
    "ENABLE_SANDBOX_EVALUATOR",
    "_feature_enabled",
    "is_sandbox_evaluator_enabled",
    "_sda_max_backtrack_depth",
    "_vcr_max_segment_actions",
    "_vcr_max_backtrack_depth",
    "_vcr_merge_gap_actions",
    "_read_config",
]
