from __future__ import annotations

from .release_models import ReleaseNotesReport

__all__ = [
    "render_release_notes_text",
]


def render_release_notes_text(report: ReleaseNotesReport) -> str:
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

    if report.grouped_features:
        lines.append("## Features")
        lines.append("")
        for group_name, entries in report.grouped_features.items():
            lines.append(f"### {group_name}")
            lines.append("")
            for entry in entries:
                marker = "validated" if entry.status_transition == "newly validated" else "archived"
                lines.append(f"- **{entry.title}** (`{entry.slug}`) [{marker}]")
                lines.append(f"  - Priority: {entry.priority}")
                lines.append(f"  - Project: {entry.project}")
                lines.append(f"  - Effort: {entry.effort}")
                lines.append(f"  - {entry.ac_summary}")
                lines.append(f"  - Validation evidence: {entry.validation_evidence_count} items")
            lines.append("")

    if report.breaking_changes:
        lines.append("## Breaking Changes")
        lines.append("")
        for bc in report.breaking_changes:
            sev_marker = bc.severity.upper()
            lines.append(f"- [{sev_marker}] `{bc.feature_id}`: {bc.description}")
            if bc.affected_commands:
                for cmd in bc.affected_commands:
                    lines.append(f"  - Affects: `{cmd}`")
        lines.append("")

    lines.append("## Safety Notes")
    lines.append("")
    for note in report.safety_notes:
        lines.append(f"- {note}")
    lines.append("")

    return "\n".join(lines)
