from __future__ import annotations

from pathlib import Path

from .feature_bundle import PullRequestDraft
from ._pr_draft_collector import PrDraftFileCollection
from ._pr_draft_context import load_draft_context, compute_draft_title, compute_draft_why
from ._pr_draft_renderer import render_draft_title, render_draft_body, render_draft_commands

__all__ = [
    "build_pull_request_draft",
]


def build_pull_request_draft(
    resolved_root: Path,
    slug: str,
    collection: PrDraftFileCollection,
) -> PullRequestDraft:
    base_title = compute_draft_title(collection.spec_content, slug)
    title = render_draft_title(base_title)
    why = compute_draft_why(collection.contents, collection.relative_paths)
    context = load_draft_context(resolved_root, slug, collection)
    handoff = context["handoff"]
    ready_report = context["ready_report"]
    metadata = context["metadata"]
    summary = context["summary"]
    recommended_commands = render_draft_commands(slug)

    body = render_draft_body(
        feature_id=slug,
        status=handoff.status,
        ready=handoff.ready,
        summary=summary,
        why=why,
        acceptance_criteria=handoff.acceptance_criteria,
        tasks=handoff.tasks,
        test_plan=handoff.test_plan,
        release_readiness=handoff.release_readiness,
        readiness_checks=ready_report.checks,
        source_files=tuple(collection.source_files),
        missing_files=tuple(collection.missing_files),
        gaps=handoff.gaps,
        recommended_commands=recommended_commands,
        metadata=metadata,
    )

    return PullRequestDraft(
        title=title,
        body=body,
        feature_id=slug,
        status=handoff.status,
        ready=handoff.ready,
        source_files=tuple(collection.source_files),
        missing_files=tuple(collection.missing_files),
        gaps=handoff.gaps,
        blocking_checks=handoff.blocking_checks,
        summary=summary,
        recommended_commands=recommended_commands,
        metadata=metadata,
    )
