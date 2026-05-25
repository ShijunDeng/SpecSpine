from __future__ import annotations

from pathlib import Path
from typing import Any

from .coverage_debt import build_coverage_debt_report
from .coverage_plan_items import (
    _build_feature_coverage_plan_item,
    _coverage_plan_safety_notes,
    _missing_feature_plan_report,
)
from .features import (
    list_feature_bundles,
    validate_feature_slug,
)

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
    if feature_filter is not None:
        feature_filter = validate_feature_slug(feature_filter)
    if limit is not None and limit < 0:
        raise ValueError("limit must be non-negative")

    features = list_feature_bundles(resolved_root)
    if feature_filter is not None:
        features = [
            feature for feature in features if str(feature["slug"]) == feature_filter
        ]
        if not features:
            return _missing_feature_plan_report(
                resolved_root,
                feature_filter=feature_filter,
                use_policy=use_policy,
            )

    debt_report = build_coverage_debt_report(resolved_root, use_policy=use_policy)
    debt_records = {
        str(record["feature_id"]): record for record in debt_report["features"]
    }
    selected_records = [
        debt_records[str(feature["slug"])]
        for feature in features
        if str(feature["slug"]) in debt_records
    ]
    required_records = [
        record for record in selected_records if bool(record["coverage_required"])
    ]
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

    returned_items = items[:limit] if limit is not None else items
    recommended_commands = [
        f"specspine coverage plan . --feature {item['feature_id']} --json"
        for item in items
    ]
    if not recommended_commands:
        recommended_commands = ["specspine coverage debt . --json"]

    summary = {
        "acceptance_criteria_total": sum(
            int(record["acceptance_criteria_total"]) for record in required_records
        ),
        "coverage_required_total": len(required_records),
        "feature_missing": False,
        "features_scanned": len(features),
        "features_with_plan_items": len(items),
        "items_returned": len(returned_items),
        "items_total": len(items),
        "missing_acceptance_criteria": sum(
            int(record["missing_acceptance_criteria"]) for record in required_records
        ),
    }
    report: dict[str, Any] = {
        "feature_filter": feature_filter,
        "items": returned_items,
        "mode": debt_report["mode"],
        "recommended_commands": recommended_commands,
        "root": str(resolved_root),
        "safety_notes": _coverage_plan_safety_notes(),
        "summary": summary,
    }
    if limit is not None:
        report["limit"] = limit
    if use_policy:
        report["policy_applied"] = debt_report.get("policy_applied", False)
        report["policy_source"] = debt_report.get("policy_source")
        report["policy_source_missing"] = debt_report.get("policy_source_missing", False)
    return report
