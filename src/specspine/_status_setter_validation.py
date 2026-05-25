from __future__ import annotations

from pathlib import Path

from .feature_bundle import (
    FeatureStatusReport,
    FeatureStatusTransitionError,
    _transition_payload,
    get_feature_status,
)
from .feature_status_transition import (
    _validate_enforced_feature_transition,
)

__all__ = [
    "_build_transition",
    "_validate_status_preconditions",
]


def _validate_status_preconditions(
    resolved_root: Path,
    slug: str,
    status: str,
    enforce_transition: bool,
) -> tuple[FeatureStatusReport, list[Path]]:
    before = get_feature_status(resolved_root, slug)
    existing_paths = [path for path in _collect_paths(resolved_root, slug).values() if path.exists()]
    if not existing_paths:
        _raise_missing_bundle_error(slug, status, enforce_transition, before)
    return before, existing_paths


def _build_transition(
    resolved_root: Path,
    slug: str,
    status: str,
    before: FeatureStatusReport,
    enforce_transition: bool,
) -> dict:
    if enforce_transition:
        return _validate_enforced_feature_transition(
            resolved_root,
            slug,
            status,
            before,
        )
    return _transition_payload(
        from_status=before.status,
        to_status=status,
        enforced=False,
        allowed=True,
    )


def _collect_paths(resolved_root: Path, slug: str) -> dict:
    from .feature_bundle import feature_bundle_paths
    return feature_bundle_paths(resolved_root, slug)


def _raise_missing_bundle_error(
    slug: str,
    status: str,
    enforce_transition: bool,
    before: FeatureStatusReport,
) -> None:
    from .feature_bundle import (
        FEATURE_FILE_PATHS,
        FeatureBundleNotFoundError,
        FeatureStatusTransitionError,
        _transition_payload,
    )
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
    paths = {kind: _resolve_path(slug, kind) for kind in FEATURE_FILE_PATHS}
    raise FeatureBundleNotFoundError(
        slug=slug,
        root=resolved_root,
        missing_paths=tuple(paths.values()),
    )


def _resolve_path(slug: str, kind: str) -> Path:
    from .feature_bundle import FEATURE_FILE_PATHS
    from pathlib import Path
    return Path(FEATURE_FILE_PATHS[kind].format(slug=slug))
