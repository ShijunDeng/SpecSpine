from __future__ import annotations

from .health_models import FeaturePipeline, WorkspaceHealth

__all__ = [
    "compute_workspace_score",
    "compute_pipeline_score",
]


def compute_workspace_score(workspace: WorkspaceHealth) -> int:
    if workspace.missing:
        return 0
    return 10 if workspace.complete else 5


def compute_pipeline_score(feature_pipeline: FeaturePipeline) -> int:
    total_features = feature_pipeline.features_total
    if total_features == 0:
        return 15
    advanced_statuses = sum(
        count for status, count in feature_pipeline.by_status.items()
        if status in {"implemented", "validated", "archived"}
    )
    return int(15 * advanced_statuses / total_features)
