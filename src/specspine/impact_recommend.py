from __future__ import annotations

from typing import Any

from .features import (
    FeatureTestsReport,
    validate_feature_slug,
    build_feature_tests_report,
)
from .impact_models import DISCOVERY_COMMAND
from .impact_inventory import _unittest_command


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

    if fallback_needed or not recommendations:
        recommendations.append(
            {
                "changed_files": list(changed_files),
                "command": DISCOVERY_COMMAND,
                "fallback": True,
                "reason": "No direct static test impact was found for at least one changed file; use full discovery as a conservative fallback.",
                "source_modules": [],
                "test_files": [str(test["path"]) for test in test_files],
            }
        )

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
    return tuple(deduped)


def _command_for_coverage_target(target_path: str) -> str | None:
    target = target_path.split("::", 1)[0]
    if not target.startswith("tests/") or not target.endswith(".py"):
        return None
    return _unittest_command(target)


def _feature_block(report: FeatureTestsReport) -> dict[str, Any]:
    coverage_targets = tuple(
        sorted(
            {
                link.target_path or link.target
                for link in report.test_coverage
                if link.target_path or link.target
            }
        )
    )
    coverage_commands = tuple(
        command
        for command in (
            _command_for_coverage_target(target)
            for target in coverage_targets
        )
        if command is not None
    )
    recommended_commands = tuple(dict.fromkeys(coverage_commands)) or report.recommended_commands
    return {
        "coverage_targets": list(coverage_targets),
        "feature_id": report.feature_id,
        "has_native_files": report.has_native_files,
        "missing_files": list(report.missing_files),
        "ready": report.ready,
        "recommended_commands": list(recommended_commands),
        "status": report.status,
        "test_coverage": [link.as_dict() for link in report.test_coverage],
    }


__all__ = [
    "_source_by_path",
    "_test_by_path",
    "_dedupe_commands",
    "_recommend_for_changed_files",
    "_command_for_coverage_target",
    "_feature_block",
]
