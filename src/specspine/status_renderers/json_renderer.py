from __future__ import annotations

import json
from typing import Any

__all__ = [
    "render_status_json",
]


def render_status_json(status: dict[str, Any]) -> str:
    return json.dumps(status, indent=2, sort_keys=True) + "\n"
