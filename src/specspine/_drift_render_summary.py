from __future__ import annotations

from .drift_models import DriftAuditReport

__all__ = [
    "render_drift_header",
    "render_drift_severity",
]


def render_drift_header(report: DriftAuditReport) -> list[str]:
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
    return lines


def render_drift_severity(report: DriftAuditReport) -> list[str]:
    summary = report.summary
    sev_dist = summary.get("severity_distribution", {})
    if not sev_dist:
        return []
    parts = []
    for sev in ("critical", "high", "medium", "low", "none"):
        count = sev_dist.get(sev, 0)
        if count:
            parts.append(f"{sev}={count}")
    if not parts:
        return []
    return [f"Severity: {' '.join(parts)}"]
