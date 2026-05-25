from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "PipelineJob",
]


@dataclass(frozen=True)
class PipelineJob:
    name: str
    steps: tuple[str, ...]
    description: str = ""
    condition: str = ""

    def as_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "name": self.name,
            "steps": list(self.steps),
        }
        if self.description:
            result["description"] = self.description
        if self.condition:
            result["condition"] = self.condition
        return result
