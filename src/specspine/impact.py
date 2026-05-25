from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .features import (
    FeatureTestsReport,
    build_feature_tests_report,
    validate_feature_slug,
)

from .impact_models import DISCOVERY_COMMAND, TestImpactReport
from .impact_inventory import (
    _relative_path,
    _source_module_name,
    _test_module_name,
    _unittest_command,
    _normalise_changed_file,
    _definition_symbols,
    _source_inventory,
    _modules_from_imports,
    _modules_from_text,
    _test_inventory,
)
from .impact_recommend import (
    _source_by_path,
    _test_by_path,
    _dedupe_commands,
    _recommend_for_changed_files,
    _command_for_coverage_target,
    _feature_block,
)
from .impact_render import render_test_impact_json, render_test_impact_text


def build_test_impact_report(
    root: Path,
    *,
    changed_files: tuple[str, ...] = (),
    feature: str | None = None,
) -> TestImpactReport:
    resolved_root = root.expanduser().resolve()
    modules = _source_inventory(resolved_root)
    test_files = _test_inventory(resolved_root, modules)
    normalised_changed_files = tuple(
        _normalise_changed_file(resolved_root, changed_file)
        for changed_file in changed_files
    )

    feature_payload = None
    if feature is not None:
        feature_slug = validate_feature_slug(feature)
        feature_payload = _feature_block(
            build_feature_tests_report(resolved_root, feature_slug)
        )

    recommendations = list(
        _recommend_for_changed_files(normalised_changed_files, modules, test_files)
    )
    if feature_payload is not None:
        for command in feature_payload["recommended_commands"]:
            recommendations.append(
                {
                    "changed_files": list(normalised_changed_files),
                    "command": command,
                    "fallback": False,
                    "reason": f"Feature {feature_payload['feature_id']} has local test coverage evidence for this target.",
                    "source_modules": [],
                    "test_files": list(feature_payload["coverage_targets"]),
                }
            )

    recommended_commands = _dedupe_commands(recommendations)
    source_modules = tuple(dict(modules[module]) for module in sorted(modules))
    tests_with_sources = sum(1 for test in test_files if test["source_modules"])
    summary = {
        "changed_files": len(normalised_changed_files),
        "direct_recommendations": sum(
            1 for recommendation in recommendations if not recommendation["fallback"]
        ),
        "fallback_recommendations": sum(
            1 for recommendation in recommendations if recommendation["fallback"]
        ),
        "source_modules": len(source_modules),
        "test_files": len(test_files),
        "tests_with_source_links": tests_with_sources,
    }
    safety_notes = (
        "This command reads local SpecSpine source, test, and optional feature artifacts only.",
        "It reports recommended test commands but does not run tests or execute subprocesses.",
        "It does not call network services, GitHub APIs, upstream CLIs, or read tokens.",
    )
    return TestImpactReport(
        root=resolved_root,
        changed_files=normalised_changed_files,
        source_modules=source_modules,
        test_files=test_files,
        recommendations=tuple(recommendations),
        recommended_commands=recommended_commands,
        summary=summary,
        safety_notes=safety_notes,
        feature=feature_payload,
    )


__all__ = [
    "DISCOVERY_COMMAND",
    "TestImpactReport",
    "_relative_path",
    "_source_module_name",
    "_test_module_name",
    "_unittest_command",
    "_normalise_changed_file",
    "_definition_symbols",
    "_source_inventory",
    "_modules_from_imports",
    "_modules_from_text",
    "_test_inventory",
    "_source_by_path",
    "_test_by_path",
    "_dedupe_commands",
    "_recommend_for_changed_files",
    "_command_for_coverage_target",
    "_feature_block",
    "build_test_impact_report",
    "render_test_impact_json",
    "render_test_impact_text",
]
