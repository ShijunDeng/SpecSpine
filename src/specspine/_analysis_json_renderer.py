from __future__ import annotations

import json

from .analysis_models import AnalysisReport

__all__ = [
    "render_analysis_json",
]


def render_analysis_json(report: AnalysisReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"
