from __future__ import annotations

import json
from pathlib import Path

from .feature_bundle import (
    FeatureBundleNotFoundError,
    FeatureHandoffReport,
    FeatureMetadata,
    FeatureReadyCheck,
    FeatureTask,
    FeatureTraceChecklistItem,
    FeatureTraceReport,
    FeatureTraceTestPlanItem,
    _relative_feature_paths,
    _trace_gap,
    feature_bundle_paths,
    get_feature_status,
    parse_release_readiness,
    read_feature_metadata,
    validate_feature_slug,
)
from .feature_ready import build_feature_ready_report
from .feature_tasks import build_feature_tasks_report
from .feature_trace import build_feature_trace_report, _empty_trace_summary, _feature_sources_from_status

__all__ = [
    "FeatureHandoffReport",
    "_handoff_next_actions",
    "build_feature_handoff_report",
    "render_feature_handoff_text",
    "render_feature_handoff_json",
]


def _recommended_handoff_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature handoff {slug} . --json",
        f"specspine feature tasks {slug} . --json",
        f"specspine feature task-issues {slug} . --json",
        f"specspine feature trace {slug} . --json",
        f"specspine feature tests {slug} . --json",
        f"specspine feature ready {slug} . --json",
        f"specspine feature pr {slug} . --json",
        "specspine validate . --fusion --features",
    )


def _append_unique(items: list[str], item: str) -> None:
    if item not in items:
        items.append(item)


def _handoff_next_actions(
    *,
    slug: str,
    has_native_files: bool,
    missing_files: tuple[str, ...],
    gaps: tuple[dict[str, str], ...],
    tasks: tuple[FeatureTask, ...],
    blocking_checks: tuple[FeatureReadyCheck, ...],
    ready: bool,
) -> tuple[str, ...]:
    actions: list[str] = []

    if not has_native_files:
        _append_unique(
            actions,
            (
                "Create or restore the native feature bundle: "
                f"specspine feature new {slug} . --title \"...\" --why \"...\""
            ),
        )
        return tuple(actions)

    if missing_files:
        _append_unique(
            actions,
            "Add missing peer file(s): " + ", ".join(missing_files),
        )

    section_gap_ids = tuple(
        gap["id"] for gap in gaps if gap["id"] != "missing_file"
    )
    if section_gap_ids:
        _append_unique(
            actions,
            "Fill missing trace section(s): " + ", ".join(section_gap_ids),
        )

    open_task_ids = tuple(task.id for task in tasks if not task.done)
    if open_task_ids:
        _append_unique(
            actions,
            "Complete open task(s): " + ", ".join(open_task_ids),
        )

    blocking_ids = tuple(check.id for check in blocking_checks)
    if blocking_ids:
        _append_unique(
            actions,
            "Resolve blocking readiness check(s): " + ", ".join(blocking_ids),
        )

    if ready:
        _append_unique(
            actions,
            "Review, merge, or archive the ready feature bundle.",
        )

    return tuple(actions)


