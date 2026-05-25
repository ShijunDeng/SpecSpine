from __future__ import annotations

from pathlib import Path
from typing import Any

from .adapters import ADAPTER_SPECS, AdapterStatus
from .features import FeatureMetadata, list_feature_bundles
from .fusion import FUSION_REQUIRED_FILES
from .status_workspace_parsers import _read_yaml_section
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


def _upstream_status(root: Path) -> dict[str, dict[str, Any]]:
    spine_adapters = _read_yaml_section(root / ".specspine" / "spine.yaml", "adapters")
    fusion_upstreams = _read_yaml_section(root / ".specspine" / "fusion.yaml", "upstreams")

    upstreams: dict[str, dict[str, Any]] = {}
    for key, spec in ADAPTER_SPECS.items():
        spine_config = spine_adapters.get(key, {})
        fusion_config = fusion_upstreams.get(key, {})
        adapter_path = spine_config.get("config")
        if not isinstance(adapter_path, str) or not adapter_path:
            adapter_path = f".specspine/adapters/{key}.md"

        enabled = fusion_config.get("enabled", spine_config.get("enabled", False))
        if not isinstance(enabled, bool):
            enabled = False

        upstreams[key] = {
            "display_name": spec.display_name,
            "enabled": enabled,
            "config": adapter_path,
            "config_exists": (root / adapter_path).exists(),
            "role": spec.role,
            "upstream_url": spec.upstream_url,
        }

    return upstreams


def _adapter_statuses(statuses: list[AdapterStatus]) -> dict[str, dict[str, Any]]:
    return {
        status.key: {
            "display_name": status.display_name,
            "available": status.available,
            "detail": status.detail,
            "version": status.version,
            "command": status.command,
            "install_hint": status.install_hint,
            "upstream_url": status.upstream_url,
        }
        for status in statuses
    }


def _empty_count_summary() -> dict[str, int]:
    return {
        "done": 0,
        "open": 0,
        "total": 0,
    }


def _empty_feature_metadata() -> FeatureMetadata:
    return FeatureMetadata(
        priority="unknown",
        owner="unassigned",
        milestone="unassigned",
        target_release="unassigned",
        project="unassigned",
        effort="unknown",
    )


__all__ = [
    "_adapter_statuses",
    "_artifact_status",
    "_empty_count_summary",
    "_empty_feature_metadata",
    "_upstream_status",
]
