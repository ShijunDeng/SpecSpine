from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "FeatureBundleExistsError",
    "FeatureBundleNotFoundError",
    "FeatureSyncPlanArtifactExistsError",
    "FeatureStatusTransitionError",
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


@dataclass(frozen=True)
class FeatureStatusTransitionError(ValueError):
    feature_id: str
    error: str
    transition: dict[str, object]
    message: str
    blocking_checks: tuple[dict[str, str], ...] = ()
    gaps: tuple[dict[str, str], ...] = ()
    missing_files: tuple[str, ...] = ()

    def __str__(self) -> str:
        return self.message

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "error": self.error,
            "feature_id": self.feature_id,
            "transition": dict(self.transition),
        }
        if self.blocking_checks:
            payload["blocking_checks"] = [dict(check) for check in self.blocking_checks]
        if self.gaps:
            payload["gaps"] = [dict(gap) for gap in self.gaps]
        if self.missing_files:
            payload["missing_files"] = list(self.missing_files)
        return payload
