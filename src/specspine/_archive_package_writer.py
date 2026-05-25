from __future__ import annotations

from pathlib import Path

from .archive_models import FeatureArchivePackage, FeatureArchiveReport
from ._archive_package_validation import validate_archive_write
from ._archive_package_file_writer import write_archive_package_files


def write_feature_archive_package(
    report: FeatureArchiveReport,
    output_dir: Path,
    *,
    force: bool = False,
) -> FeatureArchivePackage:
    resolved_output_dir = output_dir.expanduser().resolve()
    write_targets = validate_archive_write(
        report, resolved_output_dir, force=force
    )
    return write_archive_package_files(
        report, resolved_output_dir, write_targets
    )


__all__ = [
    "write_feature_archive_package",
]
