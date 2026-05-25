from __future__ import annotations

import json

from .feature_bundle import (
    FeatureHandoffReport,
)

__all__ = [
    "render_feature_handoff_json",
]


def render_feature_handoff_json(report: FeatureHandoffReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"
