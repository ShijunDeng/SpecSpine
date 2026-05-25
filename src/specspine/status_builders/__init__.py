from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from ..adapters import AdapterStatus, probe_adapters
from ..features import list_feature_bundles
from ..fusion import FUSION_REQUIRED_FILES
from ..workspace import BASE_WORKSPACE_FILES, check_workspace
from ..status_readiness import build_readiness_summary
from ..status_features import build_feature_summaries
from .recommendations import _build_recommendations
from ..status_workspace import (
    _artifact_status,
    _upstream_status,
    _adapter_statuses,
    _relative_paths,
)
from .recommendations import _build_recommendations

__all__ = [
    "_build_recommendations",
    "build_status",
]

AdapterProbe = Callable[[], list[AdapterStatus]]


def build_status(
    path: Path,
    *,
    include_adapters: bool = False,
    include_feature_summaries: bool = False,
    include_readiness_summary: bool = False,
    feature_summary_statuses: tuple[str, ...] = (),
    feature_summary_ready: bool | None = None,
    feature_summary_priorities: tuple[str, ...] = (),
    feature_summary_owners: tuple[str, ...] = (),
    feature_summary_milestones: tuple[str, ...] = (),
    feature_summary_target_releases: tuple[str, ...] = (),
    feature_summary_projects: tuple[str, ...] = (),
    feature_summary_efforts: tuple[str, ...] = (),
    feature_summary_sort: str | None = None,
    feature_summary_sort_desc: bool = False,
    feature_summary_require_coverage: bool = False,
    feature_summary_use_policy: bool = False,
    readiness_require_coverage: bool = False,
    readiness_use_policy: bool = False,
    adapter_probe: AdapterProbe = probe_adapters,
) -> dict[str, Any]:
    root = path.expanduser().resolve()

    workspace_present, workspace_missing_paths = check_workspace(
        root,
        required_files=BASE_WORKSPACE_FILES,
    )
    fusion_required_files = dict(BASE_WORKSPACE_FILES)
    fusion_required_files.update(FUSION_REQUIRED_FILES)
    fusion_present, fusion_missing_paths = check_workspace(
        root,
        required_files=fusion_required_files,
    )

    workspace_missing = _relative_paths(workspace_missing_paths, root)
    fusion_missing = _relative_paths(fusion_missing_paths, root)
    upstreams = _upstream_status(root)
    features = list_feature_bundles(root)

    adapters = None
    if include_adapters:
        adapters = _adapter_statuses(adapter_probe())

    status: dict[str, Any] = {
        "root": str(root),
        "workspace": {
            "complete": not workspace_missing,
            "present": _relative_paths(workspace_present, root),
            "missing": workspace_missing,
        },
        "fusion": {
            "complete": not fusion_missing,
            "present": _relative_paths(fusion_present, root),
            "missing": fusion_missing,
        },
        "artifacts": _artifact_status(root),
        "features": features,
        "upstreams": upstreams,
        "recommendations": _build_recommendations(
            root=root,
            workspace_missing=workspace_missing,
            fusion_missing=fusion_missing,
            upstreams=upstreams,
            adapters=adapters,
        ),
    }

    if adapters is not None:
        status["adapters"] = adapters

    if include_feature_summaries:
        status["feature_summaries"] = build_feature_summaries(
            root,
            features=features,
            status_filters=feature_summary_statuses,
            ready_filter=feature_summary_ready,
            priority_filters=feature_summary_priorities,
            owner_filters=feature_summary_owners,
            milestone_filters=feature_summary_milestones,
            target_release_filters=feature_summary_target_releases,
            project_filters=feature_summary_projects,
            effort_filters=feature_summary_efforts,
            sort_key=feature_summary_sort,
            sort_desc=feature_summary_sort_desc,
            require_coverage=feature_summary_require_coverage,
            use_policy=feature_summary_use_policy,
        )

    if include_readiness_summary:
        status["readiness_summary"] = build_readiness_summary(
            root,
            features=features,
            require_coverage=readiness_require_coverage,
            use_policy=readiness_use_policy,
        )

    return status
