from __future__ import annotations

from .adapter_handoff_render import _adapter_handoff_blocking_checks
from .adapter_models import (
    ADAPTER_HANDOFF_SAFETY_FLAGS,
    ADAPTER_SPECS,
    AdapterFeatureHandoffReport,
)

__all__ = [
    "_adapter_handoff_artifact_manifest",
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
