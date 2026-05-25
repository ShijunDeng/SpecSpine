from __future__ import annotations

from dataclasses import dataclass

from ..metadata import FeatureMetadata
from ..ready import FeatureReadyCheck
from ..trace import FeatureTask, FeatureTraceChecklistItem, FeatureTraceTestPlanItem
from ._handoff_serializers import serialize_gaps, serialize_items

__all__ = [
    "FeatureHandoffReport",
]


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
            "acceptance_criteria": serialize_items(self.acceptance_criteria),
            "blocking_checks": serialize_items(self.blocking_checks),
            "feature_id": self.feature_id,
            "gaps": serialize_gaps(self.gaps),
            "missing_files": list(self.missing_files),
            "metadata": self.metadata.as_dict(),
            "next_actions": list(self.next_actions),
            "quality_checks": serialize_items(self.quality_checks),
            "ready": self.ready,
            "recommended_commands": list(self.recommended_commands),
            "release_readiness": serialize_items(self.release_readiness),
            "sources": self.sources,
            "status": self.status,
            "summary": self.summary,
            "tasks": serialize_items(self.tasks),
            "test_plan": serialize_items(self.test_plan),
        }
