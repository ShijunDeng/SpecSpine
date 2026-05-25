from __future__ import annotations

from .health_models import QualityGates, ReadinessGates

__all__ = [
    "compute_readiness_score",
    "compute_gates_score",
]


def compute_readiness_score(readiness: ReadinessGates) -> int:
    total_ready = readiness.features_total
    if total_ready == 0:
        return 15
    return int(15 * readiness.ready / total_ready)


def compute_gates_score(quality_gates: QualityGates) -> int:
    total_gates = quality_gates.required_total
    if total_gates == 0:
        return 5
    return int(5 * quality_gates.required_done / total_gates)
