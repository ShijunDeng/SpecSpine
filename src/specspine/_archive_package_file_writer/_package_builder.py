from __future__ import annotations

from pathlib import Path

from ..archive_models import FeatureArchivePackage, FeatureArchiveReport
from .._archive_paths import _source_snapshot_path

__all__ = [
    "_build_archive_package",
]


def _build_archive_package(
    report: FeatureArchiveReport,
    resolved_output_dir: Path,
    write_targets: tuple[Path, ...],
) -> FeatureArchivePackage:
    return FeatureArchivePackage(
        output_dir=resolved_output_dir,
        readme_path=resolved_output_dir / "README.md",
        report_path=resolved_output_dir / "archive.json",
        source_paths=tuple(
            resolved_output_dir / _source_snapshot_path(kind)
            for kind, file in report.status_report.files.items()
            if bool(file["exists"])
        ),
        written_paths=write_targets,
    )
