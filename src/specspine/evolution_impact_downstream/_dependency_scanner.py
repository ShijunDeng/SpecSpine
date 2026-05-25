from __future__ import annotations

from pathlib import Path

from ..features import (
    FEATURE_FILE_PATHS,
    list_feature_bundles,
)
from ._extractors import _extract_feature_refs

__all__ = [
    "_scan_dependency_downstream",
]


def _scan_dependency_downstream(
    slug: str,
    root: Path,
    all_features: list[dict],
) -> list[dict[str, str]]:
    references: list[dict[str, str]] = []
    for feature in all_features:
        feature_slug = feature["slug"]
        if feature_slug == slug:
            continue
        for file_kind in FEATURE_FILE_PATHS:
            file_path = root / FEATURE_FILE_PATHS[file_kind].format(slug=feature_slug)
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                feature_refs = _extract_feature_refs(content)
                if slug in feature_refs:
                    references.append({
                        "feature_id": feature_slug,
                        "reference_type": file_kind,
                    })
    return references
