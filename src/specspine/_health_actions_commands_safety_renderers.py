from __future__ import annotations

from typing import List

from .health_models import HealthReport

__all__ = [
    "render_health_actions_section",
    "render_health_commands_section",
    "render_health_safety_section",
]


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
