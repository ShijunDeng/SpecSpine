from __future__ import annotations

from pathlib import Path

from ..feature_bundle import (
    FeatureBundleNotFoundError,
    FeatureStatusReport,
    FeatureStatusTransitionError,
    _transition_payload,
)

__all__ = [
    "_check_bundle_exists",
]


def _check_bundle_exists(
    slug: str,
    status: str,
    resolved_root: Path,
    paths: dict[str, Path],
    before: FeatureStatusReport,
    enforce_transition: bool,
) -> None:
    existing_paths = [path for path in paths.values() if path.exists()]
    if not existing_paths:
        if enforce_transition:
            reason = "Current peer-file statuses are missing or inconsistent."
            raise FeatureStatusTransitionError(
                feature_id=slug,
                error="current_status_inconsistent",
                transition=_transition_payload(
                    from_status=before.status,
                    to_status=status,
                    enforced=True,
                    allowed=False,
                    reason=reason,
                ),
                message=(
                    f"Cannot update feature {slug} status with enforced transition: "
                    f"current status is unknown; {reason}"
                ),
                missing_files=before.missing_files,
            )
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(paths.values()),
        )
