from __future__ import annotations

from typing import List

from .health_models import HealthReport

__all__ = [
    "render_health_header",
    "render_health_workspace_section",
    "render_health_feature_pipeline_section",
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
