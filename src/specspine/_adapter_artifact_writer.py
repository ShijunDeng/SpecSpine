from __future__ import annotations

from typing import Any

from .adapter_models import (
    AdapterHandoffArtifacts,
    AdapterFeatureHandoffReport,
)
from .adapter_handoff_checksums import _sha256_hex
from .adapter_handoff_manifests import _adapter_handoff_artifact_manifest
from ._adapter_content_builder import _build_adapter_handoff_content

__all__ = [
    "_compute_adapter_handoff_checksums",
    "_write_adapter_handoff_artifacts",
]


def _compute_adapter_handoff_checksums(
    content_by_relative_path: dict[str, str],
) -> dict[str, str]:
    return {
        relative_path: _sha256_hex(content.encode("utf-8"))
        for relative_path, content in content_by_relative_path.items()
    }


def _write_adapter_handoff_artifacts(
    targets: dict[str, Any],
    report: AdapterFeatureHandoffReport,
) -> AdapterHandoffArtifacts:
    content_by_relative_path = _build_adapter_handoff_content(report)
    artifact_checksums = _compute_adapter_handoff_checksums(content_by_relative_path)
    manifest = _adapter_handoff_artifact_manifest(report, artifact_checksums)

    resolved_output_dir = targets["resolved_output_dir"]
    manifest_path = targets["manifest_path"]

    for relative_path, content in content_by_relative_path.items():
        (resolved_output_dir / relative_path).write_text(content, encoding="utf-8")
    manifest_path.write_text(
        _format_json(manifest),
        encoding="utf-8",
    )

    return AdapterHandoffArtifacts(
        output_dir=resolved_output_dir,
        manifest_path=manifest_path,
        combined_path=targets["combined_path"],
        combined_json_path=targets["combined_json_path"],
        adapter_paths=targets["adapter_paths"],
        adapter_json_paths=targets["adapter_json_paths"],
        written_paths=targets["write_targets"],
        manifest=manifest,
    )


def _format_json(data: Any) -> str:
    import json
    return json.dumps(data, indent=2, sort_keys=True) + "\n"
