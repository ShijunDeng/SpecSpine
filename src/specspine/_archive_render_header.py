from __future__ import annotations

from .archive_models import FeatureArchiveReport

__all__ = [
    "_build_archive_header_lines",
]


def _build_archive_header_lines(report: FeatureArchiveReport) -> list[str]:
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
    return lines
