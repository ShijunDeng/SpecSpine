from __future__ import annotations

from .workspace import normalize_template
from ._spec_template_frontmatter import build_frontmatter_section
from ._spec_template_body import build_body_sections

__all__ = [
    "build_spec_content",
]


def build_spec_content(
    resolved_slug: str,
    title: str,
    parsed: dict,
    criteria: list[dict],
    priority: str,
    owner: str,
    milestone: str,
    target_release: str,
    project: str,
    effort: str,
    intent: str,
) -> str:
    frontmatter = build_frontmatter_section(
        resolved_slug=resolved_slug,
        title=title,
        priority=priority,
        owner=owner,
        milestone=milestone,
        target_release=target_release,
        project=project,
        effort=effort,
    )
    body = build_body_sections(
        parsed=parsed,
        criteria=criteria,
        intent=intent,
        resolved_slug=resolved_slug,
    )
    return normalize_template(frontmatter + body)
