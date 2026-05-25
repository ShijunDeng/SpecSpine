from __future__ import annotations

from typing import List

from .health_models import HealthReport

__all__ = [
    "render_health_validation_section",
    "render_health_coverage_section",
    "render_health_consistency_section",
    "render_health_readiness_section",
]


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
