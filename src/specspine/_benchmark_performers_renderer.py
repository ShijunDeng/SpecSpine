from __future__ import annotations

from .benchmark_models import BenchmarkReport


def _render_top_performers(report: BenchmarkReport) -> list[str]:
    lines: list[str] = []
    if report.top_performers:
        lines.append("Top Performers:")
        for p in report.top_performers:
            lines.append(
                f"  {p['feature_id']}: score={p['score']}, "
                f"coverage={p['coverage_pct']}%, drift={p['drift_events']}"
            )
        lines.append("")
    return lines


def _render_improvement_areas(report: BenchmarkReport) -> list[str]:
    lines: list[str] = []
    if report.improvement_areas:
        lines.append("Improvement Areas:")
        for a in report.improvement_areas:
            lines.append(
                f"  {a['feature_id']}: score={a['score']}, "
                f"coverage={a['coverage_pct']}%, issue={a.get('primary_issue', 'needs_review')}"
            )
        lines.append("")
    return lines


__all__ = [
    "_render_top_performers",
    "_render_improvement_areas",
]
