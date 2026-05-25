from __future__ import annotations

from typing import Any

from .audit_models import AuditTrail
from ._compliance_dimension_checker import _evaluate_trail_dimensions


def _generate_compliance_summary(trails: list[AuditTrail]) -> dict[str, Any]:
    pass_fail: dict[str, str] = {}
    gaps: list[str] = []
    total_features = len(trails)
    compliant_features = 0

    for trail in trails:
        trail_pass_fail, trail_gaps, feature_compliant = _evaluate_trail_dimensions(trail)
        pass_fail.update(trail_pass_fail)
        gaps.extend(trail_gaps)
        if feature_compliant:
            compliant_features += 1

    total_checks = len(pass_fail)
    passed_checks = sum(1 for v in pass_fail.values() if v == "pass")

    return {
        "compliant_features": compliant_features,
        "gaps": gaps,
        "pass_fail_per_dimension": pass_fail,
        "total_checks": total_checks,
        "total_features": total_features,
        "passed_checks": passed_checks,
        "compliance_rate": (
            round(compliant_features / total_features, 2) if total_features > 0 else 0.0
        ),
    }


__all__ = [
    "_generate_compliance_summary",
]
