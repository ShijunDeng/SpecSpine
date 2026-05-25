from __future__ import annotations

from typing import Any

from .review_checks import _build_review_checks, _build_feature_commands
from .helpers import _dedupe_commands

__all__ = [
    "_build_review_data",
]


def _build_review_data(
    validation: dict[str, Any],
    gates: Any,
    impact: Any,
    feature_slug: str | None,
    feature_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    review_checks = _build_review_checks(
        validation_ok=validation["ok"],
        gates_source_missing=gates.source_missing,
        has_impact_recommendations=bool(impact.recommendations),
        feature_payload=feature_payload,
    )
    failed_checks = tuple(
        check["id"] for check in review_checks if check["status"] != "pass"
    )
    feature_commands = _build_feature_commands(feature_slug)

    recommended_commands = _dedupe_commands(
        impact.recommended_commands,
        gates.recommended_commands,
        (
            "specspine review packet . --json",
            "specspine validate . --fusion --features",
        ),
        feature_commands,
    )

    return {
        "review_checks": review_checks,
        "failed_checks": failed_checks,
        "recommended_commands": recommended_commands,
        "summary": {
            "changed_files": len(impact.changed_files),
            "failed_review_checks": len(failed_checks),
            "feature_included": feature_slug is not None,
            "passed_review_checks": len(review_checks) - len(failed_checks),
            "recommended_commands": len(recommended_commands),
            "review_checks": len(review_checks),
            "test_impact_recommendations": len(impact.recommendations),
            "validation_ok": bool(validation["ok"]),
        },
    }
