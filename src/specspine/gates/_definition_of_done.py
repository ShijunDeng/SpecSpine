from __future__ import annotations

__all__ = [
    "DefinitionOfDoneItem",
]

from dataclasses import dataclass


@dataclass(frozen=True)
class DefinitionOfDoneItem:
    id: str
    text: str
    source_file: str
    line: int

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "line": self.line,
            "source_file": self.source_file,
            "text": self.text,
        }
