from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .consistency_models import (
    ConsistencyCheck,
    ConsistencyReport,
    FeatureConsistency,
    DOCUMENTATION_GLOBS,
    IMPLEMENTATION_GLOBS,
    TEST_GLOBS,
)
from .consistency_references import (
    _changed_references,
    _coverage_references,
    _explicit_paths_from_feature_files,
    _feature_missing_files,
    _feature_source_files,
    _references_for_area,
)
from .consistency_utils import (
    _dedupe,
    _dedupe_references,
    _normalise_changed_file,
)
from .features import (
    FEATURE_FILE_PATHS,
    InvalidFeatureSlug,
    build_feature_tests_report,
    get_feature_status,
    list_feature_bundles,
    validate_feature_slug,
)

__all__ = [
    "_build_feature_record",
    "_check",
    "_feature_checks",
    "_missing_feature_record",
    "_recommended_commands",
    "_summary",
    "build_consistency_report",
    "render_consistency_json",
    "render_consistency_text",
]


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
    implementation_references: tuple,
    test_references: tuple,
    documentation_references: tuple,
    changed_references: tuple,
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
    changed_reference_list = _changed_references(
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
        changed_references=changed_reference_list,
        changed_files=changed_files,
    )
    summary = {
        "changed_references": len(changed_reference_list),
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
        changed_references=changed_reference_list,
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
