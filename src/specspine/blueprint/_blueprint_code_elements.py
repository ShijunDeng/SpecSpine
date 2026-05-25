from __future__ import annotations

from dataclasses import dataclass


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


__all__ = [
    "BlueprintFunction",
    "BlueprintModule",
]
