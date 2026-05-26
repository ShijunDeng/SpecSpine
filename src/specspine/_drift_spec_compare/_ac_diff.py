from __future__ import annotations

__all__ = [
    "_compute_ac_diff",
]


def _compute_ac_diff(
    before_acs: list[str],
    current_acs: list[str],
) -> tuple[list[str], list[str]]:
    before_set = set(before_acs)
    current_set = set(current_acs)

    removed = sorted(before_set - current_set)
    added = sorted(current_set - before_set)

    return removed, added
