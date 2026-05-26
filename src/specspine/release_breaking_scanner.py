from __future__ import annotations

from pathlib import Path
from typing import Any

from .release_breaking_file_reader import _read_feature_content
from .release_models import (
    BreakingChange,
    ReleaseEntry,
    _BREAKING_CHANGE_PATTERNS,
)

__all__ = [
    "_detect_breaking_changes",
]


def _detect_breaking_changes(
    features: list[ReleaseEntry],
    root: Path,
) -> list[BreakingChange]:
    resolved_root = root.expanduser().resolve()
    breaking: list[BreakingChange] = []

    for feature in features:
        slug = feature.slug
        full_content = _read_feature_content(slug, resolved_root)

        seen_types: set[str] = set()
        for pattern, severity, description in _BREAKING_CHANGE_PATTERNS:
            matches = pattern.findall(full_content)
            if matches:
                if description in seen_types:
                    continue
                seen_types.add(description)
                affected: list[str] = []
                for match in matches:
                    if isinstance(match, str):
                        affected.append(match)
                    elif isinstance(match, tuple):
                        affected.extend(m for m in match if m)

                breaking.append(
                    BreakingChange(
                        feature_id=slug,
                        description=f"[{description}] {feature.title}",
                        severity=severity,
                        affected_commands=tuple(sorted(set(affected))),
                    )
                )

    breaking.sort(key=lambda bc: (bc.severity, bc.feature_id))
    return breaking
