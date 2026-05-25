from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    FeatureStatusReport,
    FeatureTask,
    FeatureTraceChecklistItem,
    FeatureTraceReport,
    FeatureTraceTestPlanItem,
    _empty_trace_summary,
    _feature_sources_from_status,
    _relative_feature_paths,
    _trace_gap,
    feature_bundle_paths,
    get_feature_status,
    parse_acceptance_criteria,
    parse_feature_tasks,
    parse_quality_checks,
    parse_test_plan,
    validate_feature_slug,
)

__all__ = [
    "build_feature_trace_report",
]


def build_feature_trace_report(root: Path, slug: str) -> FeatureTraceReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = _relative_feature_paths(slug)

    contents: dict[str, str] = {}
    missing_files: list[str] = []
    missing_paths: list[Path] = []
    sources: dict[str, dict[str, object]] = {}

    for kind in FEATURE_FILE_PATHS:
        path = paths[kind]
        relative_path = relative_paths[kind]
        exists = path.exists()
        sources[kind] = {
            "exists": exists,
            "path": relative_path,
        }
        if exists:
            contents[kind] = path.read_text(encoding="utf-8")
            continue

        missing_files.append(relative_path)
        missing_paths.append(path)

    if not contents:
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(missing_paths),
        )

    spec_file = relative_paths["spec"]
    execution_file = relative_paths["execution"]
    quality_file = relative_paths["quality"]

    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...] = ()
    tasks: tuple[FeatureTask, ...] = ()
    quality_checks: tuple[FeatureTraceChecklistItem, ...] = ()
    test_plan: tuple[FeatureTraceTestPlanItem, ...] = ()

    spec_content = contents.get("spec")
    if spec_content is not None:
        acceptance_criteria = parse_acceptance_criteria(
            spec_content,
            source_file=spec_file,
        )

    execution_content = contents.get("execution")
    if execution_content is not None:
        tasks = parse_feature_tasks(execution_content, source_file=execution_file)

    quality_content = contents.get("quality")
    if quality_content is not None:
        quality_checks = parse_quality_checks(
            quality_content,
            source_file=quality_file,
        )
        test_plan = parse_test_plan(quality_content, source_file=quality_file)

    gaps: list[dict[str, str]] = []
    for relative_path in missing_files:
        gaps.append(
            _trace_gap(
                "missing_file",
                relative_path,
                f"Missing native feature file: {relative_path}",
            )
        )
    if not acceptance_criteria:
        gaps.append(
            _trace_gap(
                "missing_acceptance_criteria",
                spec_file,
                "No acceptance criteria checklist items found.",
            )
        )
    if not tasks:
        gaps.append(
            _trace_gap(
                "missing_tasks",
                execution_file,
                "No task checklist items found.",
            )
        )
    if not quality_checks:
        gaps.append(
            _trace_gap(
                "missing_required_checks",
                quality_file,
                "No required check checklist items found.",
            )
        )
    if not test_plan:
        gaps.append(
            _trace_gap(
                "missing_test_plan",
                quality_file,
                "No non-empty test plan content found.",
            )
        )

    status_report = get_feature_status(resolved_root, slug)

    return FeatureTraceReport(
        feature_id=slug,
        status=status_report.status or "unknown",
        sources=sources,
        missing_files=tuple(missing_files),
        acceptance_criteria=acceptance_criteria,
        tasks=tasks,
        quality_checks=quality_checks,
        test_plan=test_plan,
        gaps=tuple(gaps),
    )
