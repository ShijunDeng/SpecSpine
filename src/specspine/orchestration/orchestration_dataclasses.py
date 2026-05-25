from __future__ import annotations

from dataclasses import dataclass, field

__all__ = [
    "OrchestrationConflict",
    "OrchestrationPlan",
    "OrchestrationReport",
    "ParallelGroup",
]


@dataclass(frozen=True)
class OrchestrationConflict:
    conflict_type: str
    affected_files: tuple[str, ...]
    affected_ac_ids: tuple[str, ...]
    features_involved: tuple[str, ...]
    severity: str
    description: str

    def as_dict(self) -> dict[str, object]:
        return {
            "affected_ac_ids": list(self.affected_ac_ids),
            "affected_files": list(self.affected_files),
            "conflict_type": self.conflict_type,
            "description": self.description,
            "features_involved": list(self.features_involved),
            "severity": self.severity,
        }


@dataclass(frozen=True)
class ParallelGroup:
    group_id: int
    features: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "features": list(self.features),
            "group_id": self.group_id,
        }


@dataclass(frozen=True)
class OrchestrationPlan:
    execution_order: tuple[str, ...]
    parallel_groups: tuple[ParallelGroup, ...]
    blocked_features: tuple[str, ...]
    safe_for_parallel: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "blocked_features": list(self.blocked_features),
            "execution_order": list(self.execution_order),
            "parallel_groups": [g.as_dict() for g in self.parallel_groups],
            "safe_for_parallel": self.safe_for_parallel,
        }


@dataclass(frozen=True)
class OrchestrationReport:
    root: str
    feature_filter: str | None
    conflicts: tuple[OrchestrationConflict, ...]
    plan: OrchestrationPlan
    integration_recommendations: tuple[str, ...]
    status: str
    blocking_items: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "blocking_items": list(self.blocking_items),
            "conflicts": [c.as_dict() for c in self.conflicts],
            "feature_filter": self.feature_filter,
            "integration_recommendations": list(self.integration_recommendations),
            "plan": self.plan.as_dict(),
            "root": self.root,
            "safety_notes": list(self.safety_notes),
            "status": self.status,
        }
