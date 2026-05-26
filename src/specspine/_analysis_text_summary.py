from __future__ import annotations

from .analysis_models import AnalysisReport

__all__ = [
    "render_analysis_summary",
]


def render_analysis_summary(report: AnalysisReport) -> list[str]:
    summary = report.summary
    severity_counts = summary["issue_counts_by_severity"]
    assert isinstance(severity_counts, dict)
    return [
        "SpecSpine analysis",
        f"Root: {report.root}",
        f"Feature filter: {report.feature_filter or 'all'}",
        (
            "Summary: "
            f"features={summary['features_analyzed']} "
            f"ready={summary['features_ready']} "
            f"issues={summary['issues_total']} "
            f"critical={severity_counts.get('critical', 0)} "
            f"high={severity_counts.get('high', 0)} "
            f"medium={severity_counts.get('medium', 0)} "
            f"low={severity_counts.get('low', 0)}"
        ),
        "",
        "Issues:",
    ]
