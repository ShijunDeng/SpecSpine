from __future__ import annotations

from dataclasses import dataclass

from ..metadata import FeatureMetadata
from ..ready import FeatureReadyCheck
from ..trace import FeatureTask, FeatureTraceChecklistItem, FeatureTraceTestPlanItem
from .drafts import FeatureTaskIssueDraft

__all__ = [
    "FeatureTaskIssuesReport",
    "FeatureHandoffReport",
]


@dataclass(frozen=True)
class FeatureTaskIssuesReport:
    feature_id: str
    status: str
    source_file: str
    source_missing: bool
    missing_files: tuple[str, ...]
    issues: tuple[FeatureTaskIssueDraft, ...]
    task_summary: dict[str, int]
    recommended_commands: tuple[str, ...]

    @property
    def summary(self) -> dict[str, int]:
        return {
            "done": self.task_summary["done"],
            "issue_total": len(self.issues),
            "open": self.task_summary["open"],
            "total": self.task_summary["total"],
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "feature_id": self.feature_id,
            "issues": [issue.as_dict() for issue in self.issues],
            "missing_files": list(self.missing_files),
            "recommended_commands": list(self.recommended_commands),
            "source_file": self.source_file,
            "source_missing": self.source_missing,
            "status": self.status,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class FeatureHandoffReport:
    feature_id: str
    status: str
    ready: bool
    sources: dict[str, dict[str, object]]
    missing_files: tuple[str, ...]
    gaps: tuple[dict[str, str], ...]
    blocking_checks: tuple[FeatureReadyCheck, ...]
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...]
    tasks: tuple[FeatureTask, ...]
    quality_checks: tuple[FeatureTraceChecklistItem, ...]
    test_plan: tuple[FeatureTraceTestPlanItem, ...]
    release_readiness: tuple[FeatureTraceChecklistItem, ...]
    trace_summary: dict[str, object]
    ready_summary: dict[str, int]
    task_summary: dict[str, int]
    recommended_commands: tuple[str, ...]
    next_actions: tuple[str, ...]
    has_native_files: bool
    metadata: FeatureMetadata

    @property
    def summary(self) -> dict[str, object]:
        return {
            "blocking_checks": {"total": len(self.blocking_checks)},
            "gaps": {"total": len(self.gaps)},
            "ready": dict(self.ready_summary),
            "tasks": dict(self.task_summary),
            "trace": dict(self.trace_summary),
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "acceptance_criteria": [
                item.as_dict() for item in self.acceptance_criteria
            ],
            "blocking_checks": [
                check.as_dict() for check in self.blocking_checks
            ],
            "feature_id": self.feature_id,
            "gaps": [dict(gap) for gap in self.gaps],
            "missing_files": list(self.missing_files),
            "metadata": self.metadata.as_dict(),
            "next_actions": list(self.next_actions),
            "quality_checks": [item.as_dict() for item in self.quality_checks],
            "ready": self.ready,
            "recommended_commands": list(self.recommended_commands),
            "release_readiness": [
                item.as_dict() for item in self.release_readiness
            ],
            "sources": self.sources,
            "status": self.status,
            "summary": self.summary,
            "tasks": [task.as_dict() for task in self.tasks],
            "test_plan": [item.as_dict() for item in self.test_plan],
        }
