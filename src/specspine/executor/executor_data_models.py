from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "ExecutionLoopResult",
    "ExecutionPlan",
    "GradingRubric",
]


@dataclass(frozen=True)
class ExecutionPlan:
    root: str
    feature_id: str
    feature_status: str
    plan_steps: list[dict[str, Any]]
    dependency_order: list[str]
    verification_commands: list[str]
    grading_rubric: dict[str, Any]
    summary: dict[str, Any]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "dependency_order": list(self.dependency_order),
            "feature_id": self.feature_id,
            "feature_status": self.feature_status,
            "grading_rubric": dict(self.grading_rubric),
            "plan_steps": [dict(s) for s in self.plan_steps],
            "root": self.root,
            "safety_notes": list(self.safety_notes),
            "summary": dict(self.summary),
            "verification_commands": list(self.verification_commands),
        }


@dataclass(frozen=True)
class GradingRubric:
    feature_id: str
    rubric_items: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "rubric_items": [dict(item) for item in self.rubric_items],
        }


@dataclass(frozen=True)
class ExecutionLoopResult:
    feature_id: str
    iterations: list[dict[str, Any]]
    final_status: str
    remaining_gaps: list[dict[str, str]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "final_status": self.final_status,
            "iterations": [dict(it) for it in self.iterations],
            "remaining_gaps": [dict(g) for g in self.remaining_gaps],
        }
