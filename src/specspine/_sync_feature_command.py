from __future__ import annotations

from .feature_bundle_io_paths import _sync_body_source
from .feature_sync_plan_commands import _sync_command
from .feature_sync_plan_labels import (
    _feature_issue_labels,
    _github_label_args,
)

__all__ = [
    "build_feature_issue_command",
]


def build_feature_issue_command(
    slug: str,
    status: str,
    priority: str,
    issue_draft: object,
) -> dict:
    feature_issue_body_source = _sync_body_source(slug, "feature-issue.md")
    feature_issue_labels = _feature_issue_labels(slug, status, priority)
    return _sync_command(
        command_id="github.issue.feature",
        kind="issue",
        description="Create one GitHub issue for the feature-level specification.",
        argv=(
            "gh",
            "issue",
            "create",
            "--title",
            issue_draft.title,
            "--body-file",
            feature_issue_body_source,
            *_github_label_args(feature_issue_labels),
        ),
        body_source=feature_issue_body_source,
        body=issue_draft.body,
    )
