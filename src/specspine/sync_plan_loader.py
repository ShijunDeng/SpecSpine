from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    FeatureBundleNotFoundError,
    _relative_feature_paths,
    feature_bundle_paths,
    get_feature_status,
    read_feature_metadata,
    validate_feature_slug,
)
from .feature_drafts import (
    build_issue_draft,
    build_pull_request_draft,
)
from .feature_handoff import build_feature_handoff_report
from .feature_task_issues import build_feature_task_issues_report

__all__ = [
    "load_sync_plan_context",
]


def load_sync_plan_context(root: Path, slug: str) -> dict:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    status_report = get_feature_status(resolved_root, slug)
    has_native_files = any(file["exists"] for file in status_report.files.values())
    if not has_native_files:
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(feature_bundle_paths(resolved_root, slug).values()),
        )

    metadata = read_feature_metadata(resolved_root, slug)
    issue_draft = build_issue_draft(resolved_root, slug)
    task_issues = build_feature_task_issues_report(resolved_root, slug)
    pull_request = build_pull_request_draft(resolved_root, slug)
    handoff = build_feature_handoff_report(resolved_root, slug)

    return {
        "slug": slug,
        "resolved_root": resolved_root,
        "metadata": metadata,
        "issue_draft": issue_draft,
        "task_issues": task_issues,
        "pull_request": pull_request,
        "handoff": handoff,
    }
