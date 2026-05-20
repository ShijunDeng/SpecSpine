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
    "FeatureTraceChecklistItem",
    "FeatureTraceTestPlanItem",
    "FeatureTraceReport",
    "build_feature_trace_report",
    "render_feature_trace_text",
    "render_feature_trace_json",
    "_feature_sources_from_status",
    "_empty_trace_summary",
]


def _render_trace_checklist_item(
    item: FeatureTraceChecklistItem | FeatureTask,
) -> str:
    marker = "x" if item.done else " "
    return f"- [{marker}] {item.id} {item.source_file}:{item.line} {item.text}"


def render_feature_trace_text(report: FeatureTraceReport) -> str:
    summary = report.summary
    lines = [
        f"Feature trace: {report.feature_id}",
        f"Status: {report.status}",
        "Sources:",
    ]
    for kind, source in report.sources.items():
        marker = "ok" if source["exists"] else "missing"
        lines.append(f"- [{marker}] {kind}: {source['path']}")

    lines.extend(
        [
            (
                "Summary: "
                f"total={summary['total']} "
                f"done={summary['done']} "
                f"open={summary['open']}"
            ),
            (
                "Counts: "
                f"ac={summary['acceptance_criteria']['total']} "
                f"tasks={summary['tasks']['total']} "
                f"quality={summary['quality_checks']['total']} "
                f"test_plan={summary['test_plan']['total']}"
            ),
            "",
            "Gaps:",
        ]
    )

    if report.gaps:
        lines.extend(
            f"- {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in report.gaps
        )
    else:
        lines.append("- None.")

    lines.extend(["", "Acceptance Criteria:"])
    if report.acceptance_criteria:
        lines.extend(
            _render_trace_checklist_item(item)
            for item in report.acceptance_criteria
        )
    else:
        lines.append("- None found.")

    lines.extend(["", "Tasks:"])
    if report.tasks:
        lines.extend(_render_trace_checklist_item(task) for task in report.tasks)
    else:
        lines.append("- None found.")

    lines.extend(["", "Quality Checks:"])
    if report.quality_checks:
        lines.extend(
            _render_trace_checklist_item(item)
            for item in report.quality_checks
        )
    else:
        lines.append("- None found.")

    lines.extend(["", "Test Plan:"])
    if report.test_plan:
        lines.extend(
            f"- {item.id} {item.source_file}:{item.line} {item.text}"
            for item in report.test_plan
        )
    else:
        lines.append("- None found.")

    return "\n".join(lines) + "\n"


def render_feature_trace_json(report: FeatureTraceReport) -> str:
    import json
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


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
