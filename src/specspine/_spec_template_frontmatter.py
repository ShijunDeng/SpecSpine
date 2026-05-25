from __future__ import annotations

__all__ = [
    "build_frontmatter_section",
]


def build_frontmatter_section(
    resolved_slug: str,
    title: str,
    priority: str,
    owner: str,
    milestone: str,
    target_release: str,
    project: str,
    effort: str,
) -> str:
    return f"""# {title}

Feature ID: {resolved_slug}
Status: proposed
Priority: {priority}
Owner: {owner}
Milestone: {milestone}
Target Release: {target_release}
Project: {project}
Effort: {effort}"""
