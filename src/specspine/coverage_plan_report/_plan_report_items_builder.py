"""Build coverage plan items from features and debt records."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from specspine.coverage_plan_items import _build_feature_coverage_plan_item

__all__ = [
    "build_coverage_plan_items",
]


def build_coverage_plan_items(
    resolved_root: Path,
    features: list[dict[str, Any]],
    debt_records: dict[str, dict[str, Any]],
    *,
    use_policy: bool = False,
) -> list[dict[str, Any]]:
    """Build plan items for each feature with debt records."""
    items: list[dict[str, Any]] = []
    for feature in features:
        slug = str(feature["slug"])
        record = debt_records.get(slug)
        if record is None:
            continue
        item = _build_feature_coverage_plan_item(
            resolved_root,
            feature,
            record=record,
            use_policy=use_policy,
        )
        if item is not None:
            items.append(item)
    return items
