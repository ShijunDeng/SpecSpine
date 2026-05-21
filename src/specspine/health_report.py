from __future__ import annotations

from pathlib import Path

from .health_builders import (
    _build_consistency_drift,
    _build_coverage_debt_data,
    _build_dependency_health,
    _build_feature_pipeline,
    _build_quality_gates,
    _build_readiness_gates,
    _build_retrospective_theme,
    _build_security_summary,
    _build_validation_health,
    _build_workspace_health,
)
from .health_models import (
    HealthReport,
    SAFETY_NOTES,
)
from .health_recommendations import (
    _generate_recommended_commands,
    generate_recommended_actions,
)
from .health_scoring import compute_health_score


def build_health_report(root: Path) -> HealthReport:
    resolved_root = root.expanduser().resolve()

    workspace = _build_workspace_health(resolved_root)
    feature_pipeline = _build_feature_pipeline(resolved_root)
    validation = _build_validation_health(resolved_root)
    coverage = _build_coverage_debt_data(resolved_root)
    consistency = _build_consistency_drift(resolved_root)
    readiness = _build_readiness_gates(resolved_root)
    quality_gates = _build_quality_gates(resolved_root)
    dependency = _build_dependency_health(resolved_root)
    security = _build_security_summary(resolved_root)
    retrospective = _build_retrospective_theme(resolved_root)

    health_score = compute_health_score(
        workspace,
        feature_pipeline,
        validation,
        coverage,
        consistency,
        readiness,
        quality_gates,
    )

    partial_report = HealthReport(
        root=str(resolved_root),
        workspace=workspace,
        feature_pipeline=feature_pipeline,
        validation_health=validation,
        coverage_debt=coverage,
        consistency_drift=consistency,
        readiness_gates=readiness,
        quality_gates=quality_gates,
        dependency_health=dependency,
        security_summary=security,
        retrospective_theme=retrospective,
        health_score=health_score,
        recommended_actions=(),
        recommended_commands=(),
        safety_notes=SAFETY_NOTES,
    )

    recommended_actions = generate_recommended_actions(partial_report)
    recommended_commands = _generate_recommended_commands(partial_report)

    return HealthReport(
        root=str(resolved_root),
        workspace=workspace,
        feature_pipeline=feature_pipeline,
        validation_health=validation,
        coverage_debt=coverage,
        consistency_drift=consistency,
        readiness_gates=readiness,
        quality_gates=quality_gates,
        dependency_health=dependency,
        security_summary=security,
        retrospective_theme=retrospective,
        health_score=health_score,
        recommended_actions=tuple(recommended_actions),
        recommended_commands=tuple(recommended_commands),
        safety_notes=SAFETY_NOTES,
    )


__all__ = [
    "build_health_report",
]
