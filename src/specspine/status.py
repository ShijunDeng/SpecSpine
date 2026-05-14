from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from .adapters import ADAPTER_SPECS, AdapterStatus, probe_adapters
from .features import (
    FEATURE_PRIORITIES,
    FEATURE_STATUSES,
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    build_feature_handoff_report,
    list_feature_bundles,
    read_feature_metadata,
)
from .fusion import FUSION_REQUIRED_FILES
from .workspace import BASE_WORKSPACE_FILES, check_workspace


AdapterProbe = Callable[[], list[AdapterStatus]]

FEATURE_SUMMARY_STATUS_FILTERS = (*FEATURE_STATUSES, "invalid", "unknown")
FEATURE_SUMMARY_PRIORITY_FILTERS = (*FEATURE_PRIORITIES, "unknown")
FEATURE_SUMMARY_READY_VALUES = {
    "yes": True,
    "true": True,
    "ready": True,
    "no": False,
    "false": False,
    "not-ready": False,
}
FEATURE_SUMMARY_SORT_KEYS = (
    "slug",
    "status",
    "ready",
    "gaps",
    "blocking",
    "tasks-open",
    "priority",
)
_FEATURE_SUMMARY_STATUS_ORDER = {
    status: index
    for index, status in enumerate(FEATURE_STATUSES)
}
_FEATURE_SUMMARY_STATUS_ORDER["invalid"] = len(_FEATURE_SUMMARY_STATUS_ORDER)
_FEATURE_SUMMARY_STATUS_ORDER["unknown"] = len(_FEATURE_SUMMARY_STATUS_ORDER)
_FEATURE_SUMMARY_PRIORITY_ORDER = {
    "high": 0,
    "medium": 1,
    "low": 2,
    "unknown": 3,
}


class InvalidFeatureSummaryOption(ValueError):
    """Raised when a feature summary filter or sort option is unsupported."""


def _relative_paths(paths: list[Path], root: Path) -> list[str]:
    return sorted(str(path.relative_to(root)) for path in paths)


def _clean_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _parse_two_level_yaml_section(content: str, section: str) -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    in_section = False
    current_key: str | None = None

    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent == 0:
            in_section = stripped == f"{section}:"
            current_key = None
            continue

        if not in_section:
            continue

        if indent == 2 and stripped.endswith(":"):
            current_key = stripped[:-1]
            values.setdefault(current_key, {})
            continue

        if indent == 4 and current_key and ":" in stripped:
            key, value = stripped.split(":", 1)
            values[current_key][key.strip()] = _clean_scalar(value)

    return values


def _read_yaml_section(path: Path, section: str) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}

    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return {}

    return _parse_two_level_yaml_section(content, section)


def _artifact_status(root: Path) -> dict[str, dict[str, Any]]:
    artifacts: dict[str, dict[str, Any]] = {}

    for relative_path in sorted(BASE_WORKSPACE_FILES):
        artifacts[relative_path] = {
            "exists": (root / relative_path).exists(),
            "required_for": ["workspace"],
        }

    for relative_path in sorted(FUSION_REQUIRED_FILES):
        entry = artifacts.setdefault(
            relative_path,
            {
                "exists": (root / relative_path).exists(),
                "required_for": [],
            },
        )
        entry["exists"] = (root / relative_path).exists()
        if "fusion" not in entry["required_for"]:
            entry["required_for"].append("fusion")

    for feature in list_feature_bundles(root):
        slug = str(feature["slug"])
        files = feature["files"]
        if not isinstance(files, dict):
            continue

        for relative_path in sorted(str(path) for path in files.values()):
            artifacts[relative_path] = {
                "exists": True,
                "required_for": ["feature", f"feature:{slug}"],
            }

    return artifacts


