from __future__ import annotations

from .contracts import RepairStrategyRegistry
from .retrac.diagnosis import ReTracRepairStrategy
from .sda.diagnosis import SDARepairStrategy
from .vcr.diagnosis import VCRRepairStrategy


def build_default_registry(
    *,
    sda_max_backtrack_depth: int,
    vcr_max_segment_actions: int,
    vcr_max_backtrack_depth: int,
    strategy_name: str,
    vcr_merge_gap_actions: int = 0,
) -> RepairStrategyRegistry:
    """Build the strategy catalog without owning the evaluation workflow."""

    return RepairStrategyRegistry(
        (
            SDARepairStrategy(
                max_backtrack_depth=sda_max_backtrack_depth,
            ),
            VCRRepairStrategy(
                max_segment_actions=vcr_max_segment_actions,
                max_backtrack_depth=vcr_max_backtrack_depth,
                merge_gap_actions=vcr_merge_gap_actions,
            ),
            ReTracRepairStrategy(),
        ),
        default_strategy=strategy_name,
    )


__all__ = ["build_default_registry"]
