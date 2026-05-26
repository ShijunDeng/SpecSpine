from __future__ import annotations

from ._analysis_text_summary import render_analysis_summary
from ._analysis_text_issues import render_analysis_issues
from ._analysis_text_recommendations import render_analysis_recommendations
from .analysis_models import (
    AnalysisReport,
    TEXT_MAX_ISSUES_PER_FEATURE,
    TEXT_MAX_RECOMMENDATIONS,
)

__all__ = [
    "render_analysis_text",
    "render_analysis_summary",
    "render_analysis_issues",
    "render_analysis_recommendations",
]


def render_analysis_text(report: AnalysisReport) -> str:
    lines = render_analysis_summary(report)
    lines.extend(render_analysis_issues(report))
    lines.extend(render_analysis_recommendations(report))
    return "\n".join(lines) + "\n"
