from __future__ import annotations

from pathlib import Path

from .consistency import build_consistency_report
from .health_models import ConsistencyDrift

__all__ = [
    "_build_consistency_drift",
]


def _build_consistency_drift(root: Path) -> ConsistencyDrift:
    try:
        report = build_consistency_report(root)
    except OSError:
        return ConsistencyDrift(
            features_scanned=0,
            checks_pass=0,
            checks_fail=0,
            checks_warn=0,
            checks_total=0,
            top_failing_features=(),
        )

    summary = report.summary
    failing_features = [
        f for f in report.features
        if any(c.status == "fail" for c in f.consistency_checks)
    ]
    top_failing = tuple(
        {
            "feature_id": f.feature_id,
            "fail_count": sum(1 for c in f.consistency_checks if c.status == "fail"),
            "status": f.status or "missing",
        }
        for f in sorted(failing_features, key=lambda x: -sum(1 for c in x.consistency_checks if c.status == "fail"))[:5]
    )

    return ConsistencyDrift(
        features_scanned=summary.get("features_scanned", 0),
        checks_pass=summary.get("checks_pass", 0),
        checks_fail=summary.get("checks_fail", 0),
        checks_warn=summary.get("checks_warn", 0),
        checks_total=summary.get("checks_total", 0),
        top_failing_features=top_failing,
    )
