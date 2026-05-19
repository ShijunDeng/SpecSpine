from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .consistency import build_consistency_report
from .coverage import build_coverage_debt_report
from .dependency import build_dependency_graph
from .features import list_feature_bundles
from .gates import build_quality_gate_report
from .retrospective import build_retrospective_report
from .security import build_security_cue_report
from .status import build_readiness_summary, build_status
from .validation import build_validation_report
from .workspace import BASE_WORKSPACE_FILES, check_workspace


SAFETY_NOTES = (
    "Health report is read-only and advisory.",
    "Does not run tests, invoke subprocesses, call network services, or read tokens.",
    "Recommended commands are advisory and are not executed.",
    "Missing evidence sources degrade gracefully.",
)


@dataclass(frozen=True)
class WorkspaceHealth:
    complete: bool
    present: tuple[str, ...]
    missing: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "complete": self.complete,
            "missing": list(self.missing),
            "present": list(self.present),
        }


@dataclass(frozen=True)
class FeaturePipeline:
    features_total: int
    by_status: dict[str, int]

    def as_dict(self) -> dict[str, Any]:
        return {
            "by_status": dict(self.by_status),
            "features_total": self.features_total,
        }


@dataclass(frozen=True)
class ValidationHealth:
    ok: bool
    pass_count: int
    fail_count: int
    warn_count: int
    skip_count: int
    total: int
    top_failing_rules: tuple[dict[str, str], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "fail_count": self.fail_count,
            "ok": self.ok,
            "pass_count": self.pass_count,
            "skip_count": self.skip_count,
            "top_failing_rules": list(self.top_failing_rules),
            "total": self.total,
            "warn_count": self.warn_count,
        }


@dataclass(frozen=True)
class CoverageDebt:
    features_with_debt: int
    missing_acceptance_criteria: int
    covered_acceptance_criteria: int
    acceptance_criteria_total: int
    top_features_with_uncovered_ac: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "acceptance_criteria_total": self.acceptance_criteria_total,
            "covered_acceptance_criteria": self.covered_acceptance_criteria,
            "features_with_debt": self.features_with_debt,
            "missing_acceptance_criteria": self.missing_acceptance_criteria,
            "top_features_with_uncovered_ac": list(self.top_features_with_uncovered_ac),
        }


@dataclass(frozen=True)
class ConsistencyDrift:
    features_scanned: int
    checks_pass: int
    checks_fail: int
    checks_warn: int
    checks_total: int
    top_failing_features: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "checks_fail": self.checks_fail,
            "checks_pass": self.checks_pass,
            "checks_total": self.checks_total,
            "checks_warn": self.checks_warn,
            "features_scanned": self.features_scanned,
            "top_failing_features": list(self.top_failing_features),
        }


@dataclass(frozen=True)
class ReadinessGates:
    features_total: int
    ready: int
    not_ready: int
    blocking_checks_total: int
    gaps_total: int
    top_blockers: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "blocking_checks_total": self.blocking_checks_total,
            "features_total": self.features_total,
            "gaps_total": self.gaps_total,
            "not_ready": self.not_ready,
            "ready": self.ready,
            "top_blockers": list(self.top_blockers),
        }


@dataclass(frozen=True)
class QualityGates:
    required_total: int
    required_done: int
    required_open: int
    definition_total: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "definition_total": self.definition_total,
            "required_done": self.required_done,
            "required_open": self.required_open,
            "required_total": self.required_total,
        }


@dataclass(frozen=True)
class DependencyHealth:
    features_total: int
    cycles: list[list[str]]
    critical_path: list[str]
    critical_path_effort: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "critical_path": self.critical_path,
            "critical_path_effort": self.critical_path_effort,
            "cycles": self.cycles,
            "features_total": self.features_total,
        }


@dataclass(frozen=True)
class SecuritySummary:
    cues_total: int
    high: int
    medium: int
    low: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "cues_total": self.cues_total,
            "high": self.high,
            "low": self.low,
            "medium": self.medium,
        }


@dataclass(frozen=True)
class RetrospectiveTheme:
    top_blocker_theme: str
    blocking_checks: dict[str, int]
    gaps: dict[str, int]
    coverage_states: dict[str, int]
    open_tasks: dict[str, int]

    def as_dict(self) -> dict[str, Any]:
        return {
            "blocking_checks": dict(self.blocking_checks),
            "coverage_states": dict(self.coverage_states),
            "gaps": dict(self.gaps),
            "open_tasks": dict(self.open_tasks),
            "top_blocker_theme": self.top_blocker_theme,
        }


