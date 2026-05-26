from __future__ import annotations

from .release_models import ReleaseNotesReport

__all__ = [
    "_render_summary_section",
]


def _render_summary_section(report: ReleaseNotesReport) -> list[str]:
    summary = report.summary
    lines = [
        "# Release Notes",
        "",
        f"Version: {report.version}",
        f"Date Range: {report.date_range}",
        "",
        "## Summary",
        "",
        f"- Features Total: {summary['features_total']}",
        f"- Validated: {summary['features_validated']}",
        f"- Archived: {summary['features_archived']}",
        f"- Breaking Changes: {summary['breaking_changes_total']}",
        f"- Validation Evidence Items: {summary['total_validation_evidence']}",
        "",
    ]

    if summary["priority_counts"]:
        lines.append("## Features by Priority")
        lines.append("")
        for priority, count in sorted(summary["priority_counts"].items()):
            lines.append(f"- {priority}: {count}")
        lines.append("")

    return lines
