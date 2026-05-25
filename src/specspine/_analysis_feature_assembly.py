from __future__ import annotations

from pathlib import Path

from .analysis_models import FeatureAnalysis, _PendingIssue
from .analysis_build_core import _build_feature_analysis, _assign_issue_ids

__all__ = [
    "_assemble_features_with_issues",
]


def _assemble_features_with_issues(
    resolved_root: Path,
    selected: list[dict],
) -> tuple[list[FeatureAnalysis], list]:
    from .analysis_models import FeatureAnalysis, AnalysisIssue

    base_features: list[FeatureAnalysis] = []
    pending_by_feature: dict[str, list[_PendingIssue]] = {}
    for feature in selected:
        analysis, pending_issues = _build_feature_analysis(resolved_root, feature)
        base_features.append(analysis)
        pending_by_feature[analysis.feature_id] = pending_issues

    assigned = _assign_issue_ids(pending_by_feature)
    features: list[FeatureAnalysis] = []
    all_issues: list[AnalysisIssue] = []
    for feature in sorted(base_features, key=lambda item: item.feature_id):
        issues = assigned.get(feature.feature_id, ())
        all_issues.extend(issues)
        features.append(
            FeatureAnalysis(
                feature_id=feature.feature_id,
                status=feature.status,
                ready=feature.ready,
                source_files=feature.source_files,
                missing_files=feature.missing_files,
                metrics=feature.metrics,
                issues=issues,
                recommended_commands=feature.recommended_commands,
            )
        )

    return features, all_issues
