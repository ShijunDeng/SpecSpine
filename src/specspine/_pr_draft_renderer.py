from __future__ import annotations

from .feature_drafts_render import (
    _pull_request_title,
    _recommended_pr_commands,
    _render_pull_request_body,
)

__all__ = [
    "render_draft_title",
    "render_draft_body",
    "render_draft_commands",
]


def render_draft_title(base_title: str) -> str:
    return _pull_request_title(base_title)


def render_draft_body(
    feature_id: str,
    status: str,
    ready: bool,
    summary: dict,
    why: str,
    acceptance_criteria: list,
    tasks: list,
    test_plan: list,
    release_readiness: dict,
    readiness_checks: list,
    source_files: tuple,
    missing_files: tuple,
    gaps: list,
    recommended_commands: list,
    metadata: dict,
) -> str:
    return _render_pull_request_body(
        feature_id=feature_id,
        status=status,
        ready=ready,
        summary=summary,
        why=why,
        acceptance_criteria=acceptance_criteria,
        tasks=tasks,
        test_plan=test_plan,
        release_readiness=release_readiness,
        readiness_checks=readiness_checks,
        source_files=source_files,
        missing_files=missing_files,
        gaps=gaps,
        recommended_commands=recommended_commands,
        metadata=metadata,
    )


def render_draft_commands(slug: str) -> list:
    return _recommended_pr_commands(slug)
