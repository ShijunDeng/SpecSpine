from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScaffoldTestMethod:
    method_name: str
    docstring: str
    ac_id: str
    ac_text: str
    body: str

    def as_dict(self) -> dict[str, str]:
        return {
            "ac_id": self.ac_id,
            "ac_text": self.ac_text,
            "body": self.body,
            "docstring": self.docstring,
            "method_name": self.method_name,
        }


__all__ = [
    "ScaffoldTestMethod",
]
