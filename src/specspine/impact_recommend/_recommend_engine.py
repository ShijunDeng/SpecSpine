from __future__ import annotations

from typing import Any

from ..impact_models import DISCOVERY_COMMAND
from ._recommend_core import (
    _build_recommendations_for_changed_files,
    _build_fallback_recommendation,
)
from ._recommend_dedup import _dedupe_recommendations

__all__ = [
    "_recommend_for_changed_files",
]


def _recommend_for_changed_files(
    changed_files: tuple[str, ...],
    modules: dict[str, dict[str, Any]],
    test_files: tuple[dict[str, Any], ...],
) -> tuple[dict[str, Any], ...]:
    if not changed_files:
        return (
            {
                "changed_files": [],
                "command": DISCOVERY_COMMAND,
                "fallback": False,
                "reason": "No changed files were provided; run the full local unittest discovery gate.",
                "source_modules": [],
                "test_files": [str(test["path"]) for test in test_files],
            },
        )

    recommendations, fallback_needed = _build_recommendations_for_changed_files(
        changed_files, modules, test_files,
    )

    if fallback_needed or not recommendations:
        recommendations.append(
            _build_fallback_recommendation(changed_files, test_files),
        )

    deduped = _dedupe_recommendations(recommendations)
    return tuple(deduped)
