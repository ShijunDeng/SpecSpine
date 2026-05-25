from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    FeatureStatusReport,
    FeatureStatusTransitionError,
    _relative_feature_paths,
    _transition_payload,
    feature_bundle_paths,
    get_feature_status,
    validate_feature_slug,
    validate_feature_status,
)
from ._status_setter_transition import _build_transition
from ._status_setter_file_writer import _write_status_to_files

__all__ = [
    "FeatureStatusTransitionError",
    "set_feature_status",
    "_validate_enforced_feature_transition",
    "_allowed_transitions",
]


def set_feature_status(
    root: Path,
    slug: str,
    status: str,
    *,
    enforce_transition: bool = False,
) -> FeatureStatusReport:
    slug = validate_feature_slug(slug)
    status = validate_feature_status(status)
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    relative_paths = _relative_feature_paths(slug)

    before = get_feature_status(resolved_root, slug)
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

    transition = _build_transition(
        resolved_root, slug, status, before, enforce_transition,
    )

    updated_files = _write_status_to_files(paths, slug, status)

    report = get_feature_status(resolved_root, slug)
    return FeatureStatusReport(
        feature_id=report.feature_id,
        status=report.status,
        consistent=report.consistent,
        files=report.files,
        missing_files=report.missing_files,
        updated_files=tuple(updated_files),
        transition=transition,
    )


def _validate_enforced_feature_transition(*args, **kwargs):
    from .feature_status_transition import _validate_enforced_feature_transition
    return _validate_enforced_feature_transition(*args, **kwargs)


def _allowed_transitions(*args, **kwargs):
    from .feature_status_helpers import _allowed_transitions
    return _allowed_transitions(*args, **kwargs)
