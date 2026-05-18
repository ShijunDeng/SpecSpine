from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .features import (
    FeatureTestsReport,
    build_feature_tests_report,
    validate_feature_slug,
)


DISCOVERY_COMMAND = "PYTHONPATH=src python3 -m unittest discover -s tests"


@dataclass(frozen=True)
class TestImpactReport:
    root: Path
    changed_files: tuple[str, ...]
    source_modules: tuple[dict[str, Any], ...]
    test_files: tuple[dict[str, Any], ...]
    recommendations: tuple[dict[str, Any], ...]
    recommended_commands: tuple[str, ...]
    summary: dict[str, Any]
    safety_notes: tuple[str, ...]
    feature: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "changed_files": list(self.changed_files),
            "recommended_commands": list(self.recommended_commands),
            "recommendations": [dict(recommendation) for recommendation in self.recommendations],
            "root": str(self.root),
            "safety_notes": list(self.safety_notes),
            "source_modules": [dict(module) for module in self.source_modules],
            "summary": dict(self.summary),
            "test_files": [dict(test_file) for test_file in self.test_files],
        }
        if self.feature is not None:
            payload["feature"] = dict(self.feature)
        return payload


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _source_module_name(path: Path) -> str:
    if path.stem == "__init__":
        return "specspine"
    return f"specspine.{path.stem}"


def _test_module_name(relative_path: str) -> str:
    return relative_path.removesuffix(".py").replace("/", ".")


def _unittest_command(test_file: str) -> str:
    return f"PYTHONPATH=src python3 -m unittest {_test_module_name(test_file)}"


def _normalise_changed_file(root: Path, value: str) -> str:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    return _relative_path(root, candidate.resolve())


def _definition_symbols(path: Path) -> tuple[str, ...]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError):
        return ()

    symbols: list[str] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append(node.name)
    return tuple(sorted(set(symbols)))


def _source_inventory(root: Path) -> dict[str, dict[str, Any]]:
    source_dir = root / "src" / "specspine"
    modules: dict[str, dict[str, Any]] = {}
    for path in sorted(source_dir.glob("*.py")):
        relative_path = _relative_path(root, path)
        module = _source_module_name(path)
        modules[module] = {
            "module": module,
            "path": relative_path,
            "symbols": list(_definition_symbols(path)),
            "test_files": [],
        }
    return modules


def _modules_from_imports(tree: ast.AST, known_modules: set[str]) -> set[str]:
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name in known_modules:
                    imported.add(name)
                elif name.startswith("specspine."):
                    parts = name.split(".")
                    candidate = ".".join(parts[:2])
                    if candidate in known_modules:
                        imported.add(candidate)
                elif name == "specspine" and name in known_modules:
                    imported.add(name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module in known_modules:
                imported.add(module)
            elif module.startswith("specspine."):
                parts = module.split(".")
                candidate = ".".join(parts[:2])
                if candidate in known_modules:
                    imported.add(candidate)
            elif module == "specspine":
                if module in known_modules:
                    imported.add(module)
                for alias in node.names:
                    candidate = f"specspine.{alias.name}"
                    if candidate in known_modules:
                        imported.add(candidate)
    return imported


def _modules_from_text(content: str, modules: dict[str, dict[str, Any]]) -> set[str]:
    matched: set[str] = set()
    for module, info in modules.items():
        stem = module.rsplit(".", 1)[-1]
        needles = {module, f"{stem}.py"}
        needles.update(str(symbol) for symbol in info["symbols"])
        if any(needle and needle in content for needle in needles):
            matched.add(module)
    return matched


def _test_inventory(
    root: Path,
    modules: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], ...]:
    tests_dir = root / "tests"
    known_modules = set(modules)
    test_records: list[dict[str, Any]] = []
    for path in sorted(tests_dir.glob("test_*.py")):
        relative_path = _relative_path(root, path)
        content = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(content, filename=str(path))
            import_matches = _modules_from_imports(tree, known_modules)
        except SyntaxError:
            import_matches = set()
        text_matches = _modules_from_text(content, modules)
        source_modules = tuple(sorted(import_matches | text_matches))
        for module in source_modules:
            modules[module]["test_files"].append(relative_path)
        test_records.append(
            {
                "imports": sorted(import_matches),
                "module": _test_module_name(relative_path),
                "path": relative_path,
                "source_modules": list(source_modules),
                "text_matches": sorted(text_matches - import_matches),
            }
        )

    for module in modules.values():
        module["test_files"] = sorted(set(module["test_files"]))
    return tuple(test_records)


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


def render_test_impact_json(report: TestImpactReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_test_impact_text(report: TestImpactReport) -> str:
    summary = report.summary
    lines = [
        f"Test impact packet: {report.root}",
        (
            "Summary: "
            f"source_modules={summary['source_modules']} "
            f"test_files={summary['test_files']} "
            f"tests_with_source_links={summary['tests_with_source_links']} "
            f"changed_files={summary['changed_files']} "
            f"fallbacks={summary['fallback_recommendations']}"
        ),
        "",
        "Changed files:",
    ]
    if report.changed_files:
        lines.extend(f"- {path}" for path in report.changed_files)
    else:
        lines.append("- None provided.")

    if report.feature is not None:
        feature = report.feature
        lines.extend(
            [
                "",
                "Feature coverage:",
                (
                    f"- {feature['feature_id']} "
                    f"status={feature['status']} "
                    f"ready={'yes' if feature['ready'] else 'no'} "
                    f"coverage_targets={len(feature['coverage_targets'])}"
                ),
            ]
        )
        if feature["missing_files"]:
            lines.extend(f"- missing {path}" for path in feature["missing_files"])

    lines.extend(["", "Recommendations:"])
    for recommendation in report.recommendations:
        marker = "fallback" if recommendation["fallback"] else "direct"
        tests = ", ".join(recommendation["test_files"]) or "none"
        lines.append(f"- [{marker}] {recommendation['command']}")
        lines.append(f"  reason: {recommendation['reason']}")
        lines.append(f"  tests: {tests}")

    lines.extend(["", "Safety notes:"])
    lines.extend(f"- {note}" for note in report.safety_notes)
    return "\n".join(lines) + "\n"
