from __future__ import annotations

import json

from .health_models import HealthReport

__all__ = [
    "render_health_json",
]


def render_health_json(report: HealthReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"
