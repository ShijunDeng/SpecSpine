from __future__ import annotations

import json

from .drift_models import DriftAuditReport

__all__ = [
    "render_drift_json",
]


def render_drift_json(report: DriftAuditReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"
