from __future__ import annotations

from pathlib import Path

from .status import build_readiness_summary
from .health_models import ReadinessGates

__all__ = [
    "_build_readiness_gates",
]


def _build_readiness_gates(root: Path) -> ReadinessGates:
    try:
        report = build_readiness_summary(root)
    except OSError:
        return ReadinessGates(
            features_total=0,
            ready=0,
            not_ready=0,
            blocking_checks_total=0,
            gaps_total=0,
            top_blockers=(),
        )

    not_ready_features = [
        f for f in report.get("features", [])
        if not f.get("ready", False)
    ]
    top_blockers = tuple(
        {
            "feature_id": f["feature_id"],
            "blocking_checks": f["blocking_checks"],
            "gaps": f["gaps"],
            "missing_files_count": len(f.get("missing_files", [])),
        }
        for f in sorted(
            not_ready_features,
            key=lambda x: (-int(x["blocking_checks"]), -int(x["gaps"])),
        )[:5]
    )

    return ReadinessGates(
        features_total=report.get("features_total", 0),
        ready=report.get("ready", 0),
        not_ready=report.get("not_ready", 0),
        blocking_checks_total=report.get("blocking_checks_total", 0),
        gaps_total=report.get("gaps_total", 0),
        top_blockers=top_blockers,
    )
