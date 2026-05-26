from __future__ import annotations

from .analysis_models import AnalysisReport, TEXT_MAX_RECOMMENDATIONS

__all__ = [
    "render_analysis_recommendations",
]


def render_analysis_recommendations(report: AnalysisReport) -> list[str]:
    lines: list[str] = ["", "Recommendations:"]
    for command in report.recommended_commands[:TEXT_MAX_RECOMMENDATIONS]:
        lines.append(f"- {command}")
    hidden_commands = len(report.recommended_commands) - TEXT_MAX_RECOMMENDATIONS
    if hidden_commands > 0:
        lines.append(
            f"- ... {hidden_commands} more recommended command(s); use --json for the full list."
        )
    if not report.issues:
        lines.append("- Analysis is clean; continue with validation or implementation handoff.")
    return lines
