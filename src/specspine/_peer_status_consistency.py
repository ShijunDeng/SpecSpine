from __future__ import annotations

from .features import FEATURE_FILE_PATHS, FEATURE_STATUSES
from .validation_feature_helpers import _check
from .validation_models import ValidationCheck

__all__ = [
    "_check_status_consistency",
]


def _check_status_consistency(
    slug: str,
    statuses_by_kind: dict[str, str],
    status_missing: bool,
) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = []
    unique_statuses = sorted(set(statuses_by_kind.values()))
    all_statuses_allowed = all(
        status in FEATURE_STATUSES for status in statuses_by_kind.values()
    )
    statuses_consistent = (
        not status_missing
        and len(statuses_by_kind) == len(FEATURE_FILE_PATHS)
        and len(unique_statuses) == 1
        and all_statuses_allowed
    )
    checks.append(
        _check(
            f"feature.status_consistency:{slug}",
            "pass" if statuses_consistent else "fail",
            f"Feature {slug} peer files consistently declare Status: {unique_statuses[0]}."
            if statuses_consistent
            else f"Feature {slug} peer files must declare the same allowed Status.",
        )
    )
    return checks
