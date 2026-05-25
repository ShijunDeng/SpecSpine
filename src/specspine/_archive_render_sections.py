from __future__ import annotations

from .archive_models import FeatureArchiveReport

__all__ = [
    "_build_archive_body_lines",
]


def _build_archive_body_lines(report: FeatureArchiveReport) -> list[str]:
    lines: list[str] = []

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

    return lines
