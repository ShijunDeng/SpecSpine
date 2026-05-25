from __future__ import annotations

from typing import Any

__all__ = [
    "_dedupe_recommendations",
]


def _dedupe_recommendations(
    recommendations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, tuple[str, ...]]] = set()
    for recommendation in recommendations:
        key = (
            str(recommendation["command"]),
            tuple(str(path) for path in recommendation["changed_files"]),
        )
        if key in seen_keys:
            continue
        deduped.append(recommendation)
        seen_keys.add(key)
    return deduped
