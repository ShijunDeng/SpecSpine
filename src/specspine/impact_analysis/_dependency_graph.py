from __future__ import annotations

from pathlib import Path

from ..dependency import (
    _list_feature_slugs,
    _read_all_feature_content,
)

from .impact_helpers import _extract_slugs_from_text

__all__ = [
    "_build_downstream_map",
]


def _build_downstream_map(
    slug: str,
    resolved_root: Path,
) -> dict[str, list[str]]:
    all_slugs = _list_feature_slugs(resolved_root)
    if slug not in all_slugs:
        return {}

    downstream: dict[str, list[str]] = {s: [] for s in all_slugs}
    for s in all_slugs:
        if s == slug:
            continue
        content = _read_all_feature_content(resolved_root, s)
        referenced = _extract_slugs_from_text(content, s, set(all_slugs))
        if slug in referenced:
            downstream[s].append(slug)

    return downstream
