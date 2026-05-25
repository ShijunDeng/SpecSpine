from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    FeatureStatusTransitionError,
    _transition_payload,
)
from .feature_ready import build_feature_ready_report

__all__ = [
    "_validate_archive_gate",
]


def _validate_archive_gate(
    root: Path,
    slug: str,
    from_status: str,
    to_status: str,
    missing_files: tuple[str, ...],
) -> None:
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
