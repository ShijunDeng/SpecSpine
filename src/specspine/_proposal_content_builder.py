from __future__ import annotations

from .feature_bundle_validation import validate_feature_slug

__all__ = [
    "build_proposal_files",
]


def build_proposal_files(
    slug: str,
    intent: str,
    *,
    priority: str = "medium",
    owner: str = "unassigned",
    milestone: str = "unassigned",
    target_release: str = "unassigned",
    project: str = "unassigned",
    effort: str = "unknown",
) -> dict[str, str]:
    from .proposer import build_proposal_content

    slug = validate_feature_slug(slug)
    return build_proposal_content(
        slug,
        intent,
        priority=priority,
        owner=owner,
        milestone=milestone,
        target_release=target_release,
        project=project,
        effort=effort,
    )
