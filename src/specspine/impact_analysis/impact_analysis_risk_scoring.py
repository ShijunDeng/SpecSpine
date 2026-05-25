from __future__ import annotations

from .impact_models import (
    SEVERITY_HIGH,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    ImpactItem,
)

__all__ = [
    "_compute_risk_score",
]


def _compute_risk_score(
    impacted_features: tuple[ImpactItem, ...],
    impacted_tests: tuple[ImpactItem, ...],
    impacted_code: tuple[ImpactItem, ...],
) -> int:
    score = 0

    high_count = sum(
        1 for item in impacted_features + impacted_tests + impacted_code
        if item.severity == SEVERITY_HIGH
    )
    medium_count = sum(
        1 for item in impacted_features + impacted_tests + impacted_code
        if item.severity == SEVERITY_MEDIUM
    )
    low_count = sum(
        1 for item in impacted_features + impacted_tests + impacted_code
        if item.severity == SEVERITY_LOW
    )

    score += high_count * 15
    score += medium_count * 8
    score += low_count * 3

    feature_count = len(impacted_features)
    test_count = len(impacted_tests)
    code_count = len(impacted_code)

    if feature_count > 3:
        score += 20
    elif feature_count > 1:
        score += 10

    if test_count > 5:
        score += 15
    elif test_count > 2:
        score += 8

    if code_count > 5:
        score += 10
    elif code_count > 2:
        score += 5

    return min(score, 100)
