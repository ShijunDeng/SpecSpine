from __future__ import annotations

from .orchestration_models import ParallelGroup

__all__ = [
    "_compute_parallel_groups",
]


def _compute_parallel_groups(
    execution_order: list[str],
    adj: dict[str, set[str]],
) -> list[ParallelGroup]:
    if not execution_order:
        return []

    order_set = set(execution_order)
    dep_in_degree: dict[str, int] = {s: 0 for s in execution_order}
    for slug in execution_order:
        for dep in adj.get(slug, set()):
            if dep in order_set and dep in dep_in_degree:
                dep_in_degree[slug] = dep_in_degree.get(slug, 0) + 1

    groups: list[ParallelGroup] = []
    remaining = set(execution_order)
    group_id = 1

    while remaining:
        ready = sorted([s for s in remaining if dep_in_degree.get(s, 0) == 0])
        if not ready:
            remaining_sorted = sorted(remaining)
            groups.append(
                ParallelGroup(group_id=group_id, features=tuple(remaining_sorted))
            )
            break
        groups.append(
            ParallelGroup(group_id=group_id, features=tuple(ready))
        )
        for slug in ready:
            remaining.discard(slug)
            for other in remaining:
                if slug in adj.get(other, set()):
                    dep_in_degree[other] -= 1
        group_id += 1

    return groups
