from __future__ import annotations

from typing import Any

from .drift_models import DriftAuditReport

__all__ = [
    "render_drift_text",
]


def render_drift_text(report: DriftAuditReport) -> str:
    summary = report.summary
    lines = [
        f"Drift monitor report: {report.root}",
        (
            "Summary: "
            f"features={summary['features_scanned']} "
            f"drift_events={summary['drift_events_total']} "
            f"drift_free={summary['drift_free_count']}"
        ),
    ]

    sev_dist = summary.get("severity_distribution", {})
    if sev_dist:
        parts = []
        for sev in ("critical", "high", "medium", "low", "none"):
            count = sev_dist.get(sev, 0)
            if count:
                parts.append(f"{sev}={count}")
        if parts:
            lines.append(f"Severity: {' '.join(parts)}")

    lines.append("")
    lines.append("Features:")
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
        for ev in f.drift_events:
            lines.append(f"  - [{ev.severity}] {ev.event_type}: {ev.description}")
            if ev.affected_acs:
                lines.append(f"    affected ACs: {', '.join(ev.affected_acs)}")
            if ev.affected_tasks:
                lines.append(f"    affected tasks: {', '.join(ev.affected_tasks)}")

    if report.trends:
        lines.extend(["", "Trends:"])
        for t in report.trends:
            lines.append(f"- {t['date']}: {t['drift_events']} events")

    if report.compliance:
        lines.extend(["", "Compliance:"])
        lines.append(f"- evidence_hash: {report.compliance.get('evidence_hash', 'N/A')}")
        pf = report.compliance.get("pass_fail_per_dimension", {})
        for dim in ("spec", "code", "test", "quality"):
            status = pf.get(dim, "N/A")
            lines.append(f"- {dim}: {status}")

    lines.extend(["", "Recommended commands:"])
    lines.extend(f"- {cmd}" for cmd in report.recommended_commands)
    lines.extend(["", "Safety notes:"])
    lines.extend(f"- {note}" for note in report.safety_notes)
    return "\n".join(lines) + "\n"
