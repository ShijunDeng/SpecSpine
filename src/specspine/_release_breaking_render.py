from __future__ import annotations

from .release_models import ReleaseNotesReport

__all__ = [
    "_render_breaking_section",
    "_render_safety_section",
]


def _render_breaking_section(report: ReleaseNotesReport) -> list[str]:
    lines = []
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
    return lines


def _render_safety_section(report: ReleaseNotesReport) -> list[str]:
    lines = []
    lines.append("## Safety Notes")
    lines.append("")
    for note in report.safety_notes:
        lines.append(f"- {note}")
    lines.append("")
    return lines
