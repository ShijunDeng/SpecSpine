from __future__ import annotations

from typing import Any

from ..impact_models import DISCOVERY_COMMAND
from ..impact_inventory import _unittest_command
from ._recommend_path_utils import _source_by_path, _test_by_path

__all__ = [
    "_build_recommendations_for_changed_files",
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


def _build_recommendations_for_changed_files(
    changed_files: tuple[str, ...],
    modules: dict[str, dict[str, Any]],
    test_files: tuple[dict[str, Any], ...],
) -> tuple[list[dict[str, Any]], bool]:
    source_by_path = _source_by_path(modules)
    test_by_path = _test_by_path(test_files)
    recommendations: list[dict[str, Any]] = []
    fallback_needed = False

    for changed_file in changed_files:
        if changed_file in test_by_path:
            recommendations.append(
                {
                    "changed_files": [changed_file],
                    "command": _unittest_command(changed_file),
                    "fallback": False,
                    "reason": "Changed file is itself a unittest module.",
                    "source_modules": list(test_by_path[changed_file]["source_modules"]),
                    "test_files": [changed_file],
                }
            )
            continue

        module = source_by_path.get(changed_file)
        if module is None:
            fallback_needed = True
            continue

        impacted_tests = tuple(modules[module]["test_files"])
        if not impacted_tests:
            fallback_needed = True
            continue

        for test_file in impacted_tests:
            recommendations.append(
                {
                    "changed_files": [changed_file],
                    "command": _unittest_command(test_file),
                    "fallback": False,
                    "reason": f"Changed source module {module} is referenced by {test_file}.",
                    "source_modules": [module],
                    "test_files": [test_file],
                }
            )

    return recommendations, fallback_needed
