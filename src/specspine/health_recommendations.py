from __future__ import annotations

from .health_models import HealthReport


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


__all__ = [
    "generate_recommended_actions",
    "_generate_recommended_commands",
]
