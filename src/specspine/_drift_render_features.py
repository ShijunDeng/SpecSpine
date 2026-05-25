from __future__ import annotations

from typing import Any

from .drift_models import DriftAuditReport

__all__ = [
    "render_drift_features",
    "render_drift_trends",
    "render_drift_compliance",
    "render_drift_footer",
]


def _render_feature_events(feature) -> list[str]:
    lines: list[str] = []
    for ev in feature.drift_events:
        lines.append(f"  - [{ev.severity}] {ev.event_type}: {ev.description}")
        if ev.affected_acs:
            lines.append(f"    affected ACs: {', '.join(ev.affected_acs)}")
        if ev.affected_tasks:
            lines.append(f"    affected tasks: {', '.join(ev.affected_tasks)}")
    return lines


def render_drift_features(report: DriftAuditReport) -> list[str]:
    lines = ["", "Features:"]
    if not report.features:
        lines.append("- none")
    for f in report.features:
        marker = "OK" if f.severity == "none" else f.severity.upper()
        cascade = " [CASCADE_RISK]" if f.cascade_risk else ""
        lines.append(
            f"- {f.feature_id}: severity={marker}{cascade} "
            f"spec={len(f.spec_drift)} code={len(f.code_drift)} "
            f"test={len(f.test_drift)} quality={len(f.quality_drift)} "
            f"total_events={len(f.drift_events)}"
        )
        lines.extend(_render_feature_events(f))
    return lines


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


def render_drift_footer(report: DriftAuditReport) -> list[str]:
    lines = ["", "Recommended commands:"]
    lines.extend(f"- {cmd}" for cmd in report.recommended_commands)
    lines.extend(["", "Safety notes:"])
    lines.extend(f"- {note}" for note in report.safety_notes)
    return lines
