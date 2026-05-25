from __future__ import annotations

from ..feature_bundle import FeatureTestsReport

__all__ = [
    "render_header_lines",
]


def render_header_lines(report: FeatureTestsReport) -> list[str]:
    summary = report.summary
    lines = [
        f"Feature test packet: {report.feature_id}",
        f"Feature: {report.feature_id}",
        f"Status: {report.status}",
        f"Ready: {'yes' if report.ready else 'no'}",
        (
            "Metadata: "
            f"priority={report.metadata.priority} "
            f"owner={report.metadata.owner} "
            f"milestone={report.metadata.milestone} "
            f"target_release={report.metadata.target_release}"
        ),
        "Sources:",
    ]
    if report.source_files:
        lines.extend(f"- [ok] {relative_path}" for relative_path in report.source_files)
    if report.missing_files:
        lines.extend(
            f"- [missing] {relative_path}"
            for relative_path in report.missing_files
        )
    if not report.source_files and not report.missing_files:
        lines.append("- None.")

    lines.append(
        "Summary: "
        f"acceptance_criteria={summary['acceptance_criteria']['total']} "
        f"test_cases={summary['test_cases']['total']} "
        f"test_coverage={summary['test_coverage']['total']} "
        f"test_plan={summary['test_plan']['total']} "
        f"quality_checks={summary['quality_checks']['total']} "
        f"gaps={summary['gaps']['total']} "
        f"blocking={summary['blocking_checks']['total']}"
    )
    return lines
