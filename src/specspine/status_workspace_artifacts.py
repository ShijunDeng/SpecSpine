from __future__ import annotations

from pathlib import Path
from typing import Any

from .fusion import FUSION_REQUIRED_FILES
from .features import list_feature_bundles
from .workspace import BASE_WORKSPACE_FILES


def _artifact_status(root: Path) -> dict[str, dict[str, Any]]:
    artifacts: dict[str, dict[str, Any]] = {}

    for relative_path in sorted(BASE_WORKSPACE_FILES):
        artifacts[relative_path] = {
            "exists": (root / relative_path).exists(),
            "required_for": ["workspace"],
        }

    for relative_path in sorted(FUSION_REQUIRED_FILES):
        entry = artifacts.setdefault(
            relative_path,
            {
                "exists": (root / relative_path).exists(),
                "required_for": [],
            },
        )
        entry["exists"] = (root / relative_path).exists()
        if "fusion" not in entry["required_for"]:
            entry["required_for"].append("fusion")

    for feature in list_feature_bundles(root):
        slug = str(feature["slug"])
        files = feature["files"]
        if not isinstance(files, dict):
            continue

        for relative_path in sorted(str(path) for path in files.values()):
            artifacts[relative_path] = {
                "exists": True,
                "required_for": ["feature", f"feature:{slug}"],
            }

    return artifacts


__all__ = [
    "_artifact_status",
]
