from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

__all__ = [
    "ValidationCheck",
    "AdapterProbe",
]


@dataclass(frozen=True)
class ValidationCheck:
    id: str
    status: str
    message: str
    severity: str

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "message": self.message,
            "severity": self.severity,
            "status": self.status,
        }


AdapterProbe = Callable[[Iterable[str]], list["AdapterStatus"]]
