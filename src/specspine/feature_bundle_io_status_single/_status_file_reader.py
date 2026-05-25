from __future__ import annotations

from pathlib import Path

from ..feature_bundle_models import FEATURE_FILE_PATHS
from ..feature_bundle_io_paths import _relative_feature_paths, feature_bundle_paths
from ..feature_bundle_render import _extract_scalar

__all__ = [
    "read_feature_files",
]


def read_feature_files(
    resolved_root: Path,
    slug: str,
) -> tuple[dict[str, dict[str, object]], list[str], list[str]]:
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = _relative_feature_paths(slug)

    files: dict[str, dict[str, object]] = {}
    missing_files: list[str] = []
    statuses: list[str] = []
    status_missing = False

    for kind in FEATURE_FILE_PATHS:
        path = paths[kind]
        relative_path = relative_paths[kind]
        entry: dict[str, object] = {
            "exists": path.exists(),
            "path": relative_path,
            "status": None,
        }
        if path.exists():
            content = path.read_text(encoding="utf-8")
            status = _extract_scalar(content, "Status")
            entry["status"] = status
            if status:
                statuses.append(status)
            else:
                status_missing = True
        else:
            missing_files.append(relative_path)

        files[kind] = entry

    return files, missing_files, statuses, status_missing
