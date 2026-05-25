from __future__ import annotations

from .audit_models import ComplianceReport


def render_audit_header(report: ComplianceReport) -> list[str]:
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

    return lines


__all__ = [
    "render_audit_header",
]
