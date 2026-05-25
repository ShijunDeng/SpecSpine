from __future__ import annotations

from pathlib import Path
from typing import Any

from ..dependency import (
    _list_feature_slugs,
    _read_all_feature_content,
)
from ..features import (
    FEATURE_FILE_PATHS,
    read_feature_metadata,
)

from .impact_helpers import _extract_slugs_from_text
from .impact_models import (
    IMPACT_TYPE_FEATURE,
    SEVERITY_HIGH,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    ImpactItem,
)

__all__ = [
    "_find_affected_features",
]


def _find_affected_features(
    slug: str,
    root: Path,
    proposed_changes: dict[str, Any] | None = None,
) -> list[ImpactItem]:
    resolved_root = root.expanduser().resolve()
    all_slugs = _list_feature_slugs(resolved_root)
    if slug not in all_slugs:
        return []

    downstream: dict[str, list[str]] = {s: [] for s in all_slugs}
    for s in all_slugs:
        if s == slug:
            continue
        content = _read_all_feature_content(resolved_root, s)
        referenced = _extract_slugs_from_text(content, s, set(all_slugs))
        if slug in referenced:
            downstream[s].append(slug)

    affected: list[ImpactItem] = []
    seen: set[str] = set()
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

    if proposed_changes and "shared_paths" in proposed_changes:
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
