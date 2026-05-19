from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .consistency import (
    build_consistency_report,
)
from .coverage import build_coverage_debt_report
from .features import (
    FEATURE_FILE_PATHS,
    InvalidFeatureSlug,
    get_feature_status,
    list_feature_bundles,
    read_feature_metadata,
    validate_feature_slug,
)
from .validation import build_validation_report

AC_ID_RE = re.compile(r"AC\d{3}")
TASK_ID_RE = re.compile(r"(?:TASK|T)\d{3}")
COV_LINK_DONE_RE = re.compile(r"-\s*\[\s*[xX]\s*\]\s+AC\d{3}\s*->")
COV_LINK_TOTAL_RE = re.compile(r"-\s*\[\s*[ xX]\s*\]\s+AC\d{3}\s*->")
CHECKLIST_DONE_RE = re.compile(r"-\s*\[\s*[xX]\s*\]")
CHECKLIST_TOTAL_RE = re.compile(r"-\s*\[\s*[ xX]\s*\]")

VALID_GROUP_BY = ("priority", "status", "project", "effort")

SAFETY_NOTES = (
    "Benchmark report is read-only and advisory.",
    "Does not run tests, invoke subprocesses, call network services, or read tokens.",
    "Recommended commands are advisory and are not executed.",
    "Missing evidence sources degrade gracefully.",
)


@dataclass(frozen=True)
class FeatureMetrics:
    feature_id: str
    status: str
    priority: str
    effort: str
    project: str
    ac_count: int
    task_count: int
    test_count: int
    coverage_pct: float
    validation_pass: int
    validation_fail: int
    consistency_fail: int
    drift_events: int
    lifecycle_duration_days: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "ac_count": self.ac_count,
            "consistency_fail": self.consistency_fail,
            "coverage_pct": self.coverage_pct,
            "drift_events": self.drift_events,
            "effort": self.effort,
            "feature_id": self.feature_id,
            "lifecycle_duration_days": self.lifecycle_duration_days,
            "priority": self.priority,
            "project": self.project,
            "status": self.status,
            "task_count": self.task_count,
            "test_count": self.test_count,
            "validation_fail": self.validation_fail,
            "validation_pass": self.validation_pass,
        }


@dataclass(frozen=True)
class BenchmarkReport:
    root: str
    feature_count: int
    metrics: tuple[FeatureMetrics, ...]
    aggregates: dict[str, Any]
    top_performers: tuple[dict[str, Any], ...]
    improvement_areas: tuple[dict[str, Any], ...]
    trends: dict[str, Any]
    recommendations: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "aggregates": dict(self.aggregates),
            "feature_count": self.feature_count,
            "improvement_areas": list(self.improvement_areas),
            "metrics": [m.as_dict() for m in self.metrics],
            "recommendations": list(self.recommendations),
            "root": self.root,
            "safety_notes": list(self.safety_notes),
            "top_performers": list(self.top_performers),
            "trends": dict(self.trends),
        }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _count_pattern(content: str, pattern: re.Pattern[str]) -> int:
    return len(pattern.findall(content))


