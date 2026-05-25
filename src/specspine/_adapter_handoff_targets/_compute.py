from __future__ import annotations

from pathlib import Path

from ..adapter_models import AdapterHandoffArtifacts
from ._target_paths import _compute_write_targets
from ._target_validator import _validate_and_prepare_dirs

__all__ = [
    "_compute_adapter_handoff_targets",
]


def _compute_adapter_handoff_targets(
    output_dir: Path,
    *,
    force: bool = False,
) -> dict:
    resolved_output_dir = output_dir.expanduser().resolve()

    paths = _compute_write_targets(resolved_output_dir)
    _validate_and_prepare_dirs(resolved_output_dir, paths["write_targets"], force=force)

    return {
        "resolved_output_dir": resolved_output_dir,
        "manifest_path": paths["manifest_path"],
        "combined_path": paths["combined_path"],
        "combined_json_path": paths["combined_json_path"],
        "adapter_paths": paths["adapter_paths"],
        "adapter_json_paths": paths["adapter_json_paths"],
        "write_targets": paths["write_targets"],
    }
