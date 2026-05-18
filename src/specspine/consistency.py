from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .features import (
    FEATURE_FILE_PATHS,
    FeatureTestsReport,
    InvalidFeatureSlug,
    build_feature_tests_report,
    get_feature_status,
    list_feature_bundles,
    validate_feature_slug,
)


LOCAL_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_./-])"
    r"(?P<path>(?:src|tests|docs|specs|execution|quality)/[A-Za-z0-9_./-]+|README\.md|AGENTS\.md)"
)

IMPLEMENTATION_GLOBS = ("src/**/*.py",)
TEST_GLOBS = ("tests/**/*.py",)
DOCUMENTATION_GLOBS = (
    "docs/**/*.md",
    "README.md",
    "AGENTS.md",
    "specs/*.md",
    "execution/*.md",
    "quality/*.md",
)


@dataclass(frozen=True)
class ConsistencyReference:
    path: str
    line: int | None
    kind: str
    matched: str
    exists: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "exists": self.exists,
            "kind": self.kind,
            "line": self.line,
            "matched": self.matched,
            "path": self.path,
        }


@dataclass(frozen=True)
class ConsistencyCheck:
    id: str
    status: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "message": self.message,
            "status": self.status,
        }


@dataclass(frozen=True)
class FeatureConsistency:
    feature_id: str
    status: str | None
    source_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    implementation_references: tuple[ConsistencyReference, ...]
    test_references: tuple[ConsistencyReference, ...]
    documentation_references: tuple[ConsistencyReference, ...]
    changed_references: tuple[ConsistencyReference, ...]
    consistency_checks: tuple[ConsistencyCheck, ...]
    summary: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "changed_references": [
                reference.as_dict() for reference in self.changed_references
            ],
            "consistency_checks": [
                check.as_dict() for check in self.consistency_checks
            ],
            "documentation_references": [
                reference.as_dict() for reference in self.documentation_references
            ],
            "feature_id": self.feature_id,
            "implementation_references": [
                reference.as_dict() for reference in self.implementation_references
            ],
            "missing_files": list(self.missing_files),
            "source_files": list(self.source_files),
            "status": self.status,
            "summary": dict(self.summary),
            "test_references": [
                reference.as_dict() for reference in self.test_references
            ],
        }


@dataclass(frozen=True)
class ConsistencyReport:
    root: Path
    feature_filter: str | None
    changed_files: tuple[str, ...]
    features: tuple[FeatureConsistency, ...]
    summary: dict[str, Any]
    recommended_commands: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "changed_files": list(self.changed_files),
            "feature_filter": self.feature_filter,
            "features": [feature.as_dict() for feature in self.features],
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "safety_notes": list(self.safety_notes),
            "summary": dict(self.summary),
        }


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _normalise_changed_file(root: Path, value: str) -> str:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    return _relative_path(root, candidate.resolve())


