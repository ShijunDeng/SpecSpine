from __future__ import annotations

import re

from ..evolution_impact_models import DEPENDENCY_PATTERNS, FEATURE_ID_RE


def _extract_feature_refs(text: str) -> list[str]:
    refs: list[str] = []
    for pattern in DEPENDENCY_PATTERNS:
        refs.extend(pattern.findall(text))
    refs.extend(FEATURE_ID_RE.findall(text))
    return sorted(set(refs))


def _extract_metadata(content: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    keys = {"Priority", "Owner", "Milestone", "Target Release", "Project", "Effort", "Status"}
    for line in content.splitlines():
        stripped = line.strip()
        if ":" in stripped and not stripped.startswith("#"):
            key, _, value = stripped.partition(":")
            key = key.strip()
            if key in keys:
                metadata[key] = value.strip()
    return metadata


__all__ = [
    "_extract_feature_refs",
    "_extract_metadata",
]
