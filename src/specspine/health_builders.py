from __future__ import annotations

from pathlib import Path
from typing import Any

from .consistency import build_consistency_report
from .coverage import build_coverage_debt_report
from .dependency import build_dependency_graph
from .features import list_feature_bundles
from .gates import build_quality_gate_report
from .retrospective import build_retrospective_report
from .security import build_security_cue_report
from .status import build_readiness_summary
from .validation import build_validation_report
from .workspace import BASE_WORKSPACE_FILES, check_workspace

from .health_models import (
    CoverageDebt,
    ConsistencyDrift,
    DependencyHealth,
    FeaturePipeline,
    QualityGates,
    ReadinessGates,
    RetrospectiveTheme,
    SecuritySummary,
    ValidationHealth,
    WorkspaceHealth,
)


def _build_workspace_health(root: Path) -> WorkspaceHealth:
    present, missing = check_workspace(root, required_files=BASE_WORKSPACE_FILES)
    present_paths = sorted(str(p.relative_to(root)) for p in present)
    missing_paths = sorted(str(m.relative_to(root)) for m in missing)
    return WorkspaceHealth(
        complete=len(missing) == 0,
        present=tuple(present_paths),
        missing=tuple(missing_paths),
    )


def _build_feature_pipeline(root: Path) -> FeaturePipeline:
    features = list_feature_bundles(root)
    by_status: dict[str, int] = {}
    for feature in features:
        status = str(feature.get("status") or "unknown")
        by_status[status] = by_status.get(status, 0) + 1
    return FeaturePipeline(
        features_total=len(features),
        by_status=dict(sorted(by_status.items())),
    )


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


def _build_dependency_health(root: Path) -> DependencyHealth:
    try:
        graph = build_dependency_graph(root)
    except OSError:
        return DependencyHealth(
            features_total=0,
            cycles=[],
            critical_path=[],
            critical_path_effort=0,
        )

    nodes = graph.get("nodes", [])
    critical = graph.get("critical_path", {})
    return DependencyHealth(
        features_total=len(nodes),
        cycles=graph.get("cycles", []),
        critical_path=critical.get("path", []),
        critical_path_effort=int(critical.get("total_effort", 0)),
    )


def _build_security_summary(root: Path) -> SecuritySummary:
    try:
        report = build_security_cue_report(root)
    except OSError:
        return SecuritySummary(
            cues_total=0,
            high=0,
            medium=0,
            low=0,
        )

    summary = report.summary
    return SecuritySummary(
        cues_total=summary.get("cues_total", 0),
        high=summary.get("high", 0),
        medium=summary.get("medium", 0),
        low=summary.get("low", 0),
    )


def _build_retrospective_theme(root: Path) -> RetrospectiveTheme:
    try:
        report = build_retrospective_report(root)
    except OSError:
        return RetrospectiveTheme(
            top_blocker_theme="none",
            blocking_checks={},
            gaps={},
            coverage_states={},
            open_tasks={},
        )

    themes = report.get("themes", {})
    blocking = themes.get("blocking_checks", {})
    gaps = themes.get("gaps", {})

    top_blocker = "none"
    if blocking:
        top_blocker = max(blocking, key=lambda k: blocking[k])

    return RetrospectiveTheme(
        top_blocker_theme=top_blocker,
        blocking_checks=dict(sorted(blocking.items())),
        gaps=dict(sorted(gaps.items())),
        coverage_states=dict(sorted(themes.get("coverage_states", {}).items())),
        open_tasks=dict(sorted(themes.get("open_tasks", {}).items())),
    )


__all__ = [
    "_build_workspace_health",
    "_build_feature_pipeline",
    "_build_validation_health",
    "_build_coverage_debt_data",
    "_build_consistency_drift",
    "_build_readiness_gates",
    "_build_quality_gates",
    "_build_dependency_health",
    "_build_security_summary",
    "_build_retrospective_theme",
]
