from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .handoff_constants import ADAPTER_HANDOFF_SAFETY_FLAGS

__all__ = [
    "AdapterHandoffStep",
    "AdapterFeatureHandoffEntry",
    "AdapterFeatureHandoffReport",
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


@dataclass(frozen=True)
class AdapterFeatureHandoffReport:
    root: Path
    feature_id: str
    status: str
    ready: bool
    sources: dict[str, dict[str, object]]
    source_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    gaps: tuple[dict[str, str], ...]
    blocking_checks: tuple[Any, ...]
    feature_summary: dict[str, object]
    adapters: dict[str, AdapterFeatureHandoffEntry]
    recommended_commands: tuple[str, ...]

    @property
    def summary(self) -> dict[str, object]:
        steps_total = sum(
            len(adapter.recommended_upstream_steps)
            for adapter in self.adapters.values()
        )
        return {
            "adapters": {
                "config_exists": sum(
                    1 for adapter in self.adapters.values() if adapter.config_exists
                ),
                "enabled": sum(
                    1 for adapter in self.adapters.values() if adapter.enabled
                ),
                "total": len(self.adapters),
            },
            "blocking_checks": {"total": len(self.blocking_checks)},
            "feature": dict(self.feature_summary),
            "gaps": {"total": len(self.gaps)},
            "steps": {"total": steps_total},
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "adapters": {
                key: adapter.as_dict()
                for key, adapter in self.adapters.items()
            },
            "blocking_checks": [
                check.as_dict() if hasattr(check, "as_dict") else dict(check)
                for check in self.blocking_checks
            ],
            "feature_id": self.feature_id,
            "gaps": [dict(gap) for gap in self.gaps],
            "missing_files": list(self.missing_files),
            "ready": self.ready,
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "source_files": list(self.source_files),
            "sources": self.sources,
            "status": self.status,
            "summary": self.summary,
        }
