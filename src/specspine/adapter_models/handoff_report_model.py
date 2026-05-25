from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .handoff_entry_model import AdapterFeatureHandoffEntry

__all__ = [
    "AdapterFeatureHandoffReport",
]


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
