"""Render trends and compliance sections for drift reports."""

from __future__ import annotations

from specspine.drift_models import DriftAuditReport

__all__ = [
    "render_drift_trends",
    "render_drift_compliance",
]


def render_drift_trends(report: DriftAuditReport) -> list[str]:
    if not report.trends:
        return []
    lines = ["", "Trends:"]
    for t in report.trends:
        lines.append(f"- {t['date']}: {t['drift_events']} events")
    return lines


def render_drift_compliance(report: DriftAuditReport) -> list[str]:
    if not report.compliance:
        return []
    lines = ["", "Compliance:"]
    lines.append(f"- evidence_hash: {report.compliance.get('evidence_hash', 'N/A')}")
    pf = report.compliance.get("pass_fail_per_dimension", {})
    for dim in ("spec", "code", "test", "quality"):
        status = pf.get(dim, "N/A")
        lines.append(f"- {dim}: {status}")
    return lines
