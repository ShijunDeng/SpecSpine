from __future__ import annotations

from .adapter_handoff_render_sections import (
    _render_header_section,
    _render_sources_section,
    _render_gaps_section,
    _render_blocking_section,
)
from .adapter_handoff_render_adapters import _render_adapters_section

__all__ = [
    "render_adapter_feature_handoff_text",
]


def render_adapter_feature_handoff_text(
    report,
) -> str:
    lines: list[str] = []
    lines.extend(_render_header_section(report))
    lines.extend(_render_sources_section(report))
    lines.extend(_render_gaps_section(report))
    lines.extend(_render_blocking_section(report))
    lines.extend(_render_adapters_section(report))

    lines.extend(["## Recommended Local Commands", ""])
    lines.extend(f"- `{command}`" for command in report.recommended_commands)

    return "\n".join(lines).rstrip() + "\n"
