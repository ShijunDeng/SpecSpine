from __future__ import annotations

from ..feature_bundle import FeatureTestsReport

__all__ = [
    "render_gaps_lines",
    "render_blocking_checks_lines",
    "render_key_commands_lines",
]


def render_gaps_lines(report: FeatureTestsReport) -> list[str]:
    lines: list[str] = ["", "Gaps:"]
    if report.gaps:
        lines.extend(
            f"- {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in report.gaps
        )
    else:
        lines.append("- None.")
    return lines


def render_blocking_checks_lines(report: FeatureTestsReport) -> list[str]:
    lines: list[str] = ["", "Blocking Checks:"]
    if report.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in report.blocking_checks
        )
    else:
        lines.append("- None.")
    return lines


def render_key_commands_lines(report: FeatureTestsReport) -> list[str]:
    lines: list[str] = ["", "Key Commands:"]
    lines.extend(f"- {command}" for command in report.recommended_commands)
    return lines
