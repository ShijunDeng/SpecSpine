from __future__ import annotations

from pathlib import Path

from .dependency import build_dependency_graph
from .retrospective import build_retrospective_report
from .security import build_security_cue_report
from .health_models import (
    DependencyHealth,
    RetrospectiveTheme,
    SecuritySummary,
)

__all__ = [
    "_build_dependency_health",
    "_build_retrospective_theme",
    "_build_security_summary",
]


def _build_dependency_health(root: Path) -> DependencyHealth:
    try:
        graph = build_dependency_graph(root)
    except OSError:
        return DependencyHealth(
            features_total=0,
            cycles=[],
            critical_path=[],
            critical_path_effort=0,
        )

    nodes = graph.get("nodes", [])
    critical = graph.get("critical_path", {})
    return DependencyHealth(
        features_total=len(nodes),
        cycles=graph.get("cycles", []),
        critical_path=critical.get("path", []),
        critical_path_effort=int(critical.get("total_effort", 0)),
    )


def _build_security_summary(root: Path) -> SecuritySummary:
    try:
        report = build_security_cue_report(root)
    except OSError:
        return SecuritySummary(
            cues_total=0,
            high=0,
            medium=0,
            low=0,
        )

    summary = report.summary
    return SecuritySummary(
        cues_total=summary.get("cues_total", 0),
        high=summary.get("high", 0),
        medium=summary.get("medium", 0),
        low=summary.get("low", 0),
    )


def _build_retrospective_theme(root: Path) -> RetrospectiveTheme:
    try:
        report = build_retrospective_report(root)
    except OSError:
        return RetrospectiveTheme(
            top_blocker_theme="none",
            blocking_checks={},
            gaps={},
            coverage_states={},
            open_tasks={},
        )

    themes = report.get("themes", {})
    blocking = themes.get("blocking_checks", {})
    gaps = themes.get("gaps", {})

    top_blocker = "none"
    if blocking:
        top_blocker = max(blocking, key=lambda k: blocking[k])

    return RetrospectiveTheme(
        top_blocker_theme=top_blocker,
        blocking_checks=dict(sorted(blocking.items())),
        gaps=dict(sorted(gaps.items())),
        coverage_states=dict(sorted(themes.get("coverage_states", {}).items())),
        open_tasks=dict(sorted(themes.get("open_tasks", {}).items())),
    )
