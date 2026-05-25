from __future__ import annotations

from .audit_models import ComplianceReport


def render_audit_footer(report: ComplianceReport) -> list[str]:
    lines = []

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

    return lines


__all__ = [
    "render_audit_footer",
]
