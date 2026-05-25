from __future__ import annotations

from .features import FEATURE_PRIORITIES, FEATURE_STATUSES
from .policy_models import ReadinessCoveragePolicy
from .policy_parser_utils import _dedupe_strings

__all__ = [
    "_build_require_coverage_policy",
]


def _build_require_coverage_policy(values: dict[str, object]) -> ReadinessCoveragePolicy:
    warnings: list[str] = []
    enabled = values.get("enabled", False)
    default = values.get("default", False)
    if not isinstance(enabled, bool):
        warnings.append("readiness.require_coverage.enabled must be true or false.")
        enabled = False
    if not isinstance(default, bool):
        warnings.append("readiness.require_coverage.default must be true or false.")
        default = False

    priorities = _dedupe_strings(values.get("priorities", []))
    statuses = _dedupe_strings(values.get("statuses", []))
    feature_ids = _dedupe_strings(values.get("feature_ids", []))

    for priority in priorities:
        if priority not in FEATURE_PRIORITIES:
            warnings.append(f"Unknown readiness.require_coverage priority: {priority}.")
    for status in statuses:
        if status not in FEATURE_STATUSES:
            warnings.append(f"Unknown readiness.require_coverage status: {status}.")

    return ReadinessCoveragePolicy(
        enabled=enabled,
        default=default,
        priorities=tuple(priority for priority in priorities if priority in FEATURE_PRIORITIES),
        statuses=tuple(status for status in statuses if status in FEATURE_STATUSES),
        feature_ids=feature_ids,
        warnings=tuple(warnings),
    )
