from __future__ import annotations

from .drift_models import DriftAuditReport
from ._drift_render_summary import render_drift_header, render_drift_severity
from ._drift_render_features import (
    render_drift_features,
    render_drift_trends,
    render_drift_compliance,
    render_drift_footer,
)

__all__ = [
    "render_drift_text",
]


def render_drift_text(report: DriftAuditReport) -> str:
    lines: list[str] = []
    lines.extend(render_drift_header(report))
    lines.extend(render_drift_severity(report))
    lines.extend(render_drift_features(report))
    lines.extend(render_drift_trends(report))
    lines.extend(render_drift_compliance(report))
    lines.extend(render_drift_footer(report))
    return "\n".join(lines) + "\n"
