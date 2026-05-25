from __future__ import annotations

from pathlib import Path

from ._adapter_handoff_targets import (
    AdapterHandoffArtifactExistsError,
    AdapterHandoffArtifacts,
    _compute_adapter_handoff_targets,
)
from ._adapter_handoff_content import (
    _write_adapter_handoff_artifacts,
)
from .adapter_handoff_checksums import _sha256_hex
from .adapter_handoff_manifests import _adapter_handoff_artifact_manifest
from .adapter_models import AdapterFeatureHandoffReport

__all__ = [
    "_adapter_handoff_artifact_manifest",
    "_sha256_hex",
    "write_adapter_feature_handoff_artifacts",
]


def write_adapter_feature_handoff_artifacts(
    report: AdapterFeatureHandoffReport,
    output_dir: Path,
    *,
    force: bool = False,
) -> AdapterHandoffArtifacts:
    targets = _compute_adapter_handoff_targets(output_dir, force=force)
    return _write_adapter_handoff_artifacts(targets, report)
