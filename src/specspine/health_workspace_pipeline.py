from __future__ import annotations

from pathlib import Path

from .features import list_feature_bundles
from .workspace import BASE_WORKSPACE_FILES, check_workspace
from .health_models import FeaturePipeline, WorkspaceHealth

__all__ = [
    "_build_feature_pipeline",
    "_build_workspace_health",
]


def _build_workspace_health(root: Path) -> WorkspaceHealth:
    present, missing = check_workspace(root, required_files=BASE_WORKSPACE_FILES)
    present_paths = sorted(str(p.relative_to(root)) for p in present)
    missing_paths = sorted(str(m.relative_to(root)) for m in missing)
    return WorkspaceHealth(
        complete=len(missing) == 0,
        present=tuple(present_paths),
        missing=tuple(missing_paths),
    )


def _build_feature_pipeline(root: Path) -> FeaturePipeline:
    features = list_feature_bundles(root)
    by_status: dict[str, int] = {}
    for feature in features:
        status = str(feature.get("status") or "unknown")
        by_status[status] = by_status.get(status, 0) + 1
    return FeaturePipeline(
        features_total=len(features),
        by_status=dict(sorted(by_status.items())),
    )
