from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BlueprintFunction:
    name: str
    parameters: tuple[str, ...]
    return_type: str
    description: str
    ac_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "ac_ids": list(self.ac_ids),
            "description": self.description,
            "name": self.name,
            "parameters": list(self.parameters),
            "return_type": self.return_type,
        }


@dataclass(frozen=True)
class BlueprintModule:
    module_path: str
    responsibility: str
    functions: tuple[BlueprintFunction, ...]
    ac_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "ac_ids": list(self.ac_ids),
            "functions": [fn.as_dict() for fn in self.functions],
            "module_path": self.module_path,
            "responsibility": self.responsibility,
        }


@dataclass(frozen=True)
class BlueprintDataEntity:
    name: str
    attributes: tuple[str, ...]
    description: str
    ac_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "ac_ids": list(self.ac_ids),
            "attributes": list(self.attributes),
            "description": self.description,
            "name": self.name,
        }


@dataclass(frozen=True)
class BlueprintErrorPath:
    condition: str
    exception_type: str
    handling: str
    ac_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "ac_ids": list(self.ac_ids),
            "condition": self.condition,
            "exception_type": self.exception_type,
            "handling": self.handling,
        }


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
    "BlueprintDataEntity",
    "BlueprintErrorPath",
    "BlueprintFunction",
    "BlueprintModule",
    "BlueprintReport",
]
