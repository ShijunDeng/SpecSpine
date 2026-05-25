from __future__ import annotations

import json

from .benchmark_models import BenchmarkReport

__all__ = [
    "render_benchmark_json",
    "render_benchmark_text",
]


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
