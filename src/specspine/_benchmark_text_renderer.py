from __future__ import annotations

from .benchmark_models import BenchmarkReport
from ._benchmark_overview_renderer import (
    _render_benchmark_header,
    _render_groups,
    _render_overview_aggregates,
)
from ._benchmark_performers_renderer import (
    _render_improvement_areas,
    _render_top_performers,
)
from ._benchmark_conclusion_renderer import (
    _render_recommendations,
    _render_safety_notes,
    _render_trends,
)

__all__ = [
    "render_benchmark_text",
]


def render_benchmark_text(report: BenchmarkReport) -> str:
    lines: list[str] = []
    lines.extend(_render_benchmark_header(report))
    lines.extend(_render_overview_aggregates(report))
    lines.extend(_render_groups(report))
    lines.extend(_render_top_performers(report))
    lines.extend(_render_improvement_areas(report))
    lines.extend(_render_trends(report))
    lines.extend(_render_recommendations(report))
    lines.extend(_render_safety_notes(report))
    return "\n".join(lines) + "\n"
