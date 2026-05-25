from __future__ import annotations

from .health_models import HealthReport
from ._health_section_renderers import (
    render_health_header,
    render_health_workspace_section,
    render_health_feature_pipeline_section,
    render_health_validation_section,
    render_health_coverage_section,
    render_health_consistency_section,
    render_health_readiness_section,
    render_health_quality_gates_section,
    render_health_dependency_section,
    render_health_security_section,
    render_health_retrospective_section,
    render_health_actions_section,
    render_health_commands_section,
    render_health_safety_section,
)

__all__ = [
    "render_health_text",
]


def render_health_text(report: HealthReport) -> str:
    lines: list[str] = []
    lines.extend(render_health_header(report))
    lines.extend(render_health_workspace_section(report))
    lines.extend(render_health_feature_pipeline_section(report))
    lines.extend(render_health_validation_section(report))
    lines.extend(render_health_coverage_section(report))
    lines.extend(render_health_consistency_section(report))
    lines.extend(render_health_readiness_section(report))
    lines.extend(render_health_quality_gates_section(report))
    lines.extend(render_health_dependency_section(report))
    lines.extend(render_health_security_section(report))
    lines.extend(render_health_retrospective_section(report))
    lines.append("")
    lines.extend(render_health_actions_section(report))
    lines.extend(render_health_commands_section(report))
    lines.extend(render_health_safety_section(report))
    return "\n".join(lines) + "\n"
