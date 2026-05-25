from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    PullRequestDraft,
    _first_line_h1,
    _why_or_placeholder,
    feature_title,
    read_feature_metadata,
)
from .feature_drafts_render import (
    _pull_request_title,
    _recommended_pr_commands,
    _render_pull_request_body,
)
from .feature_handoff import build_feature_handoff_report
from .feature_ready import build_feature_ready_report

from ._pr_draft_collector import PrDraftFileCollection

__all__ = [
    "build_pull_request_draft",
]


def build_pull_request_draft(
    resolved_root: Path,
    slug: str,
    collection: PrDraftFileCollection,
) -> PullRequestDraft:
    base_title = _first_line_h1(collection.spec_content) or feature_title(slug)
    title = _pull_request_title(base_title)
    why = _why_or_placeholder(collection.contents, relative_path=collection.relative_paths["spec"])
    handoff = build_feature_handoff_report(resolved_root, slug)
    ready_report = build_feature_ready_report(resolved_root, slug)
    metadata = read_feature_metadata(resolved_root, slug)
    recommended_commands = _recommended_pr_commands(slug)
    summary = {
        **handoff.summary,
        "source_files": {"total": len(collection.source_files)},
        "missing_files": {"total": len(collection.missing_files)},
    }

    body = _render_pull_request_body(
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
