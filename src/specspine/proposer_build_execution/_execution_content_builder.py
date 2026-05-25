from __future__ import annotations

from ..workspace import normalize_template
from ._execution_template import build_execution_header
from ._execution_handoff import build_agent_handoff


def build_execution_content(
    resolved_slug: str,
    title: str,
    parsed: dict,
    tasks: list[dict],
    intent: str,
) -> str:
    header = build_execution_header(resolved_slug, title, parsed, tasks, intent)
    handoff = build_agent_handoff(resolved_slug)
    return header + handoff


__all__ = [
    "build_execution_content",
]
