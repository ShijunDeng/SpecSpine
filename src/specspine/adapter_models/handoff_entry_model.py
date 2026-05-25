from __future__ import annotations

from dataclasses import dataclass

from .handoff_step_model import AdapterHandoffStep

__all__ = [
    "AdapterFeatureHandoffEntry",
]


@dataclass(frozen=True)
class AdapterFeatureHandoffEntry:
    key: str
    display_name: str
    enabled: bool
    config: str
    config_exists: bool
    upstream_url: str
    integration_surface: str
    native_status: str
    upstream_phase: str
    upstream_artifacts: tuple[str, ...]
    agent_focus: str
    local_commands: tuple[str, ...]
    recommended_upstream_steps: tuple[AdapterHandoffStep, ...]
    notes: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "agent_focus": self.agent_focus,
            "config": self.config,
            "config_exists": self.config_exists,
            "display_name": self.display_name,
            "enabled": self.enabled,
            "integration_surface": self.integration_surface,
            "key": self.key,
            "local_commands": list(self.local_commands),
            "native_status": self.native_status,
            "notes": list(self.notes),
            "recommended_upstream_steps": [
                step.as_dict() for step in self.recommended_upstream_steps
            ],
            "upstream_artifacts": list(self.upstream_artifacts),
            "upstream_phase": self.upstream_phase,
            "upstream_url": self.upstream_url,
        }
