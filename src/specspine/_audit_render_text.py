from __future__ import annotations

from .audit_models import ComplianceReport


def render_compliance_text(report: ComplianceReport) -> str:
    summary = report.compliance_summary
    lines = [
        f"Compliance audit report: {report.root}",
        f"Audit date: {report.audit_date}",
        f"Scope: {report.scope}",
        "",
        f"Summary: "
        f"features={summary['total_features']} "
        f"compliant={summary['compliant_features']} "
        f"checks={summary['total_checks']} "
        f"passed={summary['passed_checks']} "
        f"rate={summary['compliance_rate']:.0%}",
    ]

    pf = summary.get("pass_fail_per_dimension", {})
    if pf:
        lines.append("")
        lines.append("Compliance dimensions:")
        for key in sorted(pf):
            status = pf[key]
            marker = "PASS" if status == "pass" else "FAIL"
            lines.append(f"  [{marker}] {key}")

    lines.append("")
    lines.append("Features:")
    if not report.features:
        lines.append("- none")
    for trail in report.features:
        n_events = len(trail.events)
        n_transitions = len(trail.lifecycle_transitions)
        n_drift = len(trail.drift_history)
        lines.append(
            f"- {trail.feature_id}: "
            f"events={n_events} "
            f"transitions={n_transitions} "
            f"drift_events={n_drift}"
        )
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

    if report.evidence_hashes:
        lines.append("")
        lines.append("Evidence hashes:")
        for i, h in enumerate(report.evidence_hashes):
            lines.append(f"  [{i}] {h[:16]}...")

    if report.recommendations:
        lines.append("")
        lines.append("Recommendations:")
        for rec in report.recommendations:
            lines.append(f"- {rec}")

    lines.append("")
    lines.append("Safety notes:")
    lines.extend(f"- {note}" for note in report.safety_notes)
    return "\n".join(lines) + "\n"


__all__ = [
    "render_compliance_text",
]
