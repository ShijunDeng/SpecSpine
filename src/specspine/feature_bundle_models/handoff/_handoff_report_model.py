from __future__ import annotations

from dataclasses import dataclass

from ..metadata import FeatureMetadata
from ..ready import FeatureReadyCheck
from ..trace import FeatureTask, FeatureTraceChecklistItem, FeatureTraceTestPlanItem

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
