from __future__ import annotations

import copy
from collections.abc import Callable
from typing import Any

from config.settings import get_config


PLANNING_FEATURE_DEFAULTS: dict[str, bool] = {
    "cognitive_planning": False,
    "cognitive_lightweight_path": False,
    "sandbox_evaluator": True,
    "semantic_audit": True,
    "state_diff_audit": False,
    "cognitive_bt_compile": False,
    "cognitive_bt_execute": False,
    "cognitive_bt_recovery_direct_replan": False,
    "cognitive_bt_execution_reflection_retry": False,
    "playbook_retrieval": True,
    "playbook_write": True,
    "candidate_rules": False,
    "cognitive_trace_write": False,
    "reflection": True,
    "preserve_failed_todo_list": False,
}
PLANNING_OPTION_DEFAULTS: dict[str, Any] = {
    "evaluation_repair_attempts": 10,
}
EVALUATION_ONLY_OPTIONS = {"repair_strategy"}
PLANNING_FEATURE_OPTIONS = frozenset(
    {*PLANNING_FEATURE_DEFAULTS.keys(), *PLANNING_OPTION_DEFAULTS.keys()}
)

REPAIR_STRATEGY_NONE = "none"
REPAIR_STRATEGY_RETRAC = "retrac"
REPAIR_STRATEGY_SDA = "sda"
REPAIR_STRATEGY_VCR = "vcr"
REPAIR_STRATEGIES = frozenset(
    {
        REPAIR_STRATEGY_NONE,
        REPAIR_STRATEGY_RETRAC,
        REPAIR_STRATEGY_SDA,
        REPAIR_STRATEGY_VCR,
    }
)


def get_planning_feature_defaults() -> dict[str, Any]:
    features: dict[str, Any] = {
        **PLANNING_FEATURE_DEFAULTS,
        **PLANNING_OPTION_DEFAULTS,
    }
    configured = get_config("planning", "features", default={}) or {}
    if isinstance(configured, dict):
        for name, value in configured.items():
            if name in EVALUATION_ONLY_OPTIONS or name not in PLANNING_FEATURE_OPTIONS:
                continue
            features[str(name)] = _planning_config_value(str(name), value)
    return features


def merge_planning_feature_flags(
    overrides: dict[str, Any] | None = None,
    *,
    include_defaults: bool = True,
) -> dict[str, Any]:
    features = get_planning_feature_defaults() if include_defaults else {}
    if isinstance(overrides, dict):
        for name, value in overrides.items():
            if name in EVALUATION_ONLY_OPTIONS or name not in PLANNING_FEATURE_OPTIONS:
                continue
            features[str(name)] = _planning_config_value(str(name), value)
    return features


def _planning_config_value(name: str, value: Any) -> Any:
    if name == "evaluation_repair_attempts":
        try:
            return max(0, min(int(value), 10))
        except (TypeError, ValueError):
            return PLANNING_OPTION_DEFAULTS[name]
    return bool(value)


def with_planning_config(state: dict | None) -> dict:
    configured = copy.deepcopy(state) if isinstance(state, dict) else {}
    include_defaults = not bool(configured.get("benchmark_strict_feature_flags", False))
    configured["feature_flags"] = merge_planning_feature_flags(
        configured.get("feature_flags"),
        include_defaults=include_defaults,
    )
    configured["planning_config"] = {
        "max_iterations": get_planning_max_iterations(),
        "features": dict(configured["feature_flags"]),
    }
    return configured


def get_planning_max_iterations() -> int:
    try:
        return int(get_config("planning", "max_iterations", default=10))
    except (TypeError, ValueError):
        return 10


def normalize_repair_strategy(value: Any) -> str:
    name = str(value or "").strip().lower().replace("-", "_")
    if name not in REPAIR_STRATEGIES:
        return f"invalid:{name}"
    return name


def configured_repair_strategy(
    config_reader: Callable[..., Any] = get_config,
) -> str:
    configured = config_reader(
        "planning",
        "evaluation",
        "repair_strategy",
        default=REPAIR_STRATEGY_NONE,
    )
    return normalize_repair_strategy(configured)


def active_repair_strategy() -> str:
    """Return the single active sequence-repair strategy from settings only."""

    return configured_repair_strategy()


def repair_strategy_event() -> dict[str, Any]:
    return {
        "layer": "repair_strategy",
        "type": "selected",
        "strategy": active_repair_strategy(),
        "source": "planning.evaluation.repair_strategy",
    }


def repair_strategy_enabled(
    strategy: str | None = None,
    *,
    config_reader: Callable[..., Any] = get_config,
) -> bool:
    if strategy is not None:
        return normalize_repair_strategy(strategy) != REPAIR_STRATEGY_NONE
    return configured_repair_strategy(config_reader) != REPAIR_STRATEGY_NONE


def max_planning_iterations() -> int:
    return get_planning_max_iterations()


def planning_feature_enabled(
    feature_flags: dict | None,
    name: str,
    default: bool | None = None,
) -> bool:
    if isinstance(feature_flags, dict) and name in feature_flags:
        return bool(feature_flags[name])
    defaults = get_planning_feature_defaults()
    if name in defaults:
        return bool(defaults[name])
    return bool(default) if default is not None else False


def feature_enabled(feature_flags: dict | None, name: str, default: bool = True) -> bool:
    return planning_feature_enabled(feature_flags, name, default)


def sda_max_backtrack_depth() -> int:
    try:
        return int(get_config("planning", "sda", "max_backtrack_depth", default=0) or 0)
    except (TypeError, ValueError):
        return 0


def sda_max_subtree_actions() -> int:
    try:
        return int(get_config("planning", "sda", "max_subtree_actions", default=80) or 80)
    except (TypeError, ValueError):
        return 80
