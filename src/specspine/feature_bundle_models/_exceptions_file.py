from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "FeatureBundleExistsError",
    "FeatureBundleNotFoundError",
    "FeatureSyncPlanArtifactExistsError",
]


@dataclass(frozen=True)
class FeatureBundleExistsError(FileExistsError):
    slug: str
    existing_paths: tuple[Path, ...]

    def __str__(self) -> str:
        return (
            f"Feature bundle '{self.slug}' already has existing files. "
            "Use --force to overwrite them."
        )


@dataclass(frozen=True)
class FeatureBundleNotFoundError(FileNotFoundError):
    slug: str
    root: Path
    missing_paths: tuple[Path, ...]

    def __str__(self) -> str:
        return (
            f"No feature files found for '{self.slug}' at {self.root}. "
            "Expected at least one native feature file."
        )


@dataclass(frozen=True)
class FeatureSyncPlanArtifactExistsError(FileExistsError):
    output_dir: Path
    existing_paths: tuple[Path, ...]

    def __str__(self) -> str:
        return (
            f"Sync plan artifact files already exist in {self.output_dir}. "
            "Use --force to overwrite files written by this command."
        )
