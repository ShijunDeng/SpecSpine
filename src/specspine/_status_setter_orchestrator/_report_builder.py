from __future__ import annotations

from ..feature_bundle import FeatureStatusReport

__all__ = [
    "_build_status_report",
]


def _build_status_report(
    report: FeatureStatusReport,
    updated_files: tuple[str, ...],
    transition: dict,
) -> FeatureStatusReport:
    return FeatureStatusReport(
        feature_id=report.feature_id,
        status=report.status,
        consistent=report.consistent,
        files=report.files,
        missing_files=report.missing_files,
        updated_files=updated_files,
        transition=transition,
    )
