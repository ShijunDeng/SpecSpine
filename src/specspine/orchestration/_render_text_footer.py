from __future__ import annotations

__all__ = [
    "_render_text_footer",
]


def _render_text_footer(report, lines: list[str]) -> None:
    if report.integration_recommendations:
        lines.append("Integration recommendations:")
        for rec in report.integration_recommendations:
            lines.append(f"  - {rec}")
    lines.append("")

    if report.blocking_items:
        lines.append("Blocking items:")
        for item in report.blocking_items:
            lines.append(f"  - {item}")
    else:
        lines.append("Blocking items: (none)")
    lines.append("")

    lines.append("Safety notes:")
    for note in report.safety_notes:
        lines.append(f"  - {note}")
