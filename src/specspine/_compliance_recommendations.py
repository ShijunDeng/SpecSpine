from __future__ import annotations

__all__ = [
    "_generate_recommendations",
]


def _generate_recommendations(gaps: list[str]) -> list[str]:
    recommendations: list[str] = []
    for gap in gaps:
        if "missing spec" in gap:
            recommendations.append(f"Create spec file for {gap.split(':')[0]}")
        elif "missing execution" in gap:
            recommendations.append(f"Create execution file for {gap.split(':')[0]}")
        elif "missing quality" in gap:
            recommendations.append(f"Create quality file for {gap.split(':')[0]}")
        elif "Uncovered ACs" in gap:
            slug_part = gap.split(":")[0]
            recommendations.append(f"Add test coverage links for uncovered ACs in {slug_part}")
        elif "no lifecycle transitions" in gap:
            recommendations.append(f"Record lifecycle transitions for {gap.split(':')[0]}")

    if not recommendations:
        recommendations.append("All features pass compliance checks")

    return recommendations
