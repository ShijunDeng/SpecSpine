from __future__ import annotations

import json

__all__ = [
    "render_evolution_json",
]


def render_evolution_json(result: dict[str, object]) -> str:
    return json.dumps(result, indent=2, sort_keys=False) + "\n"
