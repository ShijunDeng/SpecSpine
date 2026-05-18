from __future__ import annotations

import json
from pathlib import Path

from .features import (
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


SAFETY_NOTES = (
    "Read-only local report: does not write files.",
    "Does not run tests or invoke subprocesses.",
    "Does not call network services, GitHub, or upstream CLIs.",
    "Does not read environment variables or tokens.",
    "Recommended commands are advisory and are not executed.",
)


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


def _recommendation_sort_key(feature: dict[str, object]) -> tuple[object, ...]:
    status = str(feature["status"])
    coverage = feature["coverage_state"]  # type: ignore[assignment]
    coverage_state = str(coverage["state"])  # type: ignore[index]
    task_counts = feature["task_counts"]  # type: ignore[assignment]
    return (
        bool(feature["ready"]),
        -len(feature["blocking_checks"]),  # type: ignore[arg-type]
        -int(feature["gap_count"]),
        -int(task_counts["open"]),  # type: ignore[index]
        0 if coverage_state in {"missing", "partial"} else 1,
        0 if status not in {"implemented", "validated", "archived"} else 1,
        str(feature["feature_id"]),
    )


def _recommendation_reason(feature: dict[str, object]) -> str:
    if not feature["ready"]:
        checks = feature["blocking_checks"]  # type: ignore[assignment]
        if checks:
            first = checks[0]  # type: ignore[index]
            return f"Not ready: {first['id']}."
        return "Not ready."
    coverage = feature["coverage_state"]  # type: ignore[assignment]
    if coverage["state"] in {"missing", "partial"}:  # type: ignore[index]
        return f"Coverage is {coverage['state']}."  # type: ignore[index]
    return "Ready feature included for trend review."


def _build_recommendations(
    features: list[dict[str, object]],
    *,
    limit: int | None,
) -> list[dict[str, object]]:
    ranked = sorted(features, key=_recommendation_sort_key)
    rows = [
        {
            "feature_id": feature["feature_id"],
            "rank": index,
            "reason": _recommendation_reason(feature),
            "recommended_commands": feature["recommended_commands"],
            "status": feature["status"],
        }
        for index, feature in enumerate(ranked, start=1)
    ]
    if limit is not None:
        return rows[:limit]
    return rows


def _count_by(features: list[dict[str, object]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for feature in features:
        value = str(feature[key])
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


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


def render_retrospective_json(report: dict[str, object]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def render_retrospective_text(report: dict[str, object]) -> str:
    summary = report["summary"]  # type: ignore[index]
    lines = [
        f"Retrospective report: {report['root']}",
        f"Feature filter: {report['feature_filter'] or 'all'}",
        (
            "Summary: "
            f"features={summary['features_total']} "
            f"ready={summary['features_ready']} "
            f"not_ready={summary['features_not_ready']} "
            f"open_tasks={summary['open_tasks']} "
            f"blocking={summary['blocking_checks']} "
            f"gaps={summary['gap_count']}"
        ),
        "",
        "Recommendations:",
    ]
    recommendations = report["recommendations"]  # type: ignore[index]
    if recommendations:
        for row in recommendations:  # type: ignore[union-attr]
            lines.append(
                f"- {row['rank']}. {row['feature_id']} ({row['status']}): {row['reason']}"
            )
    else:
        lines.append("- None.")

    missing_feature = summary.get("missing_feature")
    if missing_feature:
        lines.extend(["", f"Missing feature bundle: {missing_feature}"])

    lines.extend(["", "Safety notes:"])
    lines.extend(f"- {note}" for note in report["safety_notes"])  # type: ignore[index]
    return "\n".join(lines) + "\n"


def _detect_anti_patterns(features: list) -> list:
    """Detect common anti-patterns across feature bundles."""
    patterns = []
    for f in features:
        fid = f.get("feature_id", "")
        coverage = f.get("coverage_state", {})
        gaps = f.get("gaps", [])
        blocking = f.get("blocking_checks", [])
        status = f.get("status", "")
        ac_count = coverage.get("total_acceptance_criteria", 0)
        links = coverage.get("total_links", 0)
        if blocking:
            for b in blocking:
                if "coverage" in b.get("id", "").lower():
                    patterns.append({
                        "anti_pattern_id": f"AP-{fid}-cov",
                        "type": "coverage_gap",
                        "severity": "high",
                        "feature_id": fid,
                        "description": f"Feature {fid} has coverage gaps",
                        "recommendation": "Add test coverage links for all ACs"
                    })
        if gaps:
            patterns.append({
                "anti_pattern_id": f"AP-{fid}-gaps",
                "type": "trace_gaps",
                "severity": "medium",
                "feature_id": fid,
                "description": f"Feature {fid} has {len(gaps)} trace gaps",
                "recommendation": "Complete traceability between ACs, tasks, and tests"
            })
        if ac_count > 0 and links == 0:
            patterns.append({
                "anti_pattern_id": f"AP-{fid}-no-tests",
                "type": "no_test_coverage",
                "severity": "high",
                "feature_id": fid,
                "description": f"Feature {fid} has {ac_count} ACs but no test coverage links",
                "recommendation": "Add test coverage links in quality file"
            })
        if status == "implemented":
            patterns.append({
                "anti_pattern_id": f"AP-{fid}-stalled",
                "type": "stalled_feature",
                "severity": "low",
                "feature_id": fid,
                "description": f"Feature {fid} stuck in implemented status",
                "recommendation": "Run feature ready and advance to validated"
            })
    return patterns


def _generate_improvements(anti_patterns: list, analytics: dict) -> list:
    """Generate improvement recommendations from anti-patterns."""
    improvements = []
    by_type = {}
    for ap in anti_patterns:
        by_type.setdefault(ap["type"], []).append(ap)
    if by_type.get("coverage_gap"):
        improvements.append({
            "id": "IMP-001",
            "priority": "high",
            "description": "Close coverage gaps across features",
            "action": "Add test coverage links for all acceptance criteria",
            "affected_features": [ap["feature_id"] for ap in by_type["coverage_gap"]]
        })
    if by_type.get("no_test_coverage"):
        improvements.append({
            "id": "IMP-002",
            "priority": "high",
            "description": "Add test coverage to features without any links",
            "action": "Map each AC to at least one test file",
            "affected_features": [ap["feature_id"] for ap in by_type["no_test_coverage"]]
        })
    if by_type.get("trace_gaps"):
        improvements.append({
            "id": "IMP-003",
            "priority": "medium",
            "description": "Complete traceability for features with gaps",
            "action": "Link ACs to tasks and tests in traceability export",
            "affected_features": [ap["feature_id"] for ap in by_type["trace_gaps"]]
        })
    if by_type.get("stalled_feature"):
        improvements.append({
            "id": "IMP-004",
            "priority": "low",
            "description": "Advance stalled features",
            "action": "Run feature ready and set status to validated",
            "affected_features": [ap["feature_id"] for ap in by_type["stalled_feature"]]
        })
    return improvements


def _workspace_analytics(features: list) -> dict:
    """Compute aggregate workspace analytics."""
    total = len(features)
    by_status = {}
    readiness_scores = []
    coverage_completeness = []
    for f in features:
        s = f.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1
        readiness = f.get("readiness_counts", {})
        total_checks = readiness.get("total", 0)
        pass_checks = readiness.get("pass", 0)
        score = (pass_checks / total_checks * 100) if total_checks > 0 else 0
        readiness_scores.append(score)
        coverage = f.get("coverage_state", {})
        ac_total = coverage.get("total_acceptance_criteria", 0)
        links = coverage.get("total_links", 0)
        cov = (links / ac_total * 100) if ac_total > 0 else 0
        coverage_completeness.append(cov)
    avg_readiness = sum(readiness_scores) / len(readiness_scores) if readiness_scores else 0
    avg_coverage = sum(coverage_completeness) / len(coverage_completeness) if coverage_completeness else 0
    return {
        "total_features": total,
        "by_status": by_status,
        "avg_readiness_score": round(avg_readiness, 1),
        "avg_coverage_completeness": round(avg_coverage, 1)
    }


def build_retrospective_analytics_report(root, *, include_improvements=False, feature_slug=None):
    """Build retrospective analytics report with anti-pattern detection."""
    from pathlib import Path
    resolved_root = Path(root).expanduser().resolve()
    features_data = build_retrospective_report(resolved_root, feature_slug=feature_slug)
    features = features_data.get("features", [])
    anti_patterns = _detect_anti_patterns(features)
    analytics = _workspace_analytics(features)
    improvements = _generate_improvements(anti_patterns, analytics) if include_improvements else []
    return {
        "analytics": analytics,
        "anti_patterns": anti_patterns,
        "features": features,
        "feature_filter": feature_slug,
        "improvements": improvements,
        "recommendations": features_data.get("recommendations", []),
        "root": str(resolved_root),
        "summary": features_data.get("summary", {}),
        "themes": features_data.get("themes", {})
    }


def render_retrospective_analytics_json(report: dict) -> str:
    """Render retrospective analytics report as JSON."""
    import json
    return json.dumps(report, indent=2, sort_keys=True) + "\n"
