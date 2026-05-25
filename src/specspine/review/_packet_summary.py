from __future__ import annotations

from typing import Any

__all__ = [
    "_build_summary",
    "_build_safety_notes",
]


def _build_summary(
    impact: Any,
    failed_checks: tuple,
    feature_slug: str | None,
    review_checks: list,
    recommended_commands: list,
    validation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "changed_files": len(impact.changed_files),
        "failed_review_checks": len(failed_checks),
        "feature_included": feature_slug is not None,
        "passed_review_checks": len(review_checks) - len(failed_checks),
        "recommended_commands": len(recommended_commands),
        "review_checks": len(review_checks),
        "test_impact_recommendations": len(impact.recommendations),
        "validation_ok": bool(validation["ok"]),
    }


def _build_safety_notes() -> tuple[str, str, str]:
    return (
        "This command composes local SpecSpine reports only.",
        "Recommended commands are advisory and are not executed.",
        "SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, or read tokens.",
    )
