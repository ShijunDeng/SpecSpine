from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .adapter_handoff_render import (
    render_adapter_feature_handoff_adapter_json,
    render_adapter_feature_handoff_adapter_text,
    render_adapter_feature_handoff_json,
    render_adapter_feature_handoff_text,
)
from .adapter_models import (
    AdapterHandoffArtifacts,
    AdapterFeatureHandoffReport,
    ADAPTER_SPECS,
)
from .adapter_handoff_checksums import _sha256_hex
from .adapter_handoff_manifests import _adapter_handoff_artifact_manifest

__all__ = [
    "_build_adapter_handoff_content",
    "_write_adapter_handoff_artifacts",
]


def _build_adapter_handoff_content(
    report: AdapterFeatureHandoffReport,
) -> dict[str, str]:
    content_by_relative_path: dict[str, str] = {
        "combined.md": render_adapter_feature_handoff_text(report),
        "combined.json": render_adapter_feature_handoff_json(report),
    }
    for key in ADAPTER_SPECS:
        content_by_relative_path[f"adapters/{key}.md"] = (
            render_adapter_feature_handoff_adapter_text(report, key)
        )
        content_by_relative_path[f"adapters/{key}.json"] = (
            render_adapter_feature_handoff_adapter_json(report, key)
        )
    return content_by_relative_path


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
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
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
