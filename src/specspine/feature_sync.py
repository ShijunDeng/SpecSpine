from __future__ import annotations

import json
import shlex
from pathlib import Path

from .feature_bundle import (
    FeatureBundleNotFoundError,
    FeatureHandoffReport,
    FeatureMetadata,
    FeatureReadyCheck,
    FeatureSyncPlan,
    FeatureSyncPlanArtifactExistsError,
    FeatureSyncPlanArtifacts,
    FeatureSyncPlanCommand,
    _path_as_posix,
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
from .feature_tasks import build_feature_task_issues_report

__all__ = [
    "FeatureSyncPlanArtifactExistsError",
    "FeatureSyncPlanCommand",
    "FeatureSyncPlan",
    "FeatureSyncPlanArtifacts",
    "build_feature_sync_plan",
    "render_feature_sync_plan_json",
    "render_feature_sync_plan_text",
    "write_feature_sync_plan_artifacts",
]


def _recommended_sync_plan_commands(slug: str) -> tuple[str, ...]:
    return (
        f"specspine feature sync-plan {slug} . --json",
        f"specspine feature issue {slug} . --json",
        f"specspine feature task-issues {slug} . --json",
        f"specspine feature pr {slug} . --json",
        f"specspine feature ready {slug} . --json",
        "specspine adapters lifecycle . --json",
        "specspine validate . --fusion --features",
    )


def _github_label_args(labels: tuple[str, ...]) -> tuple[str, ...]:
    args: list[str] = []
    for label in labels:
        args.extend(("--label", label))
    return tuple(args)


def _feature_issue_labels(slug: str, status: str, priority: str) -> tuple[str, ...]:
    return (
        "specspine",
        f"feature:{slug}",
        f"status:{status}",
        f"priority:{priority}",
    )


def _task_issue_labels(slug: str, status: str) -> tuple[str, ...]:
    return (
        "specspine",
        f"feature:{slug}",
        "task",
        f"status:{status}",
    )


def _pull_request_labels(slug: str, status: str) -> tuple[str, ...]:
    return (
        "specspine",
        f"feature:{slug}",
        f"status:{status}",
    )


def _sync_command(
    *,
    command_id: str,
    kind: str,
    description: str,
    argv: tuple[str, ...],
    body_source: str,
    body: str,
) -> FeatureSyncPlanCommand:
    return FeatureSyncPlanCommand(
        id=command_id,
        kind=kind,
        description=description,
        argv=argv,
        body_source=body_source,
        body=body,
    )


def _sync_plan_notes(metadata: FeatureMetadata) -> tuple[str, ...]:
    notes = [
        (
            "SpecSpine generated this as a local review plan only; it did not "
            "execute gh, call GitHub APIs, read tokens, or access the network."
        ),
        (
            "Every command would create remote GitHub resources if a human runs "
            "it, so review the argv list, labels, and draft body first."
        ),
        (
            "A human must authenticate GitHub CLI before running these commands; "
            "adding issues or pull requests to Projects may require the gh "
            "project scope."
        ),
        (
            "Do not rely on gh pr create dry-run as an automatic safety mode; "
            "GitHub CLI documentation says dry-run may still push git changes."
        ),
        (
            f"Priority is represented as the compatible label "
            f"priority:{metadata.priority}; this plan does not call GitHub Issue "
            "Fields APIs."
        ),
        (
            "Milestone, target release, project, and effort are local SpecSpine "
            "draft context in this plan; SpecSpine does not call GitHub Issue "
            "Fields or Projects APIs."
        ),
    ]
    if metadata.owner == "unassigned":
        notes.append(
            "Owner is unassigned; local owner metadata is not automatically "
            "mapped to --assignee."
        )
    else:
        notes.append(
            f"Owner '{metadata.owner}' is local SpecSpine metadata and is not "
            "automatically mapped to --assignee."
        )
    return tuple(notes)


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

    commands: list[FeatureSyncPlanCommand] = []

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


def render_feature_sync_plan_json(plan: FeatureSyncPlan) -> str:
    return json.dumps(plan.as_dict(), indent=2, sort_keys=True) + "\n"


def _sync_artifact_relative_path(command: FeatureSyncPlanCommand) -> Path:
    body_source = Path(command.body_source)
    if command.kind == "issue":
        return Path("feature-issue.md")
    if command.kind == "pull-request":
        return Path("pull-request.md")
    if command.kind == "task-issue":
        return Path("task-issues") / body_source.name
    return Path(body_source.name)


def _argv_with_local_body_file(
    argv: tuple[str, ...],
    body_file: str,
) -> tuple[str, ...]:
    updated = list(argv)
    for index, arg in enumerate(updated[:-1]):
        if arg == "--body-file":
            updated[index + 1] = body_file
            return tuple(updated)
    return (*argv, "--body-file", body_file)


def _sync_plan_artifact_manifest(
    plan: FeatureSyncPlan,
) -> tuple[dict[str, object], dict[str, Path]]:
    payload = plan.as_dict()
    artifact_paths: dict[str, Path] = {}
    commands: list[dict[str, object]] = []
    task_issue_artifacts: list[dict[str, str]] = []

    for command in plan.commands:
        relative_path = _sync_artifact_relative_path(command)
        artifact_paths[command.id] = relative_path
        artifact_path = _path_as_posix(relative_path)
        command_payload = command.as_dict()
        command_payload["artifact_path"] = artifact_path
        command_payload["body_file"] = artifact_path
        commands.append(command_payload)

        if command.kind == "task-issue":
            task_issue_artifacts.append(
                {
                    "command_id": command.id,
                    "path": artifact_path,
                    "task_id": command.id.rsplit(".", 1)[-1],
                }
            )

    payload["commands"] = commands
    payload["artifact_version"] = 1
    payload["artifact_root"] = "."
    payload["artifacts"] = {
        "commands": "commands.sh",
        "feature_issue": "feature-issue.md",
        "manifest": "manifest.json",
        "pull_request": "pull-request.md",
        "task_issues": task_issue_artifacts,
    }
    return payload, artifact_paths


def _render_sync_plan_commands_sh(
    plan: FeatureSyncPlan,
    artifact_paths: dict[str, Path],
) -> str:
    lines = [
        "# SpecSpine GitHub sync plan artifacts",
        "# review-only / do not run blindly",
        "# SpecSpine did not execute gh, read tokens, call GitHub APIs, or use the network.",
        "# Review manifest.json and the body files before manually running any command.",
        "",
    ]

    for command in plan.commands:
        body_file = _path_as_posix(artifact_paths[command.id])
        argv = _argv_with_local_body_file(command.argv, body_file)
        lines.extend(
            [
                f"# {command.id}: {command.description}",
                shlex.join(argv),
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def write_feature_sync_plan_artifacts(
    plan: FeatureSyncPlan,
    output_dir: Path,
    *,
    force: bool = False,
) -> FeatureSyncPlanArtifacts:
    resolved_output_dir = output_dir.expanduser().resolve()
    if resolved_output_dir.exists() and not resolved_output_dir.is_dir():
        raise NotADirectoryError(f"Output path is not a directory: {resolved_output_dir}")

    manifest, artifact_paths = _sync_plan_artifact_manifest(plan)
    body_targets = tuple(
        resolved_output_dir / relative_path
        for relative_path in artifact_paths.values()
    )
    manifest_path = resolved_output_dir / "manifest.json"
    commands_path = resolved_output_dir / "commands.sh"
    write_targets = (*body_targets, manifest_path, commands_path)

    parent_conflicts = tuple(
        path.parent
        for path in write_targets
        if path.parent.exists() and not path.parent.is_dir()
    )
    if parent_conflicts:
        first_conflict = parent_conflicts[0]
        raise NotADirectoryError(f"Output artifact parent is not a directory: {first_conflict}")

    existing_paths = tuple(path for path in write_targets if path.exists())
    if existing_paths and not force:
        raise FeatureSyncPlanArtifactExistsError(
            output_dir=resolved_output_dir,
            existing_paths=existing_paths,
        )

    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    for command in plan.commands:
        target = resolved_output_dir / artifact_paths[command.id]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(command.body, encoding="utf-8")

    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    commands_path.write_text(
        _render_sync_plan_commands_sh(plan, artifact_paths),
        encoding="utf-8",
    )

    return FeatureSyncPlanArtifacts(
        output_dir=resolved_output_dir,
        manifest_path=manifest_path,
        commands_path=commands_path,
        body_paths=body_targets,
        written_paths=write_targets,
        manifest=manifest,
    )


def render_feature_sync_plan_text(plan: FeatureSyncPlan) -> str:
    summary = plan.summary
    lines = [
        f"# GitHub Sync Plan: {plan.feature_id}",
        "",
        "## Summary",
        "",
        f"- Status: {plan.status}",
        f"- Ready: {'yes' if plan.ready else 'no'}",
        (
            "- Commands: "
            f"total={summary['commands_total']} "
            f"feature_issues={summary['issue_commands']} "
            f"task_issues={summary['task_issue_commands']} "
            f"pull_requests={summary['pull_request_commands']}"
        ),
        f"- Notes: {summary['notes_total']}",
        "",
        "## Metadata",
        "",
        *_render_metadata_lines(plan.metadata),
        "",
        "## Notes",
        "",
    ]
    lines.extend(f"- {note}" for note in plan.notes)

    lines.extend(["", "## Sources", ""])
    if plan.source_files:
        lines.extend(f"- [ok] {relative_path}" for relative_path in plan.source_files)
    else:
        lines.append("- None.")

    lines.extend(["", "## Missing Files", ""])
    if plan.missing_files:
        lines.extend(f"- [missing] {relative_path}" for relative_path in plan.missing_files)
    else:
        lines.append("- None.")

    lines.extend(["", "## Gaps", ""])
    if plan.gaps:
        lines.extend(
            f"- {gap['id']}: {gap['source_file']} - {gap['message']}"
            for gap in plan.gaps
        )
    else:
        lines.append("- None.")

    lines.extend(["", "## Blocking Checks", ""])
    if plan.blocking_checks:
        lines.extend(
            f"- {check.id}: {check.message}"
            for check in plan.blocking_checks
        )
    else:
        lines.append("- None.")

    lines.extend(["", "## Commands", ""])
    for command in plan.commands:
        lines.extend(
            [
                f"### {command.id}",
                "",
                f"- Kind: {command.kind}",
                f"- Description: {command.description}",
                f"- Body source: {command.body_source}",
                f"- Creates remote: {'yes' if command.creates_remote else 'no'}",
                f"- Requires token: {'yes' if command.requires_token else 'no'}",
                f"- Requires network: {'yes' if command.requires_network else 'no'}",
                (
                    "- Safe to auto-run: "
                    f"{'yes' if command.safe_to_auto_run else 'no'}"
                ),
                f"- Command: `{shlex.join(command.argv)}`",
                "",
            ]
        )

    lines.extend(["## Recommended Local Commands", ""])
    lines.extend(f"- `{command}`" for command in plan.recommended_commands)

    return "\n".join(lines).rstrip() + "\n"
