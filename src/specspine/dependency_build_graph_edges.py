from __future__ import annotations

from pathlib import Path

from .dependency_models import DependencyEdge
from .dependency_build_extract import (
    _extract_slugs_from_text,
    _read_all_feature_content,
)

__all__ = [
    "_build_adjacency",
    "_build_edges",
]


def _build_adjacency(
    resolved_root: Path,
    valid_slugs: list[str],
) -> tuple[dict[str, set[str]], list[DependencyEdge]]:
    adj: dict[str, set[str]] = {slug: set() for slug in valid_slugs}
    edges: list[DependencyEdge] = []

    for slug in valid_slugs:
        content = _read_all_feature_content(resolved_root, slug)
        referenced_slugs = _extract_slugs_from_text(content, slug, set(valid_slugs))
        for ref_slug in referenced_slugs:
            if ref_slug not in adj[slug]:
                adj[slug].add(ref_slug)
                reason = f"Explicit reference in {slug} artifacts"
                edges.append(
                    DependencyEdge(
                        from_slug=slug,
                        to_slug=ref_slug,
                        reason=reason,
                        inference="explicit",
                    )
                )

    return adj, edges
