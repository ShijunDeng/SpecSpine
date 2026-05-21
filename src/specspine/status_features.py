from __future__ import annotations

from pathlib import Path
from typing import Any

from .features import (
    FEATURE_PRIORITIES,
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    build_feature_handoff_report,
    list_feature_bundles,
    read_feature_metadata,
)
from .policy import WorkspacePolicy, load_workspace_policy
from .status_workspace import (
    FEATURE_SUMMARY_PRIORITY_FILTERS,
    FEATURE_SUMMARY_READY_VALUES,
    FEATURE_SUMMARY_SORT_KEYS,
    FEATURE_SUMMARY_STATUS_FILTERS,
    InvalidFeatureSummaryOption,
    _FEATURE_SUMMARY_DEFAULT_VALUES,
    _FEATURE_SUMMARY_EFFORT_ORDER,
    _FEATURE_SUMMARY_PRIORITY_ORDER,
    _FEATURE_SUMMARY_STATUS_ORDER,
    _empty_count_summary,
    _empty_feature_metadata,
)

__all__ = [
    "parse_feature_summary_status_filters",
    "parse_feature_summary_ready_filter",
    "parse_feature_summary_priority_filters",
    "parse_feature_summary_owner_filters",
    "parse_feature_summary_metadata_filters",
    "parse_feature_summary_sort_key",
    "_feature_summary_status_bucket",
    "_feature_summary_matches_status",
    "_feature_summary_matches_priority",
    "_feature_summary_matches_owner",
    "_feature_summary_matches_metadata",
    "_feature_summary_tasks_open",
    "_feature_summary_sort_value",
    "_feature_summary_sort_metadata_desc",
    "filter_and_sort_feature_summaries",
    "_invalid_feature_summary",
    "_missing_feature_summary",
    "build_feature_summaries",
]

FEATURE_SUMMARY_PRIORITY_FILTERS_LOCAL = (*FEATURE_PRIORITIES, "unknown")


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
        if normalized not in FEATURE_SUMMARY_PRIORITY_FILTERS_LOCAL:
            allowed = ", ".join(FEATURE_SUMMARY_PRIORITY_FILTERS_LOCAL)
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
    if status in FEATURE_SUMMARY_STATUS_FILTERS:
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
