from __future__ import annotations

from dataclasses import dataclass

from .metadata import FeatureMetadata
from ._sync_plan_commands import FeatureSyncPlanCommand

__all__ = [
    "FeatureSyncPlan",
]


@dataclass(frozen=True)
class FeatureSyncPlan:
    feature_id: str
    status: str
    ready: bool
    source_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    gaps: tuple[dict[str, str], ...]
    blocking_checks: tuple["FeatureReadyCheck", ...]
    metadata: FeatureMetadata
    commands: tuple[FeatureSyncPlanCommand, ...]
    notes: tuple[str, ...]
    recommended_commands: tuple[str, ...]

    @property
    def summary(self) -> dict[str, int]:
        issue_commands = sum(1 for command in self.commands if command.kind == "issue")
        task_issue_commands = sum(
            1 for command in self.commands if command.kind == "task-issue"
        )
        pull_request_commands = sum(
            1 for command in self.commands if command.kind == "pull-request"
        )
        return {
            "commands_total": len(self.commands),
            "issue_commands": issue_commands,
            "notes_total": len(self.notes),
            "pull_request_commands": pull_request_commands,
            "task_issue_commands": task_issue_commands,
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "blocking_checks": [
                check.as_dict() for check in self.blocking_checks
            ],
            "commands": [command.as_dict() for command in self.commands],
            "feature_id": self.feature_id,
            "gaps": [dict(gap) for gap in self.gaps],
            "metadata": self.metadata.as_dict(),
            "missing_files": list(self.missing_files),
            "notes": list(self.notes),
            "ready": self.ready,
            "recommended_commands": list(self.recommended_commands),
            "source_files": list(self.source_files),
            "status": self.status,
            "summary": self.summary,
        }
