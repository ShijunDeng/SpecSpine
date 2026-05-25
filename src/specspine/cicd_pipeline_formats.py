from __future__ import annotations

from pathlib import Path

from .cicd_format_generators import (
    _generate_github_actions_yaml,
    _generate_gitlab_ci_yaml,
    _generate_generic_shell,
)
from .cicd_jobs import _build_core_jobs

__all__ = [
    "generate_github_actions",
    "generate_gitlab_ci",
    "generate_generic",
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
