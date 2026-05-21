from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from .adapters import AdapterStatus, probe_adapters
from .features import list_feature_bundles
from .fusion import FUSION_REQUIRED_FILES
from .workspace import BASE_WORKSPACE_FILES, check_workspace
from .status_readiness import build_readiness_summary
from .status_features import build_feature_summaries
from .status_workspace import (
    _artifact_status,
    _upstream_status,
    _adapter_statuses,
    _relative_paths,
)

__all__ = [
    "_build_recommendations",
    "build_status",
    "render_status_json",
    "_marker",
    "_complete_marker",
    "render_status_text",
]

AdapterProbe = Callable[[], list[AdapterStatus]]


def _build_recommendations(
    *,
    root: Path,
    workspace_missing: list[str],
    fusion_missing: list[str],
    upstreams: dict[str, dict[str, Any]],
    adapters: dict[str, dict[str, Any]] | None,
) -> list[str]:
    recommendations: list[str] = []

    if workspace_missing:
        recommendations.append(f"Run `specspine init {root}` to create missing workspace artifacts.")

    fusion_specific_missing = [
        path for path in fusion_missing if path in FUSION_REQUIRED_FILES
    ]
    if fusion_specific_missing:
        recommendations.append(
            f"Run `specspine fuse {root} --agent codex` to create or repair fusion artifacts."
        )

    enabled_upstreams = [
        key for key, upstream in upstreams.items() if bool(upstream["enabled"])
    ]
    if not enabled_upstreams:
        recommendations.append(
            "Run `specspine fuse <path> --agent codex` when OpenSpec, Spec Kit, or Superpowers integration is needed."
        )

    if adapters is not None:
        for key in enabled_upstreams:
            adapter = adapters.get(key)
            if adapter and not adapter["available"]:
                recommendations.append(
                    f"Install {adapter['display_name']}: {adapter['install_hint']}"
                )

    if not recommendations:
        recommendations.append("Use `specspine status --json` as the compact context packet for agents.")

    return recommendations


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


def render_status_json(status: dict[str, Any]) -> str:
    return json.dumps(status, indent=2, sort_keys=True) + "\n"


def _marker(value: bool) -> str:
    return "ok" if value else "missing"


def _complete_marker(value: bool) -> str:
    return "complete" if value else "incomplete"


def render_status_text(status: dict[str, Any]) -> str:
    lines = [
        f"SpecSpine status at {status['root']}",
        f"Workspace: {_complete_marker(status['workspace']['complete'])}",
        f"Fusion: {_complete_marker(status['fusion']['complete'])}",
        "Artifacts:",
    ]

    for relative_path, artifact in status["artifacts"].items():
        lines.append(f"  [{_marker(artifact['exists'])}] {relative_path}")

    lines.append("Features:")
    if status["features"]:
        for feature in status["features"]:
            marker = "complete" if feature["complete"] else "incomplete"
            lifecycle = feature.get("status") or "unknown"
            consistency = "consistent" if feature.get("status_consistent") else "mixed"
            lines.append(
                f"  [{marker}] {feature['slug']} - {lifecycle} ({consistency})"
            )
    else:
        lines.append("  none")

    lines.append("Enabled upstreams:")
    enabled = [
        (key, upstream)
        for key, upstream in status["upstreams"].items()
        if upstream["enabled"]
    ]
    if enabled:
        for key, upstream in enabled:
            marker = _marker(upstream["config_exists"])
            lines.append(f"  [{marker}] {key}: {upstream['config']}")
    else:
        lines.append("  none")

    adapters = status.get("adapters")
    if adapters is not None:
        lines.append("External adapters:")
        for key, adapter in adapters.items():
            version = f" ({adapter['version']})" if adapter["version"] else ""
            lines.append(
                f"  [{_marker(adapter['available'])}] {key}: {adapter['display_name']}{version}"
            )
            lines.append(f"      {adapter['detail']}")

    validation = status.get("validation")
    if validation is not None:
        result = "ok" if validation["ok"] else "failed"
        summary = validation["summary"]
        lines.append("Validation:")
        lines.append(f"  Result: {result}")
        lines.append(
            "  Summary: "
            f"pass={summary['pass']} "
            f"fail={summary['fail']} "
            f"warn={summary['warn']} "
            f"skip={summary['skip']} "
            f"total={summary['total']}"
        )
        failed_checks = validation.get("failed_checks", [])
        if failed_checks:
            lines.append("  Failed checks:")
            for check in failed_checks:
                lines.append(f"    - {check['id']}")
        warning_checks = validation.get("warning_checks")
        if warning_checks is not None:
            lines.append("  Warning checks:")
            if warning_checks:
                for check in warning_checks:
                    lines.append(f"    - {check['id']}")
            else:
                lines.append("    none")

    feature_summaries = status.get("feature_summaries")
    if feature_summaries is not None:
        lines.append("Feature summaries:")
        if feature_summaries:
            for summary in feature_summaries:
                tasks = summary["tasks_summary"]
                next_actions = summary.get("next_actions", [])
                first_action = next_actions[0] if next_actions else "None."
                coverage_marker = (
                    "coverage=yes "
                    if summary.get("coverage_required")
                    else ""
                )
                lines.append(
                    "  "
                    f"{summary['slug']} - "
                    f"status={summary['status']} "
                    f"priority={summary['priority']} "
                    f"owner={summary['owner']} "
                    f"milestone={summary['milestone']} "
                    f"target_release={summary['target_release']} "
                    f"ready={'yes' if summary['ready'] else 'no'} "
                    f"{coverage_marker}"
                    f"tasks={tasks['done']}/{tasks['open']} "
                    f"gaps={summary['gaps']} "
                    f"blocking={summary['blocking_checks']}"
                )
                lines.append(f"    next: {first_action}")
        else:
            lines.append("  none")

    readiness_summary = status.get("readiness_summary")
    if readiness_summary is not None:
        lines.append("Readiness summary:")
        lines.append(
            "  "
            f"features={readiness_summary['features_total']} "
            f"ready={readiness_summary['ready']} "
            f"not_ready={readiness_summary['not_ready']} "
            f"blocking={readiness_summary['blocking_checks_total']} "
            f"gaps={readiness_summary['gaps_total']} "
            f"coverage_required={readiness_summary['coverage_required_total']}"
        )
        not_ready = [
            feature
            for feature in readiness_summary["features"]
            if not feature["ready"]
        ]
        if not_ready:
            lines.append("  Not-ready features:")
            for feature in not_ready:
                commands = feature.get("recommended_commands", [])
                command = commands[0] if commands else f"specspine feature ready {feature['feature_id']} . --json"
                lines.append(
                    "    "
                    f"- {feature['feature_id']} "
                    f"status={feature['status']} "
                    f"blocking={feature['blocking_checks']} "
                    f"gaps={feature['gaps']} "
                    f"missing={len(feature['missing_files'])}"
                )
                lines.append(f"      command: {command}")

    lines.append("Recommended next actions:")
    for recommendation in status["recommendations"]:
        lines.append(f"  - {recommendation}")

    return "\n".join(lines) + "\n"
