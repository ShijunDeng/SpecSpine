from __future__ import annotations

import json

from ..models import QualityGateReport

__all__ = [
    "render_quality_gate_json",
]


def render_quality_gate_json(report: QualityGateReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"