def _dedupe(values: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        deduped.append(value)
        seen.add(value)
    return tuple(deduped)


def _feature_source_files(root: Path, slug: str) -> tuple[str, ...]:
    status = get_feature_status(root, slug)
    paths: list[str] = []
    for details in status.files.values():
        if details["exists"]:
            paths.append(str(details["path"]))
    return tuple(paths)


def _feature_missing_files(root: Path, slug: str) -> tuple[str, ...]:
    return tuple(get_feature_status(root, slug).missing_files)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def _explicit_paths_from_feature_files(root: Path, source_files: tuple[str, ...]) -> set[str]:
    paths: set[str] = set()
    for relative_path in source_files:
        path = root / relative_path
        if not path.exists():
            continue
        for match in LOCAL_PATH_RE.finditer(_read_text(path)):
            paths.add(match.group("path").rstrip(".,);]`"))
    return paths


def _candidate_files(root: Path, globs: tuple[str, ...]) -> tuple[Path, ...]:
    files: list[Path] = []
    for pattern in globs:
        files.extend(path for path in root.glob(pattern) if path.is_file())
    return tuple(sorted(set(files)))


def _references_for_area(
    root: Path,
    *,
    slug: str,
    explicit_paths: set[str],
    globs: tuple[str, ...],
    area: str,
) -> tuple[ConsistencyReference, ...]:
    references: list[ConsistencyReference] = []
    seen: set[tuple[str, int | None, str, str]] = set()
    for explicit_path in sorted(explicit_paths):
        if not explicit_path.startswith(_area_prefixes(area)):
            continue
        references.append(
            ConsistencyReference(
                path=explicit_path,
                line=None,
                kind=area,
                matched="explicit feature artifact path",
                exists=(root / explicit_path).exists(),
            )
        )

    for path in _candidate_files(root, globs):
        relative_path = _relative_path(root, path)
        content = _read_text(path)
        for line_number, line in enumerate(content.splitlines(), start=1):
            if slug not in line:
                continue
            key = (relative_path, line_number, area, slug)
            if key in seen:
                continue
            references.append(
                ConsistencyReference(
                    path=relative_path,
                    line=line_number,
                    kind=area,
                    matched=slug,
                    exists=True,
                )
            )
            seen.add(key)
    return tuple(_dedupe_references(references))


def _area_prefixes(area: str) -> tuple[str, ...]:
    if area == "implementation":
        return ("src/",)
    if area == "test":
        return ("tests/",)
    return ("docs/", "README.md", "AGENTS.md", "specs/", "execution/", "quality/")


def _dedupe_references(
    references: list[ConsistencyReference],
) -> tuple[ConsistencyReference, ...]:
    seen: set[tuple[str, int | None, str, str]] = set()
    deduped: list[ConsistencyReference] = []
    for reference in references:
        key = (reference.path, reference.line, reference.kind, reference.matched)
        if key in seen:
            continue
        deduped.append(reference)
        seen.add(key)
    return tuple(sorted(deduped, key=lambda item: (item.path, item.line or 0, item.kind)))


def _coverage_references(report: FeatureTestsReport) -> tuple[ConsistencyReference, ...]:
    references: list[ConsistencyReference] = []
    for link in report.test_coverage:
        if not link.target_path.startswith("tests/"):
            continue
        references.append(
            ConsistencyReference(
                path=link.target_path,
                line=link.line,
                kind="test",
                matched=link.acceptance_criterion_id,
                exists=link.target_exists,
            )
        )
    return _dedupe_references(references)


def _changed_references(
    *,
    root: Path,
    slug: str,
    changed_files: tuple[str, ...],
    source_files: tuple[str, ...],
    implementation_references: tuple[ConsistencyReference, ...],
    test_references: tuple[ConsistencyReference, ...],
    documentation_references: tuple[ConsistencyReference, ...],
) -> tuple[ConsistencyReference, ...]:
    known_paths = set(source_files)
    known_paths.update(reference.path for reference in implementation_references)
    known_paths.update(reference.path for reference in test_references)
    known_paths.update(reference.path for reference in documentation_references)
    references: list[ConsistencyReference] = []
    for changed_file in changed_files:
        if changed_file in known_paths:
            matched = "feature evidence path"
        elif slug in changed_file:
            matched = slug
        else:
            continue
        references.append(
            ConsistencyReference(
                path=changed_file,
                line=None,
                kind="changed",
                matched=matched,
                exists=(root / changed_file).exists(),
            )
        )
    return tuple(references)


def _check(
    check_id: str,
    status: str,
    message: str,
) -> ConsistencyCheck:
    return ConsistencyCheck(id=check_id, status=status, message=message)


def _feature_checks(
    *,
    source_files: tuple[str, ...],
    missing_files: tuple[str, ...],
    implementation_references: tuple[ConsistencyReference, ...],
    test_references: tuple[ConsistencyReference, ...],
    documentation_references: tuple[ConsistencyReference, ...],
    changed_references: tuple[ConsistencyReference, ...],
    changed_files: tuple[str, ...],
) -> tuple[ConsistencyCheck, ...]:
    checks = [
        _check(
            "feature.bundle_files",
            "pass" if source_files and not missing_files else "fail",
            "Feature has all native peer files."
            if source_files and not missing_files
            else "Feature is missing one or more native peer files.",
        ),
        _check(
            "feature.implementation_references",
            "pass" if implementation_references else "warn",
            "Feature links to local implementation evidence."
            if implementation_references
            else "No local implementation references were found.",
        ),
        _check(
            "feature.test_references",
            "pass" if test_references else "warn",
            "Feature links to local test evidence."
            if test_references
            else "No local test references were found.",
        ),
        _check(
            "feature.documentation_references",
            "pass" if documentation_references else "warn",
            "Feature links to local documentation evidence."
            if documentation_references
            else "No local documentation references were found.",
        ),
    ]
    if changed_files:
        checks.append(
            _check(
                "feature.changed_references",
                "pass" if changed_references else "warn",
                "Changed paths intersect this feature evidence."
                if changed_references
                else "No changed paths intersect this feature evidence.",
            )
        )
    return tuple(checks)


def _build_feature_record(
    root: Path,
    slug: str,
    *,
    changed_files: tuple[str, ...],
) -> FeatureConsistency:
    status_report = get_feature_status(root, slug)
    source_files = _feature_source_files(root, slug)
    missing_files = _feature_missing_files(root, slug)
    explicit_paths = _explicit_paths_from_feature_files(root, source_files)
    implementation_references = _references_for_area(
        root,
        slug=slug,
        explicit_paths=explicit_paths,
        globs=IMPLEMENTATION_GLOBS,
        area="implementation",
    )
    test_references = _references_for_area(
        root,
        slug=slug,
        explicit_paths=explicit_paths,
        globs=TEST_GLOBS,
        area="test",
    )
    test_references = _dedupe_references(
        list(test_references)
        + list(_coverage_references(build_feature_tests_report(root, slug)))
    )
    documentation_references = _references_for_area(
        root,
        slug=slug,
        explicit_paths=explicit_paths,
        globs=DOCUMENTATION_GLOBS,
        area="documentation",
    )
    changed_references = _changed_references(
        root=root,
        slug=slug,
        changed_files=changed_files,
        source_files=source_files,
        implementation_references=implementation_references,
        test_references=test_references,
        documentation_references=documentation_references,
    )
    checks = _feature_checks(
        source_files=source_files,
        missing_files=missing_files,
        implementation_references=implementation_references,
        test_references=test_references,
        documentation_references=documentation_references,
        changed_references=changed_references,
        changed_files=changed_files,
    )
    summary = {
        "changed_references": len(changed_references),
        "checks_fail": sum(1 for check in checks if check.status == "fail"),
        "checks_pass": sum(1 for check in checks if check.status == "pass"),
        "checks_warn": sum(1 for check in checks if check.status == "warn"),
        "documentation_references": len(documentation_references),
        "implementation_references": len(implementation_references),
        "source_files": len(source_files),
        "test_references": len(test_references),
    }
    return FeatureConsistency(
        feature_id=slug,
        status=status_report.status,
        source_files=source_files,
        missing_files=missing_files,
        implementation_references=implementation_references,
        test_references=test_references,
        documentation_references=documentation_references,
        changed_references=changed_references,
        consistency_checks=checks,
        summary=summary,
    )


def _missing_feature_record(root: Path, slug: str) -> FeatureConsistency:
    missing_files = tuple(
        relative_path.format(slug=slug) for relative_path in FEATURE_FILE_PATHS.values()
    )
    checks = (
        _check(
            "feature.bundle_files",
            "fail",
            f"No native feature files found for '{slug}'.",
        ),
    )
    return FeatureConsistency(
        feature_id=slug,
        status=None,
        source_files=(),
        missing_files=missing_files,
        implementation_references=(),
        test_references=(),
        documentation_references=(),
        changed_references=(),
        consistency_checks=checks,
        summary={
            "changed_references": 0,
            "checks_fail": 1,
            "checks_pass": 0,
            "checks_warn": 0,
            "documentation_references": 0,
            "implementation_references": 0,
            "source_files": 0,
            "test_references": 0,
        },
    )


def _recommended_commands(feature_ids: tuple[str, ...]) -> tuple[str, ...]:
    commands: list[str] = ["specspine consistency scan . --json"]
    for slug in feature_ids:
        commands.extend(
            [
                f"specspine consistency scan . --feature {slug} --json",
                f"specspine feature trace {slug} . --json",
                f"specspine tests impact . --feature {slug} --json",
                f"specspine review packet . --feature {slug} --json",
            ]
        )
    commands.append("specspine validate . --fusion --features")
    return _dedupe(commands)


def _summary(features: tuple[FeatureConsistency, ...], discovered_features: int) -> dict[str, Any]:
    checks = [check for feature in features for check in feature.consistency_checks]
    return {
        "changed_references": sum(len(feature.changed_references) for feature in features),
        "checks_fail": sum(1 for check in checks if check.status == "fail"),
        "checks_pass": sum(1 for check in checks if check.status == "pass"),
        "checks_total": len(checks),
        "checks_warn": sum(1 for check in checks if check.status == "warn"),
        "discovered_features": discovered_features,
        "documentation_references": sum(
            len(feature.documentation_references) for feature in features
        ),
        "features_scanned": len(features),
        "features_with_missing_files": sum(1 for feature in features if feature.missing_files),
        "implementation_references": sum(
            len(feature.implementation_references) for feature in features
        ),
        "test_references": sum(len(feature.test_references) for feature in features),
    }


def build_consistency_report(
    root: Path,
    *,
    feature_filter: str | None = None,
    changed_files: tuple[str, ...] = (),
) -> ConsistencyReport:
    resolved_root = root.expanduser().resolve()
    if feature_filter is not None:
        feature_filter = validate_feature_slug(feature_filter)
    normalised_changed_files = tuple(
        _dedupe(
            [
                _normalise_changed_file(resolved_root, changed_file)
                for changed_file in changed_files
            ]
        )
    )

    discovered = list_feature_bundles(resolved_root)
    discovered_slugs = tuple(str(feature["slug"]) for feature in discovered)
    if feature_filter is not None:
        slugs = (feature_filter,)
    else:
        slugs = discovered_slugs

    features: list[FeatureConsistency] = []
    for slug in slugs:
        validate_feature_slug(slug)
        if slug not in discovered_slugs:
            features.append(_missing_feature_record(resolved_root, slug))
        else:
            features.append(
                _build_feature_record(
                    resolved_root,
                    slug,
                    changed_files=normalised_changed_files,
                )
            )

    feature_tuple = tuple(sorted(features, key=lambda feature: feature.feature_id))
    safety_notes = (
        "This report reads local workspace files only.",
        "Recommended commands are advisory only and are not executed.",
        "SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, or read tokens.",
    )
    return ConsistencyReport(
        root=resolved_root,
        feature_filter=feature_filter,
        changed_files=normalised_changed_files,
        features=feature_tuple,
        summary=_summary(feature_tuple, discovered_features=len(discovered)),
        recommended_commands=_recommended_commands(
            tuple(feature.feature_id for feature in feature_tuple)
        ),
        safety_notes=safety_notes,
    )


def render_consistency_json(report: ConsistencyReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_consistency_text(report: ConsistencyReport) -> str:
    summary = report.summary
    lines = [
        f"Spec-code consistency report: {report.root}",
        f"Feature filter: {report.feature_filter or 'all'}",
        (
            "Summary: "
            f"features={summary['features_scanned']} "
            f"implementation_refs={summary['implementation_references']} "
            f"test_refs={summary['test_references']} "
            f"documentation_refs={summary['documentation_references']} "
            f"changed_refs={summary['changed_references']} "
            f"fail={summary['checks_fail']} "
            f"warn={summary['checks_warn']}"
        ),
        "",
        "Features:",
    ]
    if not report.features:
        lines.append("- none")
    for feature in report.features:
        lines.append(
            f"- {feature.feature_id}: status={feature.status or 'missing'} "
            f"sources={len(feature.source_files)} "
            f"impl={len(feature.implementation_references)} "
            f"tests={len(feature.test_references)} "
            f"docs={len(feature.documentation_references)} "
            f"changed={len(feature.changed_references)}"
        )
        for check in feature.consistency_checks:
            if check.status == "pass":
                continue
            lines.append(f"  - [{check.status}] {check.id}: {check.message}")

    lines.extend(["", "Changed files:"])
    if report.changed_files:
        lines.extend(f"- {path}" for path in report.changed_files)
    else:
        lines.append("- None provided.")

    lines.extend(["", "Recommended commands:"])
    lines.extend(f"- {command}" for command in report.recommended_commands)
    lines.extend(["", "Safety notes:"])
    lines.extend(f"- {note}" for note in report.safety_notes)
    return "\n".join(lines) + "\n"
