from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .adapter_handoff_render import (
    _adapter_handoff_blocking_checks,
    adapter_feature_handoff_focused_payload,
    render_adapter_feature_handoff_adapter_json,
    render_adapter_feature_handoff_adapter_text,
    render_adapter_feature_handoff_json,
    render_adapter_feature_handoff_text,
)
from .adapter_models import (
    ADAPTER_HANDOFF_SAFETY_FLAGS,
    ADAPTER_SPECS,
    AdapterFeatureHandoffReport,
    AdapterHandoffArtifactExistsError,
    AdapterHandoffArtifacts,
)

__all__ = [
    "_adapter_handoff_artifact_manifest",
    "_sha256_hex",
    "write_adapter_feature_handoff_artifacts",
]


def _adapter_handoff_artifact_manifest(
    report: AdapterFeatureHandoffReport,
    artifact_checksums: dict[str, str],
) -> dict[str, object]:
    adapter_artifacts = {
        key: f"adapters/{key}.md"
        for key in ADAPTER_SPECS
    }
    adapter_json_artifacts = {
        key: f"adapters/{key}.json"
        for key in ADAPTER_SPECS
    }
    return {
        "artifact_version": 1,
        "artifact_root": ".",
        "artifact_checksums": artifact_checksums,
        "artifacts": {
            "manifest": "manifest.json",
            "combined": "combined.md",
            "combined_json": "combined.json",
            "adapters": adapter_artifacts,
            "adapter_json": adapter_json_artifacts,
        },
        "blocking_checks": _adapter_handoff_blocking_checks(report),
        "checksum_algorithm": "sha256",
        "feature_id": report.feature_id,
        "gaps": [dict(gap) for gap in report.gaps],
        "missing_files": list(report.missing_files),
        "ready": report.ready,
        "safety_flags": dict(ADAPTER_HANDOFF_SAFETY_FLAGS),
        "safety_notes": [
            (
                "Artifact export does not execute upstream tools, subprocesses, "
                "network calls, GitHub operations, or token reads."
            ),
            "Recommended upstream steps are review data only.",
        ],
        "source_files": list(report.source_files),
        "status": report.status,
        "summary": report.summary,
    }


def _sha256_hex(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def write_adapter_feature_handoff_artifacts(
    report: AdapterFeatureHandoffReport,
    output_dir: Path,
    *,
    force: bool = False,
) -> AdapterHandoffArtifacts:
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

    artifact_checksums = {
        relative_path: _sha256_hex(content.encode("utf-8"))
        for relative_path, content in content_by_relative_path.items()
    }
    manifest = _adapter_handoff_artifact_manifest(report, artifact_checksums)

    for relative_path, content in content_by_relative_path.items():
        (resolved_output_dir / relative_path).write_text(content, encoding="utf-8")
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return AdapterHandoffArtifacts(
        output_dir=resolved_output_dir,
        manifest_path=manifest_path,
        combined_path=combined_path,
        combined_json_path=combined_json_path,
        adapter_paths=adapter_paths,
        adapter_json_paths=adapter_json_paths,
        written_paths=write_targets,
        manifest=manifest,
    )