@dataclass(frozen=True)
class HealthReport:
    root: str
    workspace: WorkspaceHealth
    feature_pipeline: FeaturePipeline
    validation_health: ValidationHealth
    coverage_debt: CoverageDebt
    consistency_drift: ConsistencyDrift
    readiness_gates: ReadinessGates
    quality_gates: QualityGates
    dependency_health: DependencyHealth
    security_summary: SecuritySummary
    retrospective_theme: RetrospectiveTheme
    health_score: int
    recommended_actions: tuple[str, ...]
    recommended_commands: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "consistency_drift": self.consistency_drift.as_dict(),
            "coverage_debt": self.coverage_debt.as_dict(),
            "dependency_health": self.dependency_health.as_dict(),
            "feature_pipeline": self.feature_pipeline.as_dict(),
            "health_score": self.health_score,
            "quality_gates": self.quality_gates.as_dict(),
            "readiness_gates": self.readiness_gates.as_dict(),
            "recommended_actions": list(self.recommended_actions),
            "recommended_commands": list(self.recommended_commands),
            "retrospective_theme": self.retrospective_theme.as_dict(),
            "root": self.root,
            "safety_notes": list(self.safety_notes),
            "security_summary": self.security_summary.as_dict(),
            "validation_health": self.validation_health.as_dict(),
            "workspace": self.workspace.as_dict(),
        }


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


def compute_health_score(
    workspace: WorkspaceHealth,
    feature_pipeline: FeaturePipeline,
    validation: ValidationHealth,
    coverage: CoverageDebt,
    consistency: ConsistencyDrift,
    readiness: ReadinessGates,
    quality_gates: QualityGates,
) -> int:
    if workspace.missing:
        return 0

    workspace_score = 10 if workspace.complete else 5

    total_features = feature_pipeline.features_total
    if total_features == 0:
        pipeline_score = 15
    else:
        advanced_statuses = sum(
            count for status, count in feature_pipeline.by_status.items()
            if status in {"implemented", "validated", "archived"}
        )
        pipeline_score = int(15 * advanced_statuses / total_features)

    if validation.total == 0:
        validation_score = 20
    else:
        validation_score = int(20 * validation.pass_count / validation.total)

    total_ac = coverage.acceptance_criteria_total
    if total_ac == 0:
        coverage_score = 20
    else:
        coverage_score = int(20 * coverage.covered_acceptance_criteria / total_ac)

    total_checks = consistency.checks_total
    if total_checks == 0:
        consistency_score = 15
    else:
        consistency_score = int(15 * consistency.checks_pass / total_checks)

    total_ready = readiness.features_total
    if total_ready == 0:
        readiness_score = 15
    else:
        readiness_score = int(15 * readiness.ready / total_ready)

    total_gates = quality_gates.required_total
    if total_gates == 0:
        gates_score = 5
    else:
        gates_score = int(5 * quality_gates.required_done / total_gates)

    score = (
        workspace_score
        + pipeline_score
        + validation_score
        + coverage_score
        + consistency_score
        + readiness_score
        + gates_score
    )

    return max(0, min(100, score))


def generate_recommended_actions(report: HealthReport) -> list[str]:
    actions: list[str] = []

    if report.workspace.missing:
        missing = ", ".join(report.workspace.missing[:3])
        actions.append(f"Create missing workspace files: {missing}")

    if report.validation_health.fail_count > 0:
        top_rule = report.validation_health.top_failing_rules[0]["id"] if report.validation_health.top_failing_rules else "unknown"
        actions.append(
            f"Fix {report.validation_health.fail_count} validation failure(s); top: {top_rule}"
        )

    if report.coverage_debt.missing_acceptance_criteria > 0:
        actions.append(
            f"Cover {report.coverage_debt.missing_acceptance_criteria} uncovered acceptance criterion/criteria"
        )

    if report.consistency_drift.checks_fail > 0:
        actions.append(
            f"Resolve {report.consistency_drift.checks_fail} consistency drift check(s)"
        )

    if report.readiness_gates.not_ready > 0:
        actions.append(
            f"Address {report.readiness_gates.not_ready} not-ready feature(s) with {report.readiness_gates.blocking_checks_total} blocking check(s)"
        )

    return actions[:5]


def _generate_recommended_commands(report: HealthReport) -> list[str]:
    commands: list[str] = []
    commands.append("specspine status health . --json")
    commands.append("specspine status . --json --validate --feature-summaries --readiness-summary")
    commands.append("specspine coverage debt . --json")
    commands.append("specspine consistency scan . --json")
    commands.append("specspine validate . --fusion --features")
    commands.append("specspine gates . --json")
    return commands


