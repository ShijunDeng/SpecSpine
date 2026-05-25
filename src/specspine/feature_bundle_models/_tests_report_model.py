from __future__ import annotations

from dataclasses import dataclass

from .metadata import FeatureMetadata
from .ready import FeatureReadyCheck
from .trace import (
    FeatureAcceptanceTestCase,
    FeatureTestCoverageLink,
    FeatureTraceChecklistItem,
    FeatureTraceTestPlanItem,
)

__all__ = [
    "FeatureTestsReport",
]


@dataclass(frozen=True)
class FeatureTestsReport:
    feature_id: str
    status: str
    ready: bool
    source_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    gaps: tuple[dict[str, str], ...]
    blocking_checks: tuple[FeatureReadyCheck, ...]
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...]
    test_plan: tuple[FeatureTraceTestPlanItem, ...]
    test_cases: tuple[FeatureAcceptanceTestCase, ...]
    quality_checks: tuple[FeatureTraceChecklistItem, ...]
    ready_summary: dict[str, int]
    recommended_commands: tuple[str, ...]
    has_native_files: bool
    metadata: FeatureMetadata
    test_coverage: tuple[FeatureTestCoverageLink, ...] = ()
