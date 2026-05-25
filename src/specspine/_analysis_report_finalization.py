from __future__ import annotations

from pathlib import Path

from .analysis_models import AnalysisIssue, FeatureAnalysis, AnalysisReport
from .analysis_build_commands import _dedupe_commands
from .analysis_build_core import _summary
from ._analysis_feature_assembly import _assemble_features_with_issues

__all__ = [
    "assemble_analysis_report",
]


def assemble_analysis_report(
    resolved_root: Path,
    selected: list[dict],
    feature_filter: str | None,
) -> AnalysisReport:
    features, all_issues = _assemble_features_with_issues(resolved_root, selected)

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
            discovered_features=len(selected),
        ),
        features=feature_tuple,
        issues=issue_tuple,
        recommended_commands=recommended_commands,
    )
