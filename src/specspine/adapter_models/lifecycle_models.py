from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "AdapterLifecycleMapping",
    "AdapterLifecycleAdapter",
    "AdapterLifecycleReport",
]


@dataclass(frozen=True)
class AdapterLifecycleMapping:
    id: str
    status: str
    specspine_meaning: str
    upstream_phase: str
    upstream_artifacts: tuple[str, ...]
    agent_focus: str
    local_commands: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "agent_focus": self.agent_focus,
            "id": self.id,
            "local_commands": list(self.local_commands),
            "specspine_meaning": self.specspine_meaning,
            "status": self.status,
            "upstream_artifacts": list(self.upstream_artifacts),
            "upstream_phase": self.upstream_phase,
        }


@dataclass(frozen=True)
class AdapterLifecycleAdapter:
    key: str
    display_name: str
    enabled: bool
    config: str
    config_exists: bool
    upstream_url: str
    mappings: tuple[AdapterLifecycleMapping, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "config": self.config,
            "config_exists": self.config_exists,
            "display_name": self.display_name,
            "enabled": self.enabled,
            "mappings": [mapping.as_dict() for mapping in self.mappings],
            "upstream_url": self.upstream_url,
        }


@dataclass(frozen=True)
class AdapterLifecycleReport:
    root: Path
    native_statuses: tuple[str, ...]
    adapters: dict[str, AdapterLifecycleAdapter]
    recommended_commands: tuple[str, ...]

    @property
    def summary(self) -> dict[str, int]:
        return {
            "adapters_total": len(self.adapters),
            "enabled_adapters": sum(1 for adapter in self.adapters.values() if adapter.enabled),
            "mappings_total": sum(len(adapter.mappings) for adapter in self.adapters.values()),
            "statuses_total": len(self.native_statuses),
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "adapters": {
                key: adapter.as_dict()
                for key, adapter in self.adapters.items()
            },
            "native_statuses": list(self.native_statuses),
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "summary": self.summary,
        }