def _compute_feature_metrics(slug: str, root: Path) -> FeatureMetrics:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()

    status_report = get_feature_status(resolved_root, slug)
    status = status_report.status or "unknown"

    metadata = read_feature_metadata(resolved_root, slug)
    priority = metadata.priority
    effort = metadata.effort
    project = metadata.project

    ac_count = 0
    task_count = 0
    test_count = 0
    coverage_pct = 0.0

    spec_path = resolved_root / FEATURE_FILE_PATHS["spec"].format(slug=slug)
    exec_path = resolved_root / FEATURE_FILE_PATHS["execution"].format(slug=slug)
    quality_path = resolved_root / FEATURE_FILE_PATHS["quality"].format(slug=slug)

    if spec_path.exists():
        content = _read_text(spec_path)
        ac_count = _count_pattern(content, AC_ID_RE)

    if exec_path.exists():
        content = _read_text(exec_path)
        task_count = _count_pattern(content, TASK_ID_RE)

    if quality_path.exists():
        content = _read_text(quality_path)
        test_count = _count_pattern(content, COV_LINK_TOTAL_RE)
        done_count = _count_pattern(content, COV_LINK_DONE_RE)
        if test_count > 0:
            coverage_pct = round(done_count / test_count * 100, 1)

    validation_pass = 0
    validation_fail = 0
    try:
        val_report = build_validation_report(
            resolved_root,
            include_fusion=True,
            include_features=False,
            include_adapters=False,
        )
        summary = val_report.get("summary", {})
        validation_pass = summary.get("pass", 0)
        validation_fail = summary.get("fail", 0)
    except OSError:
        pass

    consistency_fail = 0
    drift_events = 0
    try:
        cons_report = build_consistency_report(
            resolved_root,
            feature_filter=slug,
        )
        for fc in cons_report.features:
            if fc.feature_id == slug:
                consistency_fail = sum(
                    1 for c in fc.consistency_checks if c.status == "fail"
                )
                break
    except (OSError, InvalidFeatureSlug):
        pass

    try:
        debt_report = build_coverage_debt_report(resolved_root)
        for feat in debt_report.get("features", []):
            if feat.get("feature_id") == slug:
                drift_events = feat.get("missing_acceptance_criteria", 0)
                break
    except OSError:
        pass

    lifecycle_duration_days = 0.0

    return FeatureMetrics(
        feature_id=slug,
        status=status,
        priority=priority,
        effort=effort,
        project=project,
        ac_count=ac_count,
        task_count=task_count,
        test_count=test_count,
        coverage_pct=coverage_pct,
        validation_pass=validation_pass,
        validation_fail=validation_fail,
        consistency_fail=consistency_fail,
        drift_events=drift_events,
        lifecycle_duration_days=lifecycle_duration_days,
    )


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n % 2 == 1:
        return sorted_vals[n // 2]
    return (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2.0


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    idx = (pct / 100.0) * (n - 1)
    lower = int(idx)
    upper = lower + 1
    if upper >= n:
        return sorted_vals[-1]
    frac = idx - lower
    return sorted_vals[lower] * (1 - frac) + sorted_vals[upper] * frac


def _aggregate_metrics(
    metrics: list[FeatureMetrics],
    group_by: str,
) -> dict[str, Any]:
    if not metrics:
        return {
            "groups": {},
            "overall": {
                "avg_ac_count": 0.0,
                "avg_consistency_fail": 0.0,
                "avg_coverage": 0.0,
                "avg_drift_events": 0.0,
                "avg_lifecycle_duration_days": 0.0,
                "avg_task_count": 0.0,
                "avg_test_count": 0.0,
                "avg_validation_fail": 0.0,
                "avg_validation_pass": 0.0,
                "median_ac_count": 0.0,
                "median_consistency_fail": 0.0,
                "median_coverage": 0.0,
                "median_drift_events": 0.0,
                "median_lifecycle_duration_days": 0.0,
                "median_task_count": 0.0,
                "median_test_count": 0.0,
                "median_validation_fail": 0.0,
                "median_validation_pass": 0.0,
                "p95_coverage": 0.0,
                "p95_lifecycle_duration_days": 0.0,
                "p95_test_count": 0.0,
                "total_features": 0,
            },
        }

    ac_counts = [m.ac_count for m in metrics]
    task_counts = [m.task_count for m in metrics]
    test_counts = [m.test_count for m in metrics]
    coverage_vals = [m.coverage_pct for m in metrics]
    validation_pass_vals = [m.validation_pass for m in metrics]
    validation_fail_vals = [m.validation_fail for m in metrics]
    consistency_fail_vals = [m.consistency_fail for m in metrics]
    drift_vals = [m.drift_events for m in metrics]
    duration_vals = [m.lifecycle_duration_days for m in metrics]

    overall = {
        "avg_ac_count": round(sum(ac_counts) / len(ac_counts), 2),
        "avg_consistency_fail": round(sum(consistency_fail_vals) / len(consistency_fail_vals), 2),
        "avg_coverage": round(sum(coverage_vals) / len(coverage_vals), 2),
        "avg_drift_events": round(sum(drift_vals) / len(drift_vals), 2),
        "avg_lifecycle_duration_days": round(sum(duration_vals) / len(duration_vals), 2),
        "avg_task_count": round(sum(task_counts) / len(task_counts), 2),
        "avg_test_count": round(sum(test_counts) / len(test_counts), 2),
        "avg_validation_fail": round(sum(validation_fail_vals) / len(validation_fail_vals), 2),
        "avg_validation_pass": round(sum(validation_pass_vals) / len(validation_pass_vals), 2),
        "median_ac_count": round(_median(ac_counts), 2),
        "median_consistency_fail": round(_median(consistency_fail_vals), 2),
        "median_coverage": round(_median(coverage_vals), 2),
        "median_drift_events": round(_median(drift_vals), 2),
        "median_lifecycle_duration_days": round(_median(duration_vals), 2),
        "median_task_count": round(_median(task_counts), 2),
        "median_test_count": round(_median(test_counts), 2),
        "median_validation_fail": round(_median(validation_fail_vals), 2),
        "median_validation_pass": round(_median(validation_pass_vals), 2),
        "p95_coverage": round(_percentile(coverage_vals, 95), 2),
        "p95_lifecycle_duration_days": round(_percentile(duration_vals, 95), 2),
        "p95_test_count": round(_percentile(test_counts, 95), 2),
        "total_features": len(metrics),
    }

    groups: dict[str, list[FeatureMetrics]] = {}
    for m in metrics:
        if group_by == "priority":
            key = m.priority
        elif group_by == "status":
            key = m.status
        elif group_by == "project":
            key = m.project
        elif group_by == "effort":
            key = m.effort
        else:
            key = "unknown"
        groups.setdefault(key, []).append(m)

    group_stats: dict[str, Any] = {}
    for key, group_metrics in sorted(groups.items()):
        g_cov = [m.coverage_pct for m in group_metrics]
        g_ac = [m.ac_count for m in group_metrics]
        g_drift = [m.drift_events for m in group_metrics]
        group_stats[key] = {
            "count": len(group_metrics),
            "avg_coverage": round(sum(g_cov) / len(g_cov), 2) if g_cov else 0.0,
            "avg_ac_count": round(sum(g_ac) / len(g_ac), 2) if g_ac else 0.0,
            "avg_drift_events": round(sum(g_drift) / len(g_drift), 2) if g_drift else 0.0,
            "median_coverage": round(_median(g_cov), 2),
            "features": [m.feature_id for m in group_metrics],
        }

    return {
        "groups": group_stats,
        "overall": overall,
    }


def _identify_top_performers(metrics: list[FeatureMetrics]) -> list[dict[str, Any]]:
    if not metrics:
        return []

    scored = []
    for m in metrics:
        score = (
            m.coverage_pct * 0.4
            + max(0, 100 - m.drift_events * 10) * 0.3
            + max(0, 100 - m.consistency_fail * 20) * 0.3
        )
        scored.append((score, m))

    scored.sort(key=lambda x: -x[0])

    top = scored[:5]
    return [
        {
            "feature_id": m.feature_id,
            "score": round(score, 2),
            "coverage_pct": m.coverage_pct,
            "drift_events": m.drift_events,
            "consistency_fail": m.consistency_fail,
        }
        for score, m in top
    ]


def _identify_improvement_areas(metrics: list[FeatureMetrics]) -> list[dict[str, Any]]:
    if not metrics:
        return []

    scored = []
    for m in metrics:
        score = (
            (100 - m.coverage_pct) * 0.4
            + m.drift_events * 10 * 0.3
            + m.consistency_fail * 20 * 0.3
        )
        scored.append((score, m))

    scored.sort(key=lambda x: -x[0])

    bottom = scored[:5]
    return [
        {
            "feature_id": m.feature_id,
            "score": round(score, 2),
            "coverage_pct": m.coverage_pct,
            "drift_events": m.drift_events,
            "consistency_fail": m.consistency_fail,
            "primary_issue": _primary_issue(m),
        }
        for score, m in bottom
    ]


def _primary_issue(m: FeatureMetrics) -> str:
    issues = []
    if m.coverage_pct < 50:
        issues.append("low_coverage")
    if m.drift_events > 2:
        issues.append("high_drift")
    if m.consistency_fail > 0:
        issues.append("consistency_failures")
    if m.ac_count > 0 and m.test_count == 0:
        issues.append("no_test_links")
    return issues[0] if issues else "needs_review"


def _compute_trends(metrics: list[FeatureMetrics]) -> dict[str, Any]:
    if not metrics:
        return {
            "coverage_trend": "stable",
            "validation_pass_rate_trend": "stable",
            "drift_frequency_trend": "stable",
            "coverage_by_status": {},
            "drift_by_priority": {},
        }

    status_coverage: dict[str, list[float]] = {}
    priority_drift: dict[str, list[int]] = {}

    for m in metrics:
        status_coverage.setdefault(m.status, []).append(m.coverage_pct)
        priority_drift.setdefault(m.priority, []).append(m.drift_events)

    coverage_by_status = {}
    for status, vals in sorted(status_coverage.items()):
        coverage_by_status[status] = round(sum(vals) / len(vals), 2)

    drift_by_priority = {}
    for prio, vals in sorted(priority_drift.items()):
        drift_by_priority[prio] = round(sum(vals) / len(vals), 2)

    all_coverage = [m.coverage_pct for m in metrics]
    avg_cov = sum(all_coverage) / len(all_coverage) if all_coverage else 0

    total_drift = sum(m.drift_events for m in metrics)
    total_val_pass = sum(m.validation_pass for m in metrics)
    total_val_fail = sum(m.validation_fail for m in metrics)
    val_pass_rate = (
        total_val_pass / (total_val_pass + total_val_fail)
        if (total_val_pass + total_val_fail) > 0
        else 1.0
    )

    coverage_trend = "stable"
    if avg_cov >= 80:
        coverage_trend = "healthy"
    elif avg_cov < 30:
        coverage_trend = "declining"

    drift_trend = "stable"
    avg_drift = total_drift / len(metrics) if metrics else 0
    if avg_drift > 5:
        drift_trend = "increasing"
    elif avg_drift < 1:
        drift_trend = "improving"

    val_trend = "stable"
    if val_pass_rate >= 0.9:
        val_trend = "healthy"
    elif val_pass_rate < 0.5:
        val_trend = "declining"

    return {
        "coverage_trend": coverage_trend,
        "validation_pass_rate_trend": val_trend,
        "drift_frequency_trend": drift_trend,
        "coverage_by_status": coverage_by_status,
        "drift_by_priority": drift_by_priority,
    }


def _generate_recommendations(
    metrics: list[FeatureMetrics],
    aggregates: dict[str, Any],
    top_performers: list[dict[str, Any]],
    improvement_areas: list[dict[str, Any]],
    trends: dict[str, Any],
) -> tuple[str, ...]:
    recs: list[str] = []

    overall = aggregates.get("overall", {})
    avg_coverage = overall.get("avg_coverage", 0)
    if avg_coverage < 50:
        recs.append(
            f"Average AC coverage is {avg_coverage}%; prioritize linking test files to acceptance criteria"
        )

    avg_drift = overall.get("avg_drift_events", 0)
    if avg_drift > 2:
        recs.append(
            f"Average drift events per feature is {avg_drift}; review consistency scan results"
        )

    if improvement_areas:
        low_cov_features = [
            a["feature_id"]
            for a in improvement_areas
            if a.get("coverage_pct", 100) < 30
        ]
        if low_cov_features:
            recs.append(
                f"Features with coverage below 30%: {', '.join(low_cov_features[:3])}"
            )

    coverage_trend = trends.get("coverage_trend", "stable")
    if coverage_trend == "declining":
        recs.append("Overall coverage trend is declining; review quality gates")

    if not recs:
        recs.append("No critical recommendations; continue current practices")

    return tuple(recs[:5])


def build_benchmark_report(
    root: Path,
    feature_filter: str | None = None,
    group_by: str = "priority",
) -> BenchmarkReport:
    resolved_root = root.expanduser().resolve()

    if group_by not in VALID_GROUP_BY:
        group_by = "priority"

    bundles = list_feature_bundles(resolved_root)
    slugs = [b["slug"] for b in bundles]

    if feature_filter:
        try:
            validate_feature_slug(feature_filter)
            if feature_filter in slugs:
                slugs = [feature_filter]
            else:
                slugs = []
        except InvalidFeatureSlug:
            slugs = []

    metrics: list[FeatureMetrics] = []
    for slug in sorted(slugs):
        try:
            m = _compute_feature_metrics(slug, resolved_root)
            metrics.append(m)
        except (InvalidFeatureSlug, OSError):
            continue

    aggregates = _aggregate_metrics(metrics, group_by)
    top_performers = _identify_top_performers(metrics)
    improvement_areas = _identify_improvement_areas(metrics)
    trends = _compute_trends(metrics)
    recommendations = _generate_recommendations(
        metrics, aggregates, top_performers, improvement_areas, trends
    )

    return BenchmarkReport(
        root=str(resolved_root),
        feature_count=len(metrics),
        metrics=tuple(metrics),
        aggregates=aggregates,
        top_performers=tuple(top_performers),
        improvement_areas=tuple(improvement_areas),
        trends=trends,
        recommendations=recommendations,
        safety_notes=SAFETY_NOTES,
    )


def render_benchmark_json(report: BenchmarkReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_benchmark_text(report: BenchmarkReport) -> str:
    lines: list[str] = []
    lines.append(f"SpecSpine Benchmark Report: {report.root}")
    lines.append(f"Features Analyzed: {report.feature_count}")
    lines.append("")

    overall = report.aggregates.get("overall", {})
    lines.append("Overall Aggregates:")
    lines.append(f"  Average AC count: {overall.get('avg_ac_count', 0)}")
    lines.append(f"  Average task count: {overall.get('avg_task_count', 0)}")
    lines.append(f"  Average test count: {overall.get('avg_test_count', 0)}")
    lines.append(f"  Average coverage: {overall.get('avg_coverage', 0)}%")
    lines.append(f"  Median coverage: {overall.get('median_coverage', 0)}%")
    lines.append(f"  P95 coverage: {overall.get('p95_coverage', 0)}%")
    lines.append(f"  Average drift events: {overall.get('avg_drift_events', 0)}")
    lines.append(f"  Average validation pass: {overall.get('avg_validation_pass', 0)}")
    lines.append(f"  Average validation fail: {overall.get('avg_validation_fail', 0)}")
    lines.append("")

    groups = report.aggregates.get("groups", {})
    if groups:
        lines.append("Groups:")
        for key, stats in sorted(groups.items()):
            lines.append(f"  {key}:")
            lines.append(f"    count: {stats['count']}")
            lines.append(f"    avg coverage: {stats['avg_coverage']}%")
            lines.append(f"    features: {', '.join(stats['features'][:5])}")
        lines.append("")

    if report.top_performers:
        lines.append("Top Performers:")
        for p in report.top_performers:
            lines.append(
                f"  {p['feature_id']}: score={p['score']}, "
                f"coverage={p['coverage_pct']}%, drift={p['drift_events']}"
            )
        lines.append("")

    if report.improvement_areas:
        lines.append("Improvement Areas:")
        for a in report.improvement_areas:
            lines.append(
                f"  {a['feature_id']}: score={a['score']}, "
                f"coverage={a['coverage_pct']}%, issue={a.get('primary_issue', 'needs_review')}"
            )
        lines.append("")

    trends = report.trends
    lines.append("Trends:")
    lines.append(f"  Coverage trend: {trends.get('coverage_trend', 'stable')}")
    lines.append(f"  Validation trend: {trends.get('validation_pass_rate_trend', 'stable')}")
    lines.append(f"  Drift trend: {trends.get('drift_frequency_trend', 'stable')}")
    cov_by_status = trends.get("coverage_by_status", {})
    if cov_by_status:
        lines.append("  Coverage by status:")
        for status, avg in sorted(cov_by_status.items()):
            lines.append(f"    {status}: {avg}%")
    lines.append("")

    if report.recommendations:
        lines.append("Recommendations:")
        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"  {i}. {rec}")
        lines.append("")

    lines.append("Safety Notes:")
    for note in report.safety_notes:
        lines.append(f"  - {note}")

    return "\n".join(lines) + "\n"
