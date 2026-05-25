from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "AnalysisIssue",
    "_PendingIssue",
]


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
