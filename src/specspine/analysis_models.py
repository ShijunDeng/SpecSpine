from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "SEVERITIES",
    "AC_REFERENCE_RE",
    "TEST_TARGET_RE",
    "QUALITY_REFERENCE_RE",
    "VAGUE_TERMS",
    "TEXT_MAX_ISSUES_PER_FEATURE",
    "TEXT_MAX_RECOMMENDATIONS",
    "AnalysisIssue",
    "FeatureAnalysis",
    "AnalysisReport",
    "_PendingIssue",
]

SEVERITIES = ("critical", "high", "medium", "low")
AC_REFERENCE_RE = __import__("re").compile(r"\bAC[-\s]?0*(\d{1,})\b", __import__("re").IGNORECASE)
TEST_TARGET_RE = __import__("re").compile(r"\b(?:tests?/|test_|_test\b|pytest|unittest)\b", __import__("re").IGNORECASE)
QUALITY_REFERENCE_RE = __import__("re").compile(r"\b(?:Q|COV|TC)[-\s]?0*(\d{1,})\b", __import__("re").IGNORECASE)
VAGUE_TERMS = (
    "appropriate",
    "easy",
    "efficient",
    "fast",
    "flexible",
    "intuitive",
    "performant",
    "reliable",
    "robust",
    "scalable",
    "seamless",
    "simple",
    "user-friendly",
)
TEXT_MAX_ISSUES_PER_FEATURE = 8
TEXT_MAX_RECOMMENDATIONS = 12


@dataclass(frozen=True)
class AnalysisIssue:
    id: str
    feature_id: str
    severity: str
    category: str
    code: str
    message: str
    source_file: str
    line: int | None = None
    evidence: dict[str, object] | None = None
    recommended_command: str | None = None

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "category": self.category,
            "code": self.code,
            "feature_id": self.feature_id,
            "id": self.id,
            "message": self.message,
            "severity": self.severity,
            "source_file": self.source_file,
        }
        if self.line is not None:
            payload["line"] = self.line
        if self.evidence:
            payload["evidence"] = dict(self.evidence)
        if self.recommended_command:
            payload["recommended_command"] = self.recommended_command
        return payload


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


@dataclass(frozen=True)
class _PendingIssue:
    feature_id: str
    severity: str
    category: str
    code: str
    message: str
    source_file: str
    line: int | None = None
    evidence: dict[str, object] | None = None
    recommended_command: str | None = None
