from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "AdapterHandoffStep",
]


@dataclass(frozen=True)
class AdapterHandoffStep:
    id: str
    kind: str
    description: str
    argv: tuple[str, ...] = ()
    instruction: str = ""
    creates_remote: bool = False
    requires_network: bool = False
    requires_token: bool = False
    safe_to_auto_run: bool = False
    executed: bool = False

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "creates_remote": self.creates_remote,
            "description": self.description,
            "executed": self.executed,
            "id": self.id,
            "kind": self.kind,
            "requires_network": self.requires_network,
            "requires_token": self.requires_token,
            "safe_to_auto_run": self.safe_to_auto_run,
        }
        if self.argv:
            payload["argv"] = list(self.argv)
        if self.instruction:
            payload["instruction"] = self.instruction
        return payload
