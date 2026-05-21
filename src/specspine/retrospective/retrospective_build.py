from __future__ import annotations

from pathlib import Path

from ..features import (
    FEATURE_STATUSES,
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
    build_feature_ready_report,
    build_feature_tests_report,
    build_feature_trace_report,
    list_feature_bundles,
    read_feature_metadata,
    validate_feature_slug,
)

from .retrospective_constants import SAFETY_NOTES


def _recommended_feature_commands(slug: str) -> list[str]:
    return [
        f"specspine feature ready {slug} . --json --require-coverage",
        f"specspine feature trace {slug} . --json",
        f"specspine feature tests {slug} . --json",
        f"specspine verify matrix {slug} . --json",
        f"specspine review packet . --feature {slug} --json",
    ]


def _workspace_commands(feature_filter: str | None) -> list[str]:
    commands = ["specspine retrospective report . --json"]
    if feature_filter:
        commands.append(
            f"specspine retrospective report . --feature {feature_filter} --json"
        )
    commands.extend(
        [
            "specspine status . --json --validate --feature-summaries",
            "specspine coverage debt . --json",
            "specspine validate . --fusion --features",
        ]
    )
    return commands


def _coverage_state(tests_report: object) -> dict[str, object]:
    acceptance = getattr(tests_report, "acceptance_criteria")
    coverage = getattr(tests_report, "test_coverage")
    total = len(acceptance)
    completed_links = [
        link for link in coverage if link.done and link.target_exists
    ]
    covered_ids = {
        link.acceptance_criterion_id
        for link in completed_links
    }
    missing_ids = [
        item.id for item in acceptance if item.id not in covered_ids
    ]
    if total == 0:
        state = "not_applicable"
    elif not coverage:
        state = "missing"
    elif missing_ids:
        state = "partial"
    else:
        state = "complete"
    return {
        "completed_links": len(completed_links),
        "missing_acceptance_criteria": missing_ids,
        "state": state,
        "total_acceptance_criteria": total,
        "total_links": len(coverage),
    }


def _feature_record(root: Path, slug: str) -> dict[str, object]:
    metadata = read_feature_metadata(root, slug)
    trace_report = build_feature_trace_report(root, slug)
    ready_report = build_feature_ready_report(root, slug, require_coverage=True)
    tests_report = build_feature_tests_report(root, slug)
    coverage = _coverage_state(tests_report)
    trace_summary = trace_report.summary
    task_counts = dict(trace_summary["tasks"])  # type: ignore[index]
    readiness_counts = dict(ready_report.summary)
    blocking_checks = [check.as_dict() for check in ready_report.blocking_checks]
    source_files = [
        str(source["path"])
        for source in trace_report.sources.values()
        if bool(source["exists"])
    ]

    return {
        "blocking_checks": blocking_checks,
        "coverage_state": coverage,
        "feature_id": slug,
        "gap_count": len(trace_report.gaps),
        "gaps": [dict(gap) for gap in trace_report.gaps],
        "owner": metadata.owner,
        "priority": metadata.priority,
        "readiness_counts": readiness_counts,
        "ready": ready_report.ready,
        "recommended_commands": _recommended_feature_commands(slug),
        "source_files": source_files,
        "status": ready_report.status,
        "task_counts": task_counts,
    }


def _empty_report(
    root: Path,
    *,
    feature_filter: str | None,
    missing_feature: str | None = None,
    limit: int | None = None,
) -> dict[str, object]:
    return {
        "features": [],
        "feature_filter": feature_filter,
        "recommendations": [],
        "recommended_commands": _workspace_commands(feature_filter),
        "root": str(root),
        "safety_notes": list(SAFETY_NOTES),
        "summary": _summary([], missing_feature=missing_feature),
        "themes": _themes([]),
    }


