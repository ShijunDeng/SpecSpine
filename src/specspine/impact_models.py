from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

DISCOVERY_COMMAND = "PYTHONPATH=src python3 -m unittest discover -s tests"


@dataclass(frozen=True)
class TestImpactReport:
    root: Path
    changed_files: tuple[str, ...]
    source_modules: tuple[dict[str, Any], ...]
    test_files: tuple[dict[str, Any], ...]
    recommendations: tuple[dict[str, Any], ...]
    recommended_commands: tuple[str, ...]
    summary: dict[str, Any]
    safety_notes: tuple[str, ...]
    feature: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "changed_files": list(self.changed_files),
            "recommended_commands": list(self.recommended_commands),
            "recommendations": [dict(recommendation) for recommendation in self.recommendations],
            "root": str(self.root),
            "safety_notes": list(self.safety_notes),
            "source_modules": [dict(module) for module in self.source_modules],
            "summary": dict(self.summary),
            "test_files": [dict(test_file) for test_file in self.test_files],
        }
        if self.feature is not None:
            payload["feature"] = dict(self.feature)
        return payload


__all__ = [
    "DISCOVERY_COMMAND",
    "TestImpactReport",
]
