from __future__ import annotations

import json

from .consistency_models import ConsistencyReport


def render_consistency_json(report: ConsistencyReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


__all__ = [
    "render_consistency_json",
]