def _count_by(features: list[dict[str, object]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for feature in features:
        value = str(feature[key])
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _summary(
    features: list[dict[str, object]],
    *,
    missing_feature: str | None,
) -> dict[str, object]:
    total = len(features)
    ready = sum(1 for feature in features if bool(feature["ready"]))
    open_tasks = sum(
        int(feature["task_counts"]["open"])  # type: ignore[index]
        for feature in features
    )
    blocking_checks = sum(
        len(feature["blocking_checks"])  # type: ignore[arg-type]
        for feature in features
    )
    gaps = sum(int(feature["gap_count"]) for feature in features)
    missing_coverage = sum(
        1
        for feature in features
        if feature["coverage_state"]["state"] in {"missing", "partial"}  # type: ignore[index]
    )
    return {
        "blocking_checks": blocking_checks,
        "features_missing_coverage": missing_coverage,
        "features_not_ready": total - ready,
        "features_ready": ready,
        "features_total": total,
        "gap_count": gaps,
        "missing_feature": missing_feature,
        "open_tasks": open_tasks,
        "recommendable_features": total,
        "statuses": _count_by(features, "status"),
    }


def _themes(features: list[dict[str, object]]) -> dict[str, object]:
    blockers: dict[str, int] = {}
    gaps: dict[str, int] = {}
    coverage: dict[str, int] = {}
    release_readiness_issues = 0
    features_with_open_tasks = 0
    open_tasks_total = 0

    for feature in features:
        task_counts = feature["task_counts"]  # type: ignore[assignment]
        open_tasks = int(task_counts["open"])  # type: ignore[index]
        if open_tasks:
            features_with_open_tasks += 1
            open_tasks_total += open_tasks

        coverage_state = str(feature["coverage_state"]["state"])  # type: ignore[index]
        coverage[coverage_state] = coverage.get(coverage_state, 0) + 1

        for check in feature["blocking_checks"]:  # type: ignore[union-attr]
            check_id = str(check["id"])
            blockers[check_id] = blockers.get(check_id, 0) + 1
            if check_id == "feature.release_readiness":
                release_readiness_issues += 1

        for gap in feature["gaps"]:  # type: ignore[union-attr]
            gap_id = str(gap["id"])
            gaps[gap_id] = gaps.get(gap_id, 0) + 1

    return {
        "blocking_checks": dict(sorted(blockers.items())),
        "coverage_states": dict(sorted(coverage.items())),
        "gaps": dict(sorted(gaps.items())),
        "open_tasks": {
            "features": features_with_open_tasks,
            "total": open_tasks_total,
        },
        "release_readiness_issues": release_readiness_issues,
        "statuses": _count_by(features, "status"),
    }


def build_retrospective_report(
    root: Path,
    *,
    feature_slug: str | None = None,
    limit: int | None = None,
) -> dict[str, object]:
    if limit is not None and limit < 0:
        raise ValueError("limit must be a nonnegative integer")

    resolved_root = root.expanduser().resolve()
    if not resolved_root.exists():
        raise FileNotFoundError(f"Path does not exist: {resolved_root}")
    if not resolved_root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {resolved_root}")
    if feature_slug is not None:
        feature_slug = validate_feature_slug(feature_slug)

    bundles = list_feature_bundles(resolved_root)
    slugs = [str(bundle["slug"]) for bundle in bundles]
    if feature_slug is not None:
        if feature_slug not in slugs:
            return _empty_report(
                resolved_root,
                feature_filter=feature_slug,
                missing_feature=feature_slug,
                limit=limit,
            )
        slugs = [feature_slug]

    features: list[dict[str, object]] = []
    for slug in slugs:
        try:
            features.append(_feature_record(resolved_root, slug))
        except (FeatureBundleNotFoundError, InvalidFeatureSlug):
            continue

    from .retrospective_recommendations import _build_recommendations

    return {
        "features": features,
        "feature_filter": feature_slug,
        "recommendations": _build_recommendations(features, limit=limit),
        "recommended_commands": _workspace_commands(feature_slug),
        "root": str(resolved_root),
        "safety_notes": list(SAFETY_NOTES),
        "summary": _summary(features, missing_feature=None),
        "themes": _themes(features),
    }


def retrospective_report_exit_code(report: dict[str, object]) -> int:
    summary = report.get("summary", {})
    if isinstance(summary, dict) and summary.get("missing_feature"):
        return 1
    return 0


__all__ = [
    "_coverage_state",
    "_count_by",
    "_empty_report",
    "_feature_record",
    "_summary",
    "_themes",
    "_workspace_commands",
    "build_retrospective_report",
    "retrospective_report_exit_code",
]
