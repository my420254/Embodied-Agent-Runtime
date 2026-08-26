from collections.abc import Callable
from typing import Any

FeatureContext = dict[str, Any]
FeatureResult = dict[str, Any]
Feature = Callable[[FeatureContext, FeatureResult], FeatureResult]


def merge_feature_update(result: FeatureResult, update: FeatureResult | None) -> FeatureResult:
    if not update:
        return result
    merged = dict(result)
    merged.update(update)
    return merged
