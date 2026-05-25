from __future__ import annotations

from typing import Any

__all__ = [
    "_classify_root_causes",
]


def _classify_root_causes(gaps: list[dict[str, str]]) -> dict[str, Any]:
    categories: dict[str, list[dict[str, str]]] = {
        "missing_spec": [],
        "missing_code": [],
        "missing_test": [],
        "stale_coverage": [],
        "contract_violation": [],
    }

    for gap in gaps:
        gap_id = gap.get("id", "")
        gap_message = gap.get("message", "").lower()

        if any(
            kw in gap_id.lower() or kw in gap_message
            for kw in ("missing_file", "missing_spec", "spec")
        ):
            categories["missing_spec"].append(gap)
        elif any(
            kw in gap_id.lower() or kw in gap_message
            for kw in ("missing_code", "implementation", "not_implemented")
        ):
            categories["missing_code"].append(gap)
        elif any(
            kw in gap_id.lower() or kw in gap_message
            for kw in ("missing_test", "test_coverage", "coverage", "no test")
        ):
            categories["missing_test"].append(gap)
        elif any(
            kw in gap_id.lower() or kw in gap_message
            for kw in ("stale", "outdated", "unknown_acceptance")
        ):
            categories["stale_coverage"].append(gap)
        else:
            categories["contract_violation"].append(gap)

    return {
        category: items
        for category, items in categories.items()
    }
