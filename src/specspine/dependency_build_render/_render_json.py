from __future__ import annotations

import json


def render_dependency_json(result: dict[str, object]) -> str:
    return json.dumps(result, indent=2, sort_keys=False) + "\n"


__all__ = [
    "render_dependency_json",
]
