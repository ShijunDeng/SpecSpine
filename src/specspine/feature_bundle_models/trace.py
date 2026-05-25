from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "FeatureTask",
    "FeatureTraceChecklistItem",
    "FeatureTraceTestPlanItem",
    "FeatureAcceptanceTestCase",
    "FeatureTestCoverageLink",
    "FeatureTraceReport",
]


@dataclass(frozen=True)
class FeatureTask:
    id: str
    text: str
    done: bool
    source_file: str
    line: int

    def as_dict(self) -> dict[str, object]:
        return {
            "done": self.done,
            "id": self.id,
            "line": self.line,
            "source_file": self.source_file,
            "text": self.text,
        }


@dataclass(frozen=True)
class FeatureTraceChecklistItem:
    id: str
    text: str
    done: bool
    source_file: str
    line: int

    def as_dict(self) -> dict[str, object]:
        return {
            "done": self.done,
            "id": self.id,
            "line": self.line,
            "source_file": self.source_file,
            "text": self.text,
        }


@dataclass(frozen=True)
class FeatureTraceTestPlanItem:
    id: str
    text: str
    source_file: str
    line: int

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "line": self.line,
            "source_file": self.source_file,
            "text": self.text,
        }


@dataclass(frozen=True)
class FeatureAcceptanceTestCase:
    id: str
    acceptance_criterion_id: str
    acceptance_criterion_text: str
    source_file: str
    line: int
    behavior: str
    status: str = "pending"
    coverage: tuple["FeatureTestCoverageLink", ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "acceptance_criterion_id": self.acceptance_criterion_id,
            "acceptance_criterion_text": self.acceptance_criterion_text,
            "behavior": self.behavior,
            "coverage": [link.as_dict() for link in self.coverage],
            "id": self.id,
            "line": self.line,
            "source_file": self.source_file,
            "status": self.status,
        }


@dataclass(frozen=True)
class FeatureTestCoverageLink:
    id: str
    acceptance_criterion_id: str
    target: str
    target_path: str
    target_exists: bool
    done: bool
    text: str
    source_file: str
    line: int

    def as_dict(self) -> dict[str, object]:
        return {
            "acceptance_criterion_id": self.acceptance_criterion_id,
            "done": self.done,
            "id": self.id,
            "line": self.line,
            "source_file": self.source_file,
            "target": self.target,
            "target_exists": self.target_exists,
            "target_path": self.target_path,
            "text": self.text,
        }


@dataclass(frozen=True)
class FeatureTraceReport:
    feature_id: str
    status: str
    sources: dict[str, dict[str, object]]
    missing_files: tuple[str, ...]
    acceptance_criteria: tuple[FeatureTraceChecklistItem, ...]
    tasks: tuple[FeatureTask, ...]
    quality_checks: tuple[FeatureTraceChecklistItem, ...]
    test_plan: tuple[FeatureTraceTestPlanItem, ...]
    gaps: tuple[dict[str, str], ...]

    @property
    def summary(self) -> dict[str, object]:
        def checklist_counts(
            items: tuple[FeatureTraceChecklistItem, ...] | tuple[FeatureTask, ...],
        ) -> dict[str, int]:
            done = sum(1 for item in items if item.done)
            total = len(items)
            return {
                "done": done,
                "open": total - done,
                "total": total,
            }

        acceptance_criteria = checklist_counts(self.acceptance_criteria)
        tasks = checklist_counts(self.tasks)
        quality_checks = checklist_counts(self.quality_checks)
        total = (
            acceptance_criteria["total"]
            + tasks["total"]
            + quality_checks["total"]
        )
        done = (
            acceptance_criteria["done"]
            + tasks["done"]
            + quality_checks["done"]
        )

        return {
            "acceptance_criteria": acceptance_criteria,
            "done": done,
            "open": total - done,
            "quality_checks": quality_checks,
            "tasks": tasks,
            "test_plan": {"total": len(self.test_plan)},
            "total": total,
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "acceptance_criteria": [
                item.as_dict() for item in self.acceptance_criteria
            ],
            "feature_id": self.feature_id,
            "gaps": [dict(gap) for gap in self.gaps],
            "missing_files": list(self.missing_files),
            "quality_checks": [item.as_dict() for item in self.quality_checks],
            "sources": self.sources,
            "status": self.status,
            "summary": self.summary,
            "tasks": [task.as_dict() for task in self.tasks],
            "test_plan": [item.as_dict() for item in self.test_plan],
        }
