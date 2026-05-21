from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SAFETY_NOTES = (
    "Health report is read-only and advisory.",
    "Does not run tests, invoke subprocesses, call network services, or read tokens.",
    "Recommended commands are advisory and are not executed.",
    "Missing evidence sources degrade gracefully.",
)


@dataclass(frozen=True)
class WorkspaceHealth:
    complete: bool
    present: tuple[str, ...]
    missing: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "complete": self.complete,
            "missing": list(self.missing),
            "present": list(self.present),
        }


@dataclass(frozen=True)
class FeaturePipeline:
    features_total: int
    by_status: dict[str, int]

    def as_dict(self) -> dict[str, Any]:
        return {
            "by_status": dict(self.by_status),
            "features_total": self.features_total,
        }


@dataclass(frozen=True)
class ValidationHealth:
    ok: bool
    pass_count: int
    fail_count: int
    warn_count: int
    skip_count: int
    total: int
    top_failing_rules: tuple[dict[str, str], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "fail_count": self.fail_count,
            "ok": self.ok,
            "pass_count": self.pass_count,
            "skip_count": self.skip_count,
            "top_failing_rules": list(self.top_failing_rules),
            "total": self.total,
            "warn_count": self.warn_count,
        }


@dataclass(frozen=True)
class CoverageDebt:
    features_with_debt: int
    missing_acceptance_criteria: int
    covered_acceptance_criteria: int
    acceptance_criteria_total: int
    top_features_with_uncovered_ac: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "acceptance_criteria_total": self.acceptance_criteria_total,
            "covered_acceptance_criteria": self.covered_acceptance_criteria,
            "features_with_debt": self.features_with_debt,
            "missing_acceptance_criteria": self.missing_acceptance_criteria,
            "top_features_with_uncovered_ac": list(self.top_features_with_uncovered_ac),
        }


@dataclass(frozen=True)
class ConsistencyDrift:
    features_scanned: int
    checks_pass: int
    checks_fail: int
    checks_warn: int
    checks_total: int
    top_failing_features: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "checks_fail": self.checks_fail,
            "checks_pass": self.checks_pass,
            "checks_total": self.checks_total,
            "checks_warn": self.checks_warn,
            "features_scanned": self.features_scanned,
            "top_failing_features": list(self.top_failing_features),
        }


@dataclass(frozen=True)
class ReadinessGates:
    features_total: int
    ready: int
    not_ready: int
    blocking_checks_total: int
    gaps_total: int
    top_blockers: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "blocking_checks_total": self.blocking_checks_total,
            "features_total": self.features_total,
            "gaps_total": self.gaps_total,
            "not_ready": self.not_ready,
            "ready": self.ready,
            "top_blockers": list(self.top_blockers),
        }


@dataclass(frozen=True)
class QualityGates:
    required_total: int
    required_done: int
    required_open: int
    definition_total: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "definition_total": self.definition_total,
            "required_done": self.required_done,
            "required_open": self.required_open,
            "required_total": self.required_total,
        }


@dataclass(frozen=True)
class DependencyHealth:
    features_total: int
    cycles: list[list[str]]
    critical_path: list[str]
    critical_path_effort: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "critical_path": self.critical_path,
            "critical_path_effort": self.critical_path_effort,
            "cycles": self.cycles,
            "features_total": self.features_total,
        }


@dataclass(frozen=True)
class SecuritySummary:
    cues_total: int
    high: int
    medium: int
    low: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "cues_total": self.cues_total,
            "high": self.high,
            "low": self.low,
            "medium": self.medium,
        }


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


__all__ = [
    "SAFETY_NOTES",
    "WorkspaceHealth",
    "FeaturePipeline",
    "ValidationHealth",
    "CoverageDebt",
    "ConsistencyDrift",
    "ReadinessGates",
    "QualityGates",
    "DependencyHealth",
    "SecuritySummary",
    "RetrospectiveTheme",
    "HealthReport",
]
