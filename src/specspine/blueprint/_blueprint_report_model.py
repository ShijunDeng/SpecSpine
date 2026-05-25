from __future__ import annotations

from dataclasses import dataclass

from ._blueprint_code_elements import BlueprintFunction, BlueprintModule
from ._blueprint_domain_elements import BlueprintDataEntity, BlueprintErrorPath


@dataclass(frozen=True)
class BlueprintReport:
    feature_id: str
    modules: tuple[BlueprintModule, ...]
    functions: tuple[BlueprintFunction, ...]
    data_entities: tuple[BlueprintDataEntity, ...]
    error_paths: tuple[BlueprintErrorPath, ...]
    coverage_summary: dict[str, object]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "coverage_summary": self.coverage_summary,
            "data_entities": [e.as_dict() for e in self.data_entities],
            "error_paths": [p.as_dict() for p in self.error_paths],
            "feature_id": self.feature_id,
            "functions": [f.as_dict() for f in self.functions],
            "modules": [m.as_dict() for m in self.modules],
            "safety_notes": list(self.safety_notes),
        }


__all__ = [
    "BlueprintReport",
]
