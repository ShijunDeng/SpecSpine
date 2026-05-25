from __future__ import annotations

from typing import Any

__all__ = [
    "_dedupe_commands",
    "_source_by_path",
    "_test_by_path",
]


def _source_by_path(modules: dict[str, dict[str, Any]]) -> dict[str, str]:
    return {str(info["path"]): module for module, info in modules.items()}


def _test_by_path(test_files: tuple[dict[str, Any], ...]) -> dict[str, dict[str, Any]]:
    return {str(test["path"]): test for test in test_files}


def _dedupe_commands(recommendations: list[dict[str, Any]]) -> tuple[str, ...]:
    commands: list[str] = []
    seen: set[str] = set()
    for recommendation in recommendations:
        command = str(recommendation["command"])
        if command not in seen:
            commands.append(command)
            seen.add(command)
    return tuple(commands)
