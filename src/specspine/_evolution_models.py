from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "EvolutionEntry",
]


@dataclass(frozen=True)
class EvolutionEntry:
    commit_hash: str
    date: str
    author: str
    message: str
    change_count: int
    categories: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "author": self.author,
            "categories": self.categories,
            "change_count": self.change_count,
            "commit_hash": self.commit_hash,
            "date": self.date,
            "message": self.message,
        }
