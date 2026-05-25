from __future__ import annotations

from typing import Any


def build_coverage_plan_summary(
    required_records: list[dict[str, Any]],
    features: list[dict[str, Any]],
    items: list[dict[str, Any]],
    returned_items: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
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


__all__ = [
    "build_coverage_plan_summary",
]
