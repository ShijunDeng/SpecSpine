from __future__ import annotations

from .feature_bundle import FeatureTraceReport


def render_trace_header(report: FeatureTraceReport) -> list[str]:
    summary = report.summary
    lines = [
        f"Feature trace: {report.feature_id}",
        f"Status: {report.status}",
        "Sources:",
    ]
    for kind, source in report.sources.items():
        marker = "ok" if source["exists"] else "missing"
        lines.append(f"- [{marker}] {kind}: {source['path']}")

    lines.extend(
        [
            (
                "Summary: "
                f"total={summary['total']} "
                f"done={summary['done']} "
                f"open={summary['open']}"
            ),
            (
                "Counts: "
                f"ac={summary['acceptance_criteria']['total']} "
                f"tasks={summary['tasks']['total']} "
                f"quality={summary['quality_checks']['total']} "
                f"test_plan={summary['test_plan']['total']}"
            ),
        ]
    )
    return lines


__all__ = [
    "render_trace_header",
]
