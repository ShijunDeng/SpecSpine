from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "FeatureMetrics",
]


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
