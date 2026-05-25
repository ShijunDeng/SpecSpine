from __future__ import annotations

from pathlib import Path

from .consistency import build_consistency_report
from .gates import build_quality_gate_report
from .status import build_readiness_summary
from .health_models import (
    ConsistencyDrift,
    QualityGates,
    ReadinessGates,
)

__all__ = [
    "_build_consistency_drift",
    "_build_readiness_gates",
    "_build_quality_gates",
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


def _build_quality_gates(root: Path) -> QualityGates:
    try:
        report = build_quality_gate_report(root)
    except OSError:
        return QualityGates(
            required_total=0,
            required_done=0,
            required_open=0,
            definition_total=0,
        )

    summary = report.summary
    return QualityGates(
        required_total=int(summary.get("required_total", 0)),
        required_done=int(summary.get("required_done", 0)),
        required_open=int(summary.get("required_open", 0)),
        definition_total=int(summary.get("definition_total", 0)),
    )
