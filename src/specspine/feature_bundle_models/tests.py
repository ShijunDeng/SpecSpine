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

    @property
    def summary(self) -> dict[str, object]:
        def checklist_counts(
            items: tuple[FeatureTraceChecklistItem, ...],
        ) -> dict[str, int]:
            done = sum(1 for item in items if item.done)
            total = len(items)
            return {
                "done": done,
                "open": total - done,
                "total": total,
            }

        return {
            "acceptance_criteria": checklist_counts(self.acceptance_criteria),
            "blocking_checks": {"total": len(self.blocking_checks)},
            "gaps": {"total": len(self.gaps)},
            "missing_files": {"total": len(self.missing_files)},
            "quality_checks": checklist_counts(self.quality_checks),
            "ready": dict(self.ready_summary),
            "source_files": {"total": len(self.source_files)},
            "test_cases": {"total": len(self.test_cases)},
            "test_coverage": checklist_counts(self.test_coverage),
            "test_plan": {"total": len(self.test_plan)},
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
            "quality_checks": [item.as_dict() for item in self.quality_checks],
            "ready": self.ready,
            "recommended_commands": list(self.recommended_commands),
            "source_files": list(self.source_files),
            "status": self.status,
            "summary": self.summary,
            "test_cases": [test_case.as_dict() for test_case in self.test_cases],
            "test_coverage": [link.as_dict() for link in self.test_coverage],
            "test_plan": [item.as_dict() for item in self.test_plan],
        }
