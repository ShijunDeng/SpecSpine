from __future__ import annotations

from typing import Any

from .helpers import _review_check

__all__ = [
    "_build_review_checks",
    "_build_feature_commands",
]


def _build_review_checks(
    validation_ok: bool,
    gates_source_missing: bool,
    has_impact_recommendations: bool,
    feature_payload: dict[str, Any] | None,
) -> tuple[dict[str, Any], ...]:
    checks = [
        _review_check(
            "review.validation",
            bool(validation_ok),
            "Workspace validation passes.",
        ),
        _review_check(
            "review.quality_gates_source",
            not gates_source_missing,
            "Quality gate source file exists.",
        ),
        _review_check(
            "review.test_impact",
            bool(has_impact_recommendations),
            "Test impact recommendations are available.",
        ),
    ]
    if feature_payload is not None:
        checks.extend(
            [
                _review_check(
                    "review.feature_exists",
                    bool(feature_payload["has_native_files"]),
                    "Native feature evidence exists.",
                ),
                _review_check(
                    "review.feature_ready",
                    bool(feature_payload["ready"]["ready"]),
                    "Feature readiness passes with coverage required.",
                ),
                _review_check(
                    "review.trace_gaps",
                    not bool(feature_payload["gaps"]),
                    "Feature trace has no gaps.",
                ),
                _review_check(
                    "review.blocking_checks",
                    not bool(feature_payload["blocking_checks"]),
                    "Feature has no blocking readiness checks.",
                ),
            ]
        )
    return tuple(checks)


def _build_feature_commands(feature_slug: str | None) -> tuple[str, ...]:
    if feature_slug is not None:
        return (
            f"specspine review packet . --feature {feature_slug} --json",
            f"specspine feature handoff {feature_slug} . --json",
            f"specspine feature ready {feature_slug} . --json --require-coverage",
            f"specspine feature trace {feature_slug} . --json",
            f"specspine feature tests {feature_slug} . --json",
        )
    return ()
