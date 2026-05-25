from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "FeatureTaskIssueDraft",
]


@dataclass(frozen=True)
class FeatureTaskIssueDraft:
    title: str
    body: str
    feature_id: str
    task_id: str
    task_text: str
    task_done: bool
    source_file: str
    line: int

    def as_dict(self) -> dict[str, object]:
        return {
            "body": self.body,
            "feature_id": self.feature_id,
            "line": self.line,
            "source_file": self.source_file,
            "task_done": self.task_done,
            "task_id": self.task_id,
            "task_text": self.task_text,
            "title": self.title,
        }
