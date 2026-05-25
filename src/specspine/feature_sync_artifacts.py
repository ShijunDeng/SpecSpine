from __future__ import annotations

import json
import shlex
from pathlib import Path

from .feature_bundle import (
    FeatureSyncPlan,
    FeatureSyncPlanArtifactExistsError,
    FeatureSyncPlanArtifacts,
    FeatureSyncPlanCommand,
    _path_as_posix,
)

__all__ = [
    "FeatureSyncPlanArtifactExistsError",
    "write_feature_sync_plan_artifacts",
]


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
