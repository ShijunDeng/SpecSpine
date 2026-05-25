from __future__ import annotations

from pathlib import Path

from ..feature_bundle import (
    FeatureSyncPlan,
    _path_as_posix,
)

__all__ = [
    "_sync_artifact_relative_path",
    "_sync_plan_artifact_manifest",
]


def _sync_artifact_relative_path(command) -> Path:
    body_source = Path(command.body_source)
    if command.kind == "issue":
        return Path("feature-issue.md")
    if command.kind == "pull-request":
        return Path("pull-request.md")
    if command.kind == "task-issue":
        return Path("task-issues") / body_source.name
    return Path(body_source.name)


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
