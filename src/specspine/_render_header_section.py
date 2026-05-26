from __future__ import annotations

__all__ = [
    "_render_header_section",
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