def _upstream_status(root: Path) -> dict[str, dict[str, Any]]:
    spine_adapters = _read_yaml_section(root / ".specspine" / "spine.yaml", "adapters")
    fusion_upstreams = _read_yaml_section(root / ".specspine" / "fusion.yaml", "upstreams")

    upstreams: dict[str, dict[str, Any]] = {}
    for key, spec in ADAPTER_SPECS.items():
        spine_config = spine_adapters.get(key, {})
        fusion_config = fusion_upstreams.get(key, {})
        adapter_path = spine_config.get("config")
        if not isinstance(adapter_path, str) or not adapter_path:
            adapter_path = f".specspine/adapters/{key}.md"

        enabled = fusion_config.get("enabled", spine_config.get("enabled", False))
        if not isinstance(enabled, bool):
            enabled = False

        upstreams[key] = {
            "display_name": spec.display_name,
            "enabled": enabled,
            "config": adapter_path,
            "config_exists": (root / adapter_path).exists(),
            "role": spec.role,
            "upstream_url": spec.upstream_url,
        }

    return upstreams


def _adapter_statuses(statuses: list[AdapterStatus]) -> dict[str, dict[str, Any]]:
    return {
        status.key: {
            "display_name": status.display_name,
            "available": status.available,
            "detail": status.detail,
            "version": status.version,
            "command": status.command,
            "install_hint": status.install_hint,
            "upstream_url": status.upstream_url,
        }
        for status in statuses
    }


def _empty_count_summary() -> dict[str, int]:
    return {
        "done": 0,
        "open": 0,
        "total": 0,
    }


def parse_feature_summary_status_filters(values: list[str] | None) -> tuple[str, ...]:
    statuses: list[str] = []
    for value in values or []:
        normalized = value.strip().lower()
        if normalized not in FEATURE_SUMMARY_STATUS_FILTERS:
            allowed = ", ".join(FEATURE_SUMMARY_STATUS_FILTERS)
            raise InvalidFeatureSummaryOption(
                f"Invalid feature summary status '{value}'. Use one of: {allowed}."
            )
        if normalized not in statuses:
            statuses.append(normalized)

    return tuple(statuses)


def parse_feature_summary_ready_filter(value: str | None) -> bool | None:
    if value is None:
        return None

    normalized = value.strip().lower()
    if normalized not in FEATURE_SUMMARY_READY_VALUES:
        allowed = ", ".join(FEATURE_SUMMARY_READY_VALUES)
        raise InvalidFeatureSummaryOption(
            f"Invalid feature summary readiness '{value}'. Use one of: {allowed}."
        )

    return FEATURE_SUMMARY_READY_VALUES[normalized]


def parse_feature_summary_priority_filters(values: list[str] | None) -> tuple[str, ...]:
    priorities: list[str] = []
    for value in values or []:
        normalized = value.strip().lower()
        if normalized not in FEATURE_SUMMARY_PRIORITY_FILTERS:
            allowed = ", ".join(FEATURE_SUMMARY_PRIORITY_FILTERS)
            raise InvalidFeatureSummaryOption(
                f"Invalid feature summary priority '{value}'. Use one of: {allowed}."
            )
        if normalized not in priorities:
            priorities.append(normalized)

    return tuple(priorities)


def parse_feature_summary_owner_filters(values: list[str] | None) -> tuple[str, ...]:
    owners: list[str] = []
    for value in values or []:
        normalized = value.strip().lower() or "unassigned"
        if normalized not in owners:
            owners.append(normalized)

    return tuple(owners)


