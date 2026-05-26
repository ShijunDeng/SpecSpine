from __future__ import annotations

from .feature_bundle import (
    FeatureReadyCheck,
    FeatureTraceChecklistItem,
)
from .feature_drafts_pr_renderers import (
    _render_pr_checklist_items,
    _render_pr_ready_checks,
)

__all__ = [
    "_render_pr_release_readiness_section",
    "_render_pr_readiness_checks_section",
]


def _render_pr_release_readiness_section(
    release_readiness: tuple[FeatureTraceChecklistItem, ...],
) -> list[str]:
    lines: list[str] = []
    lines.extend(["", "## Release Readiness", ""])
    lines.extend(
        _render_pr_checklist_items(
            release_readiness,
            empty_text="Add release readiness checklist items before review.",
        )
    )
    return lines


def _render_pr_readiness_checks_section(
    readiness_checks: tuple[FeatureReadyCheck, ...],
) -> list[str]:
    lines: list[str] = []
    lines.extend(["", "## Readiness / Blocking Checks", ""])
    lines.extend(_render_pr_ready_checks(readiness_checks))
    return lines
