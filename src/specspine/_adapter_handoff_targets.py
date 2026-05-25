from __future__ import annotations

from pathlib import Path
from typing import Tuple

from .adapter_models import (
    AdapterHandoffArtifactExistsError,
    AdapterHandoffArtifacts,
    ADAPTER_SPECS,
)

__all__ = [
    "AdapterHandoffArtifactExistsError",
    "AdapterHandoffArtifacts",
    "_compute_adapter_handoff_targets",
]


def _compute_adapter_handoff_targets(
    output_dir: Path,
    *,
    force: bool = False,
) -> dict:
    resolved_output_dir = output_dir.expanduser().resolve()
    if resolved_output_dir.exists() and not resolved_output_dir.is_dir():
        raise NotADirectoryError(f"Output path is not a directory: {resolved_output_dir}")

    manifest_path = resolved_output_dir / "manifest.json"
    combined_path = resolved_output_dir / "combined.md"
    combined_json_path = resolved_output_dir / "combined.json"
    adapter_paths = tuple(
        resolved_output_dir / "adapters" / f"{key}.md"
        for key in ADAPTER_SPECS
    )
    adapter_json_paths = tuple(
        resolved_output_dir / "adapters" / f"{key}.json"
        for key in ADAPTER_SPECS
    )
    write_targets = (
        manifest_path,
        combined_path,
        combined_json_path,
        *adapter_paths,
        *adapter_json_paths,
    )

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

    return {
        "resolved_output_dir": resolved_output_dir,
        "manifest_path": manifest_path,
        "combined_path": combined_path,
        "combined_json_path": combined_json_path,
        "adapter_paths": adapter_paths,
        "adapter_json_paths": adapter_json_paths,
        "write_targets": write_targets,
    }
