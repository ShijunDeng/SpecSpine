from __future__ import annotations

from pathlib import Path

from .archive_models import (
    TEST_COVERAGE_HEADING_RE,
    FeatureStatusReport,
)
from .features import feature_bundle_paths

__all__ = [
    "_coverage_section_exists",
    "_source_and_missing_files",
]


def _coverage_section_exists(root: Path, slug: str) -> bool:
    quality_path = feature_bundle_paths(root, slug)["quality"]
    if not quality_path.exists():
        return False
    return bool(
        TEST_COVERAGE_HEADING_RE.search(quality_path.read_text(encoding="utf-8"))
    )


def _source_and_missing_files(
    status_report: FeatureStatusReport,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    source_files = tuple(
        str(file["path"])
        for file in status_report.files.values()
        if bool(file["exists"])
    )
    missing_files = tuple(str(path) for path in status_report.missing_files)
    return source_files, missing_files
