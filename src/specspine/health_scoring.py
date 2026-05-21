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


def compute_health_score(
    workspace: WorkspaceHealth,
    feature_pipeline: FeaturePipeline,
    validation: ValidationHealth,
    coverage: CoverageDebt,
    consistency: ConsistencyDrift,
    readiness: ReadinessGates,
    quality_gates: QualityGates,
) -> int:
    if workspace.missing:
        return 0

    workspace_score = 10 if workspace.complete else 5

    total_features = feature_pipeline.features_total
    if total_features == 0:
        pipeline_score = 15
    else:
        advanced_statuses = sum(
            count for status, count in feature_pipeline.by_status.items()
            if status in {"implemented", "validated", "archived"}
        )
        pipeline_score = int(15 * advanced_statuses / total_features)

    if validation.total == 0:
        validation_score = 20
    else:
        validation_score = int(20 * validation.pass_count / validation.total)

    total_ac = coverage.acceptance_criteria_total
    if total_ac == 0:
        coverage_score = 20
    else:
        coverage_score = int(20 * coverage.covered_acceptance_criteria / total_ac)

    total_checks = consistency.checks_total
    if total_checks == 0:
        consistency_score = 15
    else:
        consistency_score = int(15 * consistency.checks_pass / total_checks)

    total_ready = readiness.features_total
    if total_ready == 0:
        readiness_score = 15
    else:
        readiness_score = int(15 * readiness.ready / total_ready)

    total_gates = quality_gates.required_total
    if total_gates == 0:
        gates_score = 5
    else:
        gates_score = int(5 * quality_gates.required_done / total_gates)

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


__all__ = [
    "compute_health_score",
]
