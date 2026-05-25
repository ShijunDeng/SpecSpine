"""Render feature events and features section for drift reports."""

from __future__ import annotations

from typing import Any

from specspine.drift_models import DriftAuditReport

__all__ = [
    "render_drift_features",
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
