from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import (
    FEATURE_FILE_PATHS,
    read_feature_metadata,
)

from .impact_models import (
    IMPACT_TYPE_FEATURE,
    SEVERITY_HIGH,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    ImpactItem,
)

__all__ = [
    "_score_feature_impact",
    "_analyze_shared_paths",
]


def _score_feature_impact(
    slug: str,
    downstream: dict[str, list[str]],
    resolved_root: Path,
    seen: set[str],
) -> list[ImpactItem]:
    affected: list[ImpactItem] = []
    for s in sorted(downstream):
        if slug in downstream[s] and s not in seen:
            seen.add(s)
            metadata = read_feature_metadata(resolved_root, s)
            severity = SEVERITY_HIGH if metadata.priority == "high" else (
                SEVERITY_MEDIUM if metadata.priority == "medium" else SEVERITY_LOW
            )
            affected.append(
                ImpactItem(
                    type=IMPACT_TYPE_FEATURE,
                    id=s,
                    path=FEATURE_FILE_PATHS["spec"].format(slug=s),
                    severity=severity,
                    reason=f"Feature '{s}' depends on '{slug}'",
                )
            )
    return affected


def _analyze_shared_paths(
    slug: str,
    proposed_changes: dict[str, Any],
    all_slugs: list[str],
    resolved_root: Path,
    seen: set[str],
) -> list[ImpactItem]:
    affected: list[ImpactItem] = []
    shared_paths = proposed_changes["shared_paths"]
    for s in sorted(all_slugs):
        if s == slug or s in seen:
            continue
        for kind in FEATURE_FILE_PATHS:
            file_path = resolved_root / FEATURE_FILE_PATHS[kind].format(slug=s)
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                for line in content.splitlines():
                    stripped = line.strip().lower()
                    for sp in shared_paths:
                        if sp.lower() in stripped and len(sp) > 3:
                            seen.add(s)
                            affected.append(
                                ImpactItem(
                                    type=IMPACT_TYPE_FEATURE,
                                    id=s,
                                    path=FEATURE_FILE_PATHS[kind].format(slug=s),
                                    severity=SEVERITY_MEDIUM,
                                    reason=f"Feature '{s}' shares file path reference '{sp}' with '{slug}'",
                                )
                            )
                            break
                    if s in seen:
                        break
            if s in seen:
                break
    return affected
