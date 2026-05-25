from __future__ import annotations

import json

from .feature_bundle import FeatureTestsReport

__all__ = [
    "render_feature_tests_json",
]


def render_feature_tests_json(report: FeatureTestsReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"
