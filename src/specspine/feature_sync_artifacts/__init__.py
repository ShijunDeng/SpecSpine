from __future__ import annotations

import json
from pathlib import Path

from ..feature_bundle import (
    FeatureSyncPlan,
    FeatureSyncPlanArtifactExistsError,
    FeatureSyncPlanArtifacts,
)
from .manifest import (
    _sync_plan_artifact_manifest,
)
from .commands_renderer import (
    _render_sync_plan_commands_sh,
)

__all__ = [
    "FeatureSyncPlanArtifactExistsError",
    "write_feature_sync_plan_artifacts",
]


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
