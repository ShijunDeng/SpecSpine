from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "FeatureStatusReport",
]


@dataclass(frozen=True)
class FeatureStatusReport:
    feature_id: str
    status: str | None
    consistent: bool
    files: dict[str, dict[str, object]]
    missing_files: tuple[str, ...]
    updated_files: tuple[str, ...] = ()
    transition: dict[str, object] | None = None

    def as_dict(self, *, include_updated: bool = False) -> dict[str, object]:
        payload: dict[str, object] = {
            "consistent": self.consistent,
            "feature_id": self.feature_id,
            "files": self.files,
            "missing_files": list(self.missing_files),
            "status": self.status,
        }
        if include_updated:
            payload["updated_files"] = list(self.updated_files)
        if self.transition is not None:
            payload["transition"] = dict(self.transition)
        return payload
