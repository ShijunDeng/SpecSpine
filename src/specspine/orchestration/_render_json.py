from __future__ import annotations

import json

__all__ = [
    "render_orchestration_json",
]


def render_orchestration_json(report) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"
