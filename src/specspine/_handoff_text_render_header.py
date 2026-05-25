from __future__ import annotations

from .feature_bundle import FeatureHandoffReport

__all__ = [
    "_render_handoff_header",
]


def _render_handoff_header(report: FeatureHandoffReport) -> list[str]:
    summary = report.summary
    trace = summary["trace"]
    ready = summary["ready"]
    tasks = summary["tasks"]
    lines = [
        f"Feature handoff: {report.feature_id}",
        f"Status: {report.status}",
        f"Ready: {'yes' if report.ready else 'no'}",
        (
            "Metadata: "
            f"priority={report.metadata.priority} "
            f"owner={report.metadata.owner} "
            f"milestone={report.metadata.milestone} "
            f"target_release={report.metadata.target_release}"
        ),
        (
            "Counts: "
            f"trace={trace['total']}/{trace['done']}/{trace['open']} "
            f"ready={ready['pass']}/{ready['fail']}/{ready['total']} "
            f"tasks={tasks['total']}/{tasks['done']}/{tasks['open']} "
            f"gaps={summary['gaps']['total']} "
            f"blocking={summary['blocking_checks']['total']}"
        ),
    ]
    return lines
