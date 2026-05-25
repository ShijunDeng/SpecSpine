from __future__ import annotations

import json

__all__ = [
    "render_retrospective_analytics_json",
]


def render_retrospective_analytics_json(report: dict) -> str:
    """Render retrospective analytics report as JSON."""
    return json.dumps(report, indent=2, sort_keys=True) + "\n"
