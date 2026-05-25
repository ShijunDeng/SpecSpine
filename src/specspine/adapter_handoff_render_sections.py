from __future__ import annotations

__all__ = [
    "_render_header_section",
    "_render_sources_section",
    "_render_gaps_section",
    "_render_blocking_section",
]


def _render_header_section(report) -> list[str]:
    summary = report.summary
    adapters_summary = summary["adapters"]
    steps_summary = summary["steps"]
    return [
        f"# Adapter Feature Handoff: {report.feature_id}",
        "",
        "## Feature",
        "",
        f"- Status: {report.status}",
        f"- Ready: {'yes' if report.ready else 'no'}",
        f"- Source files: {len(report.source_files)}",
        f"- Missing files: {len(report.missing_files)}",
        f"- Gaps: {summary['gaps']['total']}",
        f"- Blocking checks: {summary['blocking_checks']['total']}",
        (
            "- Summary: "
            f"adapters={adapters_summary['total']} "
            f"enabled={adapters_summary['enabled']} "
            f"config_exists={adapters_summary['config_exists']} "
            f"steps={steps_summary['total']}"
        ),
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
