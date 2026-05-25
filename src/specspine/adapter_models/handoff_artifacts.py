from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "AdapterHandoffArtifactExistsError",
    "AdapterHandoffArtifacts",
]


@dataclass(frozen=True)
class AdapterHandoffArtifactExistsError(FileExistsError):
    output_dir: Path
    existing_paths: tuple[Path, ...]

    def __str__(self) -> str:
        return (
            f"Adapter handoff artifact files already exist in {self.output_dir}. "
            "Use --force to overwrite files written by this command."
        )


@dataclass(frozen=True)
class AdapterHandoffArtifacts:
    output_dir: Path
    manifest_path: Path
    combined_path: Path
    combined_json_path: Path
    adapter_paths: tuple[Path, ...]
    adapter_json_paths: tuple[Path, ...]
    written_paths: tuple[Path, ...]
    manifest: dict[str, object]
