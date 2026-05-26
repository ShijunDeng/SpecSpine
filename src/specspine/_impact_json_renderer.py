from __future__ import annotations

import json

from .impact_models import TestImpactReport


def render_test_impact_json(report: TestImpactReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


__all__ = [
    "render_test_impact_json",
]
