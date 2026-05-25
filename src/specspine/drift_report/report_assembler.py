from __future__ import annotations

from pathlib import Path
from typing import Any

from ..drift_models import DriftAuditReport, _now_iso
from ..drift_report.drift_gatherer import _gather_feature_drift_records
from ..drift_report.commands import _recommended_commands
from .compliance import _build_compliance_section

__all__ = [
    "build_drift_monitor_report",
]


def build_drift_monitor_report(
    root: Path,
    *,
    feature_filter: str | None = None,
    baseline: str | None = None,
    since: str | None = None,
) -> DriftAuditReport:
    resolved_root = root.expanduser().resolve()

    feature_tuple, summary, scan_metadata, trends = _gather_feature_drift_records(
        resolved_root,
        feature_filter=feature_filter,
        baseline=baseline,
        since=since,
    )

    scan_metadata_with_ts = {
        **scan_metadata,
        "timestamp": _now_iso(),
    }

    report = DriftAuditReport(
        root=resolved_root,
        scan_metadata=scan_metadata_with_ts,
        features=feature_tuple,
        summary=summary,
        trends=trends,
        compliance={},
        recommended_commands=_recommended_commands(tuple(f.feature_id for f in feature_tuple)),
        safety_notes=(
            "This drift monitor report reads local workspace files only.",
            "Recommended commands are advisory only and are not executed.",
            "SpecSpine did not run tests, invoke subprocesses (except git show/log for baseline comparison), call network services, call GitHub APIs, invoke upstream CLIs, or read tokens.",
        ),
    )

    compliance = _build_compliance_section(report)
    object.__setattr__(report, "compliance", compliance)

    return report
