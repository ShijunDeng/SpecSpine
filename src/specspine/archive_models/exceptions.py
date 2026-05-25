from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "InvalidArchiveId",
    "FeatureArchiveArtifactExistsError",
]


class InvalidArchiveId(ValueError):
    """Raised when an archive id cannot be used safely in a local package."""


@dataclass(frozen=True)
class FeatureArchiveArtifactExistsError(FileExistsError):
    output_dir: Path
    existing_paths: tuple[Path, ...]

    def __str__(self) -> str:
        return (
            f"Feature archive package files already exist in {self.output_dir}. "
            "Use --force to overwrite files written by this command."
        )
