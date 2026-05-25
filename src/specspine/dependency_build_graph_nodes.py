from __future__ import annotations

from pathlib import Path

from .dependency_models import DependencyNode
from .features import read_feature_metadata

__all__ = [
    "_build_node_map",
    "_build_nodes",
]


def _build_node_map(
    resolved_root: Path,
    valid_slugs: list[str],
) -> dict[str, dict[str, object]]:
    node_map: dict[str, dict[str, object]] = {}
    for slug in valid_slugs:
        metadata = read_feature_metadata(resolved_root, slug)
        node_map[slug] = {
            "slug": slug,
            "effort": metadata.effort,
            "milestone": metadata.milestone,
        }
    return node_map


def _build_nodes(
    node_map: dict[str, dict[str, object]],
    valid_slugs: list[str],
) -> list[DependencyNode]:
    return [
        DependencyNode(
            slug=node_map[s]["slug"],
            effort=node_map[s]["effort"],
            milestone=node_map[s]["milestone"],
            dep_count=node_map[s]["dep_count"],
        )
        for s in valid_slugs
    ]
