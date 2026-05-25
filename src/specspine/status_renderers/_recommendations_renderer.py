from __future__ import annotations

from typing import Any

__all__ = [
    "_render_text_recommendations",
]


def _render_text_recommendations(status: dict[str, Any], lines: list[str]) -> None:
    lines.append("Recommended next actions:")
    for recommendation in status["recommendations"]:
        lines.append(f"  - {recommendation}")
