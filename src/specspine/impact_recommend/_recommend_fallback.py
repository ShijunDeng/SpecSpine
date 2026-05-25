from __future__ import annotations

from typing import Any

from ..impact_models import DISCOVERY_COMMAND

__all__ = [
    "_build_fallback_recommendation",
]


def _build_fallback_recommendation(
    changed_files: tuple[str, ...],
    test_files: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    return {
        "changed_files": list(changed_files),
        "command": DISCOVERY_COMMAND,
        "fallback": True,
        "reason": "No direct static test impact was found for at least one changed file; use full discovery as a conservative fallback.",
        "source_modules": [],
        "test_files": [str(test["path"]) for test in test_files],
    }
