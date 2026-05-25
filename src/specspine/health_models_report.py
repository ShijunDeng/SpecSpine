from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .health_models_core import (
    WorkspaceHealth,
    FeaturePipeline,
    ValidationHealth,
    CoverageDebt,
    ConsistencyDrift,
)
from .health_models_gates import (
    ReadinessGates,
    QualityGates,
    DependencyHealth,
    SecuritySummary,
)

SAFETY_NOTES = (
    "Health report is read-only and advisory.",
    "Does not run tests, invoke subprocesses, call network services, or read tokens.",
    "Recommended commands are advisory and are not executed.",
    "Missing evidence sources degrade gracefully.",
)

__all__ = [
    "SAFETY_NOTES",
    "RetrospectiveTheme",
    "HealthReport",
]


@dataclass(frozen=True)
class RetrospectiveTheme:
    top_blocker_theme: str
    blocking_checks: dict[str, int]
    gaps: dict[str, int]
    coverage_states: dict[str, int]
    open_tasks: dict[str, int]

    def as_dict(self) -> dict[str, Any]:
        return {
            "blocking_checks": dict(self.blocking_checks),
            "coverage_states": dict(self.coverage_states),
            "gaps": dict(self.gaps),
            "open_tasks": dict(self.open_tasks),
            "top_blocker_theme": self.top_blocker_theme,
        }


@dataclass(frozen=True)
class HealthReport:
    root: str
    workspace: WorkspaceHealth
    feature_pipeline: FeaturePipeline
    validation_health: ValidationHealth
    coverage_debt: CoverageDebt
    consistency_drift: ConsistencyDrift
    readiness_gates: ReadinessGates
    quality_gates: QualityGates
    dependency_health: DependencyHealth
    security_summary: SecuritySummary
    retrospective_theme: RetrospectiveTheme
    health_score: int
    recommended_actions: tuple[str, ...]
    recommended_commands: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "consistency_drift": self.consistency_drift.as_dict(),
            "coverage_debt": self.coverage_debt.as_dict(),
            "dependency_health": self.dependency_health.as_dict(),
            "feature_pipeline": self.feature_pipeline.as_dict(),
            "health_score": self.health_score,
            "quality_gates": self.quality_gates.as_dict(),
            "readiness_gates": self.readiness_gates.as_dict(),
            "recommended_actions": list(self.recommended_actions),
            "recommended_commands": list(self.recommended_commands),
            "retrospective_theme": self.retrospective_theme.as_dict(),
            "root": self.root,
            "safety_notes": list(self.safety_notes),
            "security_summary": self.security_summary.as_dict(),
            "validation_health": self.validation_health.as_dict(),
            "workspace": self.workspace.as_dict(),
        }
