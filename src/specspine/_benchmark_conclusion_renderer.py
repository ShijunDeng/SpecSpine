from __future__ import annotations

from .benchmark_models import BenchmarkReport


def _render_trends(report: BenchmarkReport) -> list[str]:
    lines: list[str] = []
    trends = report.trends
    lines.append("Trends:")
    lines.append(f"  Coverage trend: {trends.get('coverage_trend', 'stable')}")
    lines.append(f"  Validation trend: {trends.get('validation_pass_rate_trend', 'stable')}")
    lines.append(f"  Drift trend: {trends.get('drift_frequency_trend', 'stable')}")
    cov_by_status = trends.get("coverage_by_status", {})
    if cov_by_status:
        lines.append("  Coverage by status:")
        for status, avg in sorted(cov_by_status.items()):
            lines.append(f"    {status}: {avg}%")
    lines.append("")
    return lines


def _render_recommendations(report: BenchmarkReport) -> list[str]:
    lines: list[str] = []
    if report.recommendations:
        lines.append("Recommendations:")
        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"  {i}. {rec}")
        lines.append("")
    return lines


def _render_safety_notes(report: BenchmarkReport) -> list[str]:
    lines: list[str] = []
    lines.append("Safety Notes:")
    for note in report.safety_notes:
        lines.append(f"  - {note}")
    return lines


__all__ = [
    "_render_trends",
    "_render_recommendations",
    "_render_safety_notes",
]
