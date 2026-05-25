from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._policy_readiness import ReadinessCoveragePolicy

__all__ = [
    "WorkspacePolicy",
]


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
