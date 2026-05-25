from __future__ import annotations

from dataclasses import dataclass

from .cicd_job_model import PipelineJob

__all__ = [
    "MergeCondition",
    "PipelineResult",
]


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
