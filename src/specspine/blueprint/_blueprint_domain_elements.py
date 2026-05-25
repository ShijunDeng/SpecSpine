from __future__ import annotations

from dataclasses import dataclass


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


__all__ = [
    "BlueprintDataEntity",
    "BlueprintErrorPath",
]
