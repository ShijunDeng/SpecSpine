from __future__ import annotations

from dataclasses import dataclass

from .metadata import FeatureMetadata

__all__ = [
    "IssueDraft",
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
