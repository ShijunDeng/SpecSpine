from __future__ import annotations

from .release_models import ReleaseEntry

__all__ = [
    "_group_features",
]


def _group_features(
    features: list[ReleaseEntry],
    group_by: str,
) -> dict[str, list[ReleaseEntry]]:
    groups: dict[str, list[ReleaseEntry]] = {}
    for feature in features:
        if group_by == "priority":
            key = feature.priority
        elif group_by == "project":
            key = feature.project
        elif group_by == "status":
            key = feature.status_transition
        elif group_by == "effort":
            key = feature.effort
        else:
            key = "all"

        groups.setdefault(key, []).append(feature)

    sorted_groups: dict[str, list[ReleaseEntry]] = {}
    for key in sorted(groups):
        sorted_groups[key] = sorted(groups[key], key=lambda e: e.slug)
    return sorted_groups
