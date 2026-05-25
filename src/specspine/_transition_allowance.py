from __future__ import annotations

from .feature_bundle import (
    FeatureStatusTransitionError,
    _transition_payload,
    FEATURE_TRANSITIONS,
)

__all__ = [
    "_validate_transition_allowed",
]


def _validate_transition_allowed(
    slug: str,
    from_status: str,
    to_status: str,
    missing_files: tuple[str, ...],
) -> dict[str, object]:
    allowed_targets = FEATURE_TRANSITIONS[from_status]
    if to_status not in allowed_targets:
        if from_status == "archived":
            reason = "Archived is terminal and cannot transition to another status."
        else:
            reason = (
                f"Transition {from_status} -> {to_status} is not allowed; "
                f"allowed targets are: {', '.join(allowed_targets)}."
            )
        raise FeatureStatusTransitionError(
            feature_id=slug,
            error="transition_not_allowed",
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
            missing_files=missing_files,
        )

    return _transition_payload(
        from_status=from_status,
        to_status=to_status,
        enforced=True,
        allowed=True,
    )
