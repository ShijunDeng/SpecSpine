from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "FeatureSyncPlanArtifacts",
]


@dataclass(frozen=True)
class FeatureSyncPlanArtifacts:
    output_dir: Path
    manifest_path: Path
    commands_path: Path
    body_paths: tuple[Path, ...]
    written_paths: tuple[Path, ...]
    manifest: dict[str, object]
