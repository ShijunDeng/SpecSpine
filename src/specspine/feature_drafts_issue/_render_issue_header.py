from __future__ import annotations

from ..feature_bundle import (
    FeatureMetadata,
    _render_metadata_lines,
)

__all__ = [
    "_render_issue_header",
]


def _render_issue_header(
    *,
    feature_id: str,
    status: str,
    metadata: FeatureMetadata,
) -> list[str]:
    return [
        "## Feature",
        "",
        f"- Feature ID: `{feature_id}`",
        f"- Status: {status}",
        "",
        "## Metadata",
        "",
        *_render_metadata_lines(metadata),
        "",
    ]
