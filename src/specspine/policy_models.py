from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .features import FEATURE_PRIORITIES, FEATURE_STATUSES, FeatureMetadata

POLICY_RELATIVE_PATH = ".specspine/policy.yaml"


@dataclass(frozen=True)
class ReadinessCoveragePolicy:
    enabled: bool = False
    default: bool = False
    priorities: tuple[str, ...] = ()
    statuses: tuple[str, ...] = ()
    feature_ids: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def requires_coverage(
        self,
        *,
        feature_id: str,
        metadata: FeatureMetadata,
        status: str,
    ) -> bool:
        if not self.enabled:
            return False
        return (
            self.default
            or feature_id in self.feature_ids
            or metadata.priority in self.priorities
            or status in self.statuses
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "default": self.default,
            "enabled": self.enabled,
            "feature_ids": list(self.feature_ids),
            "priorities": list(self.priorities),
            "statuses": list(self.statuses),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class WorkspacePolicy:
    root: Path
    source_file: Path
    source_missing: bool
    require_coverage: ReadinessCoveragePolicy

    @property
    def summary(self) -> dict[str, int]:
        return {
            "coverage_rule_count": (
                len(self.require_coverage.feature_ids)
                + len(self.require_coverage.priorities)
                + len(self.require_coverage.statuses)
                + (1 if self.require_coverage.default else 0)
            ),
            "feature_ids": len(self.require_coverage.feature_ids),
            "priorities": len(self.require_coverage.priorities),
            "statuses": len(self.require_coverage.statuses),
            "warning_count": len(self.require_coverage.warnings),
            "warnings": len(self.require_coverage.warnings),
        }

    @property
    def recommended_commands(self) -> tuple[str, ...]:
        return (
            f"specspine policy {self.root} --json",
            "specspine status . --json --feature-summaries --feature-policy",
            "specspine feature ready <slug> . --json --policy",
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "readiness": {
                "require_coverage": self.require_coverage.as_dict(),
            },
            "recommended_commands": list(self.recommended_commands),
            "root": str(self.root),
            "source_file": str(self.source_file),
            "source_missing": self.source_missing,
            "summary": dict(self.summary),
        }


__all__ = [
    "POLICY_RELATIVE_PATH",
    "ReadinessCoveragePolicy",
    "WorkspacePolicy",
]
