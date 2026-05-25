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

__all__ = [
    "compute_workspace_score",
    "compute_pipeline_score",
    "compute_validation_score",
    "compute_coverage_score",
    "compute_consistency_score",
    "compute_readiness_score",
    "compute_gates_score",
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


def compute_validation_score(validation: ValidationHealth) -> int:
    if validation.total == 0:
        return 20
    return int(20 * validation.pass_count / validation.total)


def compute_coverage_score(coverage: CoverageDebt) -> int:
    total_ac = coverage.acceptance_criteria_total
    if total_ac == 0:
        return 20
    return int(20 * coverage.covered_acceptance_criteria / total_ac)


def compute_consistency_score(consistency: ConsistencyDrift) -> int:
    total_checks = consistency.checks_total
    if total_checks == 0:
        return 15
    return int(15 * consistency.checks_pass / total_checks)


def compute_readiness_score(readiness: ReadinessGates) -> int:
    total_ready = readiness.features_total
    if total_ready == 0:
        return 15
    return int(15 * readiness.ready / total_ready)


def compute_gates_score(quality_gates: QualityGates) -> int:
    total_gates = quality_gates.required_total
    if total_gates == 0:
        return 5
    return int(5 * quality_gates.required_done / total_gates)
