from __future__ import annotations

__all__ = [
    "_render_sources_section",
    "_render_gaps_section",
    "_render_blocking_section",
]


def _render_sources_section(report) -> list[str]:
    lines = ["", "## Sources", ""]
    for kind, source in report.sources.items():
        marker = "ok" if source["exists"] else "missing"
        lines.append(f"- [{marker}] {kind}: {source['path']}")
    return lines


def _render_gaps_section(report) -> list[str]:
    lines = ["", "## Gaps", ""]
    if report.gaps:
        lines.extend(
            f"- {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in report.gaps
        )
    else:
        lines.append("- None.")
    return lines


def _render_blocking_section(report) -> list[str]:
    lines = ["", "## Blocking Checks", ""]
    if report.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in report.blocking_checks
        )
    else:
        lines.append("- None.")
    return lines
