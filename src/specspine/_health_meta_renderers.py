from __future__ import annotations

from typing import List

from .health_models import HealthReport

__all__ = [
    "render_health_quality_gates_section",
    "render_health_dependency_section",
    "render_health_security_section",
    "render_health_retrospective_section",
    "render_health_actions_section",
    "render_health_commands_section",
    "render_health_safety_section",
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
