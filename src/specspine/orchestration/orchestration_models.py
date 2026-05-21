from __future__ import annotations

import re
from dataclasses import dataclass, field

CONTRACT_PATTERN = re.compile(
    r"(?P<type>endpoint|schema|config|api|route|table|collection)\s*[=:]\s*(?P<name>[A-Za-z0-9_/.:-]+)",
    re.IGNORECASE,
)

API_ENDPOINT_PATTERNS = [
    re.compile(r"(?:GET|POST|PUT|DELETE|PATCH)\s+(/[A-Za-z0-9_/.:{}-]+)"),
    re.compile(r"(?:route|endpoint|url|path)\s*[=:]\s*['\"]?(/[A-Za-z0-9_/.:{}-]+)"),
]

SCHEMA_PATTERNS = [
    re.compile(r"(?:schema|model|table|collection)\s*[=:]\s*([A-Za-z_][A-Za-z0-9_]*)"),
    re.compile(r"class\s+([A-Za-z_][A-Za-z0-9_]*)(?:\(.*Model|:.*BaseModel|:.*Schema)"),
]

CONFIG_PATTERNS = [
    re.compile(r"(?:config|setting|env|variable)\s*[=:]\s*([A-Z_][A-Z0-9_]*)"),
    re.compile(r"(?:key|flag)\s*[=:]\s*['\"]?([a-z_][a-z0-9_.]*)['\"]?"),
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


__all__ = [
    "API_ENDPOINT_PATTERNS",
    "CONFIG_PATTERNS",
    "CONTRACT_PATTERN",
    "OrchestrationConflict",
    "OrchestrationPlan",
    "OrchestrationReport",
    "ParallelGroup",
    "SCHEMA_PATTERNS",
]
