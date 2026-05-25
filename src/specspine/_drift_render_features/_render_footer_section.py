"""Render footer section for drift reports."""

from __future__ import annotations

from specspine.drift_models import DriftAuditReport

__all__ = [
    "render_drift_footer",
]


def render_drift_footer(report: DriftAuditReport) -> list[str]:
    lines = ["", "Recommended commands:"]
    lines.extend(f"- {cmd}" for cmd in report.recommended_commands)
    lines.extend(["", "Safety notes:"])
    lines.extend(f"- {note}" for note in report.safety_notes)
    return lines
