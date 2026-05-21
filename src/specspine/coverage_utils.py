from __future__ import annotations

from typing import Any

__all__ = [
    "_coverage_detail_command",
    "_coverage_plan_commands",
    "_feature_tests_command",
    "_source_files",
]


def _coverage_detail_command(slug: str, *, use_policy: bool) -> str:
    command = f"specspine feature ready {slug} . --json"
    if use_policy:
        return command + " --policy"
    return command + " --require-coverage"


def _feature_tests_command(slug: str) -> str:
    return f"specspine feature tests {slug} . --json"


def _source_files(feature: dict[str, object]) -> list[str]:
    files = feature.get("files", {})
    if not isinstance(files, dict):
        return []
    return sorted(str(path) for path in files.values())


def _coverage_plan_commands(slug: str, *, use_policy: bool) -> list[str]:
    ready_command = _coverage_detail_command(slug, use_policy=use_policy)
    return [
        f"specspine feature trace {slug} . --json",
        _feature_tests_command(slug),
        ready_command,
        "specspine validate . --fusion --features",
    ]
