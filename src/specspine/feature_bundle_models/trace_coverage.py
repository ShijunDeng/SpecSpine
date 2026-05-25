from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "FeatureAcceptanceTestCase",
    "FeatureTestCoverageLink",
]


@dataclass(frozen=True)
class FeatureAcceptanceTestCase:
    id: str
    acceptance_criterion_id: str
    acceptance_criterion_text: str
    source_file: str
    line: int
    behavior: str
    status: str = "pending"
    coverage: tuple["FeatureTestCoverageLink", ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "acceptance_criterion_id": self.acceptance_criterion_id,
            "acceptance_criterion_text": self.acceptance_criterion_text,
            "behavior": self.behavior,
            "coverage": [link.as_dict() for link in self.coverage],
            "id": self.id,
            "line": self.line,
            "source_file": self.source_file,
            "status": self.status,
        }


@dataclass(frozen=True)
class FeatureTestCoverageLink:
    id: str
    acceptance_criterion_id: str
    target: str
    target_path: str
    target_exists: bool
    done: bool
    text: str
    source_file: str
    line: int

    def as_dict(self) -> dict[str, object]:
        return {
            "acceptance_criterion_id": self.acceptance_criterion_id,
            "done": self.done,
            "id": self.id,
            "line": self.line,
            "source_file": self.source_file,
            "target": self.target,
            "target_exists": self.target_exists,
            "target_path": self.target_path,
            "text": self.text,
        }
