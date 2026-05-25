from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "SUPPORTED_FORMATS",
    "SAFETY_NOTES",
    "PipelineJob",
    "MergeCondition",
    "PipelineResult",
]

SUPPORTED_FORMATS = ("github-actions", "gitlab-ci", "generic")


@dataclass(frozen=True)
class PipelineJob:
    name: str
    steps: tuple[str, ...]
    description: str = ""
    condition: str = ""

    def as_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "name": self.name,
            "steps": list(self.steps),
        }
        if self.description:
            result["description"] = self.description
        if self.condition:
            result["condition"] = self.condition
        return result


@dataclass(frozen=True)
class MergeCondition:
    id: str
    text: str
    required: bool = True

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "required": self.required,
            "text": self.text,
        }


@dataclass(frozen=True)
class PipelineResult:
    pipeline_type: str
    jobs: tuple[PipelineJob, ...]
    merge_conditions: tuple[MergeCondition, ...]
    safety_notes: tuple[str, ...]
    feature_slug: str | None = None
    raw_content: str = ""

    def as_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "jobs": [job.as_dict() for job in self.jobs],
            "merge_conditions": [
                mc.as_dict() for mc in self.merge_conditions
            ],
            "pipeline_type": self.pipeline_type,
            "safety_notes": list(self.safety_notes),
        }
        if self.feature_slug:
            result["feature_slug"] = self.feature_slug
        return result


SAFETY_NOTES = (
    "This pipeline is generated read-only: no network calls, no subprocess execution, no token reads.",
    "Acceptance criteria from spec bundles become test gates in the pipeline.",
    "Quality metrics from quality/checklist.md become merge requirements.",
    "Feature readiness gates become deployment conditions when --feature is specified.",
    "Review generated pipeline before committing to CI system.",
)
