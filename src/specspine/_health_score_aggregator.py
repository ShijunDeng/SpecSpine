from __future__ import annotations

from .health_models import (
    CoverageDebt,
    ConsistencyDrift,
    FeaturePipeline,
    QualityGates,
    ReadinessGates,
    ValidationHealth,
    WorkspaceHealth,
)
from ._health_dimension_scorer import (
    compute_workspace_score,
    compute_pipeline_score,
    compute_validation_score,
    compute_coverage_score,
    compute_consistency_score,
    compute_readiness_score,
    compute_gates_score,
)

__all__ = [
    "compute_health_score",
]


def compute_health_score(
    workspace: WorkspaceHealth,
    feature_pipeline: FeaturePipeline,
    validation: ValidationHealth,
    coverage: CoverageDebt,
    consistency: ConsistencyDrift,
    readiness: ReadinessGates,
    quality_gates: QualityGates,
) -> int:
    workspace_score = compute_workspace_score(workspace)
    if workspace_score == 0:
        return 0

    pipeline_score = compute_pipeline_score(feature_pipeline)
    validation_score = compute_validation_score(validation)
    coverage_score = compute_coverage_score(coverage)
    consistency_score = compute_consistency_score(consistency)
    readiness_score = compute_readiness_score(readiness)
    gates_score = compute_gates_score(quality_gates)

    score = (
        workspace_score
        + pipeline_score
        + validation_score
        + coverage_score
        + consistency_score
        + readiness_score
        + gates_score
    )

    return max(0, min(100, score))
