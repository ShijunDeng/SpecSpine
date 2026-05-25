from __future__ import annotations

from pathlib import Path
from typing import Any

from .cicd_jobs import _build_core_jobs, _build_merge_conditions, _validate_workspace
from .cicd_models import SAFETY_NOTES, SUPPORTED_FORMATS
from .cicd_format_generators import (
    _generate_github_actions_yaml,
    _generate_gitlab_ci_yaml,
    _generate_generic_shell,
)

__all__ = [
    "generate_github_actions",
    "generate_gitlab_ci",
    "generate_generic",
    "generate_pipeline",
]

_GENERATORS = {
    "github-actions": _generate_github_actions_yaml,
    "gitlab-ci": _generate_gitlab_ci_yaml,
    "generic": _generate_generic_shell,
}


def generate_github_actions(
    root: Path,
    feature_slug: str | None = None,
) -> str:
    jobs = _build_core_jobs(feature_slug)
    return _generate_github_actions_yaml(jobs, feature_slug)


def generate_gitlab_ci(
    root: Path,
    feature_slug: str | None = None,
) -> str:
    jobs = _build_core_jobs(feature_slug)
    return _generate_gitlab_ci_yaml(jobs, feature_slug)


def generate_generic(
    root: Path,
    feature_slug: str | None = None,
) -> str:
    jobs = _build_core_jobs(feature_slug)
    return _generate_generic_shell(jobs, feature_slug)


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
