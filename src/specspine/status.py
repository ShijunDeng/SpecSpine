from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from .adapters import ADAPTER_SPECS, AdapterStatus, probe_adapters
from .features import (
    FEATURE_PRIORITIES,
    FEATURE_STATUSES,
    FeatureBundleNotFoundError,
    FeatureMetadata,
    InvalidFeatureSlug,
    build_feature_ready_report,
    build_feature_handoff_report,
    list_feature_bundles,
    read_feature_metadata,
)
from .fusion import FUSION_REQUIRED_FILES
from .policy import WorkspacePolicy, load_workspace_policy
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
    "milestone",
    "target-release",
    "project",
    "effort",
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
_FEATURE_SUMMARY_EFFORT_ORDER = {
    "xs": 0,
    "s": 1,
    "m": 2,
    "l": 3,
    "xl": 4,
    "xxl": 5,
    "unknown": 6,
}
_FEATURE_SUMMARY_DEFAULT_VALUES = {
    "milestone": "unassigned",
    "target-release": "unassigned",
    "project": "unassigned",
    "effort": "unknown",
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


def _empty_feature_metadata() -> FeatureMetadata:
    return FeatureMetadata(
        priority="unknown",
        owner="unassigned",
        milestone="unassigned",
        target_release="unassigned",
        project="unassigned",
        effort="unknown",
    )


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


def parse_feature_summary_metadata_filters(
    values: list[str] | None,
    *,
    default: str,
) -> tuple[str, ...]:
    filters: list[str] = []
    for value in values or []:
        normalized = value.strip().lower() or default
        if normalized not in filters:
            filters.append(normalized)

    return tuple(filters)


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


def _feature_summary_matches_metadata(
    summary: dict[str, Any],
    field: str,
    filters: tuple[str, ...],
    *,
    default: str,
) -> bool:
    if not filters:
        return True

    value = str(summary.get(field) or default).strip().lower() or default
    return value in filters


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
    if sort_key in {"milestone", "target-release", "project"}:
        field = "target_release" if sort_key == "target-release" else sort_key
        default = _FEATURE_SUMMARY_DEFAULT_VALUES[sort_key]
        value = str(summary.get(field) or default).strip() or default
        default_bucket = 1 if value.lower() == default else 0
        return (default_bucket, value.lower(), value, slug)
    if sort_key == "effort":
        effort = str(summary.get("effort") or "unknown").strip() or "unknown"
        effort_key = effort.lower()
        order = _FEATURE_SUMMARY_EFFORT_ORDER.get(
            effort_key,
            _FEATURE_SUMMARY_EFFORT_ORDER["unknown"],
        )
        default_bucket = 1 if effort_key == "unknown" else 0
        return (default_bucket, order, effort_key, slug)
    return (slug,)


def _feature_summary_sort_metadata_desc(
    summaries: list[dict[str, Any]],
    sort_key: str,
) -> list[dict[str, Any]]:
    assigned: list[dict[str, Any]] = []
    defaults: list[dict[str, Any]] = []
    for summary in summaries:
        if _feature_summary_sort_value(summary, sort_key)[0] == 0:
            assigned.append(summary)
        else:
            defaults.append(summary)

    def slug_key(summary: dict[str, Any]) -> str:
        return str(summary.get("slug") or summary.get("feature_id") or "")

    assigned_by_slug = sorted(assigned, key=slug_key)
    return [
        *sorted(
            assigned_by_slug,
            key=lambda summary: _feature_summary_sort_value(summary, sort_key)[1:3],
            reverse=True,
        ),
        *sorted(defaults, key=slug_key),
    ]


def filter_and_sort_feature_summaries(
    summaries: list[dict[str, Any]],
    *,
    status_filters: tuple[str, ...] = (),
    ready_filter: bool | None = None,
    priority_filters: tuple[str, ...] = (),
    owner_filters: tuple[str, ...] = (),
    milestone_filters: tuple[str, ...] = (),
    target_release_filters: tuple[str, ...] = (),
    project_filters: tuple[str, ...] = (),
    effort_filters: tuple[str, ...] = (),
    sort_key: str | None = None,
    sort_desc: bool = False,
) -> list[dict[str, Any]]:
    filtered = [
        summary
        for summary in summaries
        if _feature_summary_matches_status(summary, status_filters)
        and _feature_summary_matches_priority(summary, priority_filters)
        and _feature_summary_matches_owner(summary, owner_filters)
        and _feature_summary_matches_metadata(
            summary,
            "milestone",
            milestone_filters,
            default="unassigned",
        )
        and _feature_summary_matches_metadata(
            summary,
            "target_release",
            target_release_filters,
            default="unassigned",
        )
        and _feature_summary_matches_metadata(
            summary,
            "project",
            project_filters,
            default="unassigned",
        )
        and _feature_summary_matches_metadata(
            summary,
            "effort",
            effort_filters,
            default="unknown",
        )
        and (
            ready_filter is None
            or bool(summary.get("ready", False)) is ready_filter
        )
    ]

    if sort_key is not None:
        if sort_desc and sort_key in _FEATURE_SUMMARY_DEFAULT_VALUES:
            return _feature_summary_sort_metadata_desc(filtered, sort_key)
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
    require_coverage: bool = False,
    policy: WorkspacePolicy | None = None,
    policy_coverage_required: bool = False,
) -> dict[str, Any]:
    slug = str(feature["slug"])
    missing_files = [
        str(relative_path)
        for relative_path in feature.get("missing_files", [])
    ]
    summary = {
        "feature_id": slug,
        "slug": slug,
        "status": "invalid",
        **_empty_feature_metadata().as_dict(),
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
    if require_coverage:
        summary["coverage_required"] = True
    if policy is not None:
        summary["policy_coverage_required"] = policy_coverage_required
        summary["policy_source"] = str(policy.source_file)
    return summary


def _missing_feature_summary(
    feature: dict[str, object],
    *,
    require_coverage: bool = False,
    policy: WorkspacePolicy | None = None,
    policy_coverage_required: bool = False,
) -> dict[str, Any]:
    slug = str(feature["slug"])
    missing_files = [
        str(relative_path)
        for relative_path in feature.get("missing_files", [])
    ]
    summary = {
        "feature_id": slug,
        "slug": slug,
        "status": str(feature.get("status") or "unknown"),
        **_empty_feature_metadata().as_dict(),
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
    if require_coverage:
        summary["coverage_required"] = True
    if policy is not None:
        summary["policy_coverage_required"] = policy_coverage_required
        summary["policy_source"] = str(policy.source_file)
    return summary


def _readiness_next_actions(slug: str, report: dict[str, Any]) -> list[str]:
    actions: list[str] = []
    missing_files = report.get("missing_files", [])
    gaps = report.get("gaps", [])
    blocking_checks = report.get("blocking_checks", [])

    if missing_files:
        actions.append("Add missing peer file(s): " + ", ".join(missing_files))
    if gaps:
        gap_ids = [str(gap.get("id", "unknown")) for gap in gaps if isinstance(gap, dict)]
        actions.append("Resolve trace gap(s): " + ", ".join(sorted(set(gap_ids))))
    if blocking_checks:
        check_ids = [
            str(check.get("id", "unknown"))
            for check in blocking_checks
            if isinstance(check, dict)
        ]
        actions.append(
            "Resolve blocking readiness check(s): "
            + ", ".join(sorted(set(check_ids)))
        )
    if not actions:
        actions.append("Review, merge, or archive the ready feature bundle.")
    if not report.get("ready"):
        actions.append(f"Inspect readiness details: specspine feature ready {slug} . --json")
    return actions


def _readiness_detail_command(
    slug: str,
    *,
    require_coverage: bool,
    use_policy: bool,
) -> str:
    command = f"specspine feature ready {slug} . --json"
    if require_coverage:
        command += " --require-coverage"
    elif use_policy:
        command += " --policy"
    return command


def _invalid_readiness_record(
    feature: dict[str, object],
    *,
    reason: str,
    require_coverage: bool,
    use_policy: bool,
    policy_coverage_required: bool = False,
    policy: WorkspacePolicy | None = None,
) -> dict[str, Any]:
    slug = str(feature["slug"])
    missing_files = [str(path) for path in feature.get("missing_files", [])]
    record: dict[str, Any] = {
        "feature_id": slug,
        "status": "invalid",
        "ready": False,
        "coverage_required": require_coverage,
        "policy_coverage_required": policy_coverage_required,
        "blocking_checks": 1,
        "gaps": max(1, len(missing_files)),
        "missing_files": missing_files,
        "next_actions": [reason],
        "recommended_commands": [],
    }
    if use_policy and policy is not None:
        record["policy_applied"] = True
        record["policy_source"] = str(policy.source_file)
    return record


def build_readiness_summary(
    root: Path,
    features: list[dict[str, object]] | None = None,
    *,
    require_coverage: bool = False,
    use_policy: bool = False,
) -> dict[str, Any]:
    resolved_root = root.expanduser().resolve()
    feature_bundles = features if features is not None else list_feature_bundles(resolved_root)
    policy = load_workspace_policy(resolved_root) if use_policy else None
    records: list[dict[str, Any]] = []

    for feature in feature_bundles:
        slug = str(feature["slug"])
        status = str(feature.get("status") or "unknown")
        policy_coverage_required = False
        try:
            metadata = read_feature_metadata(resolved_root, slug)
        except InvalidFeatureSlug as error:
            records.append(
                _invalid_readiness_record(
                    feature,
                    reason=str(error),
                    require_coverage=require_coverage,
                    use_policy=use_policy,
                    policy=policy,
                )
            )
            continue

        if policy is not None:
            policy_coverage_required = policy.require_coverage.requires_coverage(
                feature_id=slug,
                metadata=metadata,
                status=status,
            )
        coverage_required = require_coverage or policy_coverage_required

        try:
            report = build_feature_ready_report(
                resolved_root,
                slug,
                require_coverage=coverage_required,
                policy_applied=use_policy,
                coverage_required_by_policy=policy_coverage_required,
                policy_source=str(policy.source_file) if policy is not None else None,
            )
        except InvalidFeatureSlug as error:
            records.append(
                _invalid_readiness_record(
                    feature,
                    reason=str(error),
                    require_coverage=coverage_required,
                    use_policy=use_policy,
                    policy_coverage_required=policy_coverage_required,
                    policy=policy,
                )
            )
            continue

        blocking_checks = [check.as_dict() for check in report.blocking_checks]
        gaps = [dict(gap) for gap in report.gaps]
        record = {
            "feature_id": report.feature_id,
            "status": report.status,
            "ready": report.ready,
            "coverage_required": coverage_required,
            "policy_coverage_required": policy_coverage_required,
            "blocking_checks": len(blocking_checks),
            "blocking_check_ids": [check["id"] for check in blocking_checks],
            "gaps": len(gaps),
            "gap_ids": sorted({str(gap["id"]) for gap in gaps}),
            "missing_files": list(report.missing_files),
            "next_actions": _readiness_next_actions(
                slug,
                {
                    "ready": report.ready,
                    "missing_files": list(report.missing_files),
                    "gaps": gaps,
                    "blocking_checks": blocking_checks,
                },
            ),
            "recommended_commands": [
                _readiness_detail_command(
                    slug,
                    require_coverage=require_coverage,
                    use_policy=use_policy,
                )
            ],
        }
        if use_policy and policy is not None:
            record["policy_applied"] = True
            record["policy_source"] = str(policy.source_file)
        records.append(record)

    ready_count = sum(1 for record in records if record["ready"])
    not_ready_records = [record for record in records if not record["ready"]]
    recommended_commands = [
        _readiness_detail_command(
            str(record["feature_id"]),
            require_coverage=require_coverage,
            use_policy=use_policy,
        )
        for record in not_ready_records
    ]
    if not recommended_commands:
        recommended_commands.append("specspine status . --json --readiness-summary")

    summary: dict[str, Any] = {
        "features_total": len(records),
        "ready": ready_count,
        "not_ready": len(records) - ready_count,
        "blocking_checks_total": sum(int(record["blocking_checks"]) for record in records),
        "gaps_total": sum(int(record["gaps"]) for record in records),
        "coverage_required_total": sum(
            1 for record in records if bool(record["coverage_required"])
        ),
        "features": records,
        "recommended_commands": recommended_commands,
    }
    if use_policy and policy is not None:
        summary["policy_applied"] = True
        summary["policy_source"] = str(policy.source_file)
        summary["policy_source_missing"] = policy.source_missing
        summary["policy_coverage_required_total"] = sum(
            1 for record in records if bool(record["policy_coverage_required"])
        )
    return summary


def build_feature_summaries(
    root: Path,
    features: list[dict[str, object]] | None = None,
    *,
    status_filters: tuple[str, ...] = (),
    ready_filter: bool | None = None,
    priority_filters: tuple[str, ...] = (),
    owner_filters: tuple[str, ...] = (),
    milestone_filters: tuple[str, ...] = (),
    target_release_filters: tuple[str, ...] = (),
    project_filters: tuple[str, ...] = (),
    effort_filters: tuple[str, ...] = (),
    sort_key: str | None = None,
    sort_desc: bool = False,
    require_coverage: bool = False,
    use_policy: bool = False,
) -> list[dict[str, Any]]:
    resolved_root = root.expanduser().resolve()
    summaries: list[dict[str, Any]] = []
    feature_bundles = features if features is not None else list_feature_bundles(resolved_root)
    policy = load_workspace_policy(resolved_root) if use_policy else None

    for feature in feature_bundles:
        slug = str(feature["slug"])
        status = str(feature.get("status") or "unknown")
        try:
            metadata = read_feature_metadata(resolved_root, slug)
        except InvalidFeatureSlug:
            metadata = _empty_feature_metadata()
        policy_coverage_required = False
        if policy is not None:
            policy_coverage_required = policy.require_coverage.requires_coverage(
                feature_id=slug,
                metadata=metadata,
                status=status,
            )
        summary_require_coverage = require_coverage or policy_coverage_required
        try:
            report = build_feature_handoff_report(
                resolved_root,
                slug,
                require_coverage=summary_require_coverage,
            )
        except InvalidFeatureSlug as error:
            summaries.append(
                _invalid_feature_summary(
                    feature,
                    reason=str(error),
                    require_coverage=summary_require_coverage,
                    policy=policy,
                    policy_coverage_required=policy_coverage_required,
                )
            )
            continue
        except FeatureBundleNotFoundError:
            summaries.append(
                _missing_feature_summary(
                    feature,
                    require_coverage=summary_require_coverage,
                    policy=policy,
                    policy_coverage_required=policy_coverage_required,
                )
            )
            continue

        summary = report.summary
        feature_summary = {
            "feature_id": report.feature_id,
            "slug": report.feature_id,
            "status": report.status,
            **metadata.as_dict(),
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
        if summary_require_coverage:
            feature_summary["coverage_required"] = True
        if policy is not None:
            feature_summary["policy_coverage_required"] = policy_coverage_required
            feature_summary["policy_source"] = str(policy.source_file)
        summaries.append(feature_summary)

    return filter_and_sort_feature_summaries(
        summaries,
        status_filters=status_filters,
        ready_filter=ready_filter,
        priority_filters=priority_filters,
        owner_filters=owner_filters,
        milestone_filters=milestone_filters,
        target_release_filters=target_release_filters,
        project_filters=project_filters,
        effort_filters=effort_filters,
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
