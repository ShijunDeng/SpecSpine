from __future__ import annotations

from .archive_models import FeatureArchivePackage, FeatureArchiveReport

__all__ = [
    "feature_archive_report_with_package",
]


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
