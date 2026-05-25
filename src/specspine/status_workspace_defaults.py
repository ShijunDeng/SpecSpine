from __future__ import annotations

from .features import FeatureMetadata


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
    "_empty_count_summary",
    "_empty_feature_metadata",
]