def parse_feature_summary_sort_key(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip().lower()
    if normalized not in FEATURE_SUMMARY_SORT_KEYS:
        allowed = ", ".join(FEATURE_SUMMARY_SORT_KEYS)
        raise InvalidFeatureSummaryOption(
            f"Invalid feature summary sort key '{value}'. Use one of: {allowed}."
        )

    return normalized


def _feature_summary_status_bucket(summary: dict[str, Any]) -> str:
    status = str(summary.get("status") or "unknown")
    if status == "unknown":
        return "unknown"
    if status in FEATURE_STATUSES:
        return status
    return "invalid"


def _feature_summary_matches_status(
    summary: dict[str, Any],
    status_filters: tuple[str, ...],
) -> bool:
    if not status_filters:
        return True

    status = str(summary.get("status") or "unknown")
    status_bucket = _feature_summary_status_bucket(summary)
    return status in status_filters or status_bucket in status_filters


def _feature_summary_matches_priority(
    summary: dict[str, Any],
    priority_filters: tuple[str, ...],
) -> bool:
    if not priority_filters:
        return True

    priority = str(summary.get("priority") or "unknown").lower()
    return priority in priority_filters


def _feature_summary_matches_owner(
    summary: dict[str, Any],
    owner_filters: tuple[str, ...],
) -> bool:
    if not owner_filters:
        return True

    owner = str(summary.get("owner") or "unassigned").strip().lower() or "unassigned"
    return owner in owner_filters


def _feature_summary_tasks_open(summary: dict[str, Any]) -> int:
    tasks = summary.get("tasks_summary", {})
    if not isinstance(tasks, dict):
        return 0
    value = tasks.get("open", 0)
    return int(value) if isinstance(value, int) else 0


def _feature_summary_sort_value(summary: dict[str, Any], sort_key: str) -> tuple[Any, ...]:
    slug = str(summary.get("slug") or summary.get("feature_id") or "")
    if sort_key == "slug":
        return (slug,)
    if sort_key == "status":
        bucket = _feature_summary_status_bucket(summary)
        status = str(summary.get("status") or "unknown")
        return (_FEATURE_SUMMARY_STATUS_ORDER[bucket], status, slug)
    if sort_key == "ready":
        return (bool(summary.get("ready", False)), slug)
    if sort_key == "gaps":
        return (int(summary.get("gaps", 0)), slug)
    if sort_key == "blocking":
        return (int(summary.get("blocking_checks", 0)), slug)
    if sort_key == "tasks-open":
        return (_feature_summary_tasks_open(summary), slug)
    if sort_key == "priority":
        priority = str(summary.get("priority") or "unknown").lower()
        order = _FEATURE_SUMMARY_PRIORITY_ORDER.get(
            priority,
            _FEATURE_SUMMARY_PRIORITY_ORDER["unknown"],
        )
        return (order, slug)
    return (slug,)


def filter_and_sort_feature_summaries(
    summaries: list[dict[str, Any]],
    *,
    status_filters: tuple[str, ...] = (),
    ready_filter: bool | None = None,
    priority_filters: tuple[str, ...] = (),
    owner_filters: tuple[str, ...] = (),
    sort_key: str | None = None,
    sort_desc: bool = False,
) -> list[dict[str, Any]]:
    filtered = [
        summary
        for summary in summaries
        if _feature_summary_matches_status(summary, status_filters)
        and _feature_summary_matches_priority(summary, priority_filters)
        and _feature_summary_matches_owner(summary, owner_filters)
        and (
            ready_filter is None
            or bool(summary.get("ready", False)) is ready_filter
        )
    ]

    if sort_key is not None:
        return sorted(
            filtered,
            key=lambda summary: _feature_summary_sort_value(summary, sort_key),
            reverse=sort_desc,
        )

    if sort_desc:
        filtered.reverse()

    return filtered


def _invalid_feature_summary(
    feature: dict[str, object],
    *,
    reason: str,
) -> dict[str, Any]:
    slug = str(feature["slug"])
    missing_files = [
        str(relative_path)
        for relative_path in feature.get("missing_files", [])
    ]
    return {
        "feature_id": slug,
        "slug": slug,
        "status": "invalid",
        "priority": "unknown",
        "owner": "unassigned",
        "complete": bool(feature.get("complete", False)),
        "ready": False,
        "missing_files": missing_files,
        "tasks_summary": _empty_count_summary(),
        "ready_summary": {"fail": 1, "pass": 0, "total": 1},
        "gaps": max(1, len(missing_files)),
        "blocking_checks": 1,
        "next_actions": [reason],
        "recommended_commands": [],
    }


def _missing_feature_summary(feature: dict[str, object]) -> dict[str, Any]:
    slug = str(feature["slug"])
    missing_files = [
        str(relative_path)
        for relative_path in feature.get("missing_files", [])
    ]
    return {
        "feature_id": slug,
        "slug": slug,
        "status": str(feature.get("status") or "unknown"),
        "priority": "unknown",
        "owner": "unassigned",
        "complete": bool(feature.get("complete", False)),
        "ready": False,
        "missing_files": missing_files,
        "tasks_summary": _empty_count_summary(),
        "ready_summary": {"fail": 1, "pass": 0, "total": 1},
        "gaps": max(1, len(missing_files)),
        "blocking_checks": 1,
        "next_actions": [
            (
                "Create or restore the native feature bundle: "
                f"specspine feature new {slug} . --title \"...\" --why \"...\""
            )
        ],
        "recommended_commands": [],
    }


def build_feature_summaries(
    root: Path,
    features: list[dict[str, object]] | None = None,
    *,
    status_filters: tuple[str, ...] = (),
    ready_filter: bool | None = None,
    priority_filters: tuple[str, ...] = (),
    owner_filters: tuple[str, ...] = (),
    sort_key: str | None = None,
    sort_desc: bool = False,
) -> list[dict[str, Any]]:
    resolved_root = root.expanduser().resolve()
    summaries: list[dict[str, Any]] = []
    feature_bundles = features if features is not None else list_feature_bundles(resolved_root)

    for feature in feature_bundles:
        slug = str(feature["slug"])
        try:
            report = build_feature_handoff_report(resolved_root, slug)
        except InvalidFeatureSlug as error:
            summaries.append(
                _invalid_feature_summary(
                    feature,
                    reason=str(error),
                )
            )
            continue
        except FeatureBundleNotFoundError:
            summaries.append(_missing_feature_summary(feature))
            continue

        summary = report.summary
        metadata = read_feature_metadata(resolved_root, report.feature_id)
        summaries.append(
            {
                "feature_id": report.feature_id,
                "slug": report.feature_id,
                "status": report.status,
                "priority": metadata.priority,
                "owner": metadata.owner,
                "complete": bool(feature.get("complete", False)),
                "ready": report.ready,
                "missing_files": list(report.missing_files),
                "tasks_summary": dict(summary["tasks"]),
                "ready_summary": dict(summary["ready"]),
                "gaps": int(summary["gaps"]["total"]),
                "blocking_checks": int(summary["blocking_checks"]["total"]),
                "next_actions": list(report.next_actions),
                "recommended_commands": list(report.recommended_commands),
            }
        )

    return filter_and_sort_feature_summaries(
        summaries,
        status_filters=status_filters,
        ready_filter=ready_filter,
        priority_filters=priority_filters,
        owner_filters=owner_filters,
        sort_key=sort_key,
        sort_desc=sort_desc,
    )


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
    feature_summary_statuses: tuple[str, ...] = (),
    feature_summary_ready: bool | None = None,
    feature_summary_priorities: tuple[str, ...] = (),
    feature_summary_owners: tuple[str, ...] = (),
    feature_summary_sort: str | None = None,
    feature_summary_sort_desc: bool = False,
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
            sort_key=feature_summary_sort,
            sort_desc=feature_summary_sort_desc,
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
                lines.append(
                    "  "
                    f"{summary['slug']} - "
                    f"status={summary['status']} "
                    f"priority={summary['priority']} "
                    f"owner={summary['owner']} "
                    f"ready={'yes' if summary['ready'] else 'no'} "
                    f"tasks={tasks['done']}/{tasks['open']} "
                    f"gaps={summary['gaps']} "
                    f"blocking={summary['blocking_checks']}"
                )
                lines.append(f"    next: {first_action}")
        else:
            lines.append("  none")

    lines.append("Recommended next actions:")
    for recommendation in status["recommendations"]:
        lines.append(f"  - {recommendation}")

    return "\n".join(lines) + "\n"
