from __future__ import annotations

import json


def render_blueprint_json(report) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


__all__ = [
    "render_blueprint_json",
]
