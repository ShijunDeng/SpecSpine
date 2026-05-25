from __future__ import annotations

from pathlib import Path

from .retrospective import build_retrospective_report
from .health_models import RetrospectiveTheme

__all__ = [
    "_build_retrospective_theme",
]


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
