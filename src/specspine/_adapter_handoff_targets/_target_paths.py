from __future__ import annotations

from pathlib import Path

from ..adapter_models import ADAPTER_SPECS

__all__ = [
    "_compute_write_targets",
]


def _compute_write_targets(output_dir: Path) -> dict:
    manifest_path = output_dir / "manifest.json"
    combined_path = output_dir / "combined.md"
    combined_json_path = output_dir / "combined.json"
    adapter_paths = tuple(
        output_dir / "adapters" / f"{key}.md"
        for key in ADAPTER_SPECS
    )
    adapter_json_paths = tuple(
        output_dir / "adapters" / f"{key}.json"
        for key in ADAPTER_SPECS
    )
    write_targets = (
        manifest_path,
        combined_path,
        combined_json_path,
        *adapter_paths,
        *adapter_json_paths,
    )

    return {
        "manifest_path": manifest_path,
        "combined_path": combined_path,
        "combined_json_path": combined_json_path,
        "adapter_paths": adapter_paths,
        "adapter_json_paths": adapter_json_paths,
        "write_targets": write_targets,
    }
