from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    FEATURE_TRANSITIONS,
    FeatureStatusReport,
    FeatureStatusTransitionError,
    _transition_payload,
)
from .feature_ready import build_feature_ready_report
from .feature_status_helpers import _allowed_transitions

__all__ = [
    "_validate_enforced_feature_transition",
]


def _validate_enforced_feature_transition(
    root: Path,
    slug: str,
    to_status: str,
    status_report: FeatureStatusReport,
) -> dict[str, object]:
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
            missing_files=status_report.missing_files,
        )

    transition = _transition_payload(
        from_status=from_status,
        to_status=to_status,
        enforced=True,
        allowed=True,
    )
    if to_status == "archived":
        ready_report = build_feature_ready_report(root, slug)
        if not ready_report.ready:
            reason = "Archive requires feature ready gate to pass first."
            raise FeatureStatusTransitionError(
                feature_id=slug,
                error="archive_not_ready",
                transition=_transition_payload(
                    from_status=from_status,
                    to_status=to_status,
                    enforced=True,
                    allowed=True,
                    reason=reason,
                ),
                message=(
                    f"Cannot archive feature {slug}: {reason} "
                    "Run feature ready and resolve blocking checks."
                ),
                blocking_checks=tuple(
                    check.as_dict() for check in ready_report.blocking_checks
                ),
                gaps=ready_report.gaps,
                missing_files=ready_report.missing_files,
            )

    return transition
