from __future__ import annotations

import json

from .analysis_models import (
    AnalysisReport,
    TEXT_MAX_ISSUES_PER_FEATURE,
    TEXT_MAX_RECOMMENDATIONS,
)

__all__ = [
    "render_analysis_text",
    "render_analysis_json",
]


def render_analysis_json(report: AnalysisReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_analysis_text(report: AnalysisReport) -> str:
    summary = report.summary
    severity_counts = summary["issue_counts_by_severity"]
    assert isinstance(severity_counts, dict)
    lines = [
        "SpecSpine analysis",
        f"Root: {report.root}",
        f"Feature filter: {report.feature_filter or 'all'}",
        (
            "Summary: "
            f"features={summary['features_analyzed']} "
            f"ready={summary['features_ready']} "
            f"issues={summary['issues_total']} "
            f"critical={severity_counts.get('critical', 0)} "
            f"high={severity_counts.get('high', 0)} "
            f"medium={severity_counts.get('medium', 0)} "
            f"low={severity_counts.get('low', 0)}"
        ),
        "",
        "Issues:",
    ]

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

    lines.extend(["", "Recommendations:"])
    for command in report.recommended_commands[:TEXT_MAX_RECOMMENDATIONS]:
        lines.append(f"- {command}")
    hidden_commands = len(report.recommended_commands) - TEXT_MAX_RECOMMENDATIONS
    if hidden_commands > 0:
        lines.append(
            f"- ... {hidden_commands} more recommended command(s); use --json for the full list."
        )
    if not report.issues:
        lines.append("- Analysis is clean; continue with validation or implementation handoff.")

    return "\n".join(lines) + "\n"
