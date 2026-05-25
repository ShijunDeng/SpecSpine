from __future__ import annotations

from pathlib import Path
from typing import Any

from .cicd_jobs import _build_core_jobs, _build_merge_conditions, _validate_workspace
from .cicd_models import SAFETY_NOTES, SUPPORTED_FORMATS
from .cicd_pipeline_formats import _GENERATORS

__all__ = [
    "generate_pipeline",
]


def generate_pipeline(
    root: Path,
    format: str = "github-actions",
    feature_slug: str | None = None,
) -> dict[str, Any]:
    if format not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported pipeline format: {format}. "
            f"Supported formats: {', '.join(SUPPORTED_FORMATS)}."
        )

    resolved_root = root.expanduser().resolve()
    valid, missing = _validate_workspace(resolved_root)
    if not valid:
        raise FileNotFoundError(
            f"No SpecSpine workspace found at {resolved_root}. "
            f"Missing: {', '.join(missing)}"
        )

    generator = _GENERATORS[format]
    raw_content = generator(jobs=_build_core_jobs(feature_slug), feature_slug=feature_slug)

    jobs = _build_core_jobs(feature_slug)
    merge_conditions = _build_merge_conditions(feature_slug)

    return {
        "pipeline_type": format,
        "jobs": tuple(jobs),
        "merge_conditions": tuple(merge_conditions),
        "safety_notes": SAFETY_NOTES,
        "feature_slug": feature_slug,
        "raw_content": raw_content,
    }
