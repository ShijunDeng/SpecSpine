from __future__ import annotations

from .feature_bundle_io_paths import _sync_body_source
from .feature_sync_plan_commands import (
    _recommended_sync_plan_commands,
    _sync_command,
    _sync_plan_notes,
)
from .feature_sync_plan_labels import (
    _feature_issue_labels,
    _github_label_args,
    _pull_request_labels,
    _task_issue_labels,
)

__all__ = [
    "build_sync_plan_commands",
]


def build_sync_plan_commands(context: dict) -> list:
    slug = context["slug"]
    metadata = context["metadata"]
    issue_draft = context["issue_draft"]
    task_issues = context["task_issues"]
    pull_request = context["pull_request"]
    handoff = context["handoff"]

    commands: list = []

    feature_issue_body_source = _sync_body_source(slug, "feature-issue.md")
    feature_issue_labels = _feature_issue_labels(
        slug,
        handoff.status,
        metadata.priority,
    )
    commands.append(
        _sync_command(
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
    )

    for task_issue in task_issues.issues:
        body_source = _sync_body_source(
            slug,
            f"task-issues/{task_issue.task_id}.md",
        )
        commands.append(
            _sync_command(
                command_id=f"github.task_issue.{task_issue.task_id}",
                kind="task-issue",
                description=(
                    f"Create one GitHub issue for execution task "
                    f"{task_issue.task_id}."
                ),
                argv=(
                    "gh",
                    "issue",
                    "create",
                    "--title",
                    task_issue.title,
                    "--body-file",
                    body_source,
                    *_github_label_args(
                        _task_issue_labels(slug, task_issues.status)
                    ),
                ),
                body_source=body_source,
                body=task_issue.body,
            )
        )

    pull_request_body_source = _sync_body_source(slug, "pull-request.md")
    commands.append(
        _sync_command(
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
    )

    return commands
