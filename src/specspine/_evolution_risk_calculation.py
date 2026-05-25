from __future__ import annotations

from .evolution_classification import ClassifiedChange
from .evolution_impact_models import ImpactEntry

__all__ = [
    "calculate_risk_level",
]


def calculate_risk_level(change: ClassifiedChange, impact: ImpactEntry) -> str:
    if change.change_type == "removed" and change.category == "ac":
        if impact.severity in ("breaking", "warning"):
            return "breaking"
    if change.change_type == "modified" and change.category == "ac":
        if impact.severity == "warning":
            return "warning"
    if change.change_type == "removed" and change.category == "task":
        if impact.severity == "breaking":
            return "breaking"
        return "warning"
    if change.change_type == "modified" and impact.severity == "warning":
        return "warning"
    return "info"
