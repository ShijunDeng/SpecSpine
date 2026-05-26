from __future__ import annotations

from pathlib import Path

from .features import (
    InvalidFeatureSlug,
    get_feature_status,
    read_feature_metadata,
    validate_feature_slug,
)

__all__ = [
    "FeatureInfo",
    "gather_feature_info",
]


class FeatureInfo:
    """Holds resolved feature status and metadata."""

    __slots__ = ("slug", "status", "priority", "effort", "project")

    def __init__(
        self,
        slug: str,
        status: str,
        priority: str,
        effort: str,
        project: str,
    ) -> None:
        object.__setattr__(self, "slug", slug)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "priority", priority)
        object.__setattr__(self, "effort", effort)
        object.__setattr__(self, "project", project)


def gather_feature_info(slug: str, root: Path) -> FeatureInfo:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()

    status_report = get_feature_status(resolved_root, slug)
    status = status_report.status or "unknown"

    metadata = read_feature_metadata(resolved_root, slug)
    return FeatureInfo(
        slug=slug,
        status=status,
        priority=metadata.priority,
        effort=metadata.effort,
        project=metadata.project,
    )
