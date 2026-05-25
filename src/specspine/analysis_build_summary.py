from __future__ import annotations

from .analysis_models import (
    SEVERITIES,
    AnalysisIssue,
    FeatureAnalysis,
)

__all__ = [
    "_summary",
]


def _summary(
    features: tuple[FeatureAnalysis, ...],
    issues: tuple[AnalysisIssue, ...],
    *,
    discovered_features: int,
) -> dict[str, object]:
    severity_counts = {severity: 0 for severity in SEVERITIES}
    category_counts: dict[str, int] = {}
    for issue in issues:
        severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        category_counts[issue.category] = category_counts.get(issue.category, 0) + 1

    return {
        "category_counts": dict(sorted(category_counts.items())),
        "discovered_features": discovered_features,
        "features_analyzed": len(features),
        "features_ready": sum(1 for feature in features if feature.ready),
        "features_total": len(features),
        "features_with_issues": sum(1 for feature in features if feature.issues),
        "issue_counts_by_category": dict(sorted(category_counts.items())),
        "issue_counts_by_severity": severity_counts,
        "issues_total": len(issues),
        "severity_counts": severity_counts,
    }
