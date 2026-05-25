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
from .health_scoring import compute_health_score

__all__ = [
    "_collect_health_sections",
]


def _collect_health_sections(resolved_root: Path) -> dict:
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

    return {
        "workspace": workspace,
        "feature_pipeline": feature_pipeline,
        "validation": validation,
        "coverage": coverage,
        "consistency": consistency,
        "readiness": readiness,
        "quality_gates": quality_gates,
        "dependency": dependency,
        "security": security,
        "retrospective": retrospective,
        "health_score": health_score,
    }
