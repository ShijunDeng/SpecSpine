from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .issues import AnalysisIssue

__all__ = [
    "FeatureAnalysis",
    "AnalysisReport",
]


@dataclass(frozen=True)
class FeatureAnalysis:
    feature_id: str
    status: str
    ready: bool
    source_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    metrics: dict[str, int | bool]
    issues: tuple[AnalysisIssue, ...]
    recommended_commands: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "feature_id": self.feature_id,
            "issues": [issue.as_dict() for issue in self.issues],
            "metrics": dict(self.metrics),
            "missing_files": list(self.missing_files),
            "ready": self.ready,
            "recommended_commands": list(self.recommended_commands),
            "source_files": list(self.source_files),
            "status": self.status,
        }


@dataclass(frozen=True)
class AnalysisReport:
    root: Path
    feature_filter: str | None
    summary: dict[str, object]
    features: tuple[FeatureAnalysis, ...]
    issues: tuple[AnalysisIssue, ...]
    recommended_commands: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "feature_filter": self.feature_filter,
            "features": [feature.as_dict() for feature in self.features],
            "issues": [issue.as_dict() for issue in self.issues],
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "summary": dict(self.summary),
        }
