from __future__ import annotations

import json
from typing import Any

__all__ = [
    "render_validation_json",
]


def render_validation_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"
