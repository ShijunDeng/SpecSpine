from __future__ import annotations

from pathlib import Path
from typing import Any

from .coverage_plan_items import (
    _coverage_plan_safety_notes,
    _missing_feature_plan_report,
)
from ._coverage_summary_builder import build_coverage_plan_summary
from ._coverage_commands import _build_recommended_commands


def assemble_coverage_plan_report(
    resolved_root: Path,
    features: list[dict[str, Any]],
    feature_filter: str | None,
    debt_report: dict[str, Any],
    items: list[dict[str, Any]],
    *,
    use_policy: bool = False,
    limit: int | None = None,
) -> dict[str, Any]:
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

    returned_items = items[:limit] if limit is not None else items
    recommended_commands = _build_recommended_commands(items)
    summary = build_coverage_plan_summary(
        required_records, features, items, returned_items,
    )

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


__all__ = [
    "assemble_coverage_plan_report",
]
