from __future__ import annotations

from pathlib import Path

from .feature_bundle_models import (
    FEATURE_DIRECTORIES,
    FEATURE_FILE_PATHS,
    InvalidFeatureSlug,
)
from .feature_bundle_io_paths import _relative_feature_paths
from .feature_bundle_io_status_single import get_feature_status


def list_feature_bundles(root: Path) -> list[dict[str, object]]:
    resolved_root = root.expanduser().resolve()
    by_slug: dict[str, dict[str, str]] = {}

    for kind, directory_name in FEATURE_DIRECTORIES.items():
        directory = resolved_root / directory_name
        if not directory.exists():
            continue

        for path in sorted(directory.glob("*.md")):
            slug = path.stem
            relative_path = str(path.relative_to(resolved_root))
            by_slug.setdefault(slug, {})[kind] = relative_path

    features: list[dict[str, object]] = []
    required_kinds = set(FEATURE_FILE_PATHS)
    for slug in sorted(by_slug):
        files = by_slug[slug]
        try:
            status_report = get_feature_status(resolved_root, slug)
            status = status_report.status
            status_consistent = status_report.consistent
            missing_files = list(status_report.missing_files)
        except InvalidFeatureSlug:
            status = None
            status_consistent = False
            missing_files = [
                relative_path.format(slug=slug)
                for kind, relative_path in FEATURE_FILE_PATHS.items()
                if kind not in files
            ]
        features.append(
            {
                "slug": slug,
                "complete": set(files) == required_kinds,
                "files": dict(sorted(files.items())),
                "status": status,
                "status_consistent": status_consistent,
                "missing_files": missing_files,
            }
        )

    return features


__all__ = [
    "list_feature_bundles",
]
