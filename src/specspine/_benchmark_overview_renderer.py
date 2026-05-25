from __future__ import annotations

from .benchmark_models import BenchmarkReport


def _render_benchmark_header(report: BenchmarkReport) -> list[str]:
    lines: list[str] = []
    lines.append(f"SpecSpine Benchmark Report: {report.root}")
    lines.append(f"Features Analyzed: {report.feature_count}")
    lines.append("")
    return lines


def _render_overview_aggregates(report: BenchmarkReport) -> list[str]:
    lines: list[str] = []
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
    return lines


def _render_groups(report: BenchmarkReport) -> list[str]:
    lines: list[str] = []
    groups = report.aggregates.get("groups", {})
    if groups:
        lines.append("Groups:")
        for key, stats in sorted(groups.items()):
            lines.append(f"  {key}:")
            lines.append(f"    count: {stats['count']}")
            lines.append(f"    avg coverage: {stats['avg_coverage']}%")
            lines.append(f"    features: {', '.join(stats['features'][:5])}")
        lines.append("")
    return lines


__all__ = [
    "_render_benchmark_header",
    "_render_overview_aggregates",
    "_render_groups",
]
