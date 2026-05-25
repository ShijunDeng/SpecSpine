from __future__ import annotations

from .benchmark_models import FeatureMetrics

__all__ = [
    "_primary_issue",
]


def _primary_issue(m: FeatureMetrics) -> str:
    issues = []
    if m.coverage_pct < 50:
        issues.append("low_coverage")
    if m.drift_events > 2:
        issues.append("high_drift")
    if m.consistency_fail > 0:
        issues.append("consistency_failures")
    if m.ac_count > 0 and m.test_count == 0:
        issues.append("no_test_links")
    return issues[0] if issues else "needs_review"
