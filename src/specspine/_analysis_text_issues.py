from __future__ import annotations

from .analysis_models import AnalysisReport, TEXT_MAX_ISSUES_PER_FEATURE

__all__ = [
    "render_analysis_issues",
]


def render_analysis_issues(report: AnalysisReport) -> list[str]:
    lines: list[str] = []
    if not report.issues:
        lines.append("- None. No consistency or coverage issues found.")
    else:
        for feature in report.features:
            if not feature.issues:
                continue
            lines.append(f"- {feature.feature_id} ({feature.status}, ready={'yes' if feature.ready else 'no'})")
            for issue in feature.issues[:TEXT_MAX_ISSUES_PER_FEATURE]:
                location = issue.source_file
                if issue.line is not None:
                    location = f"{location}:{issue.line}"
                lines.append(
                    f"  - [{issue.severity}] {issue.category}/{issue.code} "
                    f"{location} - {issue.message}"
                )
            hidden = len(feature.issues) - TEXT_MAX_ISSUES_PER_FEATURE
            if hidden > 0:
                lines.append(f"  - ... {hidden} more issue(s); use --json for the full list.")
    return lines
