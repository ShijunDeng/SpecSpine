from __future__ import annotations

from ..models import QualityGateReport

__all__ = [
    "render_text_header_lines",
]


def render_text_header_lines(report: QualityGateReport) -> list[str]:
    summary = report.summary
    lines = [
        f"Quality gates: {report.root}",
        f"Source: {report.source_file}",
    ]
    if report.source_missing:
        lines.append("Source missing: yes")
    else:
        lines.append("Source missing: no")

    lines.append(
        "Summary: "
        f"required={summary['required_total']} "
        f"done={summary['required_done']} "
        f"open={summary['required_open']} "
        f"definition={summary['definition_total']}"
    )
    return lines
