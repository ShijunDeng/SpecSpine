from __future__ import annotations

__all__ = [
    "_render_text_header",
]


def _render_text_header(report, lines: list[str]) -> None:
    lines.append(f"Orchestration plan: {report.root}")
    if report.feature_filter:
        lines.append(f"Feature filter: {report.feature_filter}")
    lines.append(f"Status: {report.status}")
    lines.append("")
