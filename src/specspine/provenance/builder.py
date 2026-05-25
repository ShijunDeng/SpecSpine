from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ..features import (
    validate_feature_slug,
)
from .models import ProvenanceManifest
from .helpers import _resolve_path
from .artifacts import (
    _dedupe_artifacts,
    _feature_artifacts,
    _include_artifact,
    _workspace_artifacts,
)
from .evidence import _feature_evidence, _summary
from .commands import _recommended_commands, _safety_notes

__all__ = [
    "build_provenance_manifest",
]


def build_provenance_manifest(
    root: str | Path,
    *,
    feature: str | None = None,
    includes: Iterable[str | Path] = (),
) -> ProvenanceManifest:
    resolved_root = _resolve_path(Path(root))
    feature_id = validate_feature_slug(feature) if feature is not None else None

    feature_artifacts = (
        _feature_artifacts(resolved_root, feature_id)
        if feature_id is not None
        else ()
    )
    include_artifacts = tuple(
        _include_artifact(resolved_root, include) for include in includes
    )
    artifacts = _dedupe_artifacts(
        (
            _workspace_artifacts(resolved_root),
            feature_artifacts,
            include_artifacts,
        )
    )
    evidence = (
        (_feature_evidence(resolved_root, feature_id),)
        if feature_id is not None
        else ()
    )

    return ProvenanceManifest(
        root=resolved_root,
        feature_id=feature_id,
        artifacts=artifacts,
        feature_evidence=evidence,
        summary=_summary(artifacts, evidence),
        recommended_commands=_recommended_commands(feature_id),
        safety_notes=_safety_notes(),
    )
