from __future__ import annotations

from ..feature_bundle_models import FEATURE_FILE_PATHS, FeatureStatusReport

__all__ = [
    "build_status_report",
]


def build_status_report(
    slug: str,
    files: dict[str, dict[str, object]],
    missing_files: list[str],
    statuses: list[str],
    status_missing: bool = False,
) -> FeatureStatusReport:
    unique_statuses = sorted(set(statuses))
    current_status = unique_statuses[0] if len(unique_statuses) == 1 else None
    if len(unique_statuses) > 1:
        current_status = "mixed"

    existing_count = len(FEATURE_FILE_PATHS) - len(missing_files)
    consistent = existing_count > 0 and not status_missing and len(unique_statuses) == 1

    return FeatureStatusReport(
        feature_id=slug,
        status=current_status,
        consistent=consistent,
        files=files,
        missing_files=tuple(missing_files),
    )
