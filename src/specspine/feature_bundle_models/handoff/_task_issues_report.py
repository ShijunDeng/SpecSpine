from __future__ import annotations

from dataclasses import dataclass

from .drafts import FeatureTaskIssueDraft

__all__ = [
    "FeatureTaskIssuesReport",
]


@dataclass(frozen=True)
class FeatureTaskIssuesReport:
    feature_id: str
    status: str
    source_file: str
    source_missing: bool
    missing_files: tuple[str, ...]
    issues: tuple[FeatureTaskIssueDraft, ...]
    task_summary: dict[str, int]
    recommended_commands: tuple[str, ...]

    @property
    def summary(self) -> dict[str, int]:
        return {
            "done": self.task_summary["done"],
            "issue_total": len(self.issues),
            "open": self.task_summary["open"],
            "total": self.task_summary["total"],
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "feature_id": self.feature_id,
            "issues": [issue.as_dict() for issue in self.issues],
            "missing_files": list(self.missing_files),
            "recommended_commands": list(self.recommended_commands),
            "source_file": self.source_file,
            "source_missing": self.source_missing,
            "status": self.status,
            "summary": self.summary,
        }
