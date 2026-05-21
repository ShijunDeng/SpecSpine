from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "FeatureMetrics",
    "BenchmarkReport",
    "VALID_GROUP_BY",
    "SAFETY_NOTES",
]

VALID_GROUP_BY = ("priority", "status", "project", "effort")

SAFETY_NOTES = (
    "Benchmark report is read-only and advisory.",
    "Does not run tests, invoke subprocesses, call network services, or read tokens.",
    "Recommended commands are advisory and are not executed.",
    "Missing evidence sources degrade gracefully.",
)


@dataclass(frozen=True)
class FeatureMetrics:
    feature_id: str
    status: str
    priority: str
    effort: str
    project: str
    ac_count: int
    task_count: int
    test_count: int
    coverage_pct: float
    validation_pass: int
    validation_fail: int
    consistency_fail: int
    drift_events: int
    lifecycle_duration_days: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "ac_count": self.ac_count,
            "consistency_fail": self.consistency_fail,
            "coverage_pct": self.coverage_pct,
            "drift_events": self.drift_events,
            "effort": self.effort,
            "feature_id": self.feature_id,
            "lifecycle_duration_days": self.lifecycle_duration_days,
            "priority": self.priority,
            "project": self.project,
            "status": self.status,
            "task_count": self.task_count,
            "test_count": self.test_count,
            "validation_fail": self.validation_fail,
            "validation_pass": self.validation_pass,
        }


@dataclass(frozen=True)
class BenchmarkReport:
    root: str
    feature_count: int
    metrics: tuple[FeatureMetrics, ...]
    aggregates: dict[str, Any]
    top_performers: tuple[dict[str, Any], ...]
    improvement_areas: tuple[dict[str, Any], ...]
    trends: dict[str, Any]
    recommendations: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "aggregates": dict(self.aggregates),
            "feature_count": self.feature_count,
            "improvement_areas": list(self.improvement_areas),
            "metrics": [m.as_dict() for m in self.metrics],
            "recommendations": list(self.recommendations),
            "root": self.root,
            "safety_notes": list(self.safety_notes),
            "top_performers": list(self.top_performers),
            "trends": dict(self.trends),
        }
