from __future__ import annotations

from dataclasses import dataclass

from .metadata import FeatureMetadata

__all__ = [
    "IssueDraft",
    "PullRequestDraft",
]


@dataclass(frozen=True)
class IssueDraft:
    title: str
    body: str
    feature_id: str
    source_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    status: str
    metadata: FeatureMetadata

    def as_dict(self) -> dict[str, object]:
        return {
            "body": self.body,
            "feature_id": self.feature_id,
            "metadata": self.metadata.as_dict(),
            "missing_files": list(self.missing_files),
            "source_files": list(self.source_files),
            "status": self.status,
            "title": self.title,
        }


@dataclass(frozen=True)
class PullRequestDraft:
    title: str
    body: str
    feature_id: str
    status: str
    ready: bool
    source_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    gaps: tuple[dict[str, str], ...]
    blocking_checks: tuple["FeatureReadyCheck", ...]
    summary: dict[str, object]
    recommended_commands: tuple[str, ...]
    metadata: FeatureMetadata

    def as_dict(self) -> dict[str, object]:
        return {
            "blocking_checks": [
                check.as_dict() for check in self.blocking_checks
            ],
            "body": self.body,
            "feature_id": self.feature_id,
            "gaps": [dict(gap) for gap in self.gaps],
            "metadata": self.metadata.as_dict(),
            "missing_files": list(self.missing_files),
            "ready": self.ready,
            "recommended_commands": list(self.recommended_commands),
            "source_files": list(self.source_files),
            "status": self.status,
            "summary": self.summary,
            "title": self.title,
        }
