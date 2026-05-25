from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "FeatureSyncPlanCommand",
]


@dataclass(frozen=True)
class FeatureSyncPlanCommand:
    id: str
    kind: str
    description: str
    argv: tuple[str, ...]
    body_source: str
    body: str
    creates_remote: bool = True
    requires_token: bool = True
    requires_network: bool = True
    safe_to_auto_run: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "argv": list(self.argv),
            "body": self.body,
            "body_source": self.body_source,
            "creates_remote": self.creates_remote,
            "description": self.description,
            "id": self.id,
            "kind": self.kind,
            "requires_network": self.requires_network,
            "requires_token": self.requires_token,
            "safe_to_auto_run": self.safe_to_auto_run,
        }
