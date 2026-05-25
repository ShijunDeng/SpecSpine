from __future__ import annotations

from .features import FeatureTraceReport
from .analysis_models import _PendingIssue
from .analysis_traceability_commands import _feature_trace_command

__all__ = [
    "_trace_gap_issues",
]


def _trace_gap_issues(slug: str, trace_report: FeatureTraceReport) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    for gap in trace_report.gaps:
        gap_id = gap["id"]
        severity = "high" if gap_id == "missing_file" else "medium"
        issues.append(
            _PendingIssue(
                feature_id=slug,
                severity=severity,
                category="artifact" if gap_id == "missing_file" else "traceability",
                code=f"trace.{gap_id}",
                message=gap["message"],
                source_file=gap["source_file"],
                recommended_command=_feature_trace_command(slug),
            )
        )
    return issues
