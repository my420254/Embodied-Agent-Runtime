from __future__ import annotations

from collections.abc import Callable
from typing import Any

from graph.planning.config import configured_repair_strategy

from . import flags
from .repair_strategies import (
    RepairStrategyRegistry,
    build_default_registry,
)


def resolve_repair_strategy(
    config_reader: Callable[..., Any],
) -> str:
    """Resolve the evaluation-owned strategy from settings only."""

    return configured_repair_strategy(config_reader)


def build_repair_registry(
    *,
    config_reader: Callable[..., Any],
    strategy_name: str,
) -> RepairStrategyRegistry:
    return build_default_registry(
        sda_max_backtrack_depth=flags._sda_max_backtrack_depth(config_reader),
        vcr_max_segment_actions=flags._vcr_max_segment_actions(config_reader),
        vcr_max_backtrack_depth=flags._vcr_max_backtrack_depth(config_reader),
        vcr_merge_gap_actions=flags._vcr_merge_gap_actions(config_reader),
        strategy_name=strategy_name,
    )


__all__ = [
    "build_repair_registry",
    "resolve_repair_strategy",
]
