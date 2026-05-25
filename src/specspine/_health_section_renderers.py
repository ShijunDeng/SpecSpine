from __future__ import annotations

from typing import List

from .health_models import HealthReport

__all__ = [
    "render_health_header",
    "render_health_workspace_section",
    "render_health_feature_pipeline_section",
    "render_health_validation_section",
    "render_health_coverage_section",
    "render_health_consistency_section",
    "render_health_readiness_section",
    "render_health_quality_gates_section",
    "render_health_dependency_section",
    "render_health_security_section",
    "render_health_retrospective_section",
    "render_health_actions_section",
    "render_health_commands_section",
    "render_health_safety_section",
]


def render_health_header(report: HealthReport) -> List[str]:
    return [
        f"SpecSpine Health Dashboard: {report.root}",
        f"Health Score: {report.health_score}/100",
        "",
    ]


def render_health_workspace_section(report: HealthReport) -> List[str]:
    lines: List[str] = []
    ws = report.workspace
    ws_marker = "OK" if ws.complete else "INCOMPLETE"
    lines.append(f"Workspace: [{ws_marker}] {len(ws.present)} present, {len(ws.missing)} missing")
    if ws.missing:
        for m in ws.missing[:5]:
            lines.append(f"  - missing: {m}")
    return lines


def render_health_feature_pipeline_section(report: HealthReport) -> List[str]:
    lines: List[str] = []
    fp = report.feature_pipeline
    lines.append(f"Feature Pipeline: {fp.features_total} features")
    if fp.by_status:
        status_parts = ", ".join(f"{k}={v}" for k, v in fp.by_status.items())
        lines.append(f"  by status: {status_parts}")
    return lines


def render_health_validation_section(report: HealthReport) -> List[str]:
    lines: List[str] = []
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
    return lines


def render_health_coverage_section(report: HealthReport) -> List[str]:
    lines: List[str] = []
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
    return lines


def render_health_consistency_section(report: HealthReport) -> List[str]:
    lines: List[str] = []
    cs = report.consistency_drift
    cs_marker = "OK" if cs.checks_fail == 0 else "DRIFT"
    lines.append(
        f"Consistency: [{cs_marker}] pass={cs.checks_pass} fail={cs.checks_fail} "
        f"warn={cs.checks_warn} total={cs.checks_total}"
    )
    return lines


def render_health_readiness_section(report: HealthReport) -> List[str]:
    lines: List[str] = []
    rg = report.readiness_gates
    lines.append(
        f"Readiness: {rg.ready} ready, {rg.not_ready} not-ready, "
        f"{rg.blocking_checks_total} blocking checks, {rg.gaps_total} gaps"
    )
    return lines


def render_health_quality_gates_section(report: HealthReport) -> List[str]:
    lines: List[str] = []
    qg = report.quality_gates
    lines.append(
        f"Quality Gates: {qg.required_done}/{qg.required_total} done, "
        f"{qg.definition_total} definition items"
    )
    return lines


def render_health_dependency_section(report: HealthReport) -> List[str]:
    lines: List[str] = []
    dh = report.dependency_health
    if dh.cycles:
        lines.append(f"Dependencies: {dh.features_total} features, {len(dh.cycles)} cycle(s)")
    else:
        lines.append(f"Dependencies: {dh.features_total} features, no cycles")
    if dh.critical_path:
        lines.append(f"  critical path: {' -> '.join(dh.critical_path)}")
    return lines


def render_health_security_section(report: HealthReport) -> List[str]:
    lines: List[str] = []
    ss = report.security_summary
    if ss.cues_total > 0:
        lines.append(
            f"Security Cues: {ss.cues_total} total "
            f"(high={ss.high}, medium={ss.medium}, low={ss.low})"
        )
    else:
        lines.append("Security Cues: none")
    return lines


def render_health_retrospective_section(report: HealthReport) -> List[str]:
    lines: List[str] = []
    rt = report.retrospective_theme
    lines.append(f"Retrospective: top blocker theme: {rt.top_blocker_theme}")
    if rt.open_tasks.get("total", 0) > 0:
        lines.append(f"  open tasks: {rt.open_tasks['total']} across {rt.open_tasks.get('features', 0)} feature(s)")
    return lines


def render_health_actions_section(report: HealthReport) -> List[str]:
    lines: List[str] = []
    actions = report.recommended_actions
    lines.append("Recommended Actions:")
    if actions:
        for i, action in enumerate(actions, 1):
            lines.append(f"  {i}. {action}")
    else:
        lines.append("  None. Workspace is healthy.")
    return lines


def render_health_commands_section(report: HealthReport) -> List[str]:
    lines: List[str] = []
    lines.append("")
    lines.append("Recommended Commands:")
    for cmd in report.recommended_commands[:4]:
        lines.append(f"  - {cmd}")
    return lines


def render_health_safety_section(report: HealthReport) -> List[str]:
    lines: List[str] = []
    lines.append("")
    lines.append("Safety Notes:")
    for note in report.safety_notes:
        lines.append(f"  - {note}")
    return lines
