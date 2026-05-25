from __future__ import annotations

from pathlib import Path

from .consistency import build_consistency_report
from .coverage import build_coverage_debt_report
from .gates import build_quality_gate_report
from .status import build_readiness_summary
from .validation import build_validation_report
from .health_models import (
    ConsistencyDrift,
    CoverageDebt,
    QualityGates,
    ReadinessGates,
    ValidationHealth,
)

__all__ = [
    "_build_consistency_drift",
    "_build_coverage_debt_data",
    "_build_quality_gates",
    "_build_readiness_gates",
    "_build_validation_health",
]


def _build_validation_health(root: Path) -> ValidationHealth:
    try:
        report = build_validation_report(
            root,
            include_fusion=True,
            include_features=True,
            include_adapters=False,
        )
    except OSError:
        return ValidationHealth(
            ok=False,
            pass_count=0,
            fail_count=0,
            warn_count=0,
            skip_count=0,
            total=0,
            top_failing_rules=(),
        )

    summary = report["summary"]
    checks = report.get("checks", [])
    failing = [c for c in checks if c["status"] == "fail"]
    top_failing = tuple(
        {"id": c["id"], "message": c["message"]}
        for c in failing[:5]
    )

    return ValidationHealth(
        ok=report["ok"],
        pass_count=summary.get("pass", 0),
        fail_count=summary.get("fail", 0),
        warn_count=summary.get("warn", 0),
        skip_count=summary.get("skip", 0),
        total=summary.get("total", 0),
        top_failing_rules=top_failing,
    )


def _build_coverage_debt_data(root: Path) -> CoverageDebt:
    try:
        report = build_coverage_debt_report(root)
    except OSError:
        return CoverageDebt(
            features_with_debt=0,
            missing_acceptance_criteria=0,
            covered_acceptance_criteria=0,
            acceptance_criteria_total=0,
            top_features_with_uncovered_ac=(),
        )

    features = report.get("features", [])
    debt_features = [
        f for f in features
        if f.get("coverage_required") and int(f.get("missing_acceptance_criteria", 0)) > 0
    ]
    top_features = tuple(
        {
            "feature_id": f["feature_id"],
            "missing": f["missing_acceptance_criteria"],
            "status": f["status"],
        }
        for f in sorted(debt_features, key=lambda x: -int(x["missing_acceptance_criteria"]))[:5]
    )

    return CoverageDebt(
        features_with_debt=report.get("features_with_debt", 0),
        missing_acceptance_criteria=report.get("missing_acceptance_criteria", 0),
        covered_acceptance_criteria=report.get("covered_acceptance_criteria", 0),
        acceptance_criteria_total=report.get("acceptance_criteria_total", 0),
        top_features_with_uncovered_ac=top_features,
    )


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
