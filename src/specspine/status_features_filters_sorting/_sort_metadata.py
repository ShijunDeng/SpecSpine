from __future__ import annotations

from typing import Any

from ._sort_value import _feature_summary_sort_value

__all__ = [
    "_feature_summary_sort_metadata_desc",
]


def _feature_summary_sort_metadata_desc(
    summaries: list[dict[str, Any]],
    sort_key: str,
) -> list[dict[str, Any]]:
    assigned: list[dict[str, Any]] = []
    defaults: list[dict[str, Any]] = []
    for summary in summaries:
        if _feature_summary_sort_value(summary, sort_key)[0] == 0:
            assigned.append(summary)
        else:
            defaults.append(summary)

    def slug_key(summary: dict[str, Any]) -> str:
        return str(summary.get("slug") or summary.get("feature_id") or "")

    assigned_by_slug = sorted(assigned, key=slug_key)
    return [
        *sorted(
            assigned_by_slug,
            key=lambda summary: _feature_summary_sort_value(summary, sort_key)[1:3],
            reverse=True,
        ),
        *sorted(defaults, key=slug_key),
    ]
