from __future__ import annotations

from .feature_bundle import (
    FeatureStatusReport,
    FeatureStatusTransitionError,
    _transition_payload,
    FEATURE_TRANSITIONS,
)

__all__ = [
    "_validate_from_status",
]


def _validate_from_status(
    slug: str,
    status_report: FeatureStatusReport,
    to_status: str,
) -> str:
    from_status = status_report.status
    if not status_report.consistent or from_status in {None, "mixed"}:
        reason = "Current peer-file statuses are missing or inconsistent."
        raise FeatureStatusTransitionError(
            feature_id=slug,
            error="current_status_inconsistent",
            transition=_transition_payload(
                from_status=from_status,
                to_status=to_status,
                enforced=True,
                allowed=False,
                reason=reason,
            ),
            message=(
                f"Cannot update feature {slug} status with enforced transition: "
                f"current status is {from_status or 'unknown'}; {reason}"
            ),
            missing_files=status_report.missing_files,
        )

    if from_status not in FEATURE_TRANSITIONS:
        reason = f"Current status '{from_status}' is not a supported lifecycle status."
        raise FeatureStatusTransitionError(
            feature_id=slug,
            error="current_status_invalid",
            transition=_transition_payload(
                from_status=from_status,
                to_status=to_status,
                enforced=True,
                allowed=False,
                reason=reason,
            ),
            message=(
                f"Cannot update feature {slug} status with enforced transition: "
                f"{reason}"
            ),
            missing_files=status_report.missing_files,
        )

    return from_status
