from __future__ import annotations

from pathlib import Path
from typing import Any

from .features import FEATURE_FILE_PATHS
from .release_models import (
    BreakingChange,
    ReleaseEntry,
    _BREAKING_CHANGE_PATTERNS,
)

__all__ = [
    "_compute_summary",
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
        spec_path = resolved_root / FEATURE_FILE_PATHS["spec"].format(slug=slug)
        execution_path = resolved_root / FEATURE_FILE_PATHS["execution"].format(slug=slug)

        contents: list[str] = []
        for path in (spec_path, execution_path):
            if path.exists():
                try:
                    contents.append(path.read_text(encoding="utf-8"))
                except OSError:
                    pass

        full_content = "\n".join(contents)

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


def _compute_summary(
    features: list[ReleaseEntry],
    breaking_changes: list[BreakingChange],
) -> dict[str, Any]:
    total = len(features)
    validated = sum(1 for f in features if f.status_transition == "newly validated")
    archived = sum(1 for f in features if f.status_transition == "released (archived)")

    high_breaking = sum(1 for bc in breaking_changes if bc.severity == "high")
    medium_breaking = sum(1 for bc in breaking_changes if bc.severity == "medium")
    low_breaking = sum(1 for bc in breaking_changes if bc.severity == "low")

    priority_counts: dict[str, int] = {}
    for f in features:
        priority_counts[f.priority] = priority_counts.get(f.priority, 0) + 1

    total_validation_evidence = sum(f.validation_evidence_count for f in features)

    summary: dict[str, Any] = {
        "features_total": total,
        "features_validated": validated,
        "features_archived": archived,
        "breaking_changes_total": len(breaking_changes),
        "breaking_changes_high": high_breaking,
        "breaking_changes_medium": medium_breaking,
        "breaking_changes_low": low_breaking,
        "priority_counts": dict(sorted(priority_counts.items())),
        "total_validation_evidence": total_validation_evidence,
    }

    return summary
