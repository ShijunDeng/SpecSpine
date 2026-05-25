from __future__ import annotations

from pathlib import Path

from .archive_models import FeatureArchiveReport
from ._archive_paths import _source_snapshot_path


def _archive_write_targets(
    report: FeatureArchiveReport,
    output_dir: Path,
) -> tuple[Path, ...]:
    targets = [
        output_dir / "README.md",
        output_dir / "archive.json",
    ]
    for kind, file in report.status_report.files.items():
        if bool(file["exists"]):
            targets.append(output_dir / _source_snapshot_path(kind))
    return tuple(targets)


__all__ = [
    "_archive_write_targets",
]
