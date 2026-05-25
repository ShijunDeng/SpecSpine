from __future__ import annotations

from pathlib import Path

from .features import (
    feature_bundle_paths,
    parse_acceptance_criteria,
)

__all__ = [
    "_extract_ac_ids",
    "_read_feature_contents",
]


def _read_feature_contents(root: Path, slug: str) -> dict[str, str]:
    paths = feature_bundle_paths(root, slug)
    contents: dict[str, str] = {}
    for kind in ("spec", "execution", "quality"):
        path = paths.get(kind)
        if path and path.exists():
            contents[kind] = path.read_text(encoding="utf-8")
    return contents


def _extract_ac_ids(contents: dict[str, str]) -> tuple[str, ...]:
    spec_content = contents.get("spec", "")
    if not spec_content:
        return ()
    ac_items = parse_acceptance_criteria(spec_content, source_file="")
    return tuple(item.id for item in ac_items)
