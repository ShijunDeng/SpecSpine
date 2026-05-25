from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._benchmark_feature_metrics import FeatureMetrics

__all__ = [
    "BenchmarkReport",
]


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
