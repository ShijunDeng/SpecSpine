from __future__ import annotations

from .release_models import ReleaseNotesReport

__all__ = [
    "_render_features_section",
]


def _render_features_section(report: ReleaseNotesReport) -> list[str]:
    lines = []
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
    return lines
