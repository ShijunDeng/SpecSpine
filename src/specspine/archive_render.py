from __future__ import annotations

import json
from pathlib import Path

from .archive_models import FeatureArchivePackage, FeatureArchiveReport


def render_feature_archive_json(report: FeatureArchiveReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def feature_archive_report_with_package(
    report: FeatureArchiveReport,
    package: FeatureArchivePackage,
) -> FeatureArchiveReport:
    return FeatureArchiveReport(
        archive_id=report.archive_id,
        feature_id=report.feature_id,
        workspace_root=report.workspace_root,
        status=report.status,
        ready=report.ready,
        coverage_required=report.coverage_required,
        status_report=report.status_report,
        ready_report=report.ready_report,
        trace_report=report.trace_report,
        tasks_report=report.tasks_report,
        tests_report=report.tests_report,
        metadata=report.metadata,
        source_files=report.source_files,
        missing_files=report.missing_files,
        safety_notes=report.safety_notes,
        recommended_commands=report.recommended_commands,
        package=package,
    )


def render_feature_archive_text(report: FeatureArchiveReport) -> str:
    summary = report.summary
    lines = [
        f"# Feature Archive Package Plan: {report.feature_id}",
        "",
        "## Summary",
        "",
        f"- Archive ID: {report.archive_id}",
        f"- Status: {report.status}",
        f"- Ready: {'yes' if report.ready else 'no'}",
        f"- Coverage required: {'yes' if report.coverage_required else 'no'}",
        (
            "- Evidence: "
            f"sources={summary['source_files']['total']} "
            f"missing={summary['missing_files']['total']} "
            f"trace_items={summary['trace']['total']} "
            f"tasks={summary['tasks']['total']} "
            f"test_coverage={summary['test_coverage']['total']} "
            f"blocking={summary['blocking_checks']['total']} "
            f"gaps={summary['gaps']['total']}"
        ),
        "",
        "## Metadata",
        "",
    ]
    lines.extend(f"- {key}: {value}" for key, value in sorted(report.metadata.items()))
    lines.extend(["", "## Source Files", ""])
    if report.source_files:
        lines.extend(f"- [ok] {path}" for path in report.source_files)
    if report.missing_files:
        lines.extend(f"- [missing] {path}" for path in report.missing_files)
    if not report.source_files and not report.missing_files:
        lines.append("- None.")

    lines.extend(["", "## Blocking Checks", ""])
    if report.ready_report.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in report.ready_report.blocking_checks
        )
    else:
        lines.append("- None.")

    lines.extend(["", "## Gaps", ""])
    if report.trace_report.gaps:
        lines.extend(
            f"- {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in report.trace_report.gaps
        )
    else:
        lines.append("- None.")

    lines.extend(["", "## Safety Notes", ""])
    lines.extend(f"- {note}" for note in report.safety_notes)

    lines.extend(["", "## Recommended Commands", ""])
    lines.extend(f"- `{command}`" for command in report.recommended_commands)

    if report.package is not None:
        lines.extend(
            [
                "",
                "## Written Package",
                "",
                f"- Output directory: {report.package.output_dir}",
                f"- Report: {report.package.report_path}",
                f"- Summary: {report.package.readme_path}",
            ]
        )
        lines.extend(f"- Source snapshot: {path}" for path in report.package.source_paths)

    return "\n".join(lines).rstrip() + "\n"


__all__ = [
    "render_feature_archive_json",
    "feature_archive_report_with_package",
    "render_feature_archive_text",
]
