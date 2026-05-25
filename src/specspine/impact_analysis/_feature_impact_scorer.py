from __future__ import annotations

from pathlib import Path

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
