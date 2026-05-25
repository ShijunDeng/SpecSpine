from __future__ import annotations

from typing import Any

from .release_models import (
    BreakingChange,
    ReleaseEntry,
)

__all__ = [
    "_compute_summary",
]


def _compute_summary(
    features: list[ReleaseEntry],
    breaking_changes: list[BreakingChange],
) -> dict[str, Any]:
    total = len(features)
    validated = sum(1 for f in features if f.status_transition == "newly validated")
    archived = sum(1 for f in features if f.status_transition == "released (archived)")

    high_breaking = sum(1 for bc in breaking_changes if bc.severity == "high")
    medium_breaking = sum(1 for bc in breaking_changes if bc.severity == "medium")
    low_breaking = sum(1 for bc in breaking_changes if bc.severity == "low")

    priority_counts: dict[str, int] = {}
    for f in features:
        priority_counts[f.priority] = priority_counts.get(f.priority, 0) + 1

    total_validation_evidence = sum(f.validation_evidence_count for f in features)

    summary: dict[str, Any] = {
        "features_total": total,
        "features_validated": validated,
        "features_archived": archived,
        "breaking_changes_total": len(breaking_changes),
        "breaking_changes_high": high_breaking,
        "breaking_changes_medium": medium_breaking,
        "breaking_changes_low": low_breaking,
        "priority_counts": dict(sorted(priority_counts.items())),
        "total_validation_evidence": total_validation_evidence,
    }

    return summary
