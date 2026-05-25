from __future__ import annotations

from .feature_bundle_io_paths import _sync_body_source
from .feature_sync_plan_commands import _sync_command
from .feature_sync_plan_labels import (
    _github_label_args,
    _pull_request_labels,
)

__all__ = [
    "build_pull_request_command",
]


def build_pull_request_command(
    slug: str,
    pull_request: object,
) -> dict:
    pull_request_body_source = _sync_body_source(slug, "pull-request.md")
    return _sync_command(
        command_id="github.pull_request",
        kind="pull-request",
        description="Create a draft GitHub Pull Request from local feature evidence.",
        argv=(
            "gh",
            "pr",
            "create",
            "--title",
            pull_request.title,
            "--body-file",
            pull_request_body_source,
            "--draft",
            *_github_label_args(_pull_request_labels(slug, pull_request.status)),
        ),
        body_source=pull_request_body_source,
        body=pull_request.body,
    )
