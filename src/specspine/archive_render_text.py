from __future__ import annotations

from .archive_models import FeatureArchiveReport

__all__ = [
    "render_feature_archive_text",
]


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
