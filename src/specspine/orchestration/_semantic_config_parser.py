from __future__ import annotations

from pathlib import Path

from ..features import validate_feature_slug
from ..dependency import _read_all_feature_content

__all__ = [
    "_parse_feature_configs",
]


def _parse_feature_configs(root: Path, feature_id: str) -> tuple[str, dict[str, str]]:
    """Parse feature flag configurations from feature content.

    Returns:
        Tuple of (validated_feature_id, configs_dict) where configs_dict
        maps flag names to their action keywords (enable/disable).
    """
    feature_id = validate_feature_slug(feature_id)
    content = _read_all_feature_content(root, feature_id)
    configs: dict[str, str] = {}
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("- ") and ("enable" in line or "disable" in line):
            for keyword in ["enable", "disable", "toggle", "flag"]:
                if keyword in line.lower():
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if keyword in part.lower() and i + 1 < len(parts):
                            flag_name = parts[i + 1].strip(".,;:")
                            if flag_name and flag_name not in ("the", "a", "an"):
                                configs[flag_name.lower()] = keyword
    return feature_id, configs
