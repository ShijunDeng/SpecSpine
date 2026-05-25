from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .feature_bundle import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    _relative_feature_paths,
    feature_bundle_paths,
)

__all__ = [
    "PrDraftFileCollection",
    "collect_pr_draft_files",
]


@dataclass(frozen=True)
class PrDraftFileCollection:
    contents: dict[str, str]
    source_files: list[str]
    missing_files: list[str]
    spec_content: str
    relative_paths: dict[str, str]


def collect_pr_draft_files(root: Path, slug: str) -> PrDraftFileCollection:
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = _relative_feature_paths(slug)

    contents: dict[str, str] = {}
    source_files: list[str] = []
    missing_files: list[str] = []
    missing_paths: list[Path] = []

    for kind in FEATURE_FILE_PATHS:
        path = paths[kind]
        relative_path = relative_paths[kind]
        if path.exists():
            contents[kind] = path.read_text(encoding="utf-8")
            source_files.append(relative_path)
            continue

        missing_files.append(relative_path)
        missing_paths.append(path)

    if not contents:
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(missing_paths),
        )

    spec_content = contents.get("spec", "")

    return PrDraftFileCollection(
        contents=contents,
        source_files=source_files,
        missing_files=missing_files,
        spec_content=spec_content,
        relative_paths=relative_paths,
    )
