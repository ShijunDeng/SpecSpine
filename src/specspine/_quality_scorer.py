from __future__ import annotations

from .health_models import ConsistencyDrift, CoverageDebt, ValidationHealth

__all__ = [
    "compute_validation_score",
    "compute_coverage_score",
    "compute_consistency_score",
]


def compute_validation_score(validation: ValidationHealth) -> int:
    if validation.total == 0:
        return 20
    return int(20 * validation.pass_count / validation.total)


def compute_coverage_score(coverage: CoverageDebt) -> int:
    total_ac = coverage.acceptance_criteria_total
    if total_ac == 0:
        return 20
    return int(20 * coverage.covered_acceptance_criteria / total_ac)


def compute_consistency_score(consistency: ConsistencyDrift) -> int:
    total_checks = consistency.checks_total
    if total_checks == 0:
        return 15
    return int(15 * consistency.checks_pass / total_checks)
