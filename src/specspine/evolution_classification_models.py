from __future__ import annotations

import re
from dataclasses import dataclass

AC_ID_RE = re.compile(r"(AC\d{3})")
TASK_ID_RE = re.compile(r"(T\d{3})")

__all__ = [
    "AC_ID_RE",
    "TASK_ID_RE",
    "ClassifiedChange",
    "ClassificationResult",
]


@dataclass(frozen=True)
class ClassifiedChange:
    change_id: str
    change_type: str
    category: str
    file: str
    line: int
    before: str | None
    after: str | None

    def as_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "category": self.category,
            "change_id": self.change_id,
            "change_type": self.change_type,
            "file": self.file,
            "line": self.line,
        }
        if self.before is not None:
            result["before"] = self.before
        if self.after is not None:
            result["after"] = self.after
        return result


@dataclass(frozen=True)
class ClassificationResult:
    slug: str
    changes: list[ClassifiedChange]

    @property
    def summary(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for change in self.changes:
            key = f"{change.category}_{change.change_type}"
            counts[key] = counts.get(key, 0) + 1
        return counts

    def as_dict(self) -> dict[str, object]:
        return {
            "changes": [c.as_dict() for c in self.changes],
            "slug": self.slug,
            "summary": self.summary,
        }
