from __future__ import annotations

from typing import Any

from .status_features_filters_sorting import (
    _feature_summary_sort_value,
    _feature_summary_sort_metadata_desc,
    _FEATURE_SUMMARY_DEFAULT_VALUES,
)

__all__ = [
    "_sort_feature_summaries",
]


def _sort_feature_summaries(
    filtered: list[dict[str, Any]],
    *,
    sort_key: str | None = None,
    sort_desc: bool = False,
) -> list[dict[str, Any]]:
    if sort_key is not None:
        if sort_desc and sort_key in _FEATURE_SUMMARY_DEFAULT_VALUES:
            return _feature_summary_sort_metadata_desc(filtered, sort_key)
        return sorted(
            filtered,
            key=lambda summary: _feature_summary_sort_value(summary, sort_key),
            reverse=sort_desc,
        )

    if sort_desc:
        filtered.reverse()

    return filtered
