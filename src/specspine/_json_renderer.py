from __future__ import annotations

import json

from .feature_bundle import FeatureTraceReport

__all__ = [
    "render_feature_trace_json",
]


def render_feature_trace_json(report: FeatureTraceReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"
