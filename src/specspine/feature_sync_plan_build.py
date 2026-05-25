from __future__ import annotations

from pathlib import Path

from .feature_bundle import FeatureSyncPlan  # noqa: F401
from .feature_bundle_io_paths import _sync_body_source  # noqa: F401
from .feature_sync_plan_commands import (  # noqa: F401
    _recommended_sync_plan_commands,
    _sync_command,
    _sync_plan_notes,
)
from .feature_sync_plan_labels import (  # noqa: F401
    _feature_issue_labels,
    _github_label_args,
    _pull_request_labels,
    _task_issue_labels,
)
from .sync_plan_loader import load_sync_plan_context
from .sync_plan_command_builder import build_sync_plan_commands
from .feature_sync_plan_commands import _sync_plan_notes

__all__ = [
    "build_feature_sync_plan",
]


def build_feature_sync_plan(root: Path, slug: str) -> FeatureSyncPlan:
    context = load_sync_plan_context(root, slug)
    commands = build_sync_plan_commands(context)

    handoff = context["handoff"]
    metadata = context["metadata"]

    source_files = tuple(
        source["path"]
        for source in handoff.sources.values()
        if bool(source["exists"])
    )

    return FeatureSyncPlan(
        feature_id=context["slug"],
        status=handoff.status,
        ready=handoff.ready,
        source_files=source_files,
        missing_files=handoff.missing_files,
        gaps=handoff.gaps,
        blocking_checks=handoff.blocking_checks,
        metadata=metadata,
        commands=tuple(commands),
        notes=_sync_plan_notes(metadata),
        recommended_commands=_recommended_sync_plan_commands(context["slug"]),
    )
