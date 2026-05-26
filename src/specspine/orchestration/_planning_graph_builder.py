from __future__ import annotations

from pathlib import Path

from ..dependency import (
    _extract_slugs_from_text,
    _read_all_feature_content,
)

__all__ = [
    "_build_dependency_graph",
]


def _build_dependency_graph(root: Path, slugs: list[str]) -> dict[str, set[str]]:
    adj: dict[str, set[str]] = {s: set() for s in slugs}
    for slug in slugs:
        content = _read_all_feature_content(root, slug)
        referenced = _extract_slugs_from_text(content, slug, set(slugs))
        for ref in referenced:
            if ref in adj:
                adj[slug].add(ref)
    return adj
