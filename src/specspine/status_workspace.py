from __future__ import annotations

from pathlib import Path
from typing import Any

from .adapters import ADAPTER_SPECS, AdapterStatus
from .features import FEATURE_STATUSES, FeatureMetadata, list_feature_bundles
from .fusion import FUSION_REQUIRED_FILES
from .workspace import BASE_WORKSPACE_FILES

__all__ = [
    "InvalidFeatureSummaryOption",
    "FEATURE_SUMMARY_STATUS_FILTERS",
    "FEATURE_SUMMARY_PRIORITY_FILTERS",
    "FEATURE_SUMMARY_READY_VALUES",
    "FEATURE_SUMMARY_SORT_KEYS",
    "_FEATURE_SUMMARY_STATUS_ORDER",
    "_FEATURE_SUMMARY_PRIORITY_ORDER",
    "_FEATURE_SUMMARY_EFFORT_ORDER",
    "_FEATURE_SUMMARY_DEFAULT_VALUES",
    "_relative_paths",
    "_clean_scalar",
    "_parse_two_level_yaml_section",
    "_read_yaml_section",
    "_artifact_status",
    "_upstream_status",
    "_adapter_statuses",
    "_empty_count_summary",
    "_empty_feature_metadata",
]

AdapterProbe = Any  # type alias defined in status.py re-export

FEATURE_SUMMARY_STATUS_FILTERS = (*FEATURE_STATUSES, "invalid", "unknown")
FEATURE_SUMMARY_PRIORITY_FILTERS = ("high", "medium", "low", "unknown")
FEATURE_SUMMARY_READY_VALUES = {
    "yes": True,
    "true": True,
    "ready": True,
    "no": False,
    "false": False,
    "not-ready": False,
}
FEATURE_SUMMARY_SORT_KEYS = (
    "slug",
    "status",
    "ready",
    "gaps",
    "blocking",
    "tasks-open",
    "priority",
    "milestone",
    "target-release",
    "project",
    "effort",
)
_FEATURE_SUMMARY_STATUS_ORDER = {
    status: index
    for index, status in enumerate(FEATURE_STATUSES)
}
_FEATURE_SUMMARY_STATUS_ORDER["invalid"] = len(_FEATURE_SUMMARY_STATUS_ORDER)
_FEATURE_SUMMARY_STATUS_ORDER["unknown"] = len(_FEATURE_SUMMARY_STATUS_ORDER)
_FEATURE_SUMMARY_PRIORITY_ORDER = {
    "high": 0,
    "medium": 1,
    "low": 2,
    "unknown": 3,
}
_FEATURE_SUMMARY_EFFORT_ORDER = {
    "xs": 0,
    "s": 1,
    "m": 2,
    "l": 3,
    "xl": 4,
    "xxl": 5,
    "unknown": 6,
}
_FEATURE_SUMMARY_DEFAULT_VALUES = {
    "milestone": "unassigned",
    "target-release": "unassigned",
    "project": "unassigned",
    "effort": "unknown",
}


class InvalidFeatureSummaryOption(ValueError):
    """Raised when a feature summary filter or sort option is unsupported."""


def _relative_paths(paths: list[Path], root: Path) -> list[str]:
    return sorted(str(path.relative_to(root)) for path in paths)


def _clean_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _parse_two_level_yaml_section(content: str, section: str) -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    in_section = False
    current_key: str | None = None

    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent == 0:
            in_section = stripped == f"{section}:"
            current_key = None
            continue

        if not in_section:
            continue

        if indent == 2 and stripped.endswith(":"):
            current_key = stripped[:-1]
            values.setdefault(current_key, {})
            continue

        if indent == 4 and current_key and ":" in stripped:
            key, value = stripped.split(":", 1)
            values[current_key][key.strip()] = _clean_scalar(value)

    return values


def _read_yaml_section(path: Path, section: str) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}

    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return {}

    return _parse_two_level_yaml_section(content, section)


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
