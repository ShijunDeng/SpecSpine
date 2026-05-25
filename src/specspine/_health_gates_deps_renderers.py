from __future__ import annotations

from typing import List

from .health_models import HealthReport

__all__ = [
    "render_health_quality_gates_section",
    "render_health_dependency_section",
]


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