def build_health_report(root: Path) -> HealthReport:
    resolved_root = root.expanduser().resolve()

    workspace = _build_workspace_health(resolved_root)
    feature_pipeline = _build_feature_pipeline(resolved_root)
    validation = _build_validation_health(resolved_root)
    coverage = _build_coverage_debt_data(resolved_root)
    consistency = _build_consistency_drift(resolved_root)
    readiness = _build_readiness_gates(resolved_root)
    quality_gates = _build_quality_gates(resolved_root)
    dependency = _build_dependency_health(resolved_root)
    security = _build_security_summary(resolved_root)
    retrospective = _build_retrospective_theme(resolved_root)

    health_score = compute_health_score(
        workspace,
        feature_pipeline,
        validation,
        coverage,
        consistency,
        readiness,
        quality_gates,
    )

    partial_report = HealthReport(
        root=str(resolved_root),
        workspace=workspace,
        feature_pipeline=feature_pipeline,
        validation_health=validation,
        coverage_debt=coverage,
        consistency_drift=consistency,
        readiness_gates=readiness,
        quality_gates=quality_gates,
        dependency_health=dependency,
        security_summary=security,
        retrospective_theme=retrospective,
        health_score=health_score,
        recommended_actions=(),
        recommended_commands=(),
        safety_notes=SAFETY_NOTES,
    )

    recommended_actions = generate_recommended_actions(partial_report)
    recommended_commands = _generate_recommended_commands(partial_report)

    return HealthReport(
        root=str(resolved_root),
        workspace=workspace,
        feature_pipeline=feature_pipeline,
        validation_health=validation,
        coverage_debt=coverage,
        consistency_drift=consistency,
        readiness_gates=readiness,
        quality_gates=quality_gates,
        dependency_health=dependency,
        security_summary=security,
        retrospective_theme=retrospective,
        health_score=health_score,
        recommended_actions=tuple(recommended_actions),
        recommended_commands=tuple(recommended_commands),
        safety_notes=SAFETY_NOTES,
    )


def render_health_json(report: HealthReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_health_text(report: HealthReport) -> str:
    lines: list[str] = []
    lines.append(f"SpecSpine Health Dashboard: {report.root}")
    lines.append(f"Health Score: {report.health_score}/100")
    lines.append("")

    ws = report.workspace
    ws_marker = "OK" if ws.complete else "INCOMPLETE"
    lines.append(f"Workspace: [{ws_marker}] {len(ws.present)} present, {len(ws.missing)} missing")
    if ws.missing:
        for m in ws.missing[:5]:
            lines.append(f"  - missing: {m}")

    fp = report.feature_pipeline
    lines.append(f"Feature Pipeline: {fp.features_total} features")
    if fp.by_status:
        status_parts = ", ".join(f"{k}={v}" for k, v in fp.by_status.items())
        lines.append(f"  by status: {status_parts}")

    vh = report.validation_health
    vh_marker = "PASS" if vh.ok else "FAIL"
    lines.append(
        f"Validation: [{vh_marker}] pass={vh.pass_count} fail={vh.fail_count} "
        f"warn={vh.warn_count} skip={vh.skip_count} total={vh.total}"
    )
    if vh.top_failing_rules:
        lines.append("  top failing:")
        for rule in vh.top_failing_rules[:3]:
            lines.append(f"    - {rule['id']}: {rule['message'][:60]}")

    cd = report.coverage_debt
    if cd.acceptance_criteria_total > 0:
        cov_pct = int(100 * cd.covered_acceptance_criteria / cd.acceptance_criteria_total)
    else:
        cov_pct = 100
    lines.append(
        f"Coverage: {cov_pct}% covered "
        f"({cd.covered_acceptance_criteria}/{cd.acceptance_criteria_total}), "
        f"{cd.features_with_debt} feature(s) with debt"
    )

    cs = report.consistency_drift
    cs_marker = "OK" if cs.checks_fail == 0 else "DRIFT"
    lines.append(
        f"Consistency: [{cs_marker}] pass={cs.checks_pass} fail={cs.checks_fail} "
        f"warn={cs.checks_warn} total={cs.checks_total}"
    )

    rg = report.readiness_gates
    lines.append(
        f"Readiness: {rg.ready} ready, {rg.not_ready} not-ready, "
        f"{rg.blocking_checks_total} blocking checks, {rg.gaps_total} gaps"
    )

    qg = report.quality_gates
    lines.append(
        f"Quality Gates: {qg.required_done}/{qg.required_total} done, "
        f"{qg.definition_total} definition items"
    )

    dh = report.dependency_health
    if dh.cycles:
        lines.append(f"Dependencies: {dh.features_total} features, {len(dh.cycles)} cycle(s)")
    else:
        lines.append(f"Dependencies: {dh.features_total} features, no cycles")
    if dh.critical_path:
        lines.append(f"  critical path: {' -> '.join(dh.critical_path)}")

    ss = report.security_summary
    if ss.cues_total > 0:
        lines.append(
            f"Security Cues: {ss.cues_total} total "
            f"(high={ss.high}, medium={ss.medium}, low={ss.low})"
        )
    else:
        lines.append("Security Cues: none")

    rt = report.retrospective_theme
    lines.append(f"Retrospective: top blocker theme: {rt.top_blocker_theme}")
    if rt.open_tasks.get("total", 0) > 0:
        lines.append(f"  open tasks: {rt.open_tasks['total']} across {rt.open_tasks.get('features', 0)} feature(s)")

    lines.append("")
    actions = report.recommended_actions
    lines.append("Recommended Actions:")
    if actions:
        for i, action in enumerate(actions, 1):
            lines.append(f"  {i}. {action}")
    else:
        lines.append("  None. Workspace is healthy.")

    lines.append("")
    lines.append("Recommended Commands:")
    for cmd in report.recommended_commands[:4]:
        lines.append(f"  - {cmd}")

    lines.append("")
    lines.append("Safety Notes:")
    for note in report.safety_notes:
        lines.append(f"  - {note}")

    return "\n".join(lines) + "\n"
