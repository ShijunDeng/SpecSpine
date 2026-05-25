from __future__ import annotations

__all__ = [
    "_assemble_recommendations",
]


def _assemble_recommendations(
    cycles: list[tuple[str, ...]],
    topo_order: list[str] | None,
    critical: dict[str, object],
    valid_slugs: list[str],
) -> list[str]:
    recommended: list[str] = []
    if cycles:
        cycle_slugs = ", ".join(c[0] for c in cycles if c)
        recommended.append(
            f"Resolve cycles before implementation: {cycle_slugs}"
        )
    if topo_order:
        recommended.append(
            "Recommended implementation order: " + " -> ".join(topo_order)
        )
    if critical["path"]:
        recommended.append(
            f"Critical path ({critical['total_effort']} effort): {' -> '.join(critical['path'])}"
        )
    if not recommended:
        recommended.append("No dependencies detected; features can be implemented independently.")
    for slug in valid_slugs:
        recommended.append(
            f"specspine feature handoff {slug} . --json"
        )
    return recommended
