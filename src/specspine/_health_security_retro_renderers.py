from __future__ import annotations

from typing import List

from .health_models import HealthReport

__all__ = [
    "render_health_security_section",
    "render_health_retrospective_section",
]


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
