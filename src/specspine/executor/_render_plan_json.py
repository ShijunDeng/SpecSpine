from __future__ import annotations

import json
from typing import Any

__all__ = [
    "render_plan_json",
]


def render_plan_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"
