"""Coverage plan report building."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from specspine._coverage_plan_filter import resolve_coverage_plan_features
from specspine._coverage_plan_assembler import assemble_coverage_plan_report
from specspine.coverage_debt import build_coverage_debt_report
from specspine.coverage_plan_items import _missing_feature_plan_report

from ._plan_report_validation import validate_coverage_plan_inputs
from ._plan_report_items_builder import build_coverage_plan_items

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
    validate_coverage_plan_inputs(
        resolved_root,
        limit=limit,
        feature_filter=feature_filter,
    )

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

    items = build_coverage_plan_items(
        resolved_root,
        features,
        debt_records,
        use_policy=use_policy,
    )

    return assemble_coverage_plan_report(
        resolved_root,
        features,
        feature_filter,
        debt_report,
        items,
        use_policy=use_policy,
        limit=limit,
    )
