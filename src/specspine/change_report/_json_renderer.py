from __future__ import annotations

import json

from ..change_models import ChangeRiskReport

__all__ = [
    "render_change_risk_json",
]


def render_change_risk_json(report: ChangeRiskReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"
