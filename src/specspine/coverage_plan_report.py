from __future__ import annotations

from pathlib import Path
from typing import Any

from ._coverage_plan_filter import resolve_coverage_plan_features
from ._coverage_plan_assembler import assemble_coverage_plan_report
from .coverage_debt import build_coverage_debt_report
from .coverage_plan_items import (
    _build_feature_coverage_plan_item,
    _missing_feature_plan_report,
)
from .features import validate_feature_slug

__all__ = [
    "build_coverage_plan_report",
]


def build_coverage_plan_report(
    root: Path,
    *,
    use_policy: bool = False,
    feature_filter: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    resolved_root = root.expanduser().resolve()
    if limit is not None and limit < 0:
        raise ValueError("limit must be non-negative")

    features, feature_filter = resolve_coverage_plan_features(
        resolved_root, feature_filter=feature_filter,
    )
    if feature_filter is not None and not features:
        return _missing_feature_plan_report(
            resolved_root,
            feature_filter=feature_filter,
            use_policy=use_policy,
        )

    debt_report = build_coverage_debt_report(resolved_root, use_policy=use_policy)
    debt_records = {
        str(record["feature_id"]): record for record in debt_report["features"]
    }

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

    return assemble_coverage_plan_report(
        resolved_root,
        features,
        feature_filter,
        debt_report,
        items,
        use_policy=use_policy,
        limit=limit,
    )
