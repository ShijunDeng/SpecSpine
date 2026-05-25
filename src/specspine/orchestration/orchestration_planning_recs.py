from __future__ import annotations

__all__ = [
    "_generate_integration_recommendations",
]


def _generate_integration_recommendations(
    conflicts: list,
    execution_order: list[str],
    adj: dict[str, set[str]],
) -> list[str]:
    recommendations: list[str] = []
    if not conflicts and not execution_order:
        recommendations.append("No integration steps required; no features or conflicts detected.")
        return recommendations

    file_conflicts = [c for c in conflicts if c.conflict_type == "file"]
    contract_conflicts = [c for c in conflicts if c.conflict_type == "contract"]

    if file_conflicts:
        affected_features: set[str] = set()
        for c in file_conflicts:
            affected_features.update(c.features_involved)
        features_str = ", ".join(sorted(affected_features))
        recommendations.append(
            f"File overlap detected for features: {features_str}. "
            "Coordinate implementation order and run consistency scan after each feature."
        )

    if contract_conflicts:
        affected_features: set[str] = set()
        for c in contract_conflicts:
            affected_features.update(c.features_involved)
        features_str = ", ".join(sorted(affected_features))
        recommendations.append(
            f"Contract overlap detected for features: {features_str}. "
            "Define shared API contracts or data schemas before implementation."
        )

    if len(execution_order) > 1:
        recommendations.append(
            f"Run integration tests after each group in execution order: {' -> '.join(execution_order)}."
        )

    deps_with_multiple = [
        slug for slug in execution_order
        if len(adj.get(slug, set())) > 1
    ]
    if deps_with_multiple:
        features_str = ", ".join(deps_with_multiple)
        recommendations.append(
            f"Features with multiple dependencies ({features_str}) need integration validation "
            "after all dependencies are implemented."
        )

    if not recommendations:
        recommendations.append("No cross-feature integration steps detected.")

    return recommendations
