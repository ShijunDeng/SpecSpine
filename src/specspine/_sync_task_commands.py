from __future__ import annotations

from .feature_bundle_io_paths import _sync_body_source
from .feature_sync_plan_commands import _sync_command
from .feature_sync_plan_labels import (
    _github_label_args,
    _task_issue_labels,
)

__all__ = [
    "build_task_issue_commands",
]


def build_task_issue_commands(
    slug: str,
    task_issues: object,
) -> list:
    commands: list = []
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
    return commands
