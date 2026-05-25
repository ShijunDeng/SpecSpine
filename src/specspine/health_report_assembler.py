from __future__ import annotations

from pathlib import Path

from .health_models import (
    HealthReport,
    SAFETY_NOTES,
)
from .health_recommendations import (
    _generate_recommended_commands,
    generate_recommended_actions,
)
from .health_report_sections import _collect_health_sections

__all__ = [
    "build_health_report",
]


def build_health_report(root: Path) -> HealthReport:
    resolved_root = root.expanduser().resolve()

    sections = _collect_health_sections(resolved_root)

    partial_report = HealthReport(
        root=str(resolved_root),
        workspace=sections["workspace"],
        feature_pipeline=sections["feature_pipeline"],
        validation_health=sections["validation"],
        coverage_debt=sections["coverage"],
        consistency_drift=sections["consistency"],
        readiness_gates=sections["readiness"],
        quality_gates=sections["quality_gates"],
        dependency_health=sections["dependency"],
        security_summary=sections["security"],
        retrospective_theme=sections["retrospective"],
        health_score=sections["health_score"],
        recommended_actions=(),
        recommended_commands=(),
        safety_notes=SAFETY_NOTES,
    )

    recommended_actions = generate_recommended_actions(partial_report)
    recommended_commands = _generate_recommended_commands(partial_report)

    return HealthReport(
        root=str(resolved_root),
        workspace=sections["workspace"],
        feature_pipeline=sections["feature_pipeline"],
        validation_health=sections["validation"],
        coverage_debt=sections["coverage"],
        consistency_drift=sections["consistency"],
        readiness_gates=sections["readiness"],
        quality_gates=sections["quality_gates"],
        dependency_health=sections["dependency"],
        security_summary=sections["security"],
        retrospective_theme=sections["retrospective"],
        health_score=sections["health_score"],
        recommended_actions=tuple(recommended_actions),
        recommended_commands=tuple(recommended_commands),
        safety_notes=SAFETY_NOTES,
    )
