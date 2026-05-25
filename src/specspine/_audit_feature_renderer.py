from __future__ import annotations

from .audit_models import ComplianceReport


def render_audit_feature_trail(trail) -> list[str]:
    n_events = len(trail.events)
    n_transitions = len(trail.lifecycle_transitions)
    n_drift = len(trail.drift_history)
    lines = [
        f"- {trail.feature_id}: "
        f"events={n_events} "
        f"transitions={n_transitions} "
        f"drift_events={n_drift}"
    ]
    ve = trail.validation_evidence
    for kind in ("spec", "execution", "quality"):
        info = ve.get(kind, {})
        exists = info.get("exists", False)
        marker = "exists" if exists else "missing"
        if kind == "spec":
            detail = f"ac_count={info.get('ac_count', 0)}"
        elif kind == "execution":
            detail = f"task_count={info.get('task_count', 0)}"
        else:
            detail = f"coverage_links={info.get('coverage_links', 0)}"
        lines.append(f"    [{marker}] {kind}: {detail}")

    if trail.lifecycle_transitions:
        for t in trail.lifecycle_transitions:
            lines.append(
                f"    transition: {t['from_status']} -> {t['to_status']} "
                f"({t['date'][:10]} by {t['author']})"
            )

    return lines


def render_audit_features(report: ComplianceReport) -> list[str]:
    lines = ["", "Features:"]
    if not report.features:
        lines.append("- none")
    for trail in report.features:
        lines.extend(render_audit_feature_trail(trail))
    return lines


__all__ = [
    "render_audit_feature_trail",
    "render_audit_features",
]
