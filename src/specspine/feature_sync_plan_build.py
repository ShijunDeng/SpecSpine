from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    FeatureBundleNotFoundError,
    FeatureSyncPlan,
    _relative_feature_paths,
    _render_metadata_lines,
    _sync_body_source,
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
from .feature_task_issues import build_feature_task_issues_report


def build_feature_sync_plan(root: Path, slug: str) -> FeatureSyncPlan:
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

    source_files = tuple(
        source["path"]
        for source in handoff.sources.values()
        if bool(source["exists"])
    )

    return FeatureSyncPlan(
        feature_id=slug,
        status=handoff.status,
        ready=handoff.ready,
        source_files=source_files,
        missing_files=handoff.missing_files,
        gaps=handoff.gaps,
        blocking_checks=handoff.blocking_checks,
        metadata=metadata,
        commands=tuple(commands),
        notes=_sync_plan_notes(metadata),
        recommended_commands=_recommended_sync_plan_commands(slug),
    )


__all__ = [
    "build_feature_sync_plan",
]
