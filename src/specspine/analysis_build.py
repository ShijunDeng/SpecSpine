from __future__ import annotations

from pathlib import Path

from .features import (
    FEATURE_FILE_PATHS,
    list_feature_bundles,
    validate_feature_slug,
)
from .analysis_models import (
    AnalysisIssue,
    FeatureAnalysis,
    AnalysisReport,
    _PendingIssue,
)
from .analysis_build_commands import _dedupe_commands
from .analysis_build_core import (
    _build_missing_feature_analysis,
    _build_feature_analysis,
    _assign_issue_ids,
    _summary,
)

__all__ = [
    "_dedupe_commands",
    "_build_missing_feature_analysis",
    "_build_feature_analysis",
    "_assign_issue_ids",
    "_summary",
    "build_analysis_report",
]


def build_analysis_report(
    root: Path,
    *,
    feature_filter: str | None = None,
) -> AnalysisReport:
    resolved_root = root.expanduser().resolve()
    if feature_filter is not None:
        feature_filter = validate_feature_slug(feature_filter)

    discovered = list_feature_bundles(resolved_root)
    selected = [
        feature
        for feature in discovered
        if feature_filter is None or str(feature["slug"]) == feature_filter
    ]
    if feature_filter is not None and not selected:
        selected = [
            {
                "slug": feature_filter,
                "complete": False,
                "files": {},
                "status": None,
                "status_consistent": False,
                "missing_files": [
                    relative_path.format(slug=feature_filter)
                    for relative_path in FEATURE_FILE_PATHS.values()
                ],
            }
        ]

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

    recommended_commands = _dedupe_commands(
        [
            command
            for issue in all_issues
            for command in ([issue.recommended_command] if issue.recommended_command else [])
        ]
        or ["specspine validate . --fusion --features --json"]
    )

    feature_tuple = tuple(features)
    issue_tuple = tuple(all_issues)
    return AnalysisReport(
        root=resolved_root,
        feature_filter=feature_filter,
        summary=_summary(
            feature_tuple,
            issue_tuple,
            discovered_features=len(discovered),
        ),
        features=feature_tuple,
        issues=issue_tuple,
        recommended_commands=recommended_commands,
    )
