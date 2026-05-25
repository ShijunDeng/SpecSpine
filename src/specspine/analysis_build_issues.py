from __future__ import annotations

from .analysis_models import (
    SEVERITIES,
    AnalysisIssue,
    _PendingIssue,
)

__all__ = [
    "_assign_issue_ids",
]


def _assign_issue_ids(
    pending_by_feature: dict[str, list[_PendingIssue]],
) -> dict[str, tuple[AnalysisIssue, ...]]:
    sequence = 1
    assigned: dict[str, tuple[AnalysisIssue, ...]] = {}
    for slug in sorted(pending_by_feature):
        feature_issues: list[AnalysisIssue] = []
        pending_issues = sorted(
            pending_by_feature[slug],
            key=lambda issue: (
                SEVERITIES.index(issue.severity),
                issue.category,
                issue.code,
                issue.source_file,
                issue.line or 0,
                issue.message,
            ),
        )
        for pending in pending_issues:
            feature_issues.append(
                AnalysisIssue(
                    id=f"AN{sequence:03d}",
                    feature_id=pending.feature_id,
                    severity=pending.severity,
                    category=pending.category,
                    code=pending.code,
                    message=pending.message,
                    source_file=pending.source_file,
                    line=pending.line,
                    evidence=pending.evidence,
                    recommended_command=pending.recommended_command,
                )
            )
            sequence += 1
        assigned[slug] = tuple(feature_issues)
    return assigned
