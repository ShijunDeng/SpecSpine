from __future__ import annotations

from ._sync_feature_command import build_feature_issue_command
from ._sync_task_commands import build_task_issue_commands
from ._sync_pr_command import build_pull_request_command

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

    commands.append(
        build_feature_issue_command(
            slug,
            handoff.status,
            metadata.priority,
            issue_draft,
        )
    )

    commands.extend(build_task_issue_commands(slug, task_issues))

    commands.append(
        build_pull_request_command(slug, pull_request)
    )

    return commands
