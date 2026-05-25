from __future__ import annotations

from typing import Any


def _build_recommended_commands(
    items: list[dict[str, Any]],
) -> list[str]:
    recommended_commands = [
        f"specspine coverage plan . --feature {item['feature_id']}"
        for item in items
    ]
    if not recommended_commands:
        recommended_commands = ["specspine coverage debt . --json"]
    return recommended_commands


__all__ = [
    "_build_recommended_commands",
]
