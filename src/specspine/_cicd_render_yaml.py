from __future__ import annotations

from typing import Any

__all__ = [
    "render_pipeline_yaml",
]


def render_pipeline_yaml(result: dict[str, Any]) -> str:
    raw = result.get("raw_content", "")
    if raw:
        return raw
    return "# No raw content available; use render_pipeline_json instead.\n"
