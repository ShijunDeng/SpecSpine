from __future__ import annotations

from pathlib import Path

from .archive_models import FeatureArchiveReport
from .archive_models import FeatureArchiveArtifactExistsError
from ._archive_targets import _archive_write_targets


def _validate_archive_output_dir(resolved_output_dir: Path) -> None:
    if resolved_output_dir.exists() and not resolved_output_dir.is_dir():
        raise NotADirectoryError(f"Output path is not a directory: {resolved_output_dir}")


def _check_archive_parent_conflicts(write_targets: tuple[Path, ...]) -> None:
    parent_conflicts = tuple(
        path
        for path in write_targets
        if path.parent.exists() and not path.parent.is_dir()
    )
    if parent_conflicts:
        raise NotADirectoryError(
            f"Output archive parent is not a directory: {parent_conflicts[0]}"
        )


def _check_archive_existing_paths(
    write_targets: tuple[Path, ...],
    force: bool,
    resolved_output_dir: Path,
) -> None:
    existing_paths = tuple(path for path in write_targets if path.exists())
    if existing_paths and not force:
        raise FeatureArchiveArtifactExistsError(
            output_dir=resolved_output_dir,
            existing_paths=existing_paths,
        )


def validate_archive_write(
    report: FeatureArchiveReport,
    resolved_output_dir: Path,
    *,
    force: bool = False,
) -> tuple[Path, ...]:
    _validate_archive_output_dir(resolved_output_dir)
    write_targets = _archive_write_targets(report, resolved_output_dir)
    _check_archive_parent_conflicts(write_targets)
    _check_archive_existing_paths(write_targets, force, resolved_output_dir)
    return write_targets


__all__ = [
    "_validate_archive_output_dir",
    "_check_archive_parent_conflicts",
    "_check_archive_existing_paths",
    "validate_archive_write",
]