def build_feature_handoff_report(
    root: Path,
    slug: str,
    *,
    require_coverage: bool = False,
) -> FeatureHandoffReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    status_report = get_feature_status(resolved_root, slug)
    metadata = read_feature_metadata(resolved_root, slug)
    has_native_files = any(file["exists"] for file in status_report.files.values())

    try:
        trace_report = build_feature_trace_report(resolved_root, slug)
    except FeatureBundleNotFoundError:
        missing_files = status_report.missing_files
        gaps = tuple(
            _trace_gap(
                "missing_file",
                relative_path,
                f"Missing native feature file: {relative_path}",
            )
            for relative_path in missing_files
        )
        trace_report = FeatureTraceReport(
            feature_id=slug,
            status=status_report.status or "unknown",
            sources=_feature_sources_from_status(status_report),
            missing_files=missing_files,
            acceptance_criteria=(),
            tasks=(),
            quality_checks=(),
            test_plan=(),
            gaps=gaps,
        )

    try:
        tasks_report = build_feature_tasks_report(resolved_root, slug)
        task_summary = tasks_report.summary
    except FeatureBundleNotFoundError:
        task_summary = {"done": 0, "open": 0, "total": 0}

    ready_report = build_feature_ready_report(
        resolved_root,
        slug,
        require_coverage=require_coverage,
    )

    relative_paths = _relative_feature_paths(slug)
    quality_path = feature_bundle_paths(resolved_root, slug)["quality"]
    release_readiness: tuple[FeatureTraceChecklistItem, ...] = ()
    if quality_path.exists():
        release_readiness = parse_release_readiness(
            quality_path.read_text(encoding="utf-8"),
            source_file=relative_paths["quality"],
        )

    next_actions = _handoff_next_actions(
        slug=slug,
        has_native_files=has_native_files,
        missing_files=trace_report.missing_files,
        gaps=trace_report.gaps,
        tasks=trace_report.tasks,
        blocking_checks=ready_report.blocking_checks,
        ready=ready_report.ready,
    )

    return FeatureHandoffReport(
        feature_id=slug,
        status=trace_report.status,
        ready=ready_report.ready,
        sources=trace_report.sources,
        missing_files=trace_report.missing_files,
        gaps=trace_report.gaps,
        blocking_checks=ready_report.blocking_checks,
        acceptance_criteria=trace_report.acceptance_criteria,
        tasks=trace_report.tasks,
        quality_checks=trace_report.quality_checks,
        test_plan=trace_report.test_plan,
        release_readiness=release_readiness,
        trace_summary=trace_report.summary if has_native_files else _empty_trace_summary(),
        ready_summary=ready_report.summary,
        task_summary=task_summary,
        recommended_commands=_recommended_handoff_commands(slug),
        next_actions=next_actions,
        has_native_files=has_native_files,
        metadata=metadata,
    )


def render_feature_handoff_json(report: FeatureHandoffReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_feature_handoff_text(report: FeatureHandoffReport) -> str:
    summary = report.summary
    trace = summary["trace"]
    ready = summary["ready"]
    tasks = summary["tasks"]
    lines = [
        f"Feature handoff: {report.feature_id}",
        f"Status: {report.status}",
        f"Ready: {'yes' if report.ready else 'no'}",
        (
            "Metadata: "
            f"priority={report.metadata.priority} "
            f"owner={report.metadata.owner} "
            f"milestone={report.metadata.milestone} "
            f"target_release={report.metadata.target_release}"
        ),
        (
            "Counts: "
            f"trace={trace['total']}/{trace['done']}/{trace['open']} "
            f"ready={ready['pass']}/{ready['fail']}/{ready['total']} "
            f"tasks={tasks['total']}/{tasks['done']}/{tasks['open']} "
            f"gaps={summary['gaps']['total']} "
            f"blocking={summary['blocking_checks']['total']}"
        ),
        "Sources:",
    ]
    for kind, source in report.sources.items():
        marker = "ok" if source["exists"] else "missing"
        lines.append(f"- [{marker}] {kind}: {source['path']}")

    lines.extend(["", "Next actions:"])
    if report.next_actions:
        lines.extend(f"- {action}" for action in report.next_actions)
    else:
        lines.append("- None.")

    open_tasks = tuple(task for task in report.tasks if not task.done)
    lines.extend(["", "Open tasks:"])
    if open_tasks:
        lines.extend(
            f"- {task.id} {task.source_file}:{task.line} {task.text}"
            for task in open_tasks
        )
    else:
        lines.append("- None.")

    lines.extend(["", "Blocking checks:"])
    if report.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in report.blocking_checks
        )
    else:
        lines.append("- None.")

    lines.extend(["", "Key commands:"])
    lines.extend(f"- {command}" for command in report.recommended_commands)

    return "\n".join(lines) + "\n"
