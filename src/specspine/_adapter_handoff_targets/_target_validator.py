from __future__ import annotations

from pathlib import Path

from ..adapter_models import (
    AdapterHandoffArtifactExistsError,
)

__all__ = [
    "AdapterHandoffArtifactExistsError",
    "_validate_and_prepare_dirs",
]


def _validate_and_prepare_dirs(
    resolved_output_dir: Path,
    write_targets: tuple,
    *,
    force: bool = False,
) -> None:
    if resolved_output_dir.exists() and not resolved_output_dir.is_dir():
        raise NotADirectoryError(f"Output path is not a directory: {resolved_output_dir}")

    parent_conflicts = tuple(
        path.parent
        for path in write_targets
        if path.parent.exists() and not path.parent.is_dir()
    )
    if parent_conflicts:
        first_conflict = parent_conflicts[0]
        raise NotADirectoryError(f"Output artifact parent is not a directory: {first_conflict}")

    existing_paths = tuple(path for path in write_targets if path.exists())
    if existing_paths and not force:
        raise AdapterHandoffArtifactExistsError(
            output_dir=resolved_output_dir,
            existing_paths=existing_paths,
        )

    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    (resolved_output_dir / "adapters").mkdir(parents=True, exist_ok=True)
