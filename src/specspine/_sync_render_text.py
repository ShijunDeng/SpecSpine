from __future__ import annotations

from .feature_bundle import FeatureSyncPlan
from ._sync_render_sections import (
    _render_header_lines,
    _render_source_lines,
    _render_gap_lines,
    _render_blocking_lines,
)
from ._sync_render_commands import (
    _render_command_lines,
    _render_recommended_commands,
)

__all__ = [
    "render_feature_sync_plan_text",
]


def render_feature_sync_plan_text(plan: FeatureSyncPlan) -> str:
    lines: list[str] = []
    lines.extend(_render_header_lines(plan))
    lines.extend(_render_source_lines(plan))
    lines.extend(_render_gap_lines(plan))
    lines.extend(_render_blocking_lines(plan))
    lines.extend(_render_command_lines(plan))
    lines.extend(_render_recommended_commands(plan))
    return "\n".join(lines).rstrip() + "\n"
